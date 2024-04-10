from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Course(db.Model):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)

class Semester(db.Model):
    __tablename__ = 'semester'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

class CourseInSemester(db.Model):
    __tablename__ = 'course_in_semester'
    id = Column(Integer, primary_key=True)
    fee = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    course = relationship('Course')
    semester = relationship('Semester')

class Student(db.Model):
    __tablename__ = 'student'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)

class StudentCourse(db.Model):
    __tablename__ = 'student_course'
    id = Column(Integer, primary_key=True)
    created_time = Column(DateTime, nullable=False)
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    course_in_semester_id = Column(Integer, ForeignKey('course_in_semester.id'), nullable=False)
    student = relationship('Student')
    course_in_semester = relationship('CourseInSemester')

class TuitionFee(db.Model):
    __tablename__ = 'tuition_fee'
    student_id = Column(Integer, ForeignKey('student.id'), primary_key=True)
    semester_id = Column(Integer, ForeignKey('semester.id'), primary_key=True)
    total_fee = Column(Integer, nullable=False)
    created_time = Column(DateTime, nullable=False)
    update_time = Column(DateTime, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    payer_id = Column(Integer)
    paid_time = Column(DateTime)
    student = relationship('Student')
    semester = relationship('Semester')

class TuitionFeeSemesterInstallment(db.Model):
    __tablename__ = 'tuition_fee_semester_installment'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    semester = relationship('Semester')