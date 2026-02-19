import csv
from pathlib import Path
from typing import List, Tuple
from models import StudentManager, CourseManager, EnrollmentManager


def print_table(headers: List[str], rows: List[Tuple], widths: List[int] = None):
    """Prints nicely formatted table."""
    if not rows:
        print("No records found.")
        return

    if widths is None:
        widths = [max(len(str(col)) for col in [h] + [row[i] for row in rows]) 
                  for i, h in enumerate(headers)]

    # Header
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("-" * (sum(widths) + 2 * (len(headers) - 1)))

    # Rows
    for row in rows:
        print("  ".join(str(v).ljust(w) if v is not None else "N/A".ljust(w) 
                        for v, w in zip(row, widths)))


def export_to_csv(filename: str, headers: List[str], rows: List[Tuple]):
    """Export data to CSV with context manager."""
    path = Path(filename)
    try:
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Exported {len(rows)} records to {path.name}")
    except Exception as e:
        print(f"Error exporting to CSV: {e}")


def export_students_to_csv(db, filename: str = "students_export.csv"):
    """Export all students to a clean CSV file."""
    mgr = StudentManager(db)
    students = mgr.get_all_students()
    
    if not students:
        print("No students to export.")
        return
    
    headers = ["id", "name", "email", "major", "year"]
    rows = [(s.id, s.name, s.email, s.major, s.year) for s in students]
    export_to_csv(filename, headers, rows)


def export_enrollments_to_csv(db, filename: str = "enrollments_export.csv"):
    """Export enrollments with readable course & student info."""
    query = """
        SELECT 
            s.id AS student_id,
            s.name AS student_name,
            c.id AS course_id,
            c.course_code,
            c.course_name,
            e.grade
        FROM enrollments e
        JOIN students s ON e.student_id = s.id
        JOIN courses c ON e.course_id = c.id
        ORDER BY s.name, c.course_code
    """
    
    cursor = db.execute(query)
    rows = cursor.fetchall()
    
    if not rows:
        print("No enrollments to export.")
        return
    
    headers = ["student_id", "student_name", "course_id", "course_code", "course_name", "grade"]
    export_to_csv(filename, headers, rows)


def export_gpa_report_to_csv(db, filename: str = "gpa_report.csv"):
    """Export GPA report for all students, including calculated GPA and total credits."""
    student_mgr = StudentManager(db)
    enroll_mgr = EnrollmentManager(db)
    
    students = student_mgr.get_all_students()
    if not students:
        print("No students to export.")
        return
    
    headers = ["id", "name", "email", "major", "year", "gpa", "total_credits", "graded_courses"]
    rows = []
    
    for s in students:
        gpa = enroll_mgr.calculate_gpa(s.id)
        grades = enroll_mgr.get_grades_for_student(s.id)
        total_credits = sum(c for _, _, c, g in grades if g is not None)
        graded_courses = len([g for g in grades if g[3] is not None])
        
        rows.append((s.id, s.name, s.email, s.major, s.year, gpa if gpa else "N/A", total_credits, graded_courses))
    
    export_to_csv(filename, headers, rows)


def import_students_from_csv(db, filename: str) -> int:
    """Import students from CSV. Skips invalid rows. Returns number added."""
    from models import Student
    
    path = Path(filename)
    if not path.is_file():
        print(f"File not found: {filename}")
        return 0
    
    mgr = StudentManager(db)
    added = 0
    skipped = 0
    
    try:
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expected = {"name", "email", "major", "year"}
            
            if not expected.issubset(reader.fieldnames):
                print("CSV must contain columns: name, email, major, year")
                return 0
            
            for row in reader:
                try:
                    year = int(row["year"].strip())
                    if not 1 <= year <= 4:
                        raise ValueError("Year must be 1–4")
                    
                    student = Student(
                        name=row["name"].strip(),
                        email=row["email"].strip(),
                        major=row["major"].strip(),
                        year=year
                    )
                    
                    mgr.add_student(student)
                    added += 1
                    
                except (ValueError, KeyError, sqlite3.IntegrityError) as e:
                    skipped += 1
                    print(f"Skipped row: {row}  →  {e}")
    
        print(f"\nImport complete: {added} students added, {skipped} skipped.")
        return added
        
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return 0


def import_enrollments_from_csv(db, filename: str) -> int:
    """
    Import enrollments using student email + course_code (more user-friendly than IDs).
    Creates enrollment if student & course exist. Grade is optional.
    """
    from models import Enrollment
    
    path = Path(filename)
    if not path.is_file():
        print(f"File not found: {filename}")
        return 0
    
    student_mgr = StudentManager(db)
    course_mgr = CourseManager(db)
    enroll_mgr = EnrollmentManager(db)
    
    added = 0
    skipped = 0
    
    try:
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            expected = {"student_email", "course_code"}
            
            if not expected.issubset(reader.fieldnames):
                print("CSV must contain at least: student_email, course_code")
                print("(grade is optional)")
                return 0
            
            for row in reader:
                try:
                    email = row["student_email"].strip()
                    code = row["course_code"].strip()
                    
                    student = next((s for s in student_mgr.get_all_students() 
                                  if s.email.lower() == email.lower()), None)
                    
                    course = next((c for c in course_mgr.get_all_courses() 
                                 if c.course_code.upper() == code.upper()), None)
                    
                    if not student or not course:
                        raise ValueError("Student or course not found")
                    
                    grade_str = row.get("grade", "").strip()
                    grade = float(grade_str) if grade_str and grade_str.lower() != "none" else None
                    
                    if grade is not None and not 0 <= grade <= 4.0:
                        raise ValueError("Grade must be 0.0–4.0")
                    
                    enroll = Enrollment(
                        student_id=student.id,
                        course_id=course.id,
                        grade=grade
                    )
                    
                    if enroll_mgr.enroll_student(enroll):
                        added += 1
                    else:
                        skipped += 1
                        print(f"Already enrolled: {email} → {code}")
                        
                except (ValueError, KeyError) as e:
                    skipped += 1
                    print(f"Skipped row: {row}  →  {e}")
    
        print(f"\nImport complete: {added} enrollments added, {skipped} skipped.")
        return added
        
    except Exception as e:
        print(f"Failed to read CSV: {e}")
        return 0
