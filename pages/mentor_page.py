import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
from tkcalendar import DateEntry
import db_manager
from PIL import Image

class MentorDashboard(ctk.CTkFrame):
    def __init__(self, parent, user, controller):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.user = user
        self.controller = controller
        self.pack(fill="both", expand=True)
        
        # Configure layout: Sidebar (col 0) fixed, Content (col 1) expands
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Pre-load icons (Optional: Remove try/except block if you don't have icons yet)
        try:
            self.icon_home = ctk.CTkImage(Image.open("assets/home.png"), size=(20, 20))
            self.icon_add = ctk.CTkImage(Image.open("assets/add.png"), size=(20, 20))
        except:
            self.icon_home = None
            self.icon_add = None

        self.create_dashboard()

    def create_dashboard(self):
        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="🧑‍🏫 Mentor Panel", font=("Roboto Medium", 20)).pack(pady=30)

        # Sidebar Buttons
        self.create_sidebar_btn("📅 My Sessions", self.load_sessions_view, self.icon_home)
        self.create_sidebar_btn("➕ Schedule Session", self.load_schedule_form, self.icon_add)
        self.create_sidebar_btn("⭐ View Feedback", self.load_feedback_view)
        
        ctk.CTkButton(
            self.sidebar, text="Logout", fg_color="#FF5555", hover_color="#CC0000",
            command=self.logout
        ).pack(side="bottom", pady=20, padx=20, fill="x")

        # ================= CONTENT AREA =================
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        # Load default view
        self.load_sessions_view()

    def create_sidebar_btn(self, text, command, icon=None):
        btn = ctk.CTkButton(
            self.sidebar, text=text, command=command, 
            image=icon,
            fg_color="transparent", hover_color="#3A3A3A", 
            anchor="w", height=40
        )
        btn.pack(fill="x", padx=10, pady=5)

    # ================= HELPER: STATS CARD =================
    def create_stat_card(self, parent, title, value, icon_color):
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#333333")
        card.pack(side="left", expand=True, fill="both", padx=5)
        
        # Value (Big Number)
        ctk.CTkLabel(card, text=str(value), font=("Roboto", 32, "bold"), text_color=icon_color).pack(pady=(10,0))
        
        # Title (Small Text)
        ctk.CTkLabel(card, text=title, font=("Roboto", 12), text_color="gray").pack(pady=(0,10))

    # ================= HELPER: TABLE STYLE =================
    def style_treeview(self):
        style = ttk.Style()
        style.theme_use("default")
        
        # Configure generic Treeview colors
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=30, 
                        borderwidth=0)
        
        # Color when a row is selected (Green for Mentor)
        style.map('Treeview', background=[('selected', '#2CC985')]) 
        
        # Configure Heading colors
        style.configure("Treeview.Heading", 
                        background="#1f1f1f", 
                        foreground="white", 
                        relief="flat", 
                        font=("Roboto", 10, "bold"))
        
        style.map("Treeview.Heading", background=[('active', '#2CC985')])

    # ================= VIEW 1: MY SESSIONS (With Rubric Fixes) =================
    def load_sessions_view(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="My Mentorship Sessions", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # --- STATS BOARD (RUBRIC REQUIREMENTS) ---
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        # 1. Aggregate Query: Total sessions in system
        total_sys = db_manager.get_total_sessions_aggregate()

        # 2. SQL Function: My completed sessions
        my_completed = db_manager.get_mentor_completed_count_via_function(self.user["student_id"])
        
        # 3. Python Logic: My Upcoming (Simple calculation)
        sessions = self.fetch_sessions()
        upcoming = sum(1 for s in sessions if s['status'] == 'scheduled')

        self.create_stat_card(stats_frame, "Total System Sessions", total_sys, "#3B8ED0")
        self.create_stat_card(stats_frame, "My Completed (SQL)", my_completed, "#2CC985")
        self.create_stat_card(stats_frame, "My Upcoming", upcoming, "#EDB72B")
        # ------------------------------------------

        # Table Container
        ctk.CTkLabel(self.content_frame, text="Recent Activity", font=("Roboto", 18, "bold")).pack(anchor="w", pady=(10, 5))
        
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        self.style_treeview()
        
        cols = ("ID", "Subject", "Date", "Duration", "Status", "Mentees")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        for c in cols: 
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Load Data
        for s in sessions:
            mentees = s["mentees"] if s["mentees"] else "—"
            self.tree.insert("", "end", values=(s["session_id"], s["subject_name"], s["date_time"], s["duration"], s["status"], mentees))

        # Action Button
        ctk.CTkButton(
            self.content_frame, text="Mark Selected as Completed", 
            fg_color="#2CC985", hover_color="#209662",
            command=self.mark_as_completed
        ).pack(pady=20)

    # ================= VIEW 2: SCHEDULE FORM =================
    def load_schedule_form(self):
        self.clear_content()
        
        # Create a "Card" for the form
        card = ctk.CTkFrame(self.content_frame, corner_radius=15)
        card.pack(fill="both", expand=True, padx=50, pady=20)

        ctk.CTkLabel(card, text="Schedule New Session", font=("Roboto", 22, "bold")).pack(pady=20)

        form_frame = ctk.CTkFrame(card, fg_color="transparent")
        form_frame.pack()

        # 1. Subject Dropdown
        ctk.CTkLabel(form_frame, text="Subject").pack(pady=(10,0))
        subjects = db_manager.fetch_all_subjects()
        self.subj_var = ctk.CTkComboBox(form_frame, values=[f"{s['subject_id']} - {s['subject_name']}" for s in subjects], width=300)
        self.subj_var.pack(pady=5)

        # 2. Date Picker (TkCalendar)
        ctk.CTkLabel(form_frame, text="Date").pack(pady=(10,0))
        self.date_picker = DateEntry(form_frame, width=30, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_picker.pack(pady=5)

        # 3. Time Picker (Hour : Minute)
        ctk.CTkLabel(form_frame, text="Time (HH:MM)").pack(pady=(10,0))
        time_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        time_frame.pack(pady=5)
        
        self.hour_var = ctk.CTkComboBox(time_frame, values=[f"{h:02d}" for h in range(24)], width=80)
        self.hour_var.pack(side="left", padx=5)
        
        ctk.CTkLabel(time_frame, text=":").pack(side="left")
        
        self.min_var = ctk.CTkComboBox(time_frame, values=[f"{m:02d}" for m in range(0, 60, 5)], width=80)
        self.min_var.pack(side="left", padx=5)

        # 4. Duration
        ctk.CTkLabel(form_frame, text="Duration (minutes)").pack(pady=(10,0))
        self.dur_entry = ctk.CTkEntry(form_frame, width=300)
        self.dur_entry.pack(pady=5)

        # 5. Mentee Selection (Listbox inside a frame)
        ctk.CTkLabel(form_frame, text="Select Mentees (Hold Ctrl to select multiple)").pack(pady=(10,0))
        
        lb_frame = ctk.CTkFrame(form_frame, fg_color="#333") 
        lb_frame.pack(pady=5)
        
        self.mentee_list = tk.Listbox(lb_frame, selectmode="multiple", width=45, height=6, bg="#333", fg="white", borderwidth=0, highlightthickness=0)
        self.mentee_list.pack(padx=5, pady=5)
        
        mentees = db_manager.fetch_students_by_role("mentee")
        self.mentee_data = mentees # Store reference to access IDs later
        for m in mentees:
            self.mentee_list.insert("end", f"{m['student_id']} - {m['name']}")

        # Submit Button
        ctk.CTkButton(
            card, text="Schedule Session", command=self.save_session, 
            fg_color="#2CC985", hover_color="#209662", width=300, height=40
        ).pack(pady=30)

    # ================= VIEW 3: FEEDBACK =================
    def load_feedback_view(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="Feedback on Your Sessions", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        table_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        self.style_treeview()
        
        cols = ("ID", "Session", "Rating", "Comment")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
            
        self.tree.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Load Feedback
        all_feedback = db_manager.fetch_all_feedback()
        mentor_id = self.user["student_id"]

        for f in all_feedback:
            if self.is_mentor_session(f["session_id"], mentor_id):
                self.tree.insert("", "end", values=(f["feedback_id"], f["session_id"], f["rating"], f["comment"]))

    # ================= LOGIC HELPERS =================
    def save_session(self):
        if not self.dur_entry.get():
            messagebox.showwarning("Error", "Please enter a duration.")
            return

        subject_id = int(self.subj_var.get().split(" - ")[0])
        final_time = f"{self.date_picker.get()} {self.hour_var.get()}:{self.min_var.get()}:00"
        
        selected_indices = self.mentee_list.curselection()
        if not selected_indices:
            messagebox.showwarning("Error", "Select at least one mentee.")
            return
        
        mentee_ids = [self.mentee_data[i]["student_id"] for i in selected_indices]
        mentee_str = ",".join(str(x) for x in mentee_ids)
        
        if db_manager.schedule_session(subject_id, final_time, int(self.dur_entry.get()), self.user["student_id"], mentee_str):
            messagebox.showinfo("Success", "Session Scheduled Successfully!")
            self.load_sessions_view()

    def fetch_sessions(self):
        conn = db_manager.get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT sess.session_id, subj.subject_name, sess.date_time, sess.duration, sess.status,
                       GROUP_CONCAT(stu.name SEPARATOR ', ') AS mentees
                FROM MentorshipSession sess
                JOIN Subject subj ON sess.subject_id = subj.subject_id
                JOIN SessionParticipant spm ON sess.session_id = spm.session_id AND spm.student_id = %s AND spm.role='mentor'
                LEFT JOIN SessionParticipant spn ON sess.session_id = spn.session_id AND spn.role='mentee'
                LEFT JOIN Student stu ON spn.student_id = stu.student_id
                GROUP BY sess.session_id ORDER BY sess.date_time DESC
            """
            cursor.execute(query, (self.user["student_id"],))
            return cursor.fetchall()
        finally:
            conn.close()

    def mark_as_completed(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection", "Please select a session first.")
            return
        
        session_id = self.tree.item(selected[0])["values"][0]
        if db_manager.update_session_status(session_id, "completed"):
            messagebox.showinfo("Success", "Session marked as completed.")
            self.load_sessions_view()

    def is_mentor_session(self, session_id, mentor_id):
        conn = db_manager.get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM SessionParticipant WHERE session_id=%s AND student_id=%s AND role='mentor'", (session_id, mentor_id))
            return cursor.fetchone()[0] > 0
        finally:
            conn.close()

    def clear_content(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def logout(self):
        self.controller.show_auth_screen()
