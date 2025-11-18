import tkinter as tk
from tkinter import ttk, messagebox
import db_manager


class MenteeDashboard(ttk.Frame):
    def __init__(self, parent, user, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller
        self.user = user
        self.pack(fill="both", expand=True)
        self.create_dashboard()

    # ==========================================================
    # MAIN LAYOUT
    # ==========================================================
    def create_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # ------------ SIDEBAR ------------
        sidebar = ttk.Frame(main_frame)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(sidebar, text="🎓 Mentee Panel",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        ttk.Button(sidebar, text="📅 My Sessions", width=20,
                   command=self.load_sessions_view).pack(pady=5)

        ttk.Button(sidebar, text="⭐ Give Feedback", width=20,
                   command=self.load_feedback_form).pack(pady=5)

        ttk.Button(sidebar, text="➕ Join Session", width=20,
                   command=self.load_join_session_form).pack(pady=5)

        ttk.Button(sidebar, text="⬅ Logout", width=20,
                   command=self.logout).pack(pady=20)

        # ------------ CONTENT AREA ------------
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True,
                                padx=20, pady=10)

        self.load_sessions_view()

    # ==========================================================
    # VIEW MENTEE'S SESSIONS
    # ==========================================================
    def load_sessions_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="My Scheduled Sessions",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(
            self.content_frame,
            columns=("ID", "Subject", "Date", "Duration", "Status", "Mentor"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)

        self.load_sessions()

    def load_sessions(self):
        sessions = self.fetch_sessions_for_mentee(self.user["student_id"])

        for row in self.tree.get_children():
            self.tree.delete(row)

        for s in sessions:
            self.tree.insert("", "end", values=(
                s["session_id"],
                s["subject_name"],
                s["date_time"],
                s["duration"],
                s["status"],
                s["mentor_name"]
            ))

    def fetch_sessions_for_mentee(self, mentee_id):
        conn = db_manager.get_db_connection()
        if not conn:
            return []

        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT sess.session_id, subj.subject_name, sess.date_time, 
                   sess.duration, sess.status, stu.name AS mentor_name
            FROM MentorshipSession sess
            JOIN Subject subj ON sess.subject_id = subj.subject_id
            JOIN SessionParticipant sp ON sess.session_id = sp.session_id
            JOIN SessionParticipant spm ON sess.session_id = spm.session_id AND spm.role='mentor'
            JOIN Student stu ON spm.student_id = stu.student_id
            WHERE sp.student_id = %s AND sp.role = 'mentee'
            ORDER BY sess.date_time DESC
            """
            cursor.execute(query, (mentee_id,))
            return cursor.fetchall()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sessions: {e}")
            return []

        finally:
            conn.close()

    # ==========================================================
    # FEEDBACK FORM
    # ==========================================================
    def load_feedback_form(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Give Feedback",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        # Completed sessions for mentee
        conn = db_manager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT sess.session_id, subj.subject_name
            FROM MentorshipSession sess
            JOIN Subject subj ON sess.subject_id=subj.subject_id
            JOIN SessionParticipant sp ON sess.session_id = sp.session_id
            WHERE sp.student_id = %s AND sp.role='mentee' AND sess.status='completed'
        """, (self.user["student_id"],))
        sessions = cursor.fetchall()
        conn.close()

        if not sessions:
            ttk.Label(self.content_frame, text="No completed sessions yet.",
                      font=("Helvetica", 12)).pack(pady=20)
            return

        # Session dropdown
        ttk.Label(self.content_frame, text="Select Session").pack()
        sess_var = tk.StringVar()
        sess_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=sess_var,
            width=40,
            state="readonly",
            values=[f"{s['session_id']} - {s['subject_name']}" for s in sessions]
        )
        sess_dropdown.pack(pady=4)

        # Rating
        ttk.Label(self.content_frame, text="Rating (1–5)").pack()
        rating_var = tk.StringVar()
        rating_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=rating_var,
            width=40,
            state="readonly",
            values=["1", "2", "3", "4", "5"]
        )
        rating_dropdown.pack(pady=4)

        # Comment box
        ttk.Label(self.content_frame, text="Comment").pack()
        comment_box = tk.Text(self.content_frame, width=50, height=5)
        comment_box.pack(pady=4)

        # Anonymous checkbox
        anon_var = tk.BooleanVar()
        ttk.Checkbutton(self.content_frame, text="Submit anonymously",
                        variable=anon_var).pack(pady=5)

        # Submit button
        def submit_feedback():
            if not sess_var.get() or not rating_var.get():
                messagebox.showwarning("Error", "Select session and rating.")
                return

            session_id = int(sess_var.get().split(" - ")[0])
            rating = int(rating_var.get())
            comment = comment_box.get("1.0", tk.END).strip()
            anon = anon_var.get()

            # Insert feedback in DB
            conn = db_manager.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Feedback (session_id, rating, comment, anonymous)
                VALUES (%s, %s, %s, %s)
            """, (session_id, rating, comment, anon))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Feedback submitted!")
            self.load_sessions_view()

        ttk.Button(self.content_frame, text="Submit Feedback",
                   command=submit_feedback).pack(pady=15)

    # ==========================================================
    # JOIN SESSION (OPTIONAL)
    # ==========================================================
    def load_join_session_form(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Join an Available Session",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        conn = db_manager.get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT sess.session_id, subj.subject_name, sess.date_time
            FROM MentorshipSession sess
            JOIN Subject subj ON sess.subject_id=subj.subject_id
            WHERE sess.status='scheduled'
        """)

        sessions = cursor.fetchall()
        conn.close()

        if not sessions:
            ttk.Label(self.content_frame, text="No sessions available.",
                      font=("Helvetica", 12)).pack(pady=20)
            return

        # Dropdown
        ttk.Label(self.content_frame, text="Select Session").pack()
        join_var = tk.StringVar()
        join_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=join_var,
            width=40,
            state="readonly",
            values=[f"{s['session_id']} - {s['subject_name']} ({s['date_time']})"
                    for s in sessions]
        )
        join_dropdown.pack(pady=4)

        def join_session():
            if not join_var.get():
                messagebox.showwarning("Error", "Select a session.")
                return

            session_id = int(join_var.get().split(" - ")[0])

            conn = db_manager.get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO SessionParticipant (session_id, student_id, role)
                VALUES (%s, %s, 'mentee')
            """, (session_id, self.user["student_id"]))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "You joined the session!")
            self.load_sessions_view()

        ttk.Button(self.content_frame, text="Join Session",
                   command=join_session).pack(pady=15)

    # ==========================================================
    # LOGOUT
    # ==========================================================
    def logout(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        messagebox.showinfo("Logout", "You have been logged out.")
        self.controller.show_auth_screen()
