from flask import jsonify, request,Blueprint,render_template
from sqlalchemy import func, select,text,exists,or_
from myapp.models.student import *
from flasgger import swag_from
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from sqlalchemy.orm import aliased,joinedload
from datetime import datetime
from dateutil.parser import parse



student_blueprint = Blueprint('student', __name__)

@student_blueprint.route('/api/tuition_fees/upsert', methods=['POST'])
def upsert_tuition_fee():
    query = """
        SELECT 
            s.id AS student_id, 
            sem.id AS semester_id, 
            sem.name AS semester_name,
            tf.start_date,
            tf.end_date,
            SUM(cis.fee) AS total_fee
        FROM 
            student s
        JOIN 
            student_course sc ON s.id = sc.student_id
        JOIN 
            course_in_semester cis ON sc.course_in_semester_id = cis.id
        JOIN 
            semester sem ON cis.semester_id = sem.id
        JOIN 
            tuition_fee_semester_installment tf ON sem.id = tf.semester_id
        WHERE 
            sem.id = :semester_id AND
            tf.start_date = (SELECT MAX(start_date) FROM tuition_fee_semester_installment WHERE semester_id = :semester_id)
        GROUP BY 
            s.id, 
            sem.id;
    """

    semester_id = request.args.get('semester_id')
    username = request.args.get('username')
    password = request.args.get('password')

    if username != 'admin' or password != 'admin':
        return jsonify({'error': 'Unauthorized'}), 401
    
    if not semester_id:
        return jsonify(msg='Please enter semester ID'), 404
    
    semester_exists = db.session.query(exists().where(Semester.id == semester_id)).scalar()
    if not semester_exists:
        return jsonify({"error": "Semester not found"}), 404
    
    result_proxy = db.session.execute(text(query), {'semester_id': semester_id})
    column_names = result_proxy.keys()
    rows = result_proxy.fetchall()
    tuition_fees = [dict(zip(column_names, row)) for row in rows]

    values = ', '.join([
        f"({int(record['student_id'])}, {int(record['semester_id'])},{record['total_fee']}, '{record['start_date']}', '{record['end_date']}', '{datetime.utcnow()}', '{datetime.utcnow()}')"
        for record in tuition_fees
    ])

    sql = text(f"""
        INSERT INTO tuition_fee (student_id, semester_id, total_fee, start_date, end_date, created_time, update_time)
        VALUES {values}
        ON CONFLICT (student_id, semester_id)
        DO UPDATE SET total_fee = EXCLUDED.total_fee, start_date = EXCLUDED.start_date, end_date = EXCLUDED.end_date, update_time = EXCLUDED.update_time
    """)

    db.session.execute(sql)
    db.session.commit()

    return jsonify(msg='Tuition fee updated'), 200

@student_blueprint.route('/api/tuition_fees', defaults={'student_id': None}, methods=['GET'])
@student_blueprint.route('/api/tuition_fees/<int:student_id>', methods=['GET'])
@jwt_required()
def get_tuition_fees(student_id):
    username=get_jwt_identity()
    earliest_unpaid = request.args.get('earliest_unpaid', default='false').lower() == 'true'
    all_paid = request.args.get('all_paid', default='false').lower() == 'true'

    query = db.session.query(TuitionFee).filter(TuitionFee.student_id == student_id)

    response_data = {}
    status_code = 200

    if (earliest_unpaid==True and all_paid==False and student_id!=None):
        current_time = datetime.now()
            # Filter for unpaid fees, specific student, and end_date before current time
        unpaid_fees = TuitionFee.query.filter(
            TuitionFee.paid_time.is_(None),
            TuitionFee.student_id == student_id,
            TuitionFee.end_date > current_time
        )
        earliest_fee = unpaid_fees.order_by(TuitionFee.start_date.asc()).first()
        if earliest_fee:
            semester = Semester.query.filter_by(id=earliest_fee.semester_id).first()
            response_data = {
                'student_id': earliest_fee.student_id,
                'semester_id': earliest_fee.semester_id,
                'semester_name': semester.name,
                'total_fee': earliest_fee.total_fee,
                'created_time': earliest_fee.created_time,
                'update_time': earliest_fee.update_time,
                'start_date': earliest_fee.start_date,
                'end_date': earliest_fee.end_date,
                'payer_id': earliest_fee.payer_id,
                'paid_time': earliest_fee.paid_time
            }
        else:
            response_data = {"error": "No unpaid tuition fee found"}
            status_code = 404
    elif (all_paid==True and earliest_unpaid==False and student_id==None):
        query = (db.session.query(TuitionFee)
                .options(joinedload(TuitionFee.semester))  # Load the related Semester
                .filter(TuitionFee.payer_id == username))
        tuition_fees = query.all()
        print(tuition_fees)
        response_data = [{
            'student_id': fee.student_id,
            'semester_id': fee.semester_id,
            'semester_name': fee.semester.name,
            'total_fee': fee.total_fee,
            'created_time': fee.created_time,
            'update_time': fee.update_time,
            'start_date': fee.start_date,
            'end_date': fee.end_date,
            'payer_id': fee.payer_id,
            'paid_time': fee.paid_time
        } for fee in tuition_fees]
    else:
        response_data = {"error": "Please specify either earliest_unpaid or all_paid"}
        status_code = 400

    return jsonify(response_data), status_code

    
@student_blueprint.route('/api/tuition_fees/<int:student_id>/<int:semester_id>', methods=['POST'])
@jwt_required()
def update_tuition_fee(student_id, semester_id):
    data = request.get_json()

    fee = db.session.query(TuitionFee).filter(TuitionFee.student_id == student_id, TuitionFee.semester_id == semester_id).first()

    if not fee:
        return jsonify({"error": "Tuition fee not found"}), 404

    fee.payer_id = data.get('payer_id', fee.payer_id)
    fee.paid_time = parse(data.get('paid_time'))

    db.session.commit()

    return jsonify({
        'student_id': fee.student_id,
        'semester_id': fee.semester_id,
        'total_fee': fee.total_fee,
        'created_time': fee.created_time,
        'update_time': fee.update_time,
        'start_date': fee.start_date,
        'end_date': fee.end_date,
        'payer_id': fee.payer_id,
        'paid_time': fee.paid_time
    }), 200
    

@student_blueprint.route('/api/students/<int:student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    student = Student.query.get(student_id)
    if student is None:
        return jsonify({'error': 'Student not found'}), 404
    return jsonify({
        'id': student.id,
        'name': student.name
    }), 200



        
