
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Custom module
from .models.tuition_fee import db
from .routes.tuition_payment_route import tuition_payment_blueprint

def create_app():
    app = Flask(__name__)
    
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    db_path = os.path.join(db_dir, 'tuition_payment.db')
    db_uri = 'sqlite:///{}'.format(db_path)

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
    app.register_blueprint(tuition_payment_blueprint)
    return app