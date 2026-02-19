# Student Grade Tracker

## Project Title and Description
**Student Grade Tracker** is a command-line application for managing student information, courses, enrollments, and grades. It uses SQLite for persistent storage and supports CRUD operations, GPA calculations, and CSV import/export. This solves the problem of tracking academic performance in a small educational setting, allowing easy management of records and generation of reports like transcripts and GPA summaries.

## Features
- Manage students: Add, view, edit, delete (with confirmation)
- Manage courses: Add, view, edit, delete (with confirmation)
- Manage enrollments/grades: Enroll, update grade, view grades, remove enrollment (with confirmation)
- Reports: Student transcripts with GPA, list all students with GPAs
- Import/Export: Export students/enrollments/GPA reports to CSV; Import students/enrollments from CSV (with validation and confirmation)
- Extra features: Sample data auto-insertion, formatted table outputs, input validation, error handling for all operations

## Database Schema
- **students** table:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - name: TEXT NOT NULL
  - email: TEXT UNIQUE NOT NULL
  - major: TEXT NOT NULL
  - year: INTEGER NOT NULL CHECK(year >= 1 AND year <= 4)

- **courses** table:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - course_code: TEXT UNIQUE NOT NULL
  - course_name: TEXT NOT NULL
  - credits: INTEGER NOT NULL CHECK(credits > 0)

- **enrollments** table:
  - id: INTEGER PRIMARY KEY AUTOINCREMENT
  - student_id: INTEGER NOT NULL FOREIGN KEY REFERENCES students(id) ON DELETE CASCADE
  - course_id: INTEGER NOT NULL FOREIGN KEY REFERENCES courses(id) ON DELETE CASCADE
  - grade: REAL CHECK(grade >= 0 AND grade <= 4.0)
  - UNIQUE(student_id, course_id)

Relationships: Enrollments link students to courses (many-to-many with grades).

## Installation and Setup
- Required Python version: 3.8+
- Dependencies: None (uses built-in sqlite3, csv, pathlib)
- Setup: Run `main.py` – database `student_grade_tracker.db` creates automatically with tables. Sample data inserts if empty.

## Usage Instructions
- Run: `python main.py`
- Navigate menus with numbers (0 to back/exit)
- Example workflows:
  - Add student: Manage Students > 1 > Enter details
  - Enroll: Manage Grades > 1 > Enter IDs (optional grade)
  - View transcript: Reports > 1 > Enter student ID
  - Export GPA: Import/Export > 3
  - Import students: Import/Export > 4 > Confirm and enter filename

## Project Structure
- `database.py`: Manages DB connection and schema creation
- `models.py`: Model classes (Student, Course, Enrollment) and managers for CRUD
- `main.py`: Main app loop, menus, user interactions
- `utils.py`: Helpers for tables, CSV import/export
- `student_grade_tracker.db`: SQLite DB
- `sample_*.csv`: For import testing
- `screenshots/`: Demo images (e.g., menu.png)

Key classes:
- Student/Course/Enrollment: Data models with from_row and __str__
- *Manager: Handle DB ops for each table

## Testing
- Import/Export: Use sample CSVs; test export by running options 1-3
- Sample data: 5 students, 5 courses, 6 enrollments (auto-inserted)
- Run all menu options; confirmations prevent accidents
- Edge cases: Invalid inputs, duplicates, deletions cascade

## Screenshots
- **menu.png**: Main menu  
  ![Main Menu](screenshots/menu.png)
- **add_record.png**: Adding a student  
  ![Add Student](screenshots/add_record.png)
- **view_all.png**: Viewing all students  
  ![View Students](screenshots/view_all.png)
- **delete_student.png**: Deleting a student  
  ![Export](screenshots/export.png)

## Reflection
Challenges: Handling confirmations and cascading deletes; solved with try-except and ON DELETE CASCADE. Learned deeper OOP (inheritance, polymorphism) and SQLite best practices. Future: Add search/filter, web UI, more reports.
