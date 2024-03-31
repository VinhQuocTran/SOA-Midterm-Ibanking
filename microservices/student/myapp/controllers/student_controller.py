from flask import jsonify, request,Blueprint,render_template
from sqlalchemy import func, select,text,exists
from myapp.models.student import *
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from sqlalchemy.orm import aliased


student_blueprint = Blueprint('student', __name__)


@student_blueprint.route('/api/login', methods=['POST'])
def login():
    data = request.json
    student_id = data.get('studentId')
    password = data.get('password')

    user = Student.query.filter_by(id=student_id).first()

    if user and user.password == password:
        access_token = create_access_token(identity=student_id)
        return jsonify(access_token=access_token,student_id=user.id), 200
    else:
        return jsonify({"msg": "Invalid username or password"}), 401


@student_blueprint.route('/api/users/myself', methods=['GET'])
@jwt_required()
def get_logged_in_user():
    student_id = get_jwt_identity()
    user = Student.query.filter_by(id=student_id).first()

    if user:
        return jsonify(username=user.name,balance=user.balance), 200
    else:
        return jsonify(msg='User not found'), 404
    

@student_blueprint.route('/api/users/myself', methods=['POST'])
@jwt_required()
def update_logged_in_user_balance():
    student_id = get_jwt_identity()
    user = Student.query.filter_by(id=student_id).first()

    data = request.json
    new_balance = data.get('balance')
    if new_balance is not None:
        user.balance = new_balance
        db.session.commit()
        return jsonify(msg='User balance updated'), 200
    else:
        return jsonify(msg='No balance provided'), 400
    
    
@student_blueprint.route('/api/users/<int:student_id>', methods=['GET'])
@jwt_required()
def get_user(student_id):
    user = Student.query.filter_by(id=student_id).first() 

    if user:
        return jsonify(username=user.name), 200
    else:
        return jsonify(msg='User not found'), 404


@student_blueprint.route('/api/get_tuition_fee', methods=['GET'])
def get_tutition_fee():
    query = """
        SELECT 
            s.id AS student_id, 
            sem.id AS semester_id, 
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
    if not semester_id:
        return jsonify(msg='Please enter semester ID'), 404
    
    semester_exists = db.session.query(exists().where(Semester.id == semester_id)).scalar()
    if not semester_exists:
        return jsonify({"error": "Semester not found"}), 404

    result_proxy = db.session.execute(text(query), {'semester_id': semester_id})
    column_names = result_proxy.keys()
    rows = result_proxy.fetchall()
    students_info = [dict(zip(column_names, row)) for row in rows]
    return jsonify(students_info), 200

        

        
