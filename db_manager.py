import mysql.connector
from tkinter import messagebox
import bcrypt


# ==========================================================
# DATABASE CONNECTION
# ==========================================================
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="maitreyi",   # change to your MySQL password
            database="PeerTutoring"
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Database Error", f"Error connecting to MySQL: {e}")
        return None


# ==========================================================
# USER REGISTRATION
# ==========================================================
def register_user(data):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()

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
        conn.close()


# ==========================================================
# LOGIN
# ==========================================================
def login_user(email, password, role):
    conn = get_db_connection()
    if not conn:
        return None

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Student WHERE email=%s AND role=%s", (email, role))
        user = cursor.fetchone()

        if not user:
            return None

        # Check plaintext (existing sample users)
        if user["password"] == password:
            return user

        # Check bcrypt
        try:
            if bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
                return user
        except:
            pass

        return None

    finally:
        conn.close()


# ==========================================================
# FETCH STUDENTS
# ==========================================================
def fetch_students():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Student ORDER BY student_id")
        return cursor.fetchall()

    finally:
        conn.close()


def fetch_students_by_role(role):
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""SELECT student_id, name 
                          FROM Student WHERE role=%s 
                          ORDER BY name""",
                       (role,))
        return cursor.fetchall()

    finally:
        conn.close()


# ==========================================================
# SESSION OPERATIONS
# ==========================================================
def fetch_all_subjects():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT subject_id, subject_name FROM Subject ORDER BY subject_name")
        return cursor.fetchall()
    finally:
        conn.close()


def schedule_session(subject_id, date_time, duration, mentor_id, mentee_ids_str):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.callproc("AddMentorshipSession", (subject_id, date_time, duration, mentor_id, mentee_ids_str))
        conn.commit()
        return True

    except mysql.connector.Error as e:
        conn.rollback()
        messagebox.showerror("Error", f"Could not schedule session: {e}")
        return False

    finally:
        conn.close()


# NEW FUNCTION: fetch all sessions
def fetch_all_sessions():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT session_id, subject_id, date_time, duration, status
            FROM MentorshipSession
            ORDER BY date_time DESC
        """)
        return cursor.fetchall()

    finally:
        conn.close()


def update_session_status(session_id, status):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE MentorshipSession SET status=%s WHERE session_id=%s",
            (status, session_id)
        )
        conn.commit()
        return True

    except mysql.connector.Error as e:
        conn.rollback()
        messagebox.showerror("Database Error", f"Error updating status: {e}")
        return False

    finally:
        conn.close()



# NEW FUNCTION: delete a session
def delete_session(session_id):
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM MentorshipSession WHERE session_id=%s", (session_id,))
        conn.commit()
        return True

    except:
        conn.rollback()
        return False

    finally:
        conn.close()


# NEW FUNCTION: fetch feedback
def fetch_all_feedback():
    conn = get_db_connection()
    if not conn:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Feedback ORDER BY feedback_id DESC")
        return cursor.fetchall()

    finally:
        conn.close()

def refresh_trigger_statuses():
    """
    Forces the trigger to run by re-updating scheduled sessions.
    Any scheduled session with date_time < NOW() will auto-update
    to completed because of the trigger.
    """
    conn = get_db_connection()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE MentorshipSession
            SET status = status
            WHERE status='scheduled'
        """)
        conn.commit()
        return True

    except Exception as e:
        print("Trigger refresh error:", e)
        return False

    finally:
        conn.close()
