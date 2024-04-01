from myapp import db
from flask import Blueprint, request,jsonify
import requests
from datetime import datetime
from sqlalchemy import text,null,desc
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from myapp.models.tuition_fee import *


import smtplib
from email.mime.text import MIMEText
import random

tuition_payment_blueprint = Blueprint('TuitionPayment', __name__)

@tuition_payment_blueprint.route('/api/update_tuition_fee', methods=['GET']) 
@jwt_required()
def update_tuition_fee():
    semester_id= int(request.args.get('semester_id'))
    headers = {
        'Content-Type': 'application/json'
    }

    url=f"http://localhost:8000/api/get_tuition_fee?semester_id={semester_id}"
    response = requests.get(url,headers=headers)
    data=response.json()

    values = ', '.join([
        f"({int(record['student_id'])}, {int(record['semester_id'])}, {record['total_fee']}, '{record['start_date']}', '{record['end_date']}', '{datetime.utcnow()}', '{datetime.utcnow()}')"
        for record in data
    ])

    sql = text(f"""
        INSERT INTO tuition_fee_in_semester (student_id, semester_id, total_fee, start_date, end_date, created_time, update_time)
        VALUES {values}
        ON CONFLICT (student_id, semester_id)
        DO UPDATE SET total_fee = EXCLUDED.total_fee, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date, update_time = EXCLUDED.update_time
    """)

    with db.session.begin():
        db.session.execute(sql)
    
    db.session.commit()

    return jsonify(msg='Tuition fee updated'), 200

@tuition_payment_blueprint.route('/api/latest_tuition_fees/<int:student_id>', methods=['GET'])
@jwt_required()
def get_latest_tuition_fee(student_id):
    tuition_fee = db.session.query(TuitionFeeInSemester.total_fee).filter_by(student_id=student_id, payer_id=None).order_by(desc(TuitionFeeInSemester.start_date)).first()

    if tuition_fee is None:
        return jsonify({'error': 'No tuition fee found for this student'}), 404

    return jsonify({'total_fee': tuition_fee.total_fee}), 200



@tuition_payment_blueprint.route('/api/latest_tuition_fees/<int:payee_id>', methods=['POST']) 
@jwt_required()
def pay_tuition_fee(payee_id):
    payer_id=get_jwt_identity()
    session = db.session()

    # Get the latest tuition fee
    tuition_fee = session.query(TuitionFeeInSemester.total_fee).filter_by(student_id=payee_id, payer_id=None).order_by(desc(TuitionFeeInSemester.start_date)).first()
    if tuition_fee is None:
        return jsonify({'error': 'No tuition fee found for this student'}), 404
    
    # Get the payer's balance
    access_token=request.headers.get("Authorization")
    response = requests.get(f"http://localhost:8000/api/users/myself", headers={'Authorization': access_token})
    payer_balance=response.json()['balance']

    if payer_balance < tuition_fee.total_fee:
        return jsonify({'error': 'Insufficient balance'}), 400
    
    try:
        # Update the payer's balance
        response = requests.post(f"http://localhost:8000/api/users/myself", headers={'Authorization':access_token}, json={'balance': payer_balance - tuition_fee.total_fee})

        if response.status_code != 200:
            return jsonify({'error': 'Failed to update payer balance'}), 500
        
        # Update the tuition fee
        session.query(TuitionFeeInSemester).filter_by(student_id=payee_id, payer_id=None).update({'payer_id': payer_id,'pay_time': datetime.utcnow()})

        session.commit()

        return jsonify({'msg': 'Tuition fee paid'}), 200

    except SQLAlchemyError as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()



@tuition_payment_blueprint.route('/api/send_otp', methods=['POST']) 
@jwt_required()
def otp_6_digit():
    # Get data from request
    data = request.get_json()
    from_email = data.get('from_email')
    from_email_app_password = data.get('from_email_app_password')
    to_email = data.get('to_email')

    # Set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(from_email, from_email_app_password)  # replace with your email and password

    # Create the message
    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    msg = MIMEText("Your OTP is: " + str(otp))
    msg['From'] = from_email  
    msg['To'] = to_email
    msg['Subject'] = "Your Ibanking OTP"

    # Send the message
    s.send_message(msg)
    s.quit()

    return {"message": "OTP sent successfully", "otp": str(otp)}, 200