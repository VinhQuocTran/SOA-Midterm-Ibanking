from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'student'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(64), nullable=False)
    email = db.Column(String(64), nullable=False)
    phone = db.Column(String(15), nullable=False)
    password = db.Column(String(64), nullable=False)
    balance = db.Column(Integer, nullable=False)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Semester(db.Model):
    __tablename__ = 'semester'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(64), nullable=False)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=False)

class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(64), nullable=False)

class CourseInSemester(db.Model):
    __tablename__ = 'course_in_semester'
    id = db.Column(Integer, primary_key=True)
    fee = db.Column(Integer, nullable=False)
    course_id = db.Column(Integer, ForeignKey('course.id'), nullable=False)
    semester_id = db.Column(Integer, ForeignKey('semester.id'), nullable=False)

class StudentCourse(db.Model):
    __tablename__ = 'student_course'
    id = db.Column(Integer, primary_key=True)
    created_time = db.Column(Date, nullable=False)
    student_id = db.Column(Integer, ForeignKey('student.id'), nullable=False)
    course_in_semester_id = db.Column(Integer, ForeignKey('course_in_semester.id'), nullable=False)

class TuitionFeeSemesterInstallment(db.Model):
    __tablename__ = 'tuition_fee_semester_installment'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(64), nullable=False)
    start_date = db.Column(DateTime, nullable=False)
    end_date = db.Column(DateTime, nullable=False)
    semester_id = db.Column(Integer, ForeignKey('semester.id'), nullable=False)