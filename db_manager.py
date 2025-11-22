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
            password="mkd@sql",   # change to your MySQL password
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


def fetch_all_sessions():
    conn = get_db_connection()
    if not conn: return []

    try:
        cursor = conn.cursor(dictionary=True)
        
        # RUBRIC: USING THE JOIN VIEW WE CREATED IN SQL
        cursor.execute("SELECT * FROM SessionMasterList ORDER BY date_time DESC")
        
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
        
# ==========================================================
# NEW: NESTED QUERY FUNCTION
# ==========================================================
def fetch_inactive_mentees():
    conn = get_db_connection()
    if not conn: return []
    
    try:
        cursor = conn.cursor(dictionary=True)
        # ---------------------------------------------------------
        # NESTED QUERY EXPLANATION:
        # The inner query (SELECT DISTINCT student_id ...) gets a list of all active mentees.
        # The outer query selects students who are NOT IN that list.
        # ---------------------------------------------------------
        query = """
            SELECT student_id, name, email, dept, year
            FROM Student
            WHERE role = 'mentee' 
            AND student_id NOT IN (
                SELECT DISTINCT student_id 
                FROM SessionParticipant 
                WHERE role = 'mentee'
            )
        """
        cursor.execute(query)
        return cursor.fetchall()

    except Exception as e:
        messagebox.showerror("Database Error", f"Error fetching inactive users: {e}")
        return []
        
    finally:
        conn.close()
        
# ==========================================================
# RUBRIC FIXES: SQL FUNCTION & AGGREGATE QUERY
# ==========================================================

# 1. Calls the SQL Stored Function 'MentorSessionCount'
def get_mentor_completed_count_via_function(mentor_id):
    conn = get_db_connection()
    if not conn: return 0
    try:
        cursor = conn.cursor()
        # Call the SQL Function defined in setup.sql
        cursor.execute("SELECT MentorSessionCount(%s)", (mentor_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error calling SQL Function: {e}")
        return 0
    finally:
        conn.close()

def get_total_sessions_aggregate():
    conn = get_db_connection()
    if not conn: return 0
    try:
        cursor = conn.cursor()
        
        # RUBRIC: CALLING THE AGGREGATE FUNCTION DEFINED IN SQL
        cursor.execute("SELECT TotalSessionsCount()") 
        
        result = cursor.fetchone()
        return result[0] if result else 0
    except Exception as e:
        print(f"Error fetching aggregate: {e}")
        return 0
    finally:
        conn.close()
        
# ==========================================================
# EDIT USER FUNCTIONS
# ==========================================================
def get_student_by_id(student_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Student WHERE student_id=%s", (student_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def update_student(student_id, name, email, ph_no, dept, year):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        query = """
            UPDATE Student 
            SET name=%s, email=%s, ph_no=%s, dept=%s, year=%s
            WHERE student_id=%s
        """
        cursor.execute(query, (name, email, ph_no, dept, year, student_id))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Update Error", f"Could not update user: {e}")
        return False
    finally:
        conn.close()
        
# ==========================================================
# DELETE USER FUNCTION
# ==========================================================
def delete_student(student_id):
    conn = get_db_connection()
    if not conn: return False
    try:
        cursor = conn.cursor()
        # ON DELETE CASCADE in your SQL will auto-remove their sessions/feedback
        cursor.execute("DELETE FROM Student WHERE student_id=%s", (student_id,))
        conn.commit()
        return True
    except Exception as e:
        messagebox.showerror("Delete Error", f"Could not delete user: {e}")
        return False
    finally:
        conn.close()
