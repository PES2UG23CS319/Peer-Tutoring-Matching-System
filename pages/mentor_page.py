import tkinter as tk
from tkinter import ttk, messagebox
import db_manager


class MentorDashboard(ttk.Frame):
    def __init__(self, parent, user, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller  # ✅ reference to App instance
        self.user = user
        self.pack(fill="both", expand=True)
        self.create_dashboard()

    def create_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(
            self,
            text=f"👨‍🏫 Welcome, {self.user['name']}!",
            font=("Helvetica", 20, "bold")
        ).pack(pady=30)

        ttk.Label(
            self,
            text="Your Scheduled Mentorship Sessions",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        self.tree = ttk.Treeview(
            self,
            columns=("Subject", "Date", "Duration", "Status", "Mentees"),
            show="headings"
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(pady=20, fill="both", expand=True)

        self.load_sessions()

        ttk.Button(
            self,
            text="⬅ Back to Login",
            command=self.logout
        ).pack(pady=15)

    def load_sessions(self):
        sessions = self.fetch_sessions_for_mentor(self.user["student_id"])
        for row in self.tree.get_children():
            self.tree.delete(row)
        if not sessions:
            self.tree.insert("", "end", values=("No sessions found", "", "", "", ""))
            return
        for s in sessions:
            mentees = s["mentees"] if s["mentees"] else "—"
            self.tree.insert("", "end", values=(
                s["subject_name"], s["date_time"], s["duration"], s["status"], mentees
            ))

    def fetch_sessions_for_mentor(self, mentor_id):
        conn = db_manager.get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT subj.subject_name, sess.date_time, sess.duration, sess.status,
                   GROUP_CONCAT(mn.name SEPARATOR ', ') AS mentees
            FROM MentorshipSession sess
            JOIN SessionParticipant spm ON sess.session_id = spm.session_id
            JOIN Subject subj ON sess.subject_id = subj.subject_id
            LEFT JOIN SessionParticipant spn ON sess.session_id = spn.session_id AND spn.role = 'mentee'
            LEFT JOIN Student mn ON spn.student_id = mn.student_id
            WHERE spm.student_id = %s AND spm.role = 'mentor'
            GROUP BY sess.session_id
            ORDER BY sess.date_time DESC
            """
            cursor.execute(query, (mentor_id,))
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading sessions: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def logout(self):
        """Logs out and returns to main login page."""
        for widget in self.parent.winfo_children():
            widget.destroy()
        messagebox.showinfo("Logout", "You have been logged out successfully.")
        self.controller.show_auth_screen()  # ✅ use App’s method to go back
