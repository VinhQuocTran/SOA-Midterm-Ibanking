from myapp import db
from flask import jsonify
import requests
from myapp.models.tuition_fee import *


class TuitionPaymentController:
    def update_tuition_fees_in_semester(self,semester_id):
        headers = {'Content-Type': 'application/json'}
        url = "http://localhost:8000/get_tuition_fees_in_semester/{semester_id}".format(semster_id=semester_id)
        response = requests.get(url, headers=headers)
        data = response.json()
        print(data)
        return data
        # if not data:
        #     return jsonify({'error': 'Semester not found'}), 404
        # else:
        #     return jsonify(data), 200