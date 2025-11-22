-- ==========================================================
-- PEER TUTORING MATCHING SYSTEM DATABASE (FINAL VERSION)
-- ==========================================================

-- 1️⃣ DATABASE CREATION
<<<<<<< HEAD
DROP DATABASE IF EXISTS PeerTutoring;
=======
>>>>>>> a7666d96e8533c1aeb34802e5ebeeae6ea1660f3
CREATE DATABASE IF NOT EXISTS PeerTutoring;
USE PeerTutoring;

-- ==========================================================
-- 2️⃣ TABLE DEFINITIONS
-- ==========================================================

-- USER TABLE — holds admin, mentors, mentees
CREATE TABLE Student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    ph_no VARCHAR(15) UNIQUE,
    role ENUM('admin', 'mentor', 'mentee') NOT NULL,
    dept VARCHAR(50),
    year INT CHECK (year BETWEEN 1 AND 4)
);

-- SUBJECT TABLE
CREATE TABLE Subject (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT
);

-- TEAM TABLE
CREATE TABLE Team (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    team_name VARCHAR(100) UNIQUE NOT NULL,
    mentor_id INT,
    creation_date DATE,
    FOREIGN KEY (mentor_id) REFERENCES Student(student_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- TEAM MEMBER TABLE
CREATE TABLE TeamMember (
    team_id INT,
    student_id INT,
    role ENUM('mentor', 'mentee') NOT NULL,
    PRIMARY KEY (team_id, student_id),
    FOREIGN KEY (team_id) REFERENCES Team(team_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- STUDENT-SUBJECT TABLE
CREATE TABLE StudentSubject (
    student_id INT,
    subject_id INT,
    PRIMARY KEY (student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- MENTORSHIP SESSION TABLE
CREATE TABLE MentorshipSession (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_id INT,
    date_time DATETIME,
    duration INT,
    status ENUM('scheduled', 'completed', 'cancelled') DEFAULT 'scheduled',
    FOREIGN KEY (subject_id) REFERENCES Subject(subject_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

-- SESSION PARTICIPANT TABLE
CREATE TABLE SessionParticipant (
    session_id INT,
    student_id INT,
    role ENUM('mentor', 'mentee') NOT NULL,
    PRIMARY KEY (session_id, student_id),
    FOREIGN KEY (session_id) REFERENCES MentorshipSession(session_id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- FEEDBACK TABLE
CREATE TABLE Feedback (
    feedback_id INT AUTO_INCREMENT PRIMARY KEY,
    session_id INT,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    anonymous BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (session_id) REFERENCES MentorshipSession(session_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);

-- ==========================================================
-- 3️⃣ SAMPLE DATA (ADMIN, MENTORS, MENTEES)
-- ==========================================================

INSERT INTO Student (name, email, password, ph_no, role, dept, year) VALUES
('Admin User', 'admin@peer.edu', 'admin123', '9000000000', 'admin', 'CSE', 4),
('Maitreyi Vijay', 'maitreyi@univ.edu', 'mentor123', '9876543210', 'mentor', 'CSE', 4),
('Mahith Das', 'mahithk@univ.edu', 'mentee123', '9876501234', 'mentee', 'CSE', 2),
('Aditya Kumar', 'adityak@univ.edu', 'mentee123', '9876505678', 'mentee', 'CSE', 1),
('Divya Singh', 'divyasingh@univ.edu', 'mentor123', '8976512345', 'mentor', 'ECE', 4),
('Esha Patel', 'eshapatel@univ.edu', 'mentee123', '7762523456', 'mentee', 'ECE', 2),
('Ravi Sharma', 'ravisharma@univ.edu', 'mentor123', '9123456789', 'mentor', 'Physics', 4),
('Neha Reddy', 'nehareddy@univ.edu', 'mentor123', '9234567890', 'mentor', 'Chemistry', 4),
('Arjun Mehta', 'arjunmehta@univ.edu', 'mentor123', '9345678901', 'mentor', 'Mathematics', 4),
('Kavya Iyer', 'kavyaiyer@univ.edu', 'mentee123', '9456789012', 'mentee', 'Mathematics', 1),
('Suresh Rao', 'sureshr@univ.edu', 'mentee123', '9567890123', 'mentee', 'Physics', 2);

-- ==========================================================
-- 4️⃣ SUBJECTS
-- ==========================================================

INSERT INTO Subject (subject_name, description) VALUES
('Data Structures', 'Study of linear and non-linear data structures'),
('Databases', 'Relational databases and SQL queries'),
('Computer Networks', 'Networking protocols and communication'),
('Digital Electronics', 'Logic gates and circuits'),
('Engineering Physics', 'Waves, optics, and modern physics'),
('Engineering Mathematics', 'Calculus, linear algebra, differential equations');

-- ==========================================================
-- 5️⃣ TEAMS & TEAM MEMBERS
-- ==========================================================

INSERT INTO Team (team_name, mentor_id, creation_date) VALUES
('CSE Mentors', 2, CURDATE()),
('ECE Mentors', 5, CURDATE()),
('Physics Mentors', 7, CURDATE());

INSERT INTO TeamMember (team_id, student_id, role) VALUES
(1, 2, 'mentor'),
(1, 3, 'mentee'),
(1, 4, 'mentee'),
(2, 5, 'mentor'),
(2, 6, 'mentee'),
(3, 7, 'mentor'),
(3, 11, 'mentee');

-- ==========================================================
-- 6️⃣ MENTORSHIP SESSIONS & PARTICIPANTS
-- ==========================================================

INSERT INTO MentorshipSession (subject_id, date_time, duration, status)
VALUES
(1, '2025-09-10 10:00:00', 60, 'scheduled'),
(2, '2025-09-11 11:00:00', 45, 'completed'),
(5, '2025-09-12 09:00:00', 50, 'scheduled');

INSERT INTO SessionParticipant (session_id, student_id, role) VALUES
(1, 2, 'mentor'),
(1, 3, 'mentee'),
(2, 2, 'mentor'),
(2, 4, 'mentee'),
(3, 7, 'mentor'),
(3, 11, 'mentee');

-- ==========================================================
-- 7️⃣ FEEDBACK
-- ==========================================================

INSERT INTO Feedback (session_id, rating, comment, anonymous)
VALUES
(1, 5, 'Great DS session!', FALSE),
(2, 4, 'Good practical examples.', TRUE);

-- ==========================================================
-- 8️⃣ TRIGGER — AUTO SESSION STATUS UPDATE
-- ==========================================================

DELIMITER //
CREATE TRIGGER update_session_status
BEFORE UPDATE ON MentorshipSession
FOR EACH ROW
BEGIN
    IF NEW.status = 'scheduled' AND NEW.date_time < NOW() THEN
        SET NEW.status = 'completed';
    END IF;
END;
//
DELIMITER ;

-- ==========================================================
-- 9️⃣ PROCEDURE — ADD MENTORSHIP SESSION
-- ==========================================================

DELIMITER //
CREATE PROCEDURE AddMentorshipSession(
    IN p_subject_id INT,
    IN p_date_time DATETIME,
    IN p_duration INT,
    IN p_mentor_id INT,
    IN p_mentee_ids TEXT
)
BEGIN
    DECLARE last_session_id INT;
    DECLARE mentee_id INT;
    DECLARE i INT DEFAULT 1;
    DECLARE mentee_count INT;

    INSERT INTO MentorshipSession(subject_id, date_time, duration)
    VALUES (p_subject_id, p_date_time, p_duration);

    SET last_session_id = LAST_INSERT_ID();

    INSERT INTO SessionParticipant(session_id, student_id, role)
    VALUES (last_session_id, p_mentor_id, 'mentor');

    SET mentee_count = (LENGTH(p_mentee_ids) - LENGTH(REPLACE(p_mentee_ids, ',', ''))) + 1;

    WHILE i <= mentee_count DO
        SET mentee_id = CAST(SUBSTRING_INDEX(SUBSTRING_INDEX(p_mentee_ids, ',', i), ',', -1) AS UNSIGNED);
        INSERT INTO SessionParticipant(session_id, student_id, role)
        VALUES (last_session_id, mentee_id, 'mentee');
        SET i = i + 1;
    END WHILE;
END;
//
DELIMITER ;

-- ==========================================================
-- 🔟 FUNCTION — MENTOR COMPLETED SESSION COUNT
-- ==========================================================

DELIMITER //
CREATE FUNCTION MentorSessionCount(p_mentor_id INT)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total_sessions INT;
    SELECT COUNT(*) INTO total_sessions
    FROM SessionParticipant sp
    JOIN MentorshipSession ms ON sp.session_id = ms.session_id
    WHERE sp.student_id = p_mentor_id
      AND sp.role = 'mentor'
      AND ms.status = 'completed';
    RETURN IFNULL(total_sessions, 0);
END;
//
DELIMITER ;

-- ==========================================================
<<<<<<< HEAD
-- 1️⃣1️⃣ PRIVILEGES 
=======
-- 1️⃣1️⃣ PRIVILEGES (LOGICAL, NOT MYSQL USERS)
>>>>>>> a7666d96e8533c1aeb34802e5ebeeae6ea1660f3
-- ==========================================================

-- Admin: Full control (view/add/delete)
-- Mentor: Create sessions, view mentees, give feedback
-- Mentee: View sessions, give feedback only

-- MySQL-level privileges (optional)
GRANT ALL PRIVILEGES ON PeerTutoring.* TO 'root'@'localhost';

-- ==========================================================
-- ✅ TEST FUNCTION
-- ==========================================================
SELECT MentorSessionCount(2) AS MentorCompletedSessions;

-- ==========================================================
-- ✅ VERIFY ADMIN LOGIN ACCOUNT
-- ==========================================================
SELECT name, email, password, role FROM Student WHERE role='admin';
<<<<<<< HEAD

-- ==========================================================
-- 1️⃣2️⃣ VIEW — INACTIVE MENTEES (NESTED QUERY)
-- ==========================================================
CREATE OR REPLACE VIEW InactiveMentees AS
SELECT student_id, name, email, dept, year
FROM Student
WHERE role = 'mentee' 
AND student_id NOT IN (
    SELECT DISTINCT student_id 
    FROM SessionParticipant 
    WHERE role = 'mentee'
);


-- ==========================================================
-- 1️⃣3️⃣ FUNCTION — TOTAL SYSTEM SESSIONS (AGGREGATE)
-- ==========================================================
-- This satisfies the "Aggregate Query" requirement explicitly in SQL
DELIMITER //
CREATE FUNCTION TotalSessionsCount()
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE total INT;
    -- Aggregate Query: COUNT(*)
    SELECT COUNT(*) INTO total FROM MentorshipSession;
    RETURN total;
END;
//
DELIMITER ;

-- ==========================================================
-- 1️⃣4️⃣ VIEW — SESSION MASTER LIST (COMPLEX JOIN)
-- ==========================================================
-- This satisfies the "Join Query" requirement explicitly.
-- It joins 4 tables to show Session Details + Subject Name + Mentor Name.

CREATE OR REPLACE VIEW SessionMasterList AS
SELECT 
    ms.session_id,
    sub.subject_name,
    ms.date_time,
    ms.duration,
    ms.status,
    stu.name AS mentor_name,
    stu.email AS mentor_email

FROM MentorshipSession ms
JOIN Subject sub ON ms.subject_id = sub.subject_id
JOIN SessionParticipant sp ON ms.session_id = sp.session_id
JOIN Student stu ON sp.student_id = stu.student_id
WHERE sp.role = 'mentor';
=======
>>>>>>> a7666d96e8533c1aeb34802e5ebeeae6ea1660f3
