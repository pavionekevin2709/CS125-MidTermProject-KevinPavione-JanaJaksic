import sqlite3
from pathlib import Path


class DatabaseConnection:
    """Manages SQLite connection with context manager support."""
    
    def __init__(self, db_path: str = "student_grade_tracker.db"):
        self.db_path = Path(db_path)
        self.connection = None
        self.cursor = None

    def __enter__(self):
        """Context manager entry - opens connection."""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - commits and closes."""
        if exc_type is None:
            self.connection.commit()
        else:
            self.connection.rollback()
        self.cursor.close()
        self.connection.close()

    def execute(self, query: str, params=()):
        """Execute query with parameters (safe from SQL injection)."""
        self.cursor.execute(query, params)
        return self.cursor

    def executemany(self, query: str, params_list):
        self.cursor.executemany(query, params_list)
        return self.cursor

    def create_tables(self):
        """Create the database schema if it doesn't exist."""
        self.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                major TEXT NOT NULL,
                year INTEGER NOT NULL CHECK(year >= 1 AND year <= 4)
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_code TEXT UNIQUE NOT NULL,
                course_name TEXT NOT NULL,
                credits INTEGER NOT NULL CHECK(credits > 0)
            )
        """)

        self.execute("""
            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                grade REAL CHECK(grade >= 0 AND grade <= 4.0),
                FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE,
                UNIQUE(student_id, course_id)
            )
        """)