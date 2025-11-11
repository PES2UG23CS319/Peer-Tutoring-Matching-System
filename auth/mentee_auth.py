import tkinter as tk
from tkinter import ttk, messagebox
import db_manager
from pages.mentee_page import MenteeDashboard


class MenteeAuth(ttk.Frame):
    def __init__(self, parent, go_back_callback, controller=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller   # ✅ Reference to main App (for going back)
        self.go_back_callback = go_back_callback
        self.pack(fill="both", expand=True)
        self.create_login_page()

    # ----------------------------------------------------------
    # LOGIN PAGE
    # ----------------------------------------------------------
    def create_login_page(self):
        """Creates the mentee login screen."""
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(
            self, text="🎓 Mentee Login", font=("Helvetica", 22, "bold")
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

        ttk.Button(
            self, text="Register as Mentee", command=self.show_register_page, width=20
        ).pack(pady=5)

        ttk.Button(
            self, text="⬅ Back", command=self.go_back_callback, width=20
        ).pack(pady=10)

    # ----------------------------------------------------------
    # REGISTRATION PAGE
    # ----------------------------------------------------------
    def show_register_page(self):
        """Creates the registration screen for new mentees."""
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(
            self, text="📝 Mentee Registration", font=("Helvetica", 22, "bold")
        ).pack(pady=25)

        # Field setup
        fields = [
            ("Full Name", "name"),
            ("Email", "email"),
            ("Password", "password"),
            ("Phone", "ph_no"),
            ("Department", "dept"),
            ("Year (1-4)", "year")
        ]

        self.reg_vars = {}

        for label, key in fields:
            ttk.Label(self, text=f"{label}:").pack(pady=4)
            var = tk.StringVar()
            entry = ttk.Entry(self, textvariable=var, width=40, show="*" if key == "password" else "")
            entry.pack(pady=3)
            self.reg_vars[key] = var

        ttk.Button(
            self, text="Register", command=self.register_user, width=20
        ).pack(pady=15)

        ttk.Button(
            self, text="⬅ Back", command=self.create_login_page, width=20
        ).pack(pady=10)

    # ----------------------------------------------------------
    # REGISTRATION FUNCTION
    # ----------------------------------------------------------
    def register_user(self):
        """Handles new mentee registration."""
        data = {key: var.get().strip() for key, var in self.reg_vars.items()}

        if not all(data.values()):
            messagebox.showwarning("Input Error", "Please fill all fields before submitting.")
            return

        try:
            year = int(data["year"])
            if year not in [1, 2, 3, 4]:
                messagebox.showwarning("Input Error", "Year must be between 1 and 4.")
                return
        except ValueError:
            messagebox.showwarning("Input Error", "Year must be a number.")
            return

        data["role"] = "mentee"

        if db_manager.register_user(data):
            messagebox.showinfo("Success", "Mentee registered successfully!")
            self.create_login_page()

    # ----------------------------------------------------------
    # LOGIN FUNCTION
    # ----------------------------------------------------------
    def handle_login(self):
        """Handles mentee login validation."""
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()

        if not email or not password:
            messagebox.showwarning("Missing Info", "Please enter both email and password.")
            return

        user = db_manager.login_user(email, password, "mentee")
        if user:
            # ✅ Clear current frame and open Mentee Dashboard
            for widget in self.parent.winfo_children():
                widget.destroy()
            MenteeDashboard(self.parent, user, self.controller)
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")
