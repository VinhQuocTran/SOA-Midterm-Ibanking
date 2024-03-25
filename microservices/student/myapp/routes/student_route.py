from flask import Blueprint, request
from flask.json import jsonify
import json
import requests
from myapp.controllers.student_controller import StudentController

# from microservices.student.myapp.models.student import Product

student_blueprint = Blueprint('student', __name__)
student_controller = StudentController()

@student_blueprint.route('/get_tuition_fees_in_semester/<int:semester_id>', methods=['GET'])
def get_tuition_fees_in_semester(semester_id):
    try:
        tuition_fees = student_controller.get_tuition_fees_in_semester(semester_id)
        

        # if not tuition_fees:
        #     return jsonify({'error': 'Semester not found'}), 404

        data = json.dumps(tuition_fees)
        # print(data)
        # headers = {'Content-Type': 'application/json'}
        # url = "http://localhost:8001/receive_tuition_fees"
        # response = requests.post(url, data=data, headers=headers)

        # if response.status_code != 200:
        #     return jsonify({'error': f"Failed to send data. Response code: {response.status_code}"}), 500

        return data
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

