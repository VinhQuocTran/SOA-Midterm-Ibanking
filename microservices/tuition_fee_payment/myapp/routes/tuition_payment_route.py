from flask import Blueprint, request,jsonify
from myapp.controllers.tuition_payment_controller import TuitionPaymentController
import requests
# from microservices.student.myapp.models.student import Product

tuition_payment_blueprint = Blueprint('TuitionPayment', __name__)
tuition_payment_controller = TuitionPaymentController()


# Note: This function is incompleted
@tuition_payment_blueprint.route('/update_tuition_fee_in_semester/<int:semester_id>', methods=['POST'])
def update_tuition_fee_in_semester(semester_id):
    print(semester_id)
    data = tuition_payment_controller.update_tuition_fees_in_semester(semester_id)
    return data

    