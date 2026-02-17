from dataclasses import dataclass
from typing import Optional, List, Dict


class BaseModel:
    """Base class for models, providing common functionality like to_dict."""
    
    def to_dict(self) -> Dict:
        """Convert model to dictionary for easy serialization (e.g., CSV)."""
        return {field: getattr(self, field) for field in self.__dataclass_fields__}


@dataclass
class Student(BaseModel):
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    major: str = ""
    year: int = 1

    @classmethod
    def from_row(cls, row):
        return cls(id=row[0], name=row[1], email=row[2], major=row[3], year=row[4])

    def __str__(self):
        return f"{self.name} ({self.email})"


@dataclass
class Course(BaseModel):
    id: Optional[int] = None
    course_code: str = ""
    course_name: str = ""
    credits: int = 3

    @classmethod
    def from_row(cls, row):
        return cls(id=row[0], course_code=row[1], course_name=row[2], credits=row[3])

    def __str__(self):
        return f"{self.course_code}: {self.course_name} ({self.credits} credits)"


@dataclass
class Enrollment(BaseModel):
    id: Optional[int] = None
    student_id: int = 0
    course_id: int = 0
    grade: Optional[float] = None

    @classmethod
    def from_row(cls, row):
        return cls(id=row[0], student_id=row[1], course_id=row[2], grade=row[3])


class StudentManager:
    """Handles all student-related database operations."""
    
    def __init__(self, db: 'DatabaseConnection'):
        self.db = db

    def add_student(self, student: Student) -> int:
        cursor = self.db.execute("""
            INSERT INTO students (name, email, major, year)
            VALUES (?, ?, ?, ?)
        """, (student.name, student.email, student.major, student.year))
        return cursor.lastrowid

    def get_all_students(self) -> List[Student]:
        cursor = self.db.execute("SELECT * FROM students ORDER BY name")
        return [Student.from_row(row) for row in cursor.fetchall()]

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        cursor = self.db.execute("SELECT * FROM students WHERE id = ?", (student_id,))
        row = cursor.fetchone()
        return Student.from_row(row) if row else None

    def update_student(self, student: Student) -> bool:
        if not student.id:
            return False
        cursor = self.db.execute("""
            UPDATE students
            SET name = ?, email = ?, major = ?, year = ?
            WHERE id = ?
        """, (student.name, student.email, student.major, student.year, student.id))
        return cursor.rowcount > 0

    def delete_student(self, student_id: int) -> bool:
        cursor = self.db.execute("DELETE FROM students WHERE id = ?", (student_id,))
        return cursor.rowcount > 0


class CourseManager:
    """Handles course-related operations."""
    
    def __init__(self, db: 'DatabaseConnection'):
        self.db = db

    def add_course(self, course: Course) -> int:
        cursor = self.db.execute("""
            INSERT INTO courses (course_code, course_name, credits)
            VALUES (?, ?, ?)
        """, (course.course_code, course.course_name, course.credits))
        return cursor.lastrowid

    def get_all_courses(self) -> List[Course]:
        cursor = self.db.execute("SELECT * FROM courses ORDER BY course_code")
        return [Course.from_row(row) for row in cursor.fetchall()]

    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        cursor = self.db.execute("SELECT * FROM courses WHERE id = ?", (course_id,))
        row = cursor.fetchone()
        return Course.from_row(row) if row else None

    def update_course(self, course: Course) -> bool:
        if not course.id:
            return False
        cursor = self.db.execute("""
            UPDATE courses
            SET course_code = ?, course_name = ?, credits = ?
            WHERE id = ?
        """, (course.course_code, course.course_name, course.credits, course.id))
        return cursor.rowcount > 0

    def delete_course(self, course_id: int) -> bool:
        cursor = self.db.execute("DELETE FROM courses WHERE id = ?", (course_id,))
        return cursor.rowcount > 0


class EnrollmentManager:
    """Handles grade recording and GPA calculations."""
    
    def __init__(self, db: 'DatabaseConnection'):
        self.db = db

    def enroll_student(self, enrollment: Enrollment) -> bool:
        try:
            self.db.execute("""
                INSERT INTO enrollments (student_id, course_id, grade)
                VALUES (?, ?, ?)
            """, (enrollment.student_id, enrollment.course_id, enrollment.grade))
            return True
        except sqlite3.IntegrityError:
            return False  # already enrolled

    def update_grade(self, student_id: int, course_id: int, grade: float) -> bool:
        cursor = self.db.execute("""
            UPDATE enrollments
            SET grade = ?
            WHERE student_id = ? AND course_id = ?
        """, (grade, student_id, course_id))
        return cursor.rowcount > 0

    def delete_enrollment(self, student_id: int, course_id: int) -> bool:
        cursor = self.db.execute("""
            DELETE FROM enrollments
            WHERE student_id = ? AND course_id = ?
        """, (student_id, course_id))
        return cursor.rowcount > 0

    def get_grades_for_student(self, student_id: int):
        query = """
            SELECT 
                c.course_code, 
                c.course_name, 
                c.credits,
                e.grade
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = ?
            ORDER BY c.course_code
        """
        cursor = self.db.execute(query, (student_id,))
        return cursor.fetchall()

    def calculate_gpa(self, student_id: int) -> Optional[float]:
        grades = self.get_grades_for_student(student_id)
        if not grades:
            return None
            
        total_points = 0.0
        total_credits = 0
        
        for _, _, credits, grade in grades:
            if grade is not None:
                total_points += grade * credits
                total_credits += credits
                
        return round(total_points / total_credits, 3) if total_credits > 0 else 0.0