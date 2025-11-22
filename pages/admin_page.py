import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import db_manager
from PIL import Image

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, parent, user, controller):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.user = user
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        # Grid layout: Column 0 = Sidebar (fixed), Column 1 = Content (expands)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Pre-load icons (ensure you have these images, or remove image= arg if not)
        # If you don't have images, the code will still run if you remove the 'image=' parts below.
        try:
            self.icon_home = ctk.CTkImage(Image.open("assets/home.png"), size=(20, 20))
            self.icon_add = ctk.CTkImage(Image.open("assets/add.png"), size=(20, 20))
            # Add more icons as needed
        except:
            self.icon_home = None
            self.icon_add = None

        self.create_dashboard()

    def create_dashboard(self):
        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="⚙ Admin Panel", font=("Roboto Medium", 20)).pack(pady=30)

        # --- CORRECT BUTTON LIST (No Duplicates) ---
        self.create_sidebar_btn("📘 View Students", self.load_students_view)
        self.create_sidebar_btn("➕ Add User", self.load_add_user_form)
        self.create_sidebar_btn("📚 View Sessions", self.load_sessions_view)
        self.create_sidebar_btn("⚠️ Inactive Mentees", self.load_inactive_view) # New Feature
        self.create_sidebar_btn("⭐ View Feedback", self.load_feedback_view)
        self.create_sidebar_btn("🗑 Delete Session", self.delete_session_popup)
        
        ctk.CTkButton(
            self.sidebar, text="Logout", fg_color="#FF5555", hover_color="#CC0000",
            command=self.logout
        ).pack(side="bottom", pady=20, padx=20, fill="x")

        # ================= CONTENT AREA =================
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.load_students_view()

    def create_sidebar_btn(self, text, command, icon=None):
        btn = ctk.CTkButton(
            self.sidebar, text=text, command=command,
            image=icon,
            fg_color="transparent", hover_color="#3A3A3A", anchor="w", height=40
        )
        btn.pack(fill="x", padx=10, pady=5)

    # ================= STYLE THE TABLE =================
    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b",
                        rowheight=30, borderwidth=0)
        style.map('Treeview', background=[('selected', '#1F6AA5')])
        style.configure("Treeview.Heading", 
                        background="#1f1f1f", 
                        foreground="white", 
                        relief="flat", font=("Roboto", 10, "bold"))
        style.map("Treeview.Heading", background=[('active', '#1F6AA5')])

# ================= VIEW 1: STUDENTS (With Edit & Delete) =================
    def load_students_view(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Student Database", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0,20))

        table_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        self.style_treeview()
        
        columns = ("ID", "Name", "Email", "Role", "Dept", "Year")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        students = db_manager.fetch_students()
        for s in students:
            self.tree.insert("", "end", values=(s["student_id"], s["name"], s["email"], s["role"], s["dept"], s["year"]))

        # --- BUTTONS CONTAINER ---
        btn_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        btn_frame.pack(pady=20)

        # Edit Button
        ctk.CTkButton(
            btn_frame, text="✏️ Edit User", 
            fg_color="#1F6AA5", hover_color="#144870",
            command=self.open_edit_student_popup,
            width=150
        ).pack(side="left", padx=10)

        # Delete Button (Red)
        ctk.CTkButton(
            btn_frame, text="🗑 Delete User", 
            fg_color="#FF5555", hover_color="#CC0000",
            command=self.delete_selected_student,
            width=150
        ).pack(side="left", padx=10)

    # ================= DELETE LOGIC =================
    def delete_selected_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a student to delete.")
            return

        # Get Data from row
        item = self.tree.item(selected[0])
        student_id = item["values"][0]
        name = item["values"][1]

        # Confirm Dialog
        confirm = messagebox.askyesno(
            "Confirm Delete", 
            f"Are you sure you want to delete '{name}'?\n\n"
            "This will also delete their scheduled sessions and feedback."
        )

        if confirm:
            if db_manager.delete_student(student_id):
                messagebox.showinfo("Success", "User deleted successfully.")
                self.load_students_view() # Refresh table
# ================= POPUP: EDIT STUDENT FORM =================
    def open_edit_student_popup(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a student to edit.")
            return

        # Get ID from the selected row
        student_id = self.tree.item(selected[0])["values"][0]
        
        # Fetch full details from DB
        student_data = db_manager.get_student_by_id(student_id)
        if not student_data:
            messagebox.showerror("Error", "Could not fetch student details.")
            return

        # Create Popup Window (Increased Height to 650)
        popup = ctk.CTkToplevel(self)
        popup.title("Edit Student Details")
        popup.geometry("400x650") # <--- INCREASED HEIGHT
        popup.grab_set()

        ctk.CTkLabel(popup, text=f"Editing: {student_data['name']}", font=("Roboto", 18, "bold")).pack(pady=20)

        # Form Fields
        entries = {}
        
        def add_field(label, key, value):
            ctk.CTkLabel(popup, text=label).pack(pady=(5,0)) # Reduced top padding slightly
            entry = ctk.CTkEntry(popup, width=300)
            entry.insert(0, str(value)) 
            entry.pack(pady=5)
            entries[key] = entry

        add_field("Full Name", "name", student_data["name"])
        add_field("Email", "email", student_data["email"])
        add_field("Phone", "ph_no", student_data["ph_no"])
        
        # Dropdowns
        ctk.CTkLabel(popup, text="Department").pack(pady=(5,0))
        dept_cb = ctk.CTkComboBox(popup, values=["CSE", "ECE", "EEE", "Physics", "Maths"], width=300)
        dept_cb.set(student_data["dept"])
        dept_cb.pack(pady=5)
        
        ctk.CTkLabel(popup, text="Year").pack(pady=(5,0))
        year_cb = ctk.CTkComboBox(popup, values=["1", "2", "3", "4"], width=300)
        year_cb.set(str(student_data["year"]))
        year_cb.pack(pady=5)

        # Save Function
        def save_changes():
            if db_manager.update_student(
                student_id,
                entries["name"].get(),
                entries["email"].get(),
                entries["ph_no"].get(),
                dept_cb.get(),
                int(year_cb.get())
            ):
                messagebox.showinfo("Success", "Student details updated!")
                popup.destroy()
                self.load_students_view() 

        # THE SAVE BUTTON
        ctk.CTkButton(
            popup, 
            text="Save Changes", 
            command=save_changes, 
            fg_color="#2CC985", 
            hover_color="#209662",
            width=200,
            height=40
        ).pack(pady=30)

    # ================= VIEW 2: ADD USER =================
    def load_add_user_form(self):
        self.clear_content()
        
        card = ctk.CTkFrame(self.content_frame, corner_radius=15)
        card.pack(fill="both", expand=True, padx=40, pady=20)
        
        ctk.CTkLabel(card, text="Add New User", font=("Roboto", 22, "bold")).pack(pady=20)
        
        self.add_vars = {}
        form_container = ctk.CTkFrame(card, fg_color="transparent")
        form_container.pack(pady=10)

        # Helper to make rows
        def make_row(label, key, is_pass=False):
            ctk.CTkLabel(form_container, text=label).pack(pady=(5,0))
            ent = ctk.CTkEntry(form_container, width=300, show="*" if is_pass else "")
            ent.pack(pady=5)
            self.add_vars[key] = ent

        make_row("Full Name", "name")
        make_row("Email", "email")
        make_row("Password", "password", True)
        make_row("Phone", "ph_no")

        ctk.CTkLabel(form_container, text="Department").pack(pady=(5,0))
        self.add_vars["dept"] = ctk.CTkComboBox(form_container, values=["CSE", "ECE", "EEE", "Physics"], width=300)
        self.add_vars["dept"].pack(pady=5)

        ctk.CTkLabel(form_container, text="Role").pack(pady=(5,0))
        self.add_vars["role"] = ctk.CTkComboBox(form_container, values=["admin", "mentor", "mentee"], width=300)
        self.add_vars["role"].pack(pady=5)
        
        ctk.CTkLabel(form_container, text="Year").pack(pady=(5,0))
        self.add_vars["year"] = ctk.CTkComboBox(form_container, values=["1", "2", "3", "4"], width=300)
        self.add_vars["year"].pack(pady=5)

        ctk.CTkButton(card, text="Save User", command=self.save_user, width=300, height=40).pack(pady=20)

    def save_user(self):
        data = {k: v.get().strip() for k, v in self.add_vars.items()}
        if not all(data.values()): return
        try: data["year"] = int(data["year"])
        except: pass
        if db_manager.register_user(data):
            messagebox.showinfo("Success", "User added.")
            self.load_students_view()

    # ================= VIEW 3: ALL SESSIONS =================
    def load_sessions_view(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="All Sessions (Master List)", font=("Roboto", 24, "bold")).pack(anchor="w", pady=20)
        
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True)
        
        self.style_treeview()
        
        # UPDATED COLUMNS to show names instead of IDs
        cols = ("ID", "Subject", "Mentor", "Date", "Status")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        # Configure column widths
        tree.heading("ID", text="ID"); tree.column("ID", width=50, anchor="center")
        tree.heading("Subject", text="Subject"); tree.column("Subject", width=150, anchor="center")
        tree.heading("Mentor", text="Mentor"); tree.column("Mentor", width=150, anchor="center")
        tree.heading("Date", text="Date"); tree.column("Date", width=150, anchor="center")
        tree.heading("Status", text="Status"); tree.column("Status", width=100, anchor="center")
        
        tree.pack(fill="both", expand=True)
        
        # Fetch from the new JOIN View
        for s in db_manager.fetch_all_sessions():
            tree.insert("", "end", values=(
                s["session_id"], 
                s["subject_name"],   # Now we have the name!
                s["mentor_name"],    # Now we have the mentor name!
                s["date_time"], 
                s["status"]
            ))

    # ================= VIEW 4: INACTIVE MENTEES (Nested Query) =================
    def load_inactive_view(self):
        self.clear_content()
        
        ctk.CTkLabel(self.content_frame, text="Inactive Mentees Report", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(self.content_frame, text="Students who have never joined a session.", font=("Roboto", 12), text_color="gray").pack(anchor="w", pady=(0, 20))

        table_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        self.style_treeview()
        
        cols = ("ID", "Name", "Email", "Dept", "Year")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")

        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        inactive_students = db_manager.fetch_inactive_mentees()
        
        if not inactive_students:
            # Optional: Show a message if empty, or just show empty table
            pass 
            
        for s in inactive_students:
            self.tree.insert("", "end", values=(s["student_id"], s["name"], s["email"], s["dept"], s["year"]))

    # ================= VIEW 5: FEEDBACK =================
    def load_feedback_view(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Feedback", font=("Roboto", 24, "bold")).pack(anchor="w", pady=20)
        table_frame = ctk.CTkFrame(self.content_frame)
        table_frame.pack(fill="both", expand=True)
        
        self.style_treeview()
        cols = ("ID", "Session", "Rating", "Comment", "Anonymous")
        tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        for c in cols: 
            tree.heading(c, text=c)
            tree.column(c, width=100, anchor="center")
        tree.pack(fill="both", expand=True)
        
        for f in db_manager.fetch_all_feedback():
            tree.insert("", "end", values=(f["feedback_id"], f["session_id"], f["rating"], f["comment"], f["anonymous"]))

    # ================= POPUP: DELETE SESSION =================
    def delete_session_popup(self):
        dialog = ctk.CTkInputDialog(text="Enter Session ID to delete:", title="Delete Session")
        sid = dialog.get_input()
        if sid:
            if db_manager.delete_session(sid):
                messagebox.showinfo("Success", "Deleted.")
                self.load_sessions_view()
            else:
                messagebox.showerror("Error", "Failed.")

    def clear_content(self):
        for widget in self.content_frame.winfo_children(): widget.destroy()

    def logout(self):
        self.controller.show_auth_screen()
