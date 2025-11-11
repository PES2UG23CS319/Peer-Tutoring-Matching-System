import tkinter as tk
from tkinter import ttk
from auth.admin_auth import AdminAuth
from auth.mentor_auth import MentorAuth
from auth.mentee_auth import MenteeAuth


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Peer Tutoring Matching System")
        self.geometry("1000x700")
        self.configure(bg="#EAF4FF")
        self.show_auth_screen()

    # ----------------------------------------------------------
    # MAIN AUTH SCREEN
    # ----------------------------------------------------------
    def show_auth_screen(self):
        """Main role selection screen."""
        for widget in self.winfo_children():
            widget.destroy()

        ttk.Label(
            self,
            text="🎓 Peer Tutoring System",
            font=("Helvetica", 24, "bold")
        ).pack(pady=40)

        ttk.Label(
            self,
            text="Select your role to continue:",
            font=("Helvetica", 14)
        ).pack(pady=10)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=40)

        ttk.Button(btn_frame, text="👑 Admin", command=self.open_admin_login, width=20).grid(row=0, column=0, padx=15)
        ttk.Button(btn_frame, text="🧑‍🏫 Mentor", command=self.open_mentor_login, width=20).grid(row=0, column=1, padx=15)
        ttk.Button(btn_frame, text="🎓 Mentee", command=self.open_mentee_login, width=20).grid(row=0, column=2, padx=15)

    # ----------------------------------------------------------
    # OPEN LOGIN SCREENS
    # ----------------------------------------------------------
    def open_admin_login(self):
        self.clear_window()
        AdminAuth(self, self.show_auth_screen, controller=self)

    def open_mentor_login(self):
        self.clear_window()
        MentorAuth(self, self.show_auth_screen, controller=self)

    def open_mentee_login(self):
        self.clear_window()
        MenteeAuth(self, self.show_auth_screen, controller=self)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = App()
    app.mainloop()
