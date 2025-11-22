import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import db_manager
from PIL import Image

class MenteeDashboard(ctk.CTkFrame):
    def __init__(self, parent, user, controller):
        super().__init__(parent, fg_color="transparent")
        self.parent = parent
        self.user = user
        self.controller = controller
        self.pack(fill="both", expand=True)

        # Grid Layout: Sidebar (col 0) fixed, Content (col 1) expands
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Pre-load icons (Optional)
        try:
            self.icon_home = ctk.CTkImage(Image.open("assets/home.png"), size=(20, 20))
            self.icon_add = ctk.CTkImage(Image.open("assets/add.png"), size=(20, 20))
            self.icon_star = ctk.CTkImage(Image.open("assets/star.png"), size=(20, 20))
        except:
            self.icon_home = None
            self.icon_add = None
            self.icon_star = None

        self.create_dashboard()

    def create_dashboard(self):
        # ================= SIDEBAR =================
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="🎓 Mentee Panel", font=("Roboto Medium", 20)).pack(pady=30)

        # Sidebar Buttons
        self.create_sidebar_btn("📅 My Sessions", self.load_sessions_view, self.icon_home)
        self.create_sidebar_btn("➕ Join Session", self.load_join_session_form, self.icon_add)
        self.create_sidebar_btn("⭐ Give Feedback", self.load_feedback_form, self.icon_star)
        
        ctk.CTkButton(
            self.sidebar, text="Logout", fg_color="#FF5555", hover_color="#CC0000",
            command=self.logout
        ).pack(side="bottom", pady=20, padx=20, fill="x")

        # ================= CONTENT AREA =================
        self.content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
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
        
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b", 
                        rowheight=30, 
                        borderwidth=0)
        
        style.map('Treeview', background=[('selected', '#EDB72B')]) 
        
        style.configure("Treeview.Heading", 
                        background="#1f1f1f", 
                        foreground="white", 
                        relief="flat", 
                        font=("Roboto", 10, "bold"))
        
        style.map("Treeview.Heading", background=[('active', '#EDB72B')])

    # ================= VIEW 1: MY SESSIONS (Stats + Table) =================
    def load_sessions_view(self):
        self.clear_content()
        ctk.CTkLabel(self.content_frame, text="My Scheduled Sessions", font=("Roboto", 24, "bold")).pack(anchor="w", pady=(0, 20))

        # --- STATS BOARD ---
        stats_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        stats_frame.pack(fill="x", pady=(0, 20))

        # 1. Total System Sessions (Aggregate Query from DB)
        total_sys = db_manager.get_total_sessions_aggregate()

        # 2. Calculate My Stats
        sessions = self.fetch_sessions()
        my_completed = sum(1 for s in sessions if s['status'] == 'completed')
        my_upcoming = sum(1 for s in sessions if s['status'] == 'scheduled')

        self.create_stat_card(stats_frame, "Total System Sessions", total_sys, "#3B8ED0")
        self.create_stat_card(stats_frame, "My Completed", my_completed, "#2CC985")
        self.create_stat_card(stats_frame, "My Upcoming", my_upcoming, "#EDB72B")
        # -------------------

        # Table Title
        ctk.CTkLabel(self.content_frame, text="Session History", font=("Roboto", 18, "bold")).pack(anchor="w", pady=(10, 5))

        # Table Frame
        table_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)

        self.style_treeview()
        cols = ("ID", "Subject", "Date", "Duration", "Status", "Mentor")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")
        
        for c in cols: 
            self.tree.heading(c, text=c)
            self.tree.column(c, width=130, anchor="center")
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, orientation="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Load Data
        for s in sessions:
            self.tree.insert("", "end", values=(s["session_id"], s["subject_name"], s["date_time"], s["duration"], s["status"], s["mentor_name"]))

    # ================= VIEW 2: JOIN SESSION =================
    def load_join_session_form(self):
        self.clear_content()
        
        card = ctk.CTkFrame(self.content_frame, corner_radius=15)
        card.pack(fill="both", expand=True, padx=50, pady=20)
        
        ctk.CTkLabel(card, text="Join an Available Session", font=("Roboto", 22, "bold")).pack(pady=20)

        conn = db_manager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT sess.session_id, subj.subject_name, sess.date_time 
            FROM MentorshipSession sess 
            JOIN Subject subj ON sess.subject_id=subj.subject_id 
            WHERE sess.status='scheduled'
        """)
        avail = cursor.fetchall()
        conn.close()

        if not avail:
            ctk.CTkLabel(card, text="No open sessions found at this time.", text_color="gray").pack(pady=20)
            return

        ctk.CTkLabel(card, text="Select a Session to Join").pack(pady=(10,0))
        
        self.join_var = ctk.CTkComboBox(
            card, 
            values=[f"{s['session_id']} - {s['subject_name']} ({s['date_time']})" for s in avail], 
            width=400, height=40
        )
        self.join_var.pack(pady=10)

        ctk.CTkButton(
            card, text="Join Session", command=self.join_session, 
            fg_color="#EDB72B", hover_color="#D4A017", text_color="black", 
            width=200, height=40
        ).pack(pady=30)

    def join_session(self):
        if not self.join_var.get():
            messagebox.showwarning("Error", "Please select a session.")
            return
            
        sid = int(self.join_var.get().split(" - ")[0])
        
        conn = db_manager.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO SessionParticipant (session_id, student_id, role) VALUES (%s, %s, 'mentee')", (sid, self.user["student_id"]))
            conn.commit()
            messagebox.showinfo("Success", "You have successfully joined the session!")
            self.load_sessions_view()
        except db_manager.mysql.connector.IntegrityError:
            messagebox.showwarning("Warning", "You have already joined this session.")
        except Exception as e:
            messagebox.showerror("Error", f"Could not join: {e}")
        finally: 
            conn.close()

    # ================= VIEW 3: FEEDBACK FORM =================
    def load_feedback_form(self):
        self.clear_content()
        
        card = ctk.CTkFrame(self.content_frame, corner_radius=15)
        card.pack(fill="both", expand=True, padx=50, pady=20)
        
        ctk.CTkLabel(card, text="Submit Feedback", font=("Roboto", 22, "bold")).pack(pady=20)
        
        # 1. Fetch completed sessions
        conn = db_manager.get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT sess.session_id, subj.subject_name
            FROM MentorshipSession sess
            JOIN Subject subj ON sess.subject_id=subj.subject_id
            JOIN SessionParticipant sp ON sess.session_id = sp.session_id
            WHERE sp.student_id = %s AND sp.role='mentee' AND sess.status='completed'
        """, (self.user["student_id"],))
        sessions = cursor.fetchall()
        conn.close()

        if not sessions:
            ctk.CTkLabel(card, text="You have no completed sessions to rate.", text_color="gray").pack(pady=20)
            return
        
        # 2. Session Dropdown
        ctk.CTkLabel(card, text="Select Completed Session").pack(pady=(10,0))
        self.fb_sess = ctk.CTkComboBox(
            card, 
            values=[f"{s['session_id']} - {s['subject_name']}" for s in sessions], 
            width=300
        ) 
        self.fb_sess.pack(pady=5)
        
        # 3. Rating Dropdown
        ctk.CTkLabel(card, text="Rating (1 = Poor, 5 = Excellent)").pack(pady=(10,0))
        self.fb_rate = ctk.CTkComboBox(card, values=["1","2","3","4","5"], width=300)
        self.fb_rate.pack(pady=5)
        
        # 4. Comment Box
        ctk.CTkLabel(card, text="Comment").pack(pady=(10,0))
        self.fb_comment = ctk.CTkTextbox(card, width=400, height=100)
        self.fb_comment.pack(pady=5)
        
        # 5. Anonymous Checkbox
        self.anon_var = ctk.BooleanVar()
        ctk.CTkCheckBox(card, text="Submit Anonymously", variable=self.anon_var, text_color="white").pack(pady=10)
        
        # Submit Button
        ctk.CTkButton(
            card, text="Submit Feedback", command=self.submit_feedback,
            fg_color="#EDB72B", hover_color="#D4A017", text_color="black",
            width=200, height=40
        ).pack(pady=20)

    def submit_feedback(self):
        if not self.fb_sess.get() or not self.fb_rate.get():
            messagebox.showwarning("Error", "Please select a session and a rating.")
            return

        session_id = int(self.fb_sess.get().split(" - ")[0])
        rating = int(self.fb_rate.get())
        comment = self.fb_comment.get("1.0", "end").strip()
        anon = self.anon_var.get()

        conn = db_manager.get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO Feedback (session_id, rating, comment, anonymous)
                VALUES (%s, %s, %s, %s)
            """, (session_id, rating, comment, anon))
            conn.commit()
            messagebox.showinfo("Success", "Feedback submitted! Thank you.")
            self.load_sessions_view()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit: {e}")
        finally:
            conn.close()

    # ================= HELPERS =================
    def fetch_sessions(self):
        conn = db_manager.get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT sess.session_id, subj.subject_name, sess.date_time, 
                   sess.duration, sess.status, stu.name AS mentor_name
            FROM MentorshipSession sess
            JOIN Subject subj ON sess.subject_id = subj.subject_id
            JOIN SessionParticipant sp ON sess.session_id = sp.session_id
            JOIN SessionParticipant spm ON sess.session_id = spm.session_id AND spm.role='mentor'
            JOIN Student stu ON spm.student_id = stu.student_id
            WHERE sp.student_id = %s AND sp.role = 'mentee'
            ORDER BY sess.date_time DESC
            """
            cursor.execute(query, (self.user["student_id"],))
            return cursor.fetchall()
        finally:
            conn.close()

    def clear_content(self):
        for w in self.content_frame.winfo_children():
            w.destroy()

    def logout(self):
        self.controller.show_auth_screen()
