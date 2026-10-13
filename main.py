import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, timedelta

from database import Database
from excel_export import export_month
from nas_backup import backup_to_nas


# -------------------------------------------------
# APPEARANCE
# -------------------------------------------------

ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")
ctk.set_widget_scaling(2)
ctk.set_window_scaling(2)

class WorkTrackerApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Work Hours")

        # Larger modern window
        self.root.geometry("800x950")

        # Allow resizing
        self.root.minsize(600, 700)

        # -------------------------------------------------
        # DATABASE
        # -------------------------------------------------

        self.database = Database()

        # Automatically close unfinished sessions
        # from previous days.
        closed_sessions = (
            self.database.close_old_unfinished_sessions()
        )

        # Current active work session
        self.current_session = (
            self.database.get_open_session()
        )

        # -------------------------------------------------
        # UI
        # -------------------------------------------------

        self.create_ui()

        # -------------------------------------------------
        # HANDLE AUTOMATICALLY CLOSED SESSIONS
        # -------------------------------------------------

        if closed_sessions:

            messagebox.showwarning(
                "Unfinished Work Session",
                "A previous work session was not closed.\n\n"
                "The end time was automatically set to 18:00.\n\n"
                "You can edit the record later if necessary."
            )

        # Update UI
        self.update_ui_state()

        # Start clock
        self.update_clock()

    # =================================================
    # UI
    # =================================================

    def create_ui(self):

        # -------------------------------------------------
        # MAIN CONTAINER
        # -------------------------------------------------

        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=0,
            fg_color="transparent"
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=25
        )

        # -------------------------------------------------
        # HEADER
        # -------------------------------------------------

        header_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        header_frame.pack(
            fill="x"
        )

        self.title_label = ctk.CTkLabel(
            header_frame,
            text="Work Hours",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        self.title_label.pack(
            side="left"
        )

        self.status_badge = ctk.CTkLabel(
            header_frame,
            text="● NOT WORKING",
            corner_radius=12,
            padx=15,
            pady=7,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            )
        )

        self.status_badge.pack(
            side="right"
        )

        # -------------------------------------------------
        # DATE
        # -------------------------------------------------

        self.date_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(
                size=15
            )
        )

        self.date_label.pack(
            pady=(25, 5)
        )

        # -------------------------------------------------
        # TIMER
        # -------------------------------------------------

        self.timer_label = ctk.CTkLabel(
            self.main_frame,
            text="00:00:00",
            font=ctk.CTkFont(
                size=52,
                weight="bold"
            )
        )

        self.timer_label.pack(
            pady=(5, 0)
        )

        self.timer_description = ctk.CTkLabel(
            self.main_frame,
            text="Today's elapsed time",
            font=ctk.CTkFont(
                size=14
            )
        )

        self.timer_description.pack(
            pady=(0, 25)
        )

        # -------------------------------------------------
        # SUMMARY CARD
        # -------------------------------------------------

        summary_card = ctk.CTkFrame(
            self.main_frame,
            corner_radius=18
        )

        summary_card.pack(
            fill="x",
            pady=5
        )

        summary_card.grid_columnconfigure(
            (0, 1, 2),
            weight=1
        )

        # Start
        self.start_value = ctk.CTkLabel(
            summary_card,
            text="--:--",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        self.start_value.grid(
            row=0,
            column=0,
            pady=(20, 3)
        )

        ctk.CTkLabel(
            summary_card,
            text="Started",
            font=ctk.CTkFont(size=12)
        ).grid(
            row=1,
            column=0,
            pady=(0, 20)
        )

        # Break
        self.break_value = ctk.CTkLabel(
            summary_card,
            text="00:00",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        self.break_value.grid(
            row=0,
            column=1,
            pady=(20, 3)
        )

        ctk.CTkLabel(
            summary_card,
            text="Break",
            font=ctk.CTkFont(size=12)
        ).grid(
            row=1,
            column=1,
            pady=(0, 20)
        )

        # Net
        self.net_value = ctk.CTkLabel(
            summary_card,
            text="00:00",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        self.net_value.grid(
            row=0,
            column=2,
            pady=(20, 3)
        )

        ctk.CTkLabel(
            summary_card,
            text="Net Work",
            font=ctk.CTkFont(size=12)
        ).grid(
            row=1,
            column=2,
            pady=(0, 20)
        )

        # -------------------------------------------------
        # START WORK BUTTON
        # -------------------------------------------------

        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="▶   START WORK",
            height=60,
            corner_radius=15,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            command=self.start_work
        )

        self.start_button.pack(
            fill="x",
            pady=(25, 10)
        )

        # -------------------------------------------------
        # BREAK BUTTONS
        # -------------------------------------------------

        break_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        break_frame.pack(
            fill="x",
            pady=5
        )

        break_frame.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        self.start_break_button = ctk.CTkButton(
            break_frame,
            text="☕  START BREAK",
            height=50,
            corner_radius=13,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            command=self.start_break
        )

        self.start_break_button.grid(
            row=0,
            column=0,
            padx=(0, 5),
            sticky="ew"
        )

        self.end_break_button = ctk.CTkButton(
            break_frame,
            text="▶  END BREAK",
            height=50,
            corner_radius=13,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            command=self.end_break
        )

        self.end_break_button.grid(
            row=0,
            column=1,
            padx=(5, 0),
            sticky="ew"
        )

        # -------------------------------------------------
        # END WORK
        # -------------------------------------------------

        self.end_button = ctk.CTkButton(
            self.main_frame,
            text="■   END WORK",
            height=60,
            corner_radius=15,
            font=ctk.CTkFont(
                size=18,
                weight="bold"
            ),
            command=self.end_work
        )

        self.end_button.pack(
            fill="x",
            pady=(10, 20)
        )

        # -------------------------------------------------
        # DIVIDER
        # -------------------------------------------------

        divider = ctk.CTkFrame(
            self.main_frame,
            height=2,
            fg_color=("gray80", "gray25")
        )

        divider.pack(
            fill="x",
            pady=5
        )

        # -------------------------------------------------
        # BOTTOM ACTIONS
        # -------------------------------------------------

        actions_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        actions_frame.pack(
            fill="x",
            pady=20
        )

        actions_frame.grid_columnconfigure(
            (0, 1, 2),
            weight=1
        )

        # Export
        self.export_button = ctk.CTkButton(
            actions_frame,
            text="📊\nMonthly Report",
            font=ctk.CTkFont(
                size=17
            ),
            height=70,
            corner_radius=13,
            command=self.export_excel
        )

        self.export_button.grid(
            row=0,
            column=0,
            padx=5,
            sticky="ew"
        )

        # NAS
        self.backup_button = ctk.CTkButton(
            actions_frame,
            text="☁\nNAS Backup",
            font=ctk.CTkFont(
                size=17
            ),
            height=70,
            corner_radius=13,
            command=self.backup_nas
        )

        self.backup_button.grid(
            row=0,
            column=1,
            padx=5,
            sticky="ew"
        )

        # Edit placeholder
        self.edit_button = ctk.CTkButton(
            actions_frame,
            text="✎\nEdit Records",
            font=ctk.CTkFont(
                size=17
            ),
            height=70,
            corner_radius=13,
            command=self.edit_records
        )

        self.edit_button.grid(
            row=0,
            column=2,
            padx=5,
            sticky="ew"
        )

        # -------------------------------------------------
        # FOOTER
        # -------------------------------------------------

        self.footer_label = ctk.CTkLabel(
            self.main_frame,
            text="Work Hours Tracker Ver 1.0",
            font=ctk.CTkFont(
                size=15
            ),
            text_color=("gray50", "gray60")
        )

        self.footer_label.pack(
            pady=(5, 0)
        )

    # =================================================
    # START WORK
    # =================================================

    def start_work(self):

        session_id = (
            self.database.start_work()
        )

        if session_id is None:

            messagebox.showwarning(
                "Already Working",
                "There is already an active work session."
            )

            return

        self.current_session = (
            self.database.get_open_session()
        )

        self.backup_silently()

        self.update_ui_state()

    # =================================================
    # START BREAK
    # =================================================

    def start_break(self):

        if not self.current_session:

            messagebox.showwarning(
                "No Work Session",
                "Start work before starting a break."
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

    # =================================================
    # END BREAK
    # =================================================

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

    # =================================================
    # END WORK
    # =================================================

    def end_work(self):

        if not self.current_session:

            messagebox.showwarning(
                "No Active Session",
                "There is no active work session."
            )

            return

        # Check active break
        active_break = (
            self.database.get_open_break(
                self.current_session["id"]
            )
        )

        if active_break:

            answer = messagebox.askyesno(
                "Active Break",
                "You are currently on a break.\n\n"
                "Do you want to end the break and end work?"
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

        self.current_session = None

        self.update_ui_state()

        messagebox.showinfo(
            "Work Finished",
            "Your working session has been recorded."
        )

    # =================================================
    # UPDATE UI STATE
    # =================================================

    def update_ui_state(self):

        # ---------------------------------------------
        # NOT WORKING
        # ---------------------------------------------

        if not self.current_session:

            self.status_badge.configure(
                text="●  NOT WORKING"
            )

            self.timer_description.configure(
                text="Ready to start"
            )

            self.start_button.configure(
                state="normal"
            )

            self.start_break_button.configure(
                state="disabled"
            )

            self.end_break_button.configure(
                state="disabled"
            )

            self.end_button.configure(
                state="disabled"
            )

            self.start_value.configure(
                text="--:--"
            )

            self.break_value.configure(
                text="00:00"
            )

            self.net_value.configure(
                text="00:00"
            )

            return

        # ---------------------------------------------
        # WORKING
        # ---------------------------------------------

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

        self.start_value.configure(
            text=start_time.strftime("%H:%M")
        )

        self.start_button.configure(
            state="disabled"
        )

        self.end_button.configure(
            state="normal"
        )

        # ---------------------------------------------
        # BREAK
        # ---------------------------------------------

        if active_break:

            self.status_badge.configure(
                text="●  ON BREAK"
            )

            self.timer_description.configure(
                text="Break in progress"
            )

            self.start_break_button.configure(
                state="disabled"
            )

            self.end_break_button.configure(
                state="normal"
            )

        # ---------------------------------------------
        # NORMAL WORK
        # ---------------------------------------------

        else:

            self.status_badge.configure(
                text="●  WORKING"
            )

            self.timer_description.configure(
                text="Today's elapsed time"
            )

            self.start_break_button.configure(
                state="normal"
            )

            self.end_break_button.configure(
                state="disabled"
            )

    # =================================================
    # LIVE TIMER
    # =================================================

    def update_clock(self):

        now = datetime.now()

        self.date_label.configure(
            text=now.strftime(
                "%A, %d %B %Y"
            )
        )

        if self.current_session:

            start_time = datetime.fromisoformat(
                self.current_session["start_time"]
            )

            elapsed = (
                now - start_time
            )

            total_seconds = max(
                0,
                int(elapsed.total_seconds())
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

            self.timer_label.configure(
                text=(
                    f"{hours:02d}:"
                    f"{minutes:02d}:"
                    f"{seconds:02d}"
                )
            )

            # Update break and net time
            self.update_summary()

        else:

            self.timer_label.configure(
                text="00:00:00"
            )

        self.root.after(
            1000,
            self.update_clock
        )

    # =================================================
    # SUMMARY
    # =================================================

    def update_summary(self):

        if not self.current_session:
            return

        session_id = (
            self.current_session["id"]
        )

        now = datetime.now()

        start = datetime.fromisoformat(
            self.current_session["start_time"]
        )

        total_break = timedelta()

        breaks = (
            self.database.get_breaks_for_session(
                session_id
            )
        )

        for item in breaks:

            break_start = datetime.fromisoformat(
                item["start_time"]
            )

            if item["end_time"]:

                break_end = datetime.fromisoformat(
                    item["end_time"]
                )

            else:

                break_end = now

            total_break += (
                break_end - break_start
            )

        gross = now - start

        net = gross - total_break

        self.break_value.configure(
            text=self.format_duration(
                total_break
            )
        )

        self.net_value.configure(
            text=self.format_duration(
                net
            )
        )

    # =================================================
    # FORMAT DURATION
    # =================================================

    @staticmethod
    def format_duration(duration):

        total_seconds = max(
            0,
            int(duration.total_seconds())
        )

        hours = (
            total_seconds // 3600
        )

        minutes = (
            total_seconds % 3600
        ) // 60

        return f"{hours:02d}:{minutes:02d}"

    # =================================================
    # EXPORT EXCEL
    # =================================================

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
                f"Excel report created:\n\n{filename}"
            )

        else:

            messagebox.showwarning(
                "No Data",
                "No completed work sessions were found "
                "for this month."
            )

    # =================================================
    # NAS BACKUP
    # =================================================

    def backup_nas(self):

        success, message = (
            backup_to_nas()
        )

        if success:

            messagebox.showinfo(
                "NAS Backup",
                "Your work-hours database has been "
                "backed up to the NAS."
            )

        else:

            messagebox.showwarning(
                "NAS Backup",
                f"Backup failed:\n\n{message}"
            )

    def backup_silently(self):

        backup_to_nas()

    # =================================================
    # EDIT RECORDS
    # =================================================
    def edit_records(self):

        EditRecordsWindow(
            self.root,
            self.database,
            self
        )

    # =================================================
    # CLOSE
    # =================================================

    def on_close(self):

        self.database.close()

        self.root.destroy()


# =====================================================
# START APPLICATION
# =====================================================

class EditRecordsWindow:

    def __init__(
        self,
        parent,
        database,
        main_app
    ):

        self.database = database
        self.main_app = main_app

        # ---------------------------------------------
        # WINDOW
        # ---------------------------------------------

        self.window = ctk.CTkToplevel(parent)

        self.window.title(
            "Edit Working Hours"
        )

        self.window.geometry(
            "950x650"
        )

        self.window.minsize(
            850,
            550
        )

        self.window.transient(parent)

        # Bring window to front
        self.window.lift()
        self.window.focus_force()

        # ---------------------------------------------
        # MAIN FRAME
        # ---------------------------------------------

        self.main_frame = ctk.CTkFrame(
            self.window,
            fg_color="transparent"
        )

        self.main_frame.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=25
        )

        # ---------------------------------------------
        # HEADER
        # ---------------------------------------------

        header = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            pady=(0, 20)
        )

        ctk.CTkLabel(
            header,
            text="Edit Working Hours",
            font=ctk.CTkFont(
                size=26,
                weight="bold"
            )
        ).pack(
            side="left"
        )

        # ---------------------------------------------
        # MONTH SELECTOR
        # ---------------------------------------------

        selector = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        selector.pack(
            fill="x",
            pady=(0, 15)
        )

        ctk.CTkLabel(
            selector,
            text="Month:",
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            )
        ).pack(
            side="left",
            padx=(0, 10)
        )

        now = datetime.now()

        self.month_var = ctk.StringVar(
            value=now.strftime("%Y-%m")
        )

        self.month_entry = ctk.CTkEntry(
            selector,
            width=140,
            textvariable=self.month_var
        )

        self.month_entry.pack(
            side="left"
        )

        self.load_button = ctk.CTkButton(
            selector,
            text="Load",
            width=100,
            command=self.load_records
        )

        self.load_button.pack(
            side="left",
            padx=10
        )

        # ---------------------------------------------
        # TABLE CONTAINER
        # ---------------------------------------------

        self.table_frame = ctk.CTkScrollableFrame(
            self.main_frame,
            corner_radius=15
        )

        self.table_frame.pack(
            fill="both",
            expand=True
        )

        # Column widths
        self.table_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self.table_frame.grid_columnconfigure(
            1,
            weight=1
        )

        self.table_frame.grid_columnconfigure(
            2,
            weight=1
        )

        self.table_frame.grid_columnconfigure(
            3,
            weight=1
        )

        self.table_frame.grid_columnconfigure(
            4,
            weight=1
        )

        self.table_frame.grid_columnconfigure(
            5,
            weight=3
        )

        self.table_frame.grid_columnconfigure(
            6,
            weight=1
        )

        # ---------------------------------------------
        # FOOTER
        # ---------------------------------------------

        footer = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )

        footer.pack(
            fill="x",
            pady=(15, 0)
        )

        self.close_button = ctk.CTkButton(
            footer,
            text="Close",
            width=120,
            command=self.window.destroy
        )

        self.close_button.pack(
            side="right"
        )

        # ---------------------------------------------
        # LOAD
        # ---------------------------------------------

        self.load_records()

    # =================================================
    # LOAD RECORDS
    # =================================================

    def load_records(self):

        # Remove previous rows
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        try:

            year, month = map(
                int,
                self.month_var.get().split("-")
            )

        except ValueError:

            messagebox.showerror(
                "Invalid Month",
                "Please enter the month as:\n\n"
                "YYYY-MM\n\n"
                "Example: 2026-08"
            )

            return

        sessions = (
            self.database.get_sessions_for_month(
                year,
                month
            )
        )

        # ---------------------------------------------
        # TABLE HEADER
        # ---------------------------------------------

        headers = [
            "Date",
            "Start",
            "End",
            "Break",
            "Net",
            "Status / Notes",
            "Action"
        ]

        for column, header in enumerate(headers):

            label = ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=ctk.CTkFont(
                    size=13,
                    weight="bold"
                )
            )

            label.grid(
                row=0,
                column=column,
                padx=8,
                pady=12,
                sticky="w"
            )

        # ---------------------------------------------
        # RECORDS
        # ---------------------------------------------

        if not sessions:

            ctk.CTkLabel(
                self.table_frame,
                text="No records found for this month.",
                font=ctk.CTkFont(
                    size=15
                )
            ).grid(
                row=1,
                column=0,
                columnspan=7,
                pady=40
            )

            return

        for row, session in enumerate(
            sessions,
            start=1
        ):

            start = datetime.fromisoformat(
                session["start_time"]
            )

            end = datetime.fromisoformat(
                session["end_time"]
            )

            breaks = (
                self.database.get_breaks_for_session(
                    session["id"]
                )
            )

            break_duration = (
                self.calculate_break_duration(
                    breaks
                )
            )

            gross = end - start

            net = (
                gross - break_duration
            )

            # -----------------------------------------
            # STATUS
            # -----------------------------------------

            if session["automatic_end"]:

                status = "⚠ AUTO END"

            elif session["end_time_edited"]:

                status = "✎ EDITED"

            else:

                status = "✓ NORMAL"

            # -----------------------------------------
            # VALUES
            # -----------------------------------------

            values = [
                start.strftime("%d.%m.%Y"),
                start.strftime("%H:%M"),
                end.strftime("%H:%M"),
                self.format_duration(
                    break_duration
                ),
                self.format_duration(
                    net
                ),
                status
            ]

            for column, value in enumerate(values):

                label = ctk.CTkLabel(
                    self.table_frame,
                    text=value,
                    anchor="w"
                )

                label.grid(
                    row=row,
                    column=column,
                    padx=8,
                    pady=8,
                    sticky="w"
                )

            # -----------------------------------------
            # EDIT BUTTON
            # -----------------------------------------

            button_frame = ctk.CTkFrame(
                self.table_frame,
                fg_color="transparent"
            )

            button_frame.grid(
                row=row,
                column=6,
                padx=5,
                pady=5
            )

            edit_button = ctk.CTkButton(
                button_frame,
                text="Edit",
                width=65,
                command=lambda s=session:
                    self.edit_session(s)
            )

            edit_button.pack(
                side="left",
                padx=2
            )

            delete_button = ctk.CTkButton(
                button_frame,
                text="X",
                width=65,
                fg_color="red",
                command=lambda s=session:
                    self.delete_session(s)
            )

            delete_button.pack(
                side="left",
                padx=2
            )

            # -----------------------------------------
            # NOTE
            # -----------------------------------------

            if session["notes"]:

                note_label = ctk.CTkLabel(
                    self.table_frame,
                    text=session["notes"],
                    text_color=(
                        "gray50",
                        "gray65"
                    ),
                    anchor="w",
                    justify="left"
                )

                note_label.grid(
                    row=row + 1000,
                    column=0,
                    columnspan=7,
                    padx=8,
                    pady=(0, 8),
                    sticky="w"
                )

    # =================================================
    # EDIT SESSION
    # =================================================

    def edit_session(self, session):

        dialog = ctk.CTkToplevel(
            self.window
        )

        dialog.title(
            "Edit Work Session"
        )

        dialog.geometry(
            "500x550"
        )

        dialog.transient(
            self.window
        )

        dialog.grab_set()

        # ---------------------------------------------
        # CONTAINER
        # ---------------------------------------------

        frame = ctk.CTkFrame(
            dialog,
            fg_color="transparent"
        )

        frame.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=30
        )

        # ---------------------------------------------
        # TITLE
        # ---------------------------------------------

        ctk.CTkLabel(
            frame,
            text="Edit Work Session",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        ).pack(
            pady=(0, 25)
        )

        # ---------------------------------------------
        # DATE
        # ---------------------------------------------

        ctk.CTkLabel(
            frame,
            text="Date",
            anchor="w"
        ).pack(
            fill="x"
        )

        date_entry = ctk.CTkEntry(
            frame,
            placeholder_text="YYYY-MM-DD"
        )

        date_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        date_entry.insert(
            0,
            session["work_date"]
        )

        # ---------------------------------------------
        # START
        # ---------------------------------------------

        ctk.CTkLabel(
            frame,
            text="Start time",
            anchor="w"
        ).pack(
            fill="x"
        )

        start_entry = ctk.CTkEntry(
            frame,
            placeholder_text="HH:MM"
        )

        start_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        start_original = datetime.fromisoformat(
            session["start_time"]
        )

        start_entry.insert(
            0,
            start_original.strftime("%H:%M")
        )

        # ---------------------------------------------
        # END
        # ---------------------------------------------

        ctk.CTkLabel(
            frame,
            text="End time",
            anchor="w"
        ).pack(
            fill="x"
        )

        end_entry = ctk.CTkEntry(
            frame,
            placeholder_text="HH:MM"
        )

        end_entry.pack(
            fill="x",
            pady=(5, 15)
        )

        end_original = datetime.fromisoformat(
            session["end_time"]
        )

        end_entry.insert(
            0,
            end_original.strftime("%H:%M")
        )

        # ---------------------------------------------
        # AUDIT INFORMATION
        # ---------------------------------------------

        audit_text = ""

        if session["automatic_end"]:

            audit_text = (
                "⚠ This session was automatically "
                "ended at 18:00 because the End Work "
                "button was not pressed."
            )

        elif session["end_button_pressed"]:

            audit_text = (
                "✓ End Work button was pressed."
            )

        if session["notes"]:

            audit_text += (
                "\n\nOriginal note:\n"
                + session["notes"]
            )

        audit_label = ctk.CTkLabel(
            frame,
            text=audit_text,
            anchor="w",
            justify="left",
            wraplength=430
        )

        audit_label.pack(
            fill="x",
            pady=(5, 20)
        )

        # ---------------------------------------------
        # SAVE
        # ---------------------------------------------

        def save_changes():

            try:

                new_date = (
                    datetime.strptime(
                        date_entry.get().strip(),
                        "%Y-%m-%d"
                    )
                )

                new_start = (
                    datetime.strptime(
                        start_entry.get().strip(),
                        "%H:%M"
                    )
                )

                new_end = (
                    datetime.strptime(
                        end_entry.get().strip(),
                        "%H:%M"
                    )
                )

            except ValueError:

                messagebox.showerror(
                    "Invalid Time",
                    "Please use:\n\n"
                    "Date: YYYY-MM-DD\n"
                    "Time: HH:MM",
                    parent=dialog
                )

                return

            start_datetime = datetime.combine(
                new_date.date(),
                new_start.time()
            )

            end_datetime = datetime.combine(
                new_date.date(),
                new_end.time()
            )

            # Handle overnight sessions
            if end_datetime < start_datetime:

                end_datetime += timedelta(
                    days=1
                )

            if end_datetime == start_datetime:

                messagebox.showerror(
                    "Invalid Time",
                    "Start and end time cannot be identical.",
                    parent=dialog
                )

                return

            # -----------------------------------------
            # SAVE
            # -----------------------------------------

            self.database.update_session(
                session["id"],
                new_date.date().isoformat(),
                start_datetime,
                end_datetime
            )

            # Backup
            backup_to_nas()

            dialog.destroy()

            self.load_records()

            # Update main application
            self.main_app.current_session = (
                self.database.get_open_session()
            )

            self.main_app.update_ui_state()

            messagebox.showinfo(
                "Saved",
                "The work session was updated.",
                parent=self.window
            )

        save_button = ctk.CTkButton(
            frame,
            text="Save Changes",
            height=45,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=save_changes
        )

        save_button.pack(
            fill="x",
            pady=5
        )

        # ---------------------------------------------
        # CANCEL
        # ---------------------------------------------

        cancel_button = ctk.CTkButton(
            frame,
            text="Cancel",
            height=40,
            fg_color="red",
            text_color="black",
            command=dialog.destroy
        )

        cancel_button.pack(
            fill="x",
            pady=5
        )

    # =================================================
    # BREAK CALCULATION
    # =================================================

    def calculate_break_duration(
        self,
        breaks
    ):

        total = timedelta()

        for item in breaks:

            if item["end_time"]:

                start = datetime.fromisoformat(
                    item["start_time"]
                )

                end = datetime.fromisoformat(
                    item["end_time"]
                )

                total += (
                    end - start
                )

        return total

    # =================================================
    # FORMAT DURATION
    # =================================================

    @staticmethod
    def format_duration(duration):

        total_seconds = max(
            0,
            int(duration.total_seconds())
        )

        hours = (
            total_seconds // 3600
        )

        minutes = (
            total_seconds % 3600
        ) // 60

        return f"{hours:02d}:{minutes:02d}"

    def delete_session(self, session):

        answer = messagebox.askyesno(
            "Delete Record",
            (
                "Are you sure you want to delete this "
                "work record?\n\n"
                f"Date: {session['work_date']}\n\n"
                "This will also delete all breaks "
                "belonging to this record."
            ),
            parent=self.window
        )

        if not answer:
            return

        self.database.delete_session(
            session["id"]
        )

        # Update NAS backup
        backup_to_nas()

        # Refresh the table
        self.load_records()

        # Refresh main window
        self.main_app.current_session = (
            self.database.get_open_session()
        )

        self.main_app.update_ui_state()

        messagebox.showinfo(
            "Record Deleted",
            "The work record has been deleted.",
            parent=self.window
        )


if __name__ == "__main__":

    root = ctk.CTk()

    app = WorkTrackerApp(root)

    root.protocol(
        "WM_DELETE_WINDOW",
        app.on_close
    )

    root.mainloop()