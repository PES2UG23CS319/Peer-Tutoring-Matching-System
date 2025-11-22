<<<<<<< HEAD
import customtkinter as ctk
=======
import tkinter as tk
from tkinter import ttk
>>>>>>> a7666d96e8533c1aeb34802e5ebeeae6ea1660f3
from auth.admin_auth import AdminAuth
from auth.mentor_auth import MentorAuth
from auth.mentee_auth import MenteeAuth

<<<<<<< HEAD
# Configuration
ctk.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Peer Tutoring Matching System")
        self.geometry("1100x700")
        
        # specific grid layout for centering
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.show_auth_screen()

    def show_auth_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

        # Create a nice frame for the login selection
        # "fg_color=None" makes it transparent, or use a color for a 'card' look
        main_frame = ctk.CTkFrame(self, corner_radius=15)
        main_frame.pack(pady=80, padx=60, fill="both", expand=True)

        ctk.CTkLabel(
            main_frame,
            text="🎓 Peer Tutoring System",
            font=("Roboto Medium", 32)
        ).pack(pady=(60, 20))

        ctk.CTkLabel(
            main_frame,
            text="Please select your role to continue",                                               
            font=("Roboto", 16),
            text_color="gray"
        ).pack(pady=10)

        btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        btn_frame.pack(pady=40)

        # Modern Buttons with Icons (or just text for now)
        # hover_color makes it interactive
        ctk.CTkButton(btn_frame, text="Admin", command=self.open_admin_login, 
                      width=160, height=50, font=("Roboto", 16, "bold"), corner_radius=32).grid(row=0, column=0, padx=20)
        
        ctk.CTkButton(btn_frame, text="Mentor", command=self.open_mentor_login,
                      width=160, height=50, font=("Roboto", 16, "bold"), corner_radius=32, fg_color="#2CC985", hover_color="#209662").grid(row=0, column=1, padx=20)
        
        ctk.CTkButton(btn_frame, text="Mentee", command=self.open_mentee_login,
                      width=160, height=50, font=("Roboto", 16, "bold"), corner_radius=32, fg_color="#EDB72B", hover_color="#D4A017").grid(row=0, column=2, padx=20)

=======

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
>>>>>>> a7666d96e8533c1aeb34802e5ebeeae6ea1660f3
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

<<<<<<< HEAD
if __name__ == "__main__":
    app = App()
    app.mainloop()
=======

if __name__ == "__main__":
    app = App()
    app.mainloop()
>>>>>>> a7666d96e8533c1aeb34802e5ebeeae6ea1660f3
