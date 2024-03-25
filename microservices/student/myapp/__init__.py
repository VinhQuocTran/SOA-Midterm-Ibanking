
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Custom module
from .models.student import db
from .routes.student_route import student_blueprint

def create_app():
    app = Flask(__name__)
    
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    db_path = os.path.join(db_dir, 'student.db')
    db_uri = 'sqlite:///{}'.format(db_path)

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
    app.register_blueprint(student_blueprint)
    return app


# print(db_uri)