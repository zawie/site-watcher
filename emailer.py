import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os 
from dotenv import load_dotenv

load_dotenv()

#Constants
SENDER_LOGIN = 'adzawie.bot@gmail.com'
SENDER_ALIAS = '🤖 Zawie Bot'
PASSWORD = os.getenv('EMAIL_PASSWORD')
SMPT_SERVER = 'smtp.gmail.com'

def sendMessage(receivers, subject, body):

    with smtplib.SMTP_SSL(SMPT_SERVER, 465) as smtp_server:
        smtp_server.login(SENDER_LOGIN, PASSWORD) #login with mail_id and password

        message = MIMEMultipart()
        message['From'] = SENDER_ALIAS
        message['To'] = ','.join(receivers)
        message['Subject'] = subject  
        message.attach(MIMEText(body, 'plain'))
        text = message.as_string()
        
        smtp_server.sendmail(SENDER_LOGIN, receivers, text)

if __name__ == '__main__':
    test_reciever = 'adzawie@gmail.com'
    print(f"Sending test email to {test_reciever}")
    sendMessage([test_reciever], 'Test Message', 'This is a test message! 🚀🚀🚀')