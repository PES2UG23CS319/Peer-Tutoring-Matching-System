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

    # ==========================================================
    # MAIN DASHBOARD LAYOUT (Sidebar + Content Area)
    # ==========================================================
    def create_dashboard(self):
        for widget in self.winfo_children():
            widget.destroy()

        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # ---------------- LEFT SIDEBAR ----------------
        sidebar = ttk.Frame(main_frame)
        sidebar.pack(side="left", fill="y", padx=10, pady=10)

        ttk.Label(
            sidebar,
            text="⚙ Admin Panel",
            font=("Helvetica", 16, "bold")
        ).pack(pady=10)

        ttk.Button(sidebar, text="📘 View Students", width=20,
                   command=self.load_students_view).pack(pady=5)

        ttk.Button(sidebar, text="➕ Add User", width=20,
                   command=self.load_add_user_form).pack(pady=5)

        ttk.Button(sidebar, text="📚 View Sessions", width=20,
                   command=self.load_sessions_view).pack(pady=5)
        
        ttk.Button(sidebar, text="🔄 Refresh Trigger Status", width=20,
                   command=self.trigger_refresh).pack(pady=5, padx=15)

        ttk.Button(sidebar, text="🗑 Delete Session", width=20,
                   command=self.delete_session_popup).pack(pady=5)

        ttk.Button(sidebar, text="⭐ View Feedback", width=20,
                   command=self.load_feedback_view).pack(pady=5)

        ttk.Button(sidebar, text="⬅ Logout", width=20,
                   command=self.logout).pack(pady=20)

        # ---------------- RIGHT CONTENT AREA ----------------
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True, padx=20, pady=10)

        self.load_students_view()

    # ==========================================================
    # VIEW STUDENTS
    # ==========================================================
    def load_students_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="All Registered Students",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(
            self.content_frame,
            columns=("ID", "Name", "Email", "Role", "Dept", "Year"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.load_students()

    def load_students(self):
        students = db_manager.fetch_students()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for s in students:
            self.tree.insert("", "end", values=(
                s["student_id"],
                s["name"],
                s["email"],
                s["role"],
                s["dept"],
                s["year"]
            ))

    # ==========================================================
    # ADD USER FORM (WITH DROPDOWNS)
    # ==========================================================
    def load_add_user_form(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Add New User",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        self.add_vars = {}

        # Full Name
        ttk.Label(self.content_frame, text="Full Name").pack()
        name_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=name_var, width=40).pack(pady=4)
        self.add_vars["name"] = name_var

        # Email
        ttk.Label(self.content_frame, text="Email").pack()
        email_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=email_var, width=40).pack(pady=4)
        self.add_vars["email"] = email_var

        # Password
        ttk.Label(self.content_frame, text="Password").pack()
        pw_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=pw_var, width=40, show="*").pack(pady=4)
        self.add_vars["password"] = pw_var

        # Phone
        ttk.Label(self.content_frame, text="Phone").pack()
        phone_var = tk.StringVar()
        ttk.Entry(self.content_frame, textvariable=phone_var, width=40).pack(pady=4)
        self.add_vars["ph_no"] = phone_var

        # Department Dropdown
        ttk.Label(self.content_frame, text="Department").pack()
        dept_var = tk.StringVar()
        dept_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=dept_var,
            width=37,
            state="readonly",
            values=[
                "CSE", "ECE", "EEE", "Mechanical", "Civil",
                "Physics", "Chemistry", "Mathematics"
            ]
        )
        dept_dropdown.pack(pady=4)
        self.add_vars["dept"] = dept_var

        # Year Dropdown
        ttk.Label(self.content_frame, text="Year (1–4)").pack()
        year_var = tk.StringVar()
        year_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=year_var,
            width=37,
            state="readonly",
            values=["1", "2", "3", "4"]
        )
        year_dropdown.pack(pady=4)
        self.add_vars["year"] = year_var

        # Role Dropdown
        ttk.Label(self.content_frame, text="Role").pack()
        role_var = tk.StringVar()
        role_dropdown = ttk.Combobox(
            self.content_frame,
            textvariable=role_var,
            width=37,
            state="readonly",
            values=["admin", "mentor", "mentee"]
        )
        role_dropdown.pack(pady=4)
        self.add_vars["role"] = role_var

        ttk.Button(self.content_frame, text="Save User",
                   command=self.save_user).pack(pady=15)

    def save_user(self):
        data = {k: v.get().strip() for k, v in self.add_vars.items()}

        if not all(data.values()):
            messagebox.showwarning("Error", "Please fill all fields.")
            return

        try:
            data["year"] = int(data["year"])
        except:
            messagebox.showwarning("Error", "Year must be a number.")
            return

        if db_manager.register_user(data):
            messagebox.showinfo("Success", "User added successfully!")
            self.load_students_view()

    # ==========================================================
    # VIEW SESSIONS
    # ==========================================================
    def load_sessions_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="All Mentorship Sessions",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(
            self.content_frame,
            columns=("ID", "Subject ID", "Date", "Duration", "Status"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.load_sessions()

    def trigger_refresh(self):
        """Runs trigger by forcing update of all scheduled sessions."""
        ok = db_manager.refresh_trigger_statuses()
        if ok:
            messagebox.showinfo("Success", "Trigger executed. Session statuses updated!")
            self.load_sessions_view()
        else:
            messagebox.showerror("Error", "Trigger refresh failed!")

    def load_sessions(self):
        sessions = db_manager.fetch_all_sessions()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for s in sessions:
            self.tree.insert("", "end", values=(
                s["session_id"],
                s["subject_id"],
                s["date_time"],
                s["duration"],
                s["status"]
            ))

    # ==========================================================
    # DELETE SESSION
    # ==========================================================
    def delete_session_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Delete Session")
        popup.geometry("300x200")

        ttk.Label(popup, text="Enter Session ID to delete:").pack(pady=10)
        sid_var = tk.StringVar()
        ttk.Entry(popup, textvariable=sid_var).pack(pady=5)

        def delete_now():
            try:
                sid = int(sid_var.get())
            except:
                messagebox.showerror("Error", "Session ID must be a number.")
                return

            if db_manager.delete_session(sid):
                messagebox.showinfo("Success", "Session deleted.")
                popup.destroy()
                self.load_sessions_view()
            else:
                messagebox.showerror("Error", "Unable to delete session.")

        ttk.Button(popup, text="Delete", command=delete_now).pack(pady=10)

    # ==========================================================
    # VIEW FEEDBACK
    # ==========================================================
    def load_feedback_view(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

        ttk.Label(self.content_frame, text="Feedback Reports",
                  font=("Helvetica", 16, "bold")).pack(pady=10)

        self.tree = ttk.Treeview(
            self.content_frame,
            columns=("ID", "Session", "Rating", "Comment", "Anonymous"),
            show="headings"
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=160, anchor="center")

        self.tree.pack(fill="both", expand=True, pady=10)
        self.load_feedback()

    def load_feedback(self):
        fb = db_manager.fetch_all_feedback()

        for row in self.tree.get_children():
            self.tree.delete(row)

        for f in fb:
            self.tree.insert("", "end", values=(
                f["feedback_id"],
                f["session_id"],
                f["rating"],
                f["comment"],
                "Yes" if f["anonymous"] else "No"
            ))

    # ==========================================================
    # LOGOUT
    # ==========================================================
    def logout(self):
        for widget in self.parent.winfo_children():
            widget.destroy()
        messagebox.showinfo("Logout", "Logged out successfully.")
        self.controller.show_auth_screen()
