import smtplib
from email.mime.text import MIMEText
import random

def otp_6_digit(from_email, from_email_password,to_email):
    # Set up the SMTP server
    s = smtplib.SMTP(host='smtp.gmail.com', port=587)
    s.starttls()
    s.login(from_email, from_email_password)  # replace with your email and password

    # Create the message
    # Generate a random 6-digit OTP
    otp = random.randint(100000, 999999)
    msg = MIMEText("Your OTP is: " + str(otp))
    msg['From'] = "vinhquoc2103@gmail.com"  # replace with your email
    msg['To'] = to_email
    msg['Subject'] = "Your OTP"

    # Send the message
    s.send_message(msg)
    s.quit()


from_email = "vinhquoc2103@gmail.com"
from_email_password = "6102002vinhaA"
to_email = "vinhquoc2103@gmail.com"
otp_6_digit(from_email, from_email_password, to_email)