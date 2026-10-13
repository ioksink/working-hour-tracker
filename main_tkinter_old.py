import tkinter as tk
from tkinter import messagebox
from datetime import datetime

from database import Database
from excel_export import export_month
from nas_backup import backup_to_nas


class WorkTrackerApp:

    def __init__(self, root):

        self.root = root

        self.root.title(
            "Working Hours Tracker"
        )

        self.root.geometry("800x950")

        self.root.resizable(
            True,
            True
        )

        # ---------------------------------
        # DATABASE
        # ---------------------------------

        self.database = Database()

        # Automatically close unfinished
        # sessions from previous days
        closed_sessions = (
            self.database.close_old_unfinished_sessions()
        )

        # ---------------------------------
        # CURRENT SESSION
        # ---------------------------------

        self.current_session = (
            self.database.get_open_session()
        )

        # ---------------------------------
        # CREATE UI
        # ---------------------------------

        self.create_ui()

        # ---------------------------------
        # NOTIFY ABOUT AUTO-CLOSED SESSION
        # ---------------------------------

        if closed_sessions:

            messagebox.showwarning(
                "Unfinished Work Session",
                "A previous work session was not "
                "closed.\n\n"
                "The end time was automatically "
                "set to 18:00.\n\n"
                "You can edit the record if needed."
            )

        # ---------------------------------
        # RESTORE CURRENT STATE
        # ---------------------------------

        self.update_ui_state()

        # Start live clock
        self.update_clock()

    # =====================================
    # CREATE USER INTERFACE
    # =====================================

    def create_ui(self):

        # Main title
        title = tk.Label(
            self.root,
            text="Working Hours Tracker",
            font=(
                "Lucida Sans",
                12,
                "bold"
            )
        )

        title.pack(
            pady=20
        )

        # ---------------------------------
        # CURRENT DATE
        # ---------------------------------

        self.date_label = tk.Label(
            self.root,
            font=(
                "Lucida Sans",
                12
            )
        )

        self.date_label.pack(
            pady=5
        )

        # ---------------------------------
        # STATUS
        # ---------------------------------

        self.status_label = tk.Label(
            self.root,
            text="Status: Not Working",
            font=(
                "Lucida Sans",
                15,
                "bold"
            )
        )

        self.status_label.pack(
            pady=10
        )

        # ---------------------------------
        # LIVE TIMER
        # ---------------------------------

        self.timer_label = tk.Label(
            self.root,
            text="00:00:00",
            font=(
                "Lucida Sans",
                32,
                "bold"
            )
        )

        self.timer_label.pack(
            pady=10
        )

        # ---------------------------------
        # INFO LABEL
        # ---------------------------------

        self.info_label = tk.Label(
            self.root,
            text="",
            font=(
                "Lucida Sans",
                11
            )
        )

        self.info_label.pack(
            pady=5
        )

        # =================================
        # BUTTON FRAME
        # =================================

        button_frame = tk.Frame(
            self.root
        )

        button_frame.pack(
            pady=15
        )

        # ---------------------------------
        # START WORK
        # ---------------------------------

        self.start_button = tk.Button(
            button_frame,
            text="▶ Start Work",
            width=22,
            height=2,
            font=(
                "Lucida Sans",
                12,
                "bold"
            ),
            command=self.start_work
        )

        self.start_button.grid(
            row=0,
            column=0,
            padx=5,
            pady=5
        )

        # ---------------------------------
        # START BREAK
        # ---------------------------------

        self.start_break_button = tk.Button(
            button_frame,
            text="☕ Start Break",
            width=22,
            height=2,
            font=(
                "Lucida Sans",
                12
            ),
            command=self.start_break
        )

        self.start_break_button.grid(
            row=1,
            column=0,
            padx=5,
            pady=5
        )

        # ---------------------------------
        # END BREAK
        # ---------------------------------

        self.end_break_button = tk.Button(
            button_frame,
            text="▶ End Break",
            width=22,
            height=2,
            font=(
                "Lucida Sans",
                12
            ),
            command=self.end_break
        )

        self.end_break_button.grid(
            row=2,
            column=0,
            padx=5,
            pady=5
        )

        # ---------------------------------
        # END WORK
        # ---------------------------------

        self.end_button = tk.Button(
            button_frame,
            text="■ End Work",
            width=22,
            height=2,
            font=(
                "Lucida Sans",
                12,
                "bold"
            ),
            command=self.end_work
        )

        self.end_button.grid(
            row=3,
            column=0,
            padx=5,
            pady=5
        )

        # =================================
        # BOTTOM BUTTONS
        # =================================

        bottom_frame = tk.Frame(
            self.root
        )

        bottom_frame.pack(
            pady=15
        )

        # ---------------------------------
        # EXPORT EXCEL
        # ---------------------------------

        self.export_button = tk.Button(
            bottom_frame,
            text="Export Monthly Excel",
            command=self.export_excel
        )

        self.export_button.grid(
            row=0,
            column=0,
            padx=5
        )

        # ---------------------------------
        # BACKUP NAS
        # ---------------------------------

        self.backup_button = tk.Button(
            bottom_frame,
            text="Backup to NAS",
            command=self.backup_nas
        )

        self.backup_button.grid(
            row=0,
            column=1,
            padx=5
        )

    # =====================================
    # START WORK
    # =====================================

    def start_work(self):

        session_id = (
            self.database.start_work()
        )

        if session_id is None:

            messagebox.showwarning(
                "Already Working",
                "There is already an active "
                "work session."
            )

            return

        self.current_session = (
            self.database.get_open_session()
        )

        self.backup_silently()

        self.update_ui_state()

    # =====================================
    # START BREAK
    # =====================================

    def start_break(self):

        if not self.current_session:

            messagebox.showwarning(
                "No Work Session",
                "Start work before starting "
                "a break."
            )

            return

        result = (
            self.database.start_break(
                self.current_session["id"]
            )
        )

        if result is None:

            messagebox.showwarning(
                "Break Already Active",
                "You are already on a break."
            )

            return

        self.backup_silently()

        self.update_ui_state()

    # =====================================
    # END BREAK
    # =====================================

    def end_break(self):

        if not self.current_session:

            return

        result = (
            self.database.end_break(
                self.current_session["id"]
            )
        )

        if not result:

            messagebox.showwarning(
                "No Active Break",
                "There is no active break."
            )

            return

        self.backup_silently()

        self.update_ui_state()

    # =====================================
    # END WORK
    # =====================================

    def end_work(self):

        if not self.current_session:

            messagebox.showwarning(
                "No Active Session",
                "There is no active work session."
            )

            return

        # Check for an active break
        active_break = (
            self.database.get_open_break(
                self.current_session["id"]
            )
        )

        if active_break:

            answer = messagebox.askyesno(
                "Active Break",
                "You currently have an active "
                "break.\n\n"
                "Do you want to end the break "
                "and end work now?"
            )

            if not answer:
                return

            self.database.end_break(
                self.current_session["id"]
            )

        # End work
        self.database.end_work(
            self.current_session["id"]
        )

        self.backup_silently()

        messagebox.showinfo(
            "Work Finished",
            "Your working session has been "
            "recorded."
        )

        self.current_session = None

        self.update_ui_state()

    # =====================================
    # EXPORT EXCEL
    # =====================================

    def export_excel(self):

        now = datetime.now()

        filename = export_month(
            self.database,
            now.year,
            now.month
        )

        if filename:

            messagebox.showinfo(
                "Export Successful",
                f"Excel file created:\n\n"
                f"{filename}"
            )

        else:

            messagebox.showwarning(
                "No Data",
                "No completed work sessions "
                "were found for this month."
            )

    # =====================================
    # NAS BACKUP
    # =====================================

    def backup_nas(self):

        success, message = (
            backup_to_nas()
        )

        if success:

            messagebox.showinfo(
                "NAS Backup",
                message
            )

        else:

            messagebox.showwarning(
                "NAS Backup Failed",
                message
            )

    def backup_silently(self):

        backup_to_nas()

    # =====================================
    # UPDATE UI
    # =====================================

    def update_ui_state(self):

        # No active session
        if not self.current_session:

            self.status_label.config(
                text="Status: Not Working"
            )

            self.info_label.config(
                text=""
            )

            self.start_button.config(
                state=tk.NORMAL
            )

            self.start_break_button.config(
                state=tk.DISABLED
            )

            self.end_break_button.config(
                state=tk.DISABLED
            )

            self.end_button.config(
                state=tk.DISABLED
            )

            return

        # Active session
        session_id = (
            self.current_session["id"]
        )

        active_break = (
            self.database.get_open_break(
                session_id
            )
        )

        start_time = datetime.fromisoformat(
            self.current_session["start_time"]
        )

        self.info_label.config(
            text=(
                f"Started: "
                f"{start_time.strftime('%H:%M:%S')}"
            )
        )

        self.start_button.config(
            state=tk.DISABLED
        )

        self.end_button.config(
            state=tk.NORMAL
        )

        # On break
        if active_break:

            self.status_label.config(
                text="Status: On Break"
            )

            self.start_break_button.config(
                state=tk.DISABLED
            )

            self.end_break_button.config(
                state=tk.NORMAL
            )

        # Working
        else:

            self.status_label.config(
                text="Status: Working"
            )

            self.start_break_button.config(
                state=tk.NORMAL
            )

            self.end_break_button.config(
                state=tk.DISABLED
            )

    # =====================================
    # LIVE CLOCK / TIMER
    # =====================================

    def update_clock(self):

        now = datetime.now()

        self.date_label.config(
            text=now.strftime(
                "%A, %d.%m.%Y"
            )
        )

        if self.current_session:

            start_time = datetime.fromisoformat(
                self.current_session["start_time"]
            )

            elapsed = now - start_time

            total_seconds = int(
                elapsed.total_seconds()
            )

            hours = (
                total_seconds // 3600
            )

            minutes = (
                total_seconds % 3600
            ) // 60

            seconds = (
                total_seconds % 60
            )

            self.timer_label.config(
                text=(
                    f"{hours:02d}:"
                    f"{minutes:02d}:"
                    f"{seconds:02d}"
                )
            )

        else:

            self.timer_label.config(
                text="00:00:00"
            )

        # Update every second
        self.root.after(
            1000,
            self.update_clock
        )

    # =====================================
    # CLOSE APPLICATION
    # =====================================

    def on_close(self):

        self.database.close()

        self.root.destroy()


# =========================================
# START APPLICATION
# =========================================

if __name__ == "__main__":

    root = tk.Tk()

    app = WorkTrackerApp(root)

    root.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )

    root.mainloop()