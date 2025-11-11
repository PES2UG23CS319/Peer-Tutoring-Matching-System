import tkinter as tk
from tkinter import ttk, messagebox
import db_manager
from pages.mentor_page import MentorDashboard


class MentorAuth(ttk.Frame):
    def __init__(self, parent, go_back_callback, controller=None):
        super().__init__(parent)
        self.parent = parent
        self.controller = controller   # ✅ store controller reference
        self.go_back_callback = go_back_callback
        self.pack(fill="both", expand=True)
        self.create_login_page()

    # ----------------------------------------------------------
    # LOGIN PAGE
    # ----------------------------------------------------------
    def create_login_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(
            self, text="🧑‍🏫 Mentor Login", font=("Helvetica", 20, "bold")
        ).pack(pady=20)

        ttk.Label(self, text="Email:").pack(pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.email_var, width=40).pack(pady=5)

        ttk.Label(self, text="Password:").pack(pady=5)
        self.password_var = tk.StringVar()
        ttk.Entry(self, textvariable=self.password_var, show="*", width=40).pack(pady=5)

        ttk.Button(self, text="Login", command=self.handle_login).pack(pady=15)
        ttk.Button(self, text="Register as Mentor", command=self.show_register_page).pack(pady=5)
        ttk.Button(self, text="Back", command=self.go_back_callback).pack(pady=5)

    # ----------------------------------------------------------
    # REGISTER PAGE
    # ----------------------------------------------------------
    def show_register_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(self, text="📝 Mentor Registration", font=("Helvetica", 20, "bold")).pack(pady=20)

        fields = [("Full Name", "name"), ("Email", "email"), ("Password", "password"),
                  ("Phone", "ph_no"), ("Department", "dept")]
        self.reg_vars = {}

        for label, key in fields:
            ttk.Label(self, text=f"{label}:").pack(pady=5)
            var = tk.StringVar()
            entry = ttk.Entry(self, textvariable=var, width=40, show="*" if key == "password" else "")
            entry.pack(pady=5)
            self.reg_vars[key] = var

        ttk.Button(self, text="Register", command=self.register_user).pack(pady=10)
        ttk.Button(self, text="Back", command=self.create_login_page).pack(pady=5)

    # ----------------------------------------------------------
    # REGISTER FUNCTION
    # ----------------------------------------------------------
    def register_user(self):
        data = {key: var.get().strip() for key, var in self.reg_vars.items()}

        if not all(data.values()):
            messagebox.showwarning("Input Error", "Please fill all fields.")
            return

        data["role"] = "mentor"
        data["year"] = 4  # default for mentors

        if db_manager.register_user(data):
            messagebox.showinfo("Success", "Mentor registered successfully!")
            self.create_login_page()

    # ----------------------------------------------------------
    # LOGIN FUNCTION
    # ----------------------------------------------------------
    def handle_login(self):
        email = self.email_var.get().strip()
        password = self.password_var.get().strip()

        if not email or not password:
            messagebox.showwarning("Missing Info", "Please enter both email and password.")
            return

        user = db_manager.login_user(email, password, "mentor")
        if user:
            for widget in self.parent.winfo_children():
                widget.destroy()
            MentorDashboard(self.parent, user, self.controller)  # ✅ Pass controller here
        else:
            messagebox.showerror("Login Failed", "Invalid email or password.")
