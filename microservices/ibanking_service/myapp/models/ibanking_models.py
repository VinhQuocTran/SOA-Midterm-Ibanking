from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey,Date
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class IBankingAccount(db.Model):
    __tablename__ = 'ibanking_account'
    username = db.Column(db.String(64), primary_key=True)
    password = db.Column(db.String(64), nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(16), nullable=False)

class Invoice(db.Model):
    __tablename__ = 'invoice'
    id = db.Column(db.Integer, primary_key=True)
    created_time = db.Column(db.DateTime, nullable=False)
    invoice_type = db.Column(db.String(64), nullable=False)
    ibanking_account_username = db.Column(db.String(64), ForeignKey('ibanking_account.username'))

class TuitionFeeTransaction(db.Model):
    __tablename__ = 'tuition_fee_transaction'
    student_id = db.Column(db.Integer, primary_key=True)
    semester_id = db.Column(db.Integer, primary_key=True)
    total_paid = db.Column(db.Integer, nullable=False)
    created_time = db.Column(db.DateTime, nullable=False)
    invoice_id = db.Column(db.Integer, ForeignKey('invoice.id'))