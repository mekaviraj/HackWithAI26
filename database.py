"""
database.py
Handles SQLite database connection, schema creation, and basic operations.
"""
import sqlite3
from pathlib import Path

DB_PATH = Path("./personalized_coach.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    c = conn.cursor()
    # Students
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL
    )''')
    # Mock Tests
    c.execute('''CREATE TABLE IF NOT EXISTS mock_tests (
        test_id INTEGER PRIMARY KEY,
        student_id INTEGER,
        date TEXT,
        FOREIGN KEY(student_id) REFERENCES students(student_id)
    )''')
    # Questions
    c.execute('''CREATE TABLE IF NOT EXISTS questions (
        question_id INTEGER PRIMARY KEY,
        test_id INTEGER,
        subject TEXT,
        topic TEXT,
        subtopic TEXT,
        difficulty_level TEXT,
        is_correct INTEGER,
        time_taken REAL,
        FOREIGN KEY(test_id) REFERENCES mock_tests(test_id)
    )''')
    # Study Material
    c.execute('''CREATE TABLE IF NOT EXISTS study_material (
        id INTEGER PRIMARY KEY,
        topic TEXT,
        subtopic TEXT,
        resource_type TEXT,
        difficulty_level TEXT,
        resource_title TEXT,
        resource_link_or_text TEXT,
        estimated_time INTEGER
    )''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized.")
