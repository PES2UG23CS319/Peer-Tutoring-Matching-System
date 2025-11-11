import tkinter as tk
from tkinter import ttk, messagebox
import db_manager


class MenteeDashboard(ttk.Frame):
    def __init__(self, parent, user, controller):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller  # ✅ App reference
        self.user = user
        self.pack(fill="both", expand=True)
        self.create_dashboard()

    # ----------------------------------------------------------
    # MAIN DASHBOARD UI
    # ----------------------------------------------------------
    def create_dashboard(self):
        # Clear any old widgets
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(
            self,
            text=f"👩‍🎓 Welcome, {self.user['name']}!",
            font=("Helvetica", 20, "bold")
        ).pack(pady=30)

        ttk.Label(
            self,
            text="Your Scheduled Sessions",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        # --- Table of Scheduled Sessions ---
        self.tree = ttk.Treeview(self, columns=("Subject", "Date", "Duration", "Status"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(pady=20, fill="both", expand=True)

        self.load_sessions()

        # --- Add Logout / Back Button ---
        ttk.Button(self, text="⬅ Back to Login", command=self.logout).pack(pady=15)

    # ----------------------------------------------------------
    # LOAD MENTEE'S SESSIONS
    # ----------------------------------------------------------
    def load_sessions(self):
        sessions = self.fetch_sessions_for_mentee(self.user["student_id"])

        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        if not sessions:
            self.tree.insert("", "end", values=("No sessions found", "", "", ""))
            return

        # Populate table
        for s in sessions:
            self.tree.insert("", "end", values=(
                s["subject_name"],
                s["date_time"],
                s["duration"],
                s["status"]
            ))

    def fetch_sessions_for_mentee(self, mentee_id):
        """Fetch all sessions for a specific mentee using a JOIN query."""
        conn = db_manager.get_db_connection()
        if not conn:
            return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT subj.subject_name, sess.date_time, sess.duration, sess.status
            FROM MentorshipSession sess
            JOIN SessionParticipant sp ON sess.session_id = sp.session_id
            JOIN Subject subj ON sess.subject_id = subj.subject_id
            WHERE sp.student_id = %s AND sp.role = 'mentee'
            ORDER BY sess.date_time DESC
            """
            cursor.execute(query, (mentee_id,))
            return cursor.fetchall()
        except Exception as e:
            messagebox.showerror("Database Error", f"Error loading sessions: {e}")
            return []
        finally:
            if conn:
                conn.close()

    # ----------------------------------------------------------
    # LOGOUT / BACK FUNCTION
    # ----------------------------------------------------------
    def logout(self):
        """Logs out and returns to main login page."""
        for widget in self.parent.winfo_children():
            widget.destroy()
        messagebox.showinfo("Logout", "You have been logged out successfully.")
        self.controller.show_auth_screen()  # ✅ correct navigation
