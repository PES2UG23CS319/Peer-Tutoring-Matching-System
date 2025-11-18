import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import db_manager


class MentorDashboard(ttk.Frame):
    def __init__(self, parent, user, controller):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.controller = controller
        self.pack(fill="both", expand=True)
        self.create_dashboard()

    # ==========================================================
    # MAIN DASHBOARD LAYOUT
    # ==========================================================
    def create_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # ------------ SIDEBAR ------------
        sidebar = ttk.Frame(main_frame)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(sidebar, text="🧑‍🏫 Mentor Panel",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        ttk.Button(sidebar, text="📅 My Sessions", width=20,
                   command=self.load_sessions_view).pack(pady=5)

        ttk.Button(sidebar, text="➕ Schedule Session", width=20,
                   command=self.load_schedule_form).pack(pady=5)

        ttk.Button(sidebar, text="⭐ View Feedback", width=20,
                   command=self.load_feedback_view).pack(pady=5)

        ttk.Button(sidebar, text="⬅ Logout", width=20,
                   command=self.logout).pack(pady=20)

        # ------------ CONTENT AREA ------------
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True,
                                padx=20, pady=10)

        self.load_sessions_view()

    # ==========================================================
    # VIEW SESSIONS
    # ==========================================================
    def load_sessions_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="My Mentorship Sessions",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(
            self.content_frame,
            columns=("ID", "Subject", "Date", "Duration", "Status", "Mentees"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.load_sessions()

        ttk.Button(
            self.content_frame,
            text="Mark Selected as Completed",
            command=self.mark_as_completed
        ).pack(pady=10)

    def load_sessions(self):
        sessions = self.fetch_sessions_for_mentor(self.user["student_id"])

        for row in self.tree.get_children():
            self.tree.delete(row)

        for s in sessions:
            mentees = s["mentees"] if s["mentees"] else "—"
            self.tree.insert("", "end", values=(
                s["session_id"],
                s["subject_name"],
                s["date_time"],
                s["duration"],
                s["status"],
                mentees
            ))

    def fetch_sessions_for_mentor(self, mentor_id):
        conn = db_manager.get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT sess.session_id, subj.subject_name,
                       sess.date_time, sess.duration, sess.status,
                       GROUP_CONCAT(stu.name SEPARATOR ', ') AS mentees
                FROM MentorshipSession sess
                JOIN Subject subj ON sess.subject_id = subj.subject_id
                JOIN SessionParticipant spm 
                     ON sess.session_id = spm.session_id 
                     AND spm.student_id = %s AND spm.role='mentor'
                LEFT JOIN SessionParticipant spn 
                     ON sess.session_id = spn.session_id AND spn.role='mentee'
                LEFT JOIN Student stu ON spn.student_id = stu.student_id
                GROUP BY sess.session_id
                ORDER BY sess.date_time DESC
            """
            cursor.execute(query, (mentor_id,))
            return cursor.fetchall()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sessions: {e}")
            return []

        finally:
            conn.close()

    def mark_as_completed(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a session.")
            return

        session_id = self.tree.item(selected[0])["values"][0]

        if db_manager.update_session_status(session_id, "completed"):
            messagebox.showinfo("Success", "Session marked as completed!")
            self.load_sessions_view()
        else:
            messagebox.showerror("Error", "Failed to update session.")

    # ==========================================================
    # SCHEDULE SESSION FORM (CALENDAR + TIME DROPDOWN)
    # ==========================================================
    def load_schedule_form(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Schedule a New Session",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        # -------- Subject dropdown --------
        ttk.Label(self.content_frame, text="Subject").pack()
        subj_var = tk.StringVar()
        subjects = db_manager.fetch_all_subjects()
        subj_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=subj_var,
            width=40,
            state="readonly",
            values=[f"{s['subject_id']} - {s['subject_name']}" for s in subjects]
        )
        subj_dropdown.pack(pady=4)

        # -------- Date Picker --------
        ttk.Label(self.content_frame, text="Select Date").pack()
        date_picker = DateEntry(
            self.content_frame,
            width=37,
            background="darkblue",
            foreground="white",
            date_pattern="yyyy-mm-dd"
        )
        date_picker.pack(pady=4)

        # -------- Hour Picker --------
        ttk.Label(self.content_frame, text="Select Hour").pack()
        hour_var = tk.StringVar()
        hour_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=hour_var,
            width=37,
            state="readonly",
            values=[f"{h:02d}" for h in range(0, 24)]
        )
        hour_dropdown.current(10)
        hour_dropdown.pack(pady=4)

        # -------- Minute Picker --------
        ttk.Label(self.content_frame, text="Select Minute").pack()
        minute_var = tk.StringVar()
        minute_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=minute_var,
            width=37,
            state="readonly",
            values=[f"{m:02d}" for m in range(0, 60, 5)]
        )
        minute_dropdown.current(0)
        minute_dropdown.pack(pady=4)

        # -------- Duration --------
        ttk.Label(self.content_frame, text="Duration (minutes)").pack()
        dur_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=dur_var, width=40).pack(pady=4)

        # -------- Mentee dropdown (multi-select) --------
        ttk.Label(self.content_frame, text="Select Mentees").pack()
        mentee_list = tk.Listbox(
            self.content_frame,
            selectmode="multiple",
            width=40,
            height=6
        )
        mentee_list.pack(pady=4)

        mentees = db_manager.fetch_students_by_role("mentee")
        for m in mentees:
            mentee_list.insert("end", f"{m['student_id']} - {m['name']}")

        # -------- SAVE BUTTON --------
        def save_session():
            if not subj_var.get() or not dur_var.get():
                messagebox.showwarning("Missing Info", "Fill all fields.")
                return

            try:
                duration = int(dur_var.get())
            except:
                messagebox.showwarning("Error", "Duration must be numeric.")
                return

            subject_id = int(subj_var.get().split(" - ")[0])

            selected = mentee_list.curselection()
            if not selected:
                messagebox.showwarning("Error", "Select at least one mentee.")
                return

            mentee_ids = [mentees[i]["student_id"] for i in selected]
            mentee_str = ",".join(str(i) for i in mentee_ids)

            # Combine date + time
            final_datetime = f"{date_picker.get()} {hour_var.get()}:{minute_var.get()}:00"

            success = db_manager.schedule_session(
                subject_id,
                final_datetime,
                duration,
                self.user["student_id"],
                mentee_str
            )

            if success:
                messagebox.showinfo("Success", "Session scheduled!")
                self.load_sessions_view()
            else:
                messagebox.showerror("Error", "Failed to schedule session.")

        ttk.Button(self.content_frame, text="Schedule Session",
                   command=save_session).pack(pady=15)

    # ==========================================================
    # VIEW FEEDBACK
    # ==========================================================
    def load_feedback_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame,
                  text="Feedback on Your Sessions",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        tree = ttk.Treeview(
            self.content_frame,
            columns=("ID", "Session", "Rating", "Comment"),
            show="headings"
        )

        for c in tree["columns"]:
            tree.heading(c, text=c)
            tree.column(c, width=150, anchor="center")

        tree.pack(fill="both", expand=True, pady=10)

        fb = db_manager.fetch_all_feedback()
        mentor_id = self.user["student_id"]

        for f in fb:
            if self.is_mentor_session(f["session_id"], mentor_id):
                tree.insert("", "end", values=(
                    f["feedback_id"],
                    f["session_id"],
                    f["rating"],
                    f["comment"]
                ))

    def is_mentor_session(self, session_id, mentor_id):
        conn = db_manager.get_db_connection()
        if not conn:
            return False

        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM SessionParticipant
                WHERE session_id=%s AND student_id=%s AND role='mentor'
            """, (session_id, mentor_id))
            result = cursor.fetchone()[0]
            return result > 0

        finally:
            conn.close()

    # ==========================================================
    # LOGOUT
    # ==========================================================
    def logout(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        messagebox.showinfo("Logout", "You have been logged out.")
        self.controller.show_auth_screen()
