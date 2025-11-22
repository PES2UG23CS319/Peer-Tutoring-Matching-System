import customtkinter as ctk
from tkinter import messagebox
import db_manager
# Make sure this import works. 
# If you get an error here later, it means pages/mentor_page.py has an issue.
from pages.mentor_page import MentorDashboard 

class MentorAuth(ctk.CTkFrame):
    def __init__(self, parent, go_back_callback, controller=None):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.controller = controller
        self.go_back_callback = go_back_callback
        self.pack(fill="both", expand=True)
        self.create_login_page()

    # ----------------------------------------------------------
    # LOGIN CARD
    # ----------------------------------------------------------
    def create_login_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        card = ctk.CTkFrame(self, width=400, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="🧑‍🏫 Mentor Login", font=("Roboto Medium", 24)).pack(pady=(40, 20))

        self.email_entry = ctk.CTkEntry(card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=10)

        self.pw_entry = ctk.CTkEntry(card, placeholder_text="Password", show="*", width=300, height=40)
        self.pw_entry.pack(pady=10)

        # Primary Action
        ctk.CTkButton(
            card, text="Login", command=self.handle_login, width=300, height=40,
            fg_color="#2CC985", hover_color="#209662", font=("Roboto", 14, "bold")
        ).pack(pady=20)

        # Secondary Actions
        ctk.CTkButton(
            card, text="Create Account", command=self.show_register_page, 
            fg_color="transparent", text_color=("#333", "#BBB"), hover=False
        ).pack(pady=5)

        ctk.CTkButton(
            card, text="Back", command=self.go_back_callback, width=100, 
            fg_color="transparent", border_width=1
        ).pack(pady=(10, 30))

    # ----------------------------------------------------------
    # REGISTER CARD
    # ----------------------------------------------------------
    def show_register_page(self):
        for widget in self.winfo_children():
            widget.destroy()

        card = ctk.CTkFrame(self, width=450, corner_radius=20)
        card.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(card, text="New Mentor Registration", font=("Roboto Medium", 20)).pack(pady=(30, 20))

        self.reg_entries = {}
        fields = [("Full Name", "name"), ("Email", "email"), ("Password", "password"), 
                  ("Phone", "ph_no"), ("Department", "dept")]

        for label, key in fields:
            entry = ctk.CTkEntry(card, placeholder_text=label, width=350, height=35)
            if key == "password": entry.configure(show="*")
            entry.pack(pady=5)
            self.reg_entries[key] = entry

        ctk.CTkButton(
            card, text="Register", command=self.register_user, width=350, height=40,
            fg_color="#2CC985", hover_color="#209662"
        ).pack(pady=20)

        ctk.CTkButton(
            card, text="Cancel", command=self.create_login_page, 
            fg_color="transparent", text_color="gray"
        ).pack(pady=(0, 30))

    def register_user(self):
        data = {key: entry.get().strip() for key, entry in self.reg_entries.items()}
        if not all(data.values()):
            messagebox.showwarning("Input Error", "Fill all fields.")
            return

        data["role"] = "mentor"
        data["year"] = 4
        if db_manager.register_user(data):
            messagebox.showinfo("Success", "Account created! Please login.")
            self.create_login_page()

    def handle_login(self):
        email = self.email_entry.get().strip()
        pw = self.pw_entry.get().strip()
        if not email or not pw: return

        user = db_manager.login_user(email, pw, "mentor")
        if user:
            for widget in self.parent.winfo_children(): widget.destroy()
            # This calls the Dashboard from pages/mentor_page.py
            MentorDashboard(self.parent, user, self.controller)
        else:
            messagebox.showerror("Error", "Invalid credentials.")
