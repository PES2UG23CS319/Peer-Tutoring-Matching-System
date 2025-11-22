import customtkinter as ctk
from tkinter import messagebox
import db_manager
from pages.admin_page import AdminDashboard

class AdminAuth(ctk.CTkFrame):
    def __init__(self, parent, go_back_callback, controller=None):
        super().__init__(parent, fg_color="transparent") # Transparent background
        self.parent = parent
        self.controller = controller
        self.go_back_callback = go_back_callback
        self.pack(fill="both", expand=True)
        self.create_login_page()

    def create_login_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        # --- CENTERED CARD FRAME ---
        # This frame holds the actual login form
        card = ctk.CTkFrame(self, width=400, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        ctk.CTkLabel(card, text="👑 Admin Portal", font=("Roboto Medium", 24)).pack(pady=(40, 20))

        # Email Entry
        self.email_entry = ctk.CTkEntry(card, placeholder_text="Email Address", width=300, height=40)
        self.email_entry.pack(pady=10)

        # Password Entry
        self.pw_entry = ctk.CTkEntry(card, placeholder_text="Password", show="*", width=300, height=40)
        self.pw_entry.pack(pady=10)

        # Login Button
        ctk.CTkButton(
            card, text="Login", command=self.handle_login, width=300, height=40,
            font=("Roboto", 14, "bold"), fg_color="#1F6AA5", hover_color="#144870"
        ).pack(pady=(20, 10))

        # Back Button (Outlined style)
        ctk.CTkButton(
            card, text="Back to Menu", command=self.go_back_callback, width=300, height=40,
            fg_color="transparent", border_width=2, text_color=("gray10", "#DCE4EE")
        ).pack(pady=(0, 40))

    def handle_login(self):
        email = self.email_entry.get().strip()
        password = self.pw_entry.get().strip()

        if not email or not password:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        user = db_manager.login_user(email, password, "admin")
        if user:
            # Clean up auth frame
            for widget in self.parent.winfo_children():
                widget.destroy()
            # Launch Dashboard
            AdminDashboard(self.parent, user, self.controller)
        else:
            messagebox.showerror("Login Failed", "Invalid credentials.")
