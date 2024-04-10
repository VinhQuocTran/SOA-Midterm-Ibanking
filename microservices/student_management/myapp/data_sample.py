from datetime import datetime,timedelta
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models.student import *
import os

# Create an engine that connects to the student.db SQLite database
db_dir = os.path.join(os.path.dirname(__file__), 'database')
db_path = os.path.join(db_dir, 'student.db')
db_uri = 'sqlite:///{}'.format(db_path)
engine = create_engine(db_uri)

# # Create a sessionmaker bound to this engine
Session = sessionmaker(bind=engine)

# # Now you can create a new session and use it to interact with the database
session = Session()
print(session)

try:
    # Execute a simple query to check the connection
    result = session.execute(text('SELECT 1'))
    print("Connection to the database is successful!")
except OperationalError as e:
    print("Failed to connect to the database:", e)

print('\n\n\n')

# Create students
student1 = Student(name='Student 1')
student2 = Student(name='Student 2')

session.add(student1)
session.add(student2)
session.commit()
print('Students created')

# Create semesters
semester1 = Semester(name='Spring-2024', start_date=datetime(2024, 3, 1), end_date=datetime(2024, 5, 31))
semester2 = Semester(name='Winter-2023', start_date=datetime(2023, 12, 1), end_date=datetime(2024, 2, 28))

session.add(semester1)
session.add(semester2)
session.commit()
print('Semesters created')

# Create installments
installment1 = TuitionFeeSemesterInstallment(name='Spring-2024-Installment-phase-1', start_date=datetime(2024, 3, 20), end_date=datetime(2024, 3, 30), semester_id=semester1.id)
installment2 = TuitionFeeSemesterInstallment(name='Spring-2024-Installment-phase-2', start_date=datetime(2024, 4, 1), end_date=datetime(2024, 4, 1) + timedelta(weeks=3), semester_id=semester1.id)
installment3 = TuitionFeeSemesterInstallment(name='Winter-2023-Installment-phase-1', start_date=datetime(2023, 11, 20), end_date=datetime(2023, 11, 20) + timedelta(weeks=3), semester_id=semester2.id)

# Add and commit the new installments
session.add(installment1)
session.add(installment2)
session.add(installment3)
session.commit()
print('Semester installment created')


# Create courses
course1 = Course(name='English 1')
course2 = Course(name='English 2')
course3 = Course(name='Stats')
course4 = Course(name='Basketball')

session.add(course1)
session.add(course2)
session.add(course3)
session.add(course4)
session.commit()
print('Courses created')

# Create courses in semesters
# Spring semester
course_in_semester1 = CourseInSemester(fee=500, course_id=course1.id, semester_id=semester1.id)
course_in_semester2 = CourseInSemester(fee=700, course_id=course2.id, semester_id=semester1.id)
course_in_semester3 = CourseInSemester(fee=800, course_id=course3.id, semester_id=semester1.id)
course_in_semester4 = CourseInSemester(fee=250, course_id=course4.id, semester_id=semester1.id)

# Winter semester
course_in_semester5 = CourseInSemester(fee=750, course_id=course3.id, semester_id=semester2.id)
course_in_semester6 = CourseInSemester(fee=200, course_id=course4.id, semester_id=semester2.id)

session.add(course_in_semester1)
session.add(course_in_semester2)
session.add(course_in_semester3)
session.add(course_in_semester4)
session.add(course_in_semester5)
session.add(course_in_semester6)
session.commit()
print('Courses in semesters created')

# Create student courses

# Spring semester
student_course1 = StudentCourse(created_time=datetime.now(), student_id=student1.id, course_in_semester_id=course_in_semester1.id)
student_course2 = StudentCourse(created_time=datetime.now(), student_id=student1.id, course_in_semester_id=course_in_semester2.id)
student_course3 = StudentCourse(created_time=datetime.now(), student_id=student2.id, course_in_semester_id=course_in_semester3.id)
student_course4 = StudentCourse(created_time=datetime.now(), student_id=student2.id, course_in_semester_id=course_in_semester4.id)

# Winter semester
student_course5 = StudentCourse(created_time=datetime.now(), student_id=student1.id, course_in_semester_id=course_in_semester5.id)
student_course6 = StudentCourse(created_time=datetime.now(), student_id=student2.id, course_in_semester_id=course_in_semester6.id)

session.add(student_course1)
session.add(student_course2)
session.add(student_course3)
session.add(student_course4)
session.add(student_course5)
session.add(student_course6)
session.commit()
print('Student courses created')

print('**Data sample created successfully!**')
session.close()