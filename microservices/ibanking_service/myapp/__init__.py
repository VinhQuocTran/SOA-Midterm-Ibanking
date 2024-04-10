from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

# Custom module
from .models.ibanking_models import db
from .controllers.ibanking_controllers import ibanking_blueprint

def create_app():
    app = Flask(__name__)

    # Enable CORS
    CORS(app, origins=['http://127.0.0.1:5500','http://127.0.0.1:8000'])
    
    db_dir = os.path.join(os.path.dirname(__file__), 'database')
    db_path = os.path.join(db_dir, 'ibanking.db')
    db_uri = 'sqlite:///{}'.format(db_path)

    if not os.path.exists(db_dir):
        os.makedirs(db_dir)

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # Initialize JWT
    app.config['JWT_SECRET_KEY'] = 'your_secret_key'  # Change this to your secret key
    jwt = JWTManager(app)

    
    with app.app_context():
        db.create_all()
        
    app.register_blueprint(ibanking_blueprint)
    return app