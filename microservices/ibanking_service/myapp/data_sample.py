from datetime import datetime,timedelta
from sqlalchemy import create_engine,text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models.ibanking_models import *
import os

# Create an engine that connects to the student.db SQLite database
db_dir = os.path.join(os.path.dirname(__file__), 'database')
db_path = os.path.join(db_dir, 'ibanking.db')
db_uri = 'sqlite:///{}'.format(db_path)
engine = create_engine(db_uri)

# # Create a sessionmaker bound to this engine
Session = sessionmaker(bind=engine)

# # Now you can create a new session and use it to interact with the database
session = Session()
print(session)

try:
    # Execute a simple query to check the connection
    result = session.execute(text('SELECT 1'))
    print("Connection to the database is successful!")
except OperationalError as e:
    print("Failed to connect to the database:", e)


# Create a new instance of IBankingAccount
account1 = IBankingAccount(
    username='user1',
    password='password1',
    balance=2000,
    email='user1@example.com',
    phone='1234567890'
)

account2 = IBankingAccount(
    username='user2',
    password='password2',
    balance=1000,
    email='user2@example.com',
    phone='0987654321'
)

# Add the new instances to the session
session.add(account1)
session.add(account2)

# Commit the session to save the changes
session.commit()

print('New accounts have been added to the database!')


print('\n\n\n')