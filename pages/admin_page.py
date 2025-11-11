import tkinter as tk
from tkinter import ttk, messagebox
import db_manager


class AdminDashboard(ttk.Frame):
    def __init__(self, parent, user, controller):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.controller = controller
        self.pack(fill="both", expand=True)
        self.create_dashboard()

    # ----------------------------------------------------------
    # MAIN DASHBOARD
    # ----------------------------------------------------------
    def create_dashboard(self):
        """Admin dashboard interface."""
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(
            self,
            text=f"👑 Welcome, {self.user['name']}!",
            font=("Helvetica", 20, "bold")
        ).pack(pady=25)

        ttk.Label(
            self,
            text="All Registered Students",
            font=("Helvetica", 14, "bold")
        ).pack(pady=10)

        # --- Table ---
        self.tree = ttk.Treeview(
            self,
            columns=("ID", "Name", "Email", "Role", "Dept", "Year"),
            show="headings"
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

        self.tree.pack(pady=20, fill="both", expand=True)
        self.load_students()

        ttk.Button(self, text="⬅ Back to Login", command=self.logout).pack(pady=15)

    # ----------------------------------------------------------
    # LOAD STUDENTS
    # ----------------------------------------------------------
    def load_students(self):
        """Fetch all students for admin view."""
        students = db_manager.fetch_students()

        for row in self.tree.get_children():
            self.tree.delete(row)

        if not students:
            self.tree.insert("", "end", values=("No records found", "", "", "", "", ""))
            return

        for s in students:
            self.tree.insert("", "end", values=(
                s["student_id"],
                s["name"],
                s["email"],
                s["role"],
                s["dept"],
                s["year"]
            ))

    # ----------------------------------------------------------
    # LOGOUT FUNCTION
    # ----------------------------------------------------------
    def logout(self):
        """Logs out and goes back to main menu."""
        for widget in self.parent.winfo_children():
            widget.destroy()
        messagebox.showinfo("Logout", "You have been logged out successfully.")
        self.controller.show_auth_screen()
