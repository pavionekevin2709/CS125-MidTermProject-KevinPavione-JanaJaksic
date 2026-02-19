import sqlite3
from database import DatabaseConnection
from models import Student, Course, Enrollment, StudentManager, CourseManager, EnrollmentManager
from utils import print_table, export_students_to_csv, export_enrollments_to_csv, export_gpa_report_to_csv, import_students_from_csv, import_enrollments_from_csv


def clear_screen():
    print("\033c", end="")


def show_main_menu():
    print("\n" + "="*50)
    print("      STUDENT GRADE TRACKER")
    print("="*50)
    print("1. Manage Students")
    print("2. Manage Courses")
    print("3. Manage Grades / Enrollments")
    print("4. View Reports")
    print("5. Import / Export Data")
    print("0. Exit")
    print("="*50)


def show_student_menu():
    print("\n--- Student Management ---")
    print("1. Add new student")
    print("2. View all students")
    print("3. Edit student")
    print("4. Delete student")
    print("0. Back")


def show_course_menu():
    print("\n--- Course Management ---")
    print("1. Add new course")
    print("2. View all courses")
    print("3. Edit course")
    print("4. Delete course")
    print("0. Back")


def show_grades_menu():
    print("\n--- Grades & Enrollments ---")
    print("1. Enroll student in course")
    print("2. Update grade")
    print("3. View student grades")
    print("4. Remove enrollment")
    print("0. Back")


def show_reports_menu():
    print("\n--- Reports ---")
    print("1. View student transcript / GPA")
    print("2. List all students with GPA")
    print("0. Back")


def show_import_export_menu():
    print("\n--- Import / Export ---")
    print("1. Export all students to CSV")
    print("2. Export all enrollments to CSV")
    print("3. Export GPA report to CSV")
    print("4. Import students from CSV")
    print("5. Import enrollments from CSV")
    print("0. Back")


def insert_sample_data(db, student_mgr, course_mgr, enroll_mgr):
    """Insert sample data if database is empty."""
    if student_mgr.get_all_students():
        return  # Already has data
    
    # Sample students
    students = [
        Student(name="Mercy Akegbesola", email="akegbesolamercy@myocu.oak.edu", major="Computer Science", year=2),
        Student(name="Santiago Salazar", email="salazarsantiago@myocu.oak.edu", major="Cybersecurity", year=1),
        Student(name="Jana Jaksic", email="jaksicjana@myocu.oak.edu", major="Computer Science", year=3),
        Student(name="Paul Muller", email="mullerpaul@myocu.oak.edu", major="Cybersecurity", year=2),
        Student(name="Kevin Pavione", email="pavionekevin@myocu.oak.edu", major="Computer Science", year=2),
    ]
    student_ids = [student_mgr.add_student(s) for s in students]
    
    # Sample courses
    courses = [
        Course(course_code="CS101", course_name="Intro to Programming", credits=3),
        Course(course_code="CS220", course_name="Data Structures & Algorithms", credits=4),
        Course(course_code="CYBR210", course_name="Network Security Fundamentals", credits=3),
        Course(course_code="CS350", course_name="Database Systems", credits=3),
        Course(course_code="MATH225", course_name="Discrete Mathematics", credits=4),
    ]
    course_ids = [course_mgr.add_course(c) for c in courses]
    
    # Sample enrollments
    enrollments = [
        Enrollment(student_id=student_ids[0], course_id=course_ids[0], grade=3.7),
        Enrollment(student_id=student_ids[0], course_id=course_ids[1]),
        Enrollment(student_id=student_ids[1], course_id=course_ids[2], grade=3.2),
        Enrollment(student_id=student_ids[2], course_id=course_ids[3], grade=4.0),
        Enrollment(student_id=student_ids[3], course_id=course_ids[4], grade=3.9),
        Enrollment(student_id=student_ids[4], course_id=course_ids[0], grade=3.5),
    ]
    for e in enrollments:
        enroll_mgr.enroll_student(e)
    
    print("Inserted sample data for testing.")


def main():
    with DatabaseConnection() as db:
        db.create_tables()
        
        student_mgr = StudentManager(db)
        course_mgr = CourseManager(db)
        enroll_mgr = EnrollmentManager(db)
        
        insert_sample_data(db, student_mgr, course_mgr, enroll_mgr)

        while True:
            clear_screen()
            show_main_menu()
            
            choice = input("\nEnter choice: ").strip()
            
            if choice == "0":
                print("\nThanks for using the Student Grade Tracker. Goodbye!\n")
                break
                
            elif choice == "1":  # Manage Students
                while True:
                    clear_screen()
                    show_student_menu()
                    sub = input("\nChoice: ").strip()
                    
                    if sub == "0":
                        break
                        
                    elif sub == "1":  # Add student
                        name = input("Full name: ").strip()
                        email = input("Email: ").strip()
                        major = input("Major: ").strip()
                        try:
                            year = int(input("Year (1-4): "))
                            if not 1 <= year <= 4:
                                raise ValueError
                        except ValueError:
                            print("Invalid input: Year must be 1–4.")
                            input("Press Enter to continue...")
                            continue
                            
                        student = Student(name=name, email=email, major=major, year=year)
                        try:
                            sid = student_mgr.add_student(student)
                            print(f"\nStudent added successfully! ID = {sid}")
                        except sqlite3.IntegrityError:
                            print("Error: Email already exists or invalid data.")
                        input("Press Enter to continue...")
                    
                    elif sub == "2":  # View all
                        students = student_mgr.get_all_students()
                        rows = [(s.id, s.name, s.email, s.major, s.year) for s in students]
                        print_table(["ID", "Name", "Email", "Major", "Year"], rows)
                        input("Press Enter to continue...")
                    
                    elif sub == "3":  # Edit student
                        try:
                            sid = int(input("Student ID to edit: "))
                            student = student_mgr.get_student_by_id(sid)
                            if not student:
                                print("Student not found.")
                                input("Press Enter to continue...")
                                continue
                                
                            print(f"\nEditing {student}. Leave blank to keep current.")
                            name = input(f"New name ({student.name}): ").strip() or student.name
                            email = input(f"New email ({student.email}): ").strip() or student.email
                            major = input(f"New major ({student.major}): ").strip() or student.major
                            year_str = input(f"New year ({student.year}): ").strip()
                            year = int(year_str) if year_str else student.year
                            
                            if not 1 <= year <= 4:
                                print("Invalid year: Must be 1–4.")
                                input("Press Enter to continue...")
                                continue
                                
                            confirm = input("\nSave changes? (y/n): ").lower().strip()
                            if confirm != 'y':
                                print("Changes discarded.")
                                input("Press Enter to continue...")
                                continue
                                
                            student.name = name
                            student.email = email
                            student.major = major
                            student.year = year
                            
                            if student_mgr.update_student(student):
                                print("Student updated successfully.")
                            else:
                                print("Update failed.")
                        except ValueError:
                            print("Invalid ID.")
                        except sqlite3.IntegrityError:
                            print("Error: Email already exists.")
                        input("Press Enter to continue...")
                    
                    elif sub == "4":  # Delete student
                        try:
                            sid = int(input("Student ID to delete: "))
                            student = student_mgr.get_student_by_id(sid)
                            if not student:
                                print("Student not found.")
                                input("Press Enter to continue...")
                                continue
                                
                            print(f"\nDeleting {student} will also remove their enrollments.")
                            confirm = input("Are you sure? (y/n): ").lower().strip()
                            if confirm != 'y':
                                print("Deletion cancelled.")
                                input("Press Enter to continue...")
                                continue
                                
                            if student_mgr.delete_student(sid):
                                print("Student deleted successfully.")
                            else:
                                print("Deletion failed.")
                        except ValueError:
                            print("Invalid ID.")
                        input("Press Enter to continue...")
            
            elif choice == "2":  # Manage Courses
                while True:
                    clear_screen()
                    show_course_menu()
                    sub = input("\nChoice: ").strip()
                    
                    if sub == "0":
                        break
                        
                    elif sub == "1":  # Add course
                        code = input("Course code (e.g., CS101): ").strip().upper()
                        name = input("Course name: ").strip()
                        try:
                            credits = int(input("Credits (>0): "))
                            if credits <= 0:
                                raise ValueError
                        except ValueError:
                            print("Invalid input: Credits must be positive integer.")
                            input("Press Enter to continue...")
                            continue
                            
                        course = Course(course_code=code, course_name=name, credits=credits)
                        try:
                            cid = course_mgr.add_course(course)
                            print(f"\nCourse added successfully! ID = {cid}")
                        except sqlite3.IntegrityError:
                            print("Error: Course code already exists.")
                        input("Press Enter to continue...")
                    
                    elif sub == "2":  # View all
                        courses = course_mgr.get_all_courses()
                        rows = [(c.id, c.course_code, c.course_name, c.credits) for c in courses]
                        print_table(["ID", "Code", "Name", "Credits"], rows)
                        input("Press Enter to continue...")
                    
                    elif sub == "3":  # Edit course
                        try:
                            cid = int(input("Course ID to edit: "))
                            course = course_mgr.get_course_by_id(cid)
                            if not course:
                                print("Course not found.")
                                input("Press Enter to continue...")
                                continue
                                
                            print(f"\nEditing {course}. Leave blank to keep current.")
                            code = input(f"New code ({course.course_code}): ").strip().upper() or course.course_code
                            name = input(f"New name ({course.course_name}): ").strip() or course.course_name
                            credits_str = input(f"New credits ({course.credits}): ").strip()
                            credits = int(credits_str) if credits_str else course.credits
                            
                            if credits <= 0:
                                print("Invalid credits: Must be >0.")
                                input("Press Enter to continue...")
                                continue
                                
                            confirm = input("\nSave changes? (y/n): ").lower().strip()
                            if confirm != 'y':
                                print("Changes discarded.")
                                input("Press Enter to continue...")
                                continue
                                
                            course.course_code = code
                            course.course_name = name
                            course.credits = credits
                            
                            if course_mgr.update_course(course):
                                print("Course updated successfully.")
                            else:
                                print("Update failed.")
                        except ValueError:
                            print("Invalid ID.")
                        except sqlite3.IntegrityError:
                            print("Error: Course code already exists.")
                        input("Press Enter to continue...")
                    
                    elif sub == "4":  # Delete course
                        try:
                            cid = int(input("Course ID to delete: "))
                            course = course_mgr.get_course_by_id(cid)
                            if not course:
                                print("Course not found.")
                                input("Press Enter to continue...")
                                continue
                                
                            print(f"\nDeleting {course} will also remove related enrollments.")
                            confirm = input("Are you sure? (y/n): ").lower().strip()
                            if confirm != 'y':
                                print("Deletion cancelled.")
                                input("Press Enter to continue...")
                                continue
                                
                            if course_mgr.delete_course(cid):
                                print("Course deleted successfully.")
                            else:
                                print("Deletion failed.")
                        except ValueError:
                            print("Invalid ID.")
                        input("Press Enter to continue...")
            
            elif choice == "3":  # Manage Grades/Enrollments
                while True:
                    clear_screen()
                    show_grades_menu()
                    sub = input("\nChoice: ").strip()
                    
                    if sub == "0":
                        break
                        
                    elif sub == "1":  # Enroll
                        try:
                            sid = int(input("Student ID: "))
                            cid = int(input("Course ID: "))
                            
                            student = student_mgr.get_student_by_id(sid)
                            course = course_mgr.get_course_by_id(cid)
                            if not student or not course:
                                print("Student or course not found.")
                                input("Press Enter to continue...")
                                continue
                                
                            grade_str = input("Initial grade (optional, 0-4.0): ").strip()
                            grade = float(grade_str) if grade_str else None
                            if grade is not None and not 0 <= grade <= 4.0:
                                print("Invalid grade: Must be 0.0–4.0.")
                                input("Press Enter to continue...")
                                continue
                                
                            enroll = Enrollment(student_id=sid, course_id=cid, grade=grade)
                            if enroll_mgr.enroll_student(enroll):
                                print(f"\nEnrolled {student} in {course} successfully.")
                            else:
                                print("Already enrolled or invalid data.")
                        except ValueError:
                            print("Invalid ID or grade.")
                        input("Press Enter to continue...")
                    
                    elif sub == "2":  # Update grade
                        try:
                            sid = int(input("Student ID: "))
                            cid = int(input("Course ID: "))
                            grade = float(input("New grade (0-4.0): "))
                            
                            if not 0 <= grade <= 4.0:
                                print("Invalid grade.")
                                input("Press Enter to continue...")
                                continue
                                
                            if enroll_mgr.update_grade(sid, cid, grade):
                                print("Grade updated successfully.")
                            else:
                                print("Enrollment not found.")
                        except ValueError:
                            print("Invalid input.")
                        input("Press Enter to continue...")
                    
                    elif sub == "3":  # View grades
                        try:
                            sid = int(input("Student ID: "))
                            student = student_mgr.get_student_by_id(sid)
                            if not student:
                                print("Student not found.")
                                input("Press Enter to continue...")
                                continue
                                
                            grades = enroll_mgr.get_grades_for_student(sid)
                            rows = [(code, name, cred, grade if grade else "In Progress") 
                                    for code, name, cred, grade in grades]
                            print_table(["Code", "Course", "Credits", "Grade"], rows, [8, 35, 8, 10])
                        except ValueError:
                            print("Invalid ID.")
                        input("Press Enter to continue...")
                    
                    elif sub == "4":  # Remove enrollment
                        try:
                            sid = int(input("Student ID: "))
                            cid = int(input("Course ID: "))
                            
                            student = student_mgr.get_student_by_id(sid)
                            course = course_mgr.get_course_by_id(cid)
                            if not student or not course:
                                print("Student or course not found.")
                                input("Press Enter to continue...")
                                continue
                                
                            confirm = input(f"Remove {student} from {course}? (y/n): ").lower().strip()
                            if confirm != 'y':
                                print("Removal cancelled.")
                                input("Press Enter to continue...")
                                continue
                                
                            if enroll_mgr.delete_enrollment(sid, cid):
                                print("Enrollment removed successfully.")
                            else:
                                print("Enrollment not found.")
                        except ValueError:
                            print("Invalid ID.")
                        input("Press Enter to continue...")
            
            elif choice == "4":  # View Reports
                while True:
                    clear_screen()
                    show_reports_menu()
                    sub = input("\nChoice: ").strip()
                    
                    if sub == "0":
                        break
                        
                    elif sub == "1":  # Transcript/GPA
                        try:
                            sid = int(input("Student ID: "))
                            student = student_mgr.get_student_by_id(sid)
                            if not student:
                                print("Student not found.")
                                input("Press Enter to continue...")
                                continue
                                
                            grades = enroll_mgr.get_grades_for_student(sid)
                            gpa = enroll_mgr.calculate_gpa(sid)
                            
                            print(f"\nTranscript for {student.name} ({student.major}, Year {student.year})")
                            print("-"*60)
                            rows = [(code, name, cred, grade if grade else "In Progress") 
                                    for code, name, cred, grade in grades]
                            print_table(["Code", "Course", "Credits", "Grade"], rows, [8, 35, 8, 10])
                            
                            if gpa is not None:
                                print(f"\nCurrent GPA: {gpa:.3f}")
                            else:
                                print("\nNo graded courses yet.")
                        except ValueError:
                            print("Invalid ID.")
                        input("Press Enter to continue...")
                    
                    elif sub == "2":  # All with GPA
                        students = student_mgr.get_all_students()
                        rows = []
                        for s in students:
                            gpa = enroll_mgr.calculate_gpa(s.id)
                            rows.append((s.id, s.name, s.major, gpa if gpa is not None else "N/A"))
                        print_table(["ID", "Name", "Major", "GPA"], rows)
                        input("Press Enter to continue...")
            
            elif choice == "5":  # Import/Export
                while True:
                    clear_screen()
                    show_import_export_menu()
                    sub = input("\nChoice: ").strip()
                    
                    if sub == "0":
                        break
                        
                    elif sub == "1":
                        filename = input("Filename (default: students_export.csv): ").strip() or "students_export.csv"
                        export_students_to_csv(db, filename)
                        input("Press Enter to continue...")
                        
                    elif sub == "2":
                        filename = input("Filename (default: enrollments_export.csv): ").strip() or "enrollments_export.csv"
                        export_enrollments_to_csv(db, filename)
                        input("Press Enter to continue...")
                        
                    elif sub == "3":
                        filename = input("Filename (default: gpa_report.csv): ").strip() or "gpa_report.csv"
                        export_gpa_report_to_csv(db, filename)
                        input("Press Enter to continue...")
                        
                    elif sub == "4":
                        filename = input("Filename (default: sample_students_import.csv): ").strip() or "sample_students_import.csv"
                        confirm = input(f"Import from {filename}? This adds new students (y/n): ").lower().strip()
                        if confirm == 'y':
                            import_students_from_csv(db, filename)
                        else:
                            print("Import cancelled.")
                        input("Press Enter to continue...")
                        
                    elif sub == "5":
                        filename = input("Filename (default: sample_enrollments_import.csv): ").strip() or "sample_enrollments_import.csv"
                        confirm = input(f"Import from {filename}? This adds new enrollments (y/n): ").lower().strip()
                        if confirm == 'y':
                            import_enrollments_from_csv(db, filename)
                        else:
                            print("Import cancelled.")
                        input("Press Enter to continue...")


if __name__ == "__main__":
    main()
