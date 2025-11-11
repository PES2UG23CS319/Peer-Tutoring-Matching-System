import mysql.connector
from tkinter import messagebox
import bcrypt  # 🔐 for secure password hashing


# ----------------------------------------------------------
# DATABASE CONNECTION
# ----------------------------------------------------------
def get_db_connection():
    """Establish connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="maitreyi",  # <-- change if needed
            database="PeerTutoring"
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
        return None


# ----------------------------------------------------------
# USER AUTHENTICATION & REGISTRATION
# ----------------------------------------------------------
def register_user(data):
    """
    Registers a user (mentor/mentee/admin) securely.
    Data must include name, email, password, ph_no, dept, year, role.
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

        # ✅ Hash the password before storing it
        hashed_pw = bcrypt.hashpw(data["password"].encode('utf-8'), bcrypt.gensalt())

        query = """
        INSERT INTO Student (name, email, password, ph_no, role, dept, year)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data["name"],
            data["email"],
            hashed_pw.decode('utf-8'),
            data["ph_no"],
            data["role"],
            data["dept"],
            data["year"]
        ))

        conn.commit()
        return True

    except mysql.connector.Error as e:
        conn.rollback()
        messagebox.showerror("Database Error", f"Error registering user: {e}")
        return False
    finally:
        if conn:
            conn.close()


def login_user(email, password, role):
    """Authenticate a user (admin, mentor, or mentee)."""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)

        # ✅ Now all users (including admin) are in Student table
        cursor.execute("SELECT * FROM Student WHERE email=%s AND role=%s", (email, role))
        user = cursor.fetchone()

        if not user:
            return None

        # --- Handle plaintext passwords (simple demo) ---
        if user["password"] == password:
            return user

        # --- Optional bcrypt check (if any hashed users exist) ---
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                return user
        except Exception:
            pass  # ignore if password isn’t hashed

        return None

    except Exception as e:
        messagebox.showerror("Login Error", f"Error logging in: {e}")
        return None
    finally:
        if conn:
            conn.close()

# ----------------------------------------------------------
# STUDENT MANAGEMENT (CRUD)
# ----------------------------------------------------------
def fetch_students():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Student ORDER BY student_id")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error fetching students: {e}")
        return []
    finally:
        if conn:
            conn.close()


def fetch_students_by_role(role):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT student_id, name FROM Student WHERE role = %s ORDER BY name", (role,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error fetching students by role: {e}")
        return []
    finally:
        if conn:
            conn.close()


# ----------------------------------------------------------
# TEAM MANAGEMENT
# ----------------------------------------------------------
def fetch_teams():
    conn = get_db_connection()
    if not conn:
        return []
    query = """
    SELECT t.team_id, t.team_name, s.name as mentor_name, t.creation_date
    FROM Team t
    LEFT JOIN Student s ON t.mentor_id = s.student_id
    ORDER BY t.team_name
    """
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error fetching teams: {e}")
        return []
    finally:
        if conn:
            conn.close()


def fetch_team_members(team_id):
    conn = get_db_connection()
    if not conn:
        return []
    query = """
    SELECT s.student_id, s.name, tm.role
    FROM TeamMember tm
    JOIN Student s ON tm.student_id = s.student_id
    WHERE tm.team_id = %s
    """
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, (team_id,))
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error fetching team members: {e}")
        return []
    finally:
        if conn:
            conn.close()


# ----------------------------------------------------------
# SESSION MANAGEMENT
# ----------------------------------------------------------
def fetch_all_subjects():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT subject_id, subject_name FROM Subject ORDER BY subject_name")
        return cursor.fetchall()
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error fetching subjects: {e}")
        return []
    finally:
        if conn:
            conn.close()


def schedule_session(subject_id, date_time, duration, mentor_id, mentee_ids_str):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        args = (subject_id, date_time, duration, mentor_id, mentee_ids_str)
        cursor.callproc("AddMentorshipSession", args)
        conn.commit()
        return True
    except mysql.connector.Error as e:
        conn.rollback()
        messagebox.showerror("Database Error", f"Error scheduling session: {e}")
        return False
    finally:
        if conn:
            conn.close()


def update_session_status(session_id, status):
    conn = get_db_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE MentorshipSession SET status=%s WHERE session_id=%s", (status, session_id))
        conn.commit()
        return True
    except mysql.connector.Error as e:
        conn.rollback()
        messagebox.showerror("Database Error", f"Error updating status: {e}")
        return False
    finally:
        if conn:
            conn.close()
