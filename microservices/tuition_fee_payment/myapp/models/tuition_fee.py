from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey,Date
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class TuitionFeeInSemester(db.Model):
    __tablename__ = 'tuition_fee_in_semester'
    student_id = db.Column(Integer, primary_key=True)
    semester_id = db.Column(Integer, primary_key=True)
    semester_name = db.Column(String(64))
    total_fee = db.Column(Integer, nullable=False)
    created_time = db.Column(DateTime, nullable=False)
    update_time = db.Column(DateTime, nullable=False)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date, nullable=False)
    payer_id = db.Column(Integer)
    pay_time = db.Column(DateTime)