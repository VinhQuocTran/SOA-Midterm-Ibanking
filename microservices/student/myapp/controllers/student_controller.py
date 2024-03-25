from flask import jsonify
from sqlalchemy import func, select,text
from myapp.models.student import db, Student, Semester, StudentCourse, CourseInSemester


class StudentController:
    def get_tuition_fees_in_semester(self, semester_id):
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

        result_proxy = db.session.execute(text(query), {'semester_id': semester_id})
        column_names = result_proxy.keys()
        rows = result_proxy.fetchall()
        students_info = [dict(zip(column_names, row)) for row in rows]


        return students_info
    

    # Note
    # def checkIfLogin():
    #     true or false


    # def token_required(f):
    # @wraps(f)
    # def decorated(args, **kwargs):
    #     token = request.headers.get('Authorization')
    #     if not token:
    #         return jsonify({'message': 'Token is missing'}), 401

    #     user = get_user_from_token(token)
    #     if not user:
    #         return jsonify({'message': 'Token is invalid'}), 401

    #     g.user = user
    #     return f(args, **kwargs)

    # return decorated



        

        
