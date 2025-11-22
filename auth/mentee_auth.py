import customtkinter as ctk
from tkinter import messagebox
import db_manager
# Ensure this import matches your file structure
from pages.mentee_page import MenteeDashboard

class MenteeAuth(ctk.CTkFrame):
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

        ctk.CTkLabel(card, text="🎓 Mentee Login", font=("Roboto Medium", 24)).pack(pady=(40, 20))

        self.email_entry = ctk.CTkEntry(card, placeholder_text="Email", width=300, height=40)
        self.email_entry.pack(pady=10)

        self.pw_entry = ctk.CTkEntry(card, placeholder_text="Password", show="*", width=300, height=40)
        self.pw_entry.pack(pady=10)

        # Primary Action (Orange/Yellow Theme)
        ctk.CTkButton(
            card, text="Login", command=self.handle_login, width=300, height=40,
            fg_color="#EDB72B", hover_color="#D4A017", text_color="black", font=("Roboto", 14, "bold")
        ).pack(pady=20)

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

        ctk.CTkLabel(card, text="Student Registration", font=("Roboto Medium", 20)).pack(pady=(30, 15))

        self.reg_entries = {}
        fields = [("Full Name", "name"), ("Email", "email"), ("Password", "password"), 
                  ("Phone", "ph_no"), ("Department", "dept")]

        for label, key in fields:
            entry = ctk.CTkEntry(card, placeholder_text=label, width=350, height=35)
            if key == "password": entry.configure(show="*")
            entry.pack(pady=5)
            self.reg_entries[key] = entry

        # Year Dropdown
        self.year_var = ctk.StringVar(value="Select Year")
        year_cb = ctk.CTkComboBox(card, values=["1", "2", "3", "4"], variable=self.year_var, width=350, height=35)
        year_cb.pack(pady=5)

        ctk.CTkButton(
            card, text="Register", command=self.register_user, width=350, height=40,
            fg_color="#EDB72B", hover_color="#D4A017", text_color="black"
        ).pack(pady=20)

        ctk.CTkButton(
            card, text="Cancel", command=self.create_login_page, 
            fg_color="transparent", text_color="gray"
        ).pack(pady=(0, 30))

    def register_user(self):
        data = {key: entry.get().strip() for key, entry in self.reg_entries.items()}
        year_val = self.year_var.get()

        if not all(data.values()) or year_val not in ["1","2","3","4"]:
            messagebox.showwarning("Input Error", "Fill all fields correctly.")
            return

        data["role"] = "mentee"
        try:
            data["year"] = int(year_val)
        except ValueError:
            messagebox.showwarning("Input Error", "Invalid Year")
            return
        
        if db_manager.register_user(data):
            messagebox.showinfo("Success", "Account created! Please login.")
            self.create_login_page()

    def handle_login(self):
        email = self.email_entry.get().strip()
        pw = self.pw_entry.get().strip()
        if not email or not pw: return

        user = db_manager.login_user(email, pw, "mentee")
        if user:
            for widget in self.parent.winfo_children(): widget.destroy()
            # Calls the Dashboard from pages/mentee_page.py
            MenteeDashboard(self.parent, user, self.controller)
        else:
            messagebox.showerror("Error", "Invalid credentials.")
