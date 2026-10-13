import sqlite3
from datetime import datetime, date, time
from pathlib import Path


DB_FILE = Path("work_hours.db")


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

        self.create_tables()

    def create_tables(self):
        # Main work sessions
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_date TEXT NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,

                end_button_pressed INTEGER DEFAULT 0,
                automatic_end INTEGER DEFAULT 0,
                end_time_edited INTEGER DEFAULT 0,

                notes TEXT DEFAULT ''
            )
        """)

        # Breaks belonging to a work session
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS breaks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,

                start_time TEXT NOT NULL,
                end_time TEXT,

                FOREIGN KEY(session_id)
                    REFERENCES work_sessions(id)
            )
        """)

        self.conn.commit()

    # -------------------------------------------------
    # WORK SESSION
    # -------------------------------------------------

    def start_work(self):
        now = datetime.now()

        # Check if there is already an open session
        open_session = self.get_open_session()

        if open_session:
            return None

        self.cursor.execute("""
            INSERT INTO work_sessions (
                work_date,
                start_time
            )
            VALUES (?, ?)
        """, (
            now.date().isoformat(),
            now.isoformat()
        ))

        self.conn.commit()

        return self.cursor.lastrowid

    def end_work(self, session_id):
        now = datetime.now()

        self.cursor.execute("""
            UPDATE work_sessions
            SET
                end_time = ?,
                end_button_pressed = 1,
                automatic_end = 0
            WHERE id = ?
        """, (
            now.isoformat(),
            session_id
        ))

        self.conn.commit()

    def get_open_session(self):
        self.cursor.execute("""
            SELECT *
            FROM work_sessions
            WHERE end_time IS NULL
            ORDER BY id DESC
            LIMIT 1
        """)

        return self.cursor.fetchone()

    # -------------------------------------------------
    # BREAKS
    # -------------------------------------------------

    def start_break(self, session_id):
        now = datetime.now()

        # Don't allow multiple simultaneous breaks
        open_break = self.get_open_break(session_id)

        if open_break:
            return None

        self.cursor.execute("""
            INSERT INTO breaks (
                session_id,
                start_time
            )
            VALUES (?, ?)
        """, (
            session_id,
            now.isoformat()
        ))

        self.conn.commit()

        return self.cursor.lastrowid

    def end_break(self, session_id):
        now = datetime.now()

        open_break = self.get_open_break(session_id)

        if not open_break:
            return False

        self.cursor.execute("""
            UPDATE breaks
            SET end_time = ?
            WHERE id = ?
        """, (
            now.isoformat(),
            open_break["id"]
        ))

        self.conn.commit()

        return True

    def get_open_break(self, session_id):
        self.cursor.execute("""
            SELECT *
            FROM breaks
            WHERE session_id = ?
            AND end_time IS NULL
            ORDER BY id DESC
            LIMIT 1
        """, (session_id,))

        return self.cursor.fetchone()

    # -------------------------------------------------
    # AUTOMATIC END AT 18:00
    # -------------------------------------------------

    def close_old_unfinished_sessions(self):
        """
        Close unfinished sessions from previous days.

        End time is automatically set to 18:00.
        """

        today = date.today()

        self.cursor.execute("""
            SELECT *
            FROM work_sessions
            WHERE end_time IS NULL
        """)

        sessions = self.cursor.fetchall()

        closed_sessions = []

        for session in sessions:
            session_date = date.fromisoformat(
                session["work_date"]
            )

            # Never close today's active session automatically
            if session_date < today:

                automatic_end = datetime.combine(
                    session_date,
                    time(18, 0)
                )

                note = (
                    "End button was not pressed. "
                    "End time automatically set to 18:00."
                )

                self.cursor.execute("""
                    UPDATE work_sessions
                    SET
                        end_time = ?,
                        end_button_pressed = 0,
                        automatic_end = 1,
                        notes = ?
                    WHERE id = ?
                """, (
                    automatic_end.isoformat(),
                    note,
                    session["id"]
                ))

                closed_sessions.append(session)

        self.conn.commit()

        return closed_sessions

    # -------------------------------------------------
    # EDIT SESSION
    # -------------------------------------------------

    def update_end_time(self, session_id, new_end_time):
        """
        Edit an end time.

        IMPORTANT:
        The original audit note is preserved.
        """

        self.cursor.execute("""
            UPDATE work_sessions
            SET
                end_time = ?,
                end_time_edited = 1
            WHERE id = ?
        """, (
            new_end_time.isoformat(),
            session_id
        ))

        self.conn.commit()

    # -------------------------------------------------
    # DATA RETRIEVAL
    # -------------------------------------------------

    def get_sessions_for_month(self, year, month):

        month_prefix = f"{year:04d}-{month:02d}"

        self.cursor.execute("""
            SELECT *
            FROM work_sessions
            WHERE work_date LIKE ?
            AND end_time IS NOT NULL
            ORDER BY work_date ASC
        """, (
            f"{month_prefix}%",
        ))

        return self.cursor.fetchall()

    def get_breaks_for_session(self, session_id):

        self.cursor.execute("""
            SELECT *
            FROM breaks
            WHERE session_id = ?
            ORDER BY start_time
        """, (
            session_id,
        ))

        return self.cursor.fetchall()
    # -------------------------------------------------
    # CLOSE DATABASE
    # -------------------------------------------------

    def close(self):
        self.conn.close()
    
    def update_session(self, session_id, work_date, start_time, end_time):
        """
        Update the date/start/end time of a work session.

        Existing audit information is deliberately preserved.
        """
        self.cursor.execute("""
            UPDATE work_sessions
            SET
                work_date = ?,
                start_time = ?,
                end_time = ?,
                end_time_edited = 1
            WHERE id = ?
        """, (
            work_date,
            start_time.isoformat(),
            end_time.isoformat(),
            session_id
        ))
        self.conn.commit()

    def delete_session(self, session_id):
        """
        Delete a work session and its associated breaks.
        """

        self.cursor.execute("""
            DELETE FROM breaks
            WHERE session_id = ?
        """, (session_id,))

        self.cursor.execute("""
            DELETE FROM work_sessions
            WHERE id = ?
        """, (session_id,))

        self.conn.commit()