import tkinter as tk
from tkinter import ttk, messagebox
import db_manager
from pages.admin_page import AdminDashboard  # ✅ Admin dashboard page


class AdminAuth(ttk.Frame):
    def __init__(self, parent, go_back_callback, controller=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller  # reference to main App
        self.go_back_callback = go_back_callback
        self.pack(fill="both", expand=True)
        self.create_login_page()

    # ----------------------------------------------------------
    # LOGIN PAGE
    # ----------------------------------------------------------
    def create_login_page(self):
        """Creates the Admin login screen."""
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(
            self,
            text="👑 Admin Login",
            font=("Helvetica", 22, "bold")
        ).pack(pady=25)

        ttk.Label(self, text="Email:").pack(pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.email_var, width=40).pack(pady=5)

        ttk.Label(self, text="Password:").pack(pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.password_var, show="*", width=40).pack(pady=5)

        ttk.Button(
            self, text="Login", command=self.handle_login, width=20
        ).pack(pady=15)

        # ✅ Back button to go to main menu
        ttk.Button(
            self, text="⬅ Back", command=self.go_back_callback, width=20
        ).pack(pady=10)

    # ----------------------------------------------------------
    # LOGIN HANDLER
    # ----------------------------------------------------------
    def handle_login(self):
        """Handles admin login validation."""
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()

        if not email or not password:
            messagebox.showwarning("Missing Info", "Please enter both email and password.")
            return

        user = db_manager.login_user(email, password, "admin")
        if user:
            for widget in self.parent.winfo_children():
                widget.destroy()
            AdminDashboard(self.parent, user, self.controller)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")
