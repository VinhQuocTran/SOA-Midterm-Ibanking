# Standard library imports
import os
import random
import smtplib
from datetime import datetime
from dateutil.parser import parse
from email.mime.text import MIMEText

# Third party imports
import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt
from sqlalchemy import and_, desc, null, or_, text
from sqlalchemy.exc import SQLAlchemyError

# Local application imports
from myapp import db
from myapp.models.ibanking_models import *

ibanking_blueprint = Blueprint('IbankingPayment', __name__)

@ibanking_blueprint.route('/api/login', methods=['POST'])
def login():
    data=request.get_json()
    username=data.get('username')
    password=data.get('password')
    user = IBankingAccount.query.filter_by(username=username, password=password).first()
    if user is None:
        return jsonify({'error': 'Invalid username or password'}), 401
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token,username=user.username), 200


@ibanking_blueprint.route('/api/accounts/myself', methods=['GET'])
@jwt_required()
def get_myself():
    username = get_jwt_identity()
    user = IBankingAccount.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'username': user.username, 'balance': user.balance, 'email': user.email, 'phone': user.phone}), 200


@ibanking_blueprint.route('/api/accounts/myself', methods=['POST'])
@jwt_required()
def update_myself():
    username = get_jwt_identity()
    user = IBankingAccount.query.filter_by(username=username).first()
    if user is None:
        return jsonify({'error': 'User not found'}), 404
    data = request.get_json()
    user.balance = data.get('balance', user.balance)
    db.session.commit()


@ibanking_blueprint.route('/api/tuition_fee_transaction', methods=['POST'])
@jwt_required()
def pay_tuition_fee():
    username = get_jwt_identity()
    user = IBankingAccount.query.filter_by(username=username).first()
    data = request.get_json()
    student_id = data.get('student_id')

    # Get the latest tuition fee
    url = f"http://localhost:8000/api/tuition_fees/{student_id}?earliest_unpaid=true"
    auth_header = request.headers.get('Authorization', None)
    headers = {'Authorization': auth_header}
    response = requests.get(url,headers=headers)
    latest_tuition_fee=response.json()

    if latest_tuition_fee is None:
        return jsonify({'error': 'No tuition fee found for this student'}), 404
    
    # Get the payer's balance
    balance = user.balance
    if balance < latest_tuition_fee['total_fee']:
        return jsonify({'error': 'Insufficient balance'}), 400

    try:
        # Update the payer's balance
        user.balance = balance - latest_tuition_fee['total_fee']

        # Update status of tuition fee
        url = "http://localhost:8000/api/tuition_fees/<student_id>/<semester_id>"
        url = url.replace("<student_id>", str(latest_tuition_fee['student_id'])).replace("<semester_id>", str(latest_tuition_fee['semester_id']))
        data = {
            'payer_id': username,  # The payer is the current user
            'paid_time': datetime.utcnow().isoformat()
        }

        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to update tuition fee'}), 500
        
        # Add the invoice and transaction
        invoice = Invoice(created_time=datetime.utcnow(), invoice_type='tuition_fee', ibanking_account_username=username)
        db.session.add(invoice)
        db.session.flush()  # Flush the session to get the id of the invoice
        transaction = TuitionFeeTransaction(student_id=latest_tuition_fee['student_id'], semester_id=latest_tuition_fee['semester_id'], total_paid=latest_tuition_fee['total_fee'], created_time=datetime.utcnow(), invoice_id=invoice.id)
        db.session.add(transaction)
        db.session.commit() 

        # Craft the success message
        paid_time = datetime.utcnow()
        formatted_paid_time = paid_time.strftime("%Y-%m-%d %H:%M:%S")  # Format the time up to only second
        msg = f"Payment Successful!\n\nInvoice: {invoice.id}\nStudent ID: {student_id}\nSemester ID: {latest_tuition_fee['semester_id']}\nTotal Fee: {latest_tuition_fee['total_fee']}\nPaid Time: {formatted_paid_time}"
        temp_email='vinhquoc2103@gmail.com'
        send_success_email(temp_email, msg)


        return jsonify({'msg': 'Tuition fee paid, check your email to see invoice'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
   
        

@ibanking_blueprint.route('/api/send_otp', methods=['POST']) 
@jwt_required()
def otp_6_digit():
    """
    API endpoint to send a 6-digit OTP to a specified email.

    Input:
    - Requires a valid JWT token in the Authorization header.
    - Requires a JSON object in the request body with 'from_email', 'from_email_app_password', and 'to_email' fields.

    Output:
    - If successful, returns a JSON object with a success message and the OTP.
    - If unsuccessful, an error will be raised.

    Description:
    Sends a 6-digit OTP to a specified email.
    """

    # Get data from request
    data = request.get_json()
    from_email = os.getenv('SERVER_SIDE_EMAIL')
    from_email_app_password = os.getenv('SERVER_SIDE_EMAI_APP_PASSWORD')
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


    
    
@ibanking_blueprint.route('/api/send_success_email', methods=['POST']) 
@jwt_required()
def send_success_email(to_email,msg):
    from_email = os.getenv('SERVER_SIDE_EMAIL')
    from_email_app_password = os.getenv('SERVER_SIDE_EMAI_APP_PASSWORD')
    data = request.get_json()

     # Set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(from_email, from_email_app_password)

    # Create the message
    date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    msg = MIMEText(msg)
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = "Ibanking: Payment Successful"

    # Send the message
    s.send_message(msg)
    s.quit()

    return {"message": "send success email successfully"}, 200
