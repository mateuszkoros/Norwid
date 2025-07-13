from dotenv import load_dotenv
import os
import sys
import datetime
from dateutil import relativedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

required_variables = ['HEARTBEAT_FILE', 
                        'THRESHOLD', 
                        'MAIL_HTML_FILE', 
                        'MAIL_TXT_FILE',
                        'SMTP_SERVER', 
                        'SMTP_PORT', 
                        'SMTP_LOGIN', 
                        'SMTP_PASSWORD', 
                        'MAIL_SUBJECT',
                        'ATTACHMENT',
                        'ERROR_RECIPIENT',
                        'RECIPIENT']
load_dotenv()


def check_requirements():
    # check if all required variables are set
    for var in required_variables:
        if var not in os.environ:
            error = f'Variable {var} is missing!'
            report_error(error)
            exit(1)
    
    # check if mail files exist
    if not Path(os.getenv('MAIL_HTML_FILE')).is_file() or not Path(os.getenv('MAIL_TXT_FILE')).is_file():
        error = 'Email body file not found!'
        report_error(error)
        exit(1)

    # check if attachment exists
    if not Path(os.getenv('ATTACHMENT')).is_file():
        error = 'Attachment file not found!'
        report_error(error)
        exit(1)


def check_heartbeat():
    heartbeat_time = datetime.datetime.fromtimestamp(os.path.getmtime(os.getenv('HEARTBEAT_FILE')))
    current_time = datetime.datetime.now()
    time_difference = relativedelta.relativedelta(current_time, heartbeat_time)
    time_difference_in_months =  time_difference.years * 12 + time_difference.months
    if time_difference_in_months > int(os.getenv('THRESHOLD')):
        notify()


def notify():
    print('Threshold exceeded')
    message = MIMEMultipart('alternative')
    message['Subject'] = os.getenv('MAIL_SUBJECT')
    message['From'] = os.getenv('SMTP_LOGIN')
    message['To'] = os.getenv('RECIPIENT')

    # read email content
    with open(os.getenv('MAIL_HTML_FILE'), 'r', encoding='utf-8') as file:
        html = file.read()
    with open(os.getenv('MAIL_TXT_FILE'), 'r', encoding='utf-8') as file:
        body = file.read()
    message.attach(MIMEText(html, 'html'))
    message.attach(MIMEText(body, 'plain'))
    
    # add attachment
    with open(os.getenv('ATTACHMENT'), "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {os.getenv('ATTACHMENT')}",
    )
    message.attach(part)
    
    send_email(message)
    

def report_error(error):
    print(error, file=sys.stderr)
    subject = "Error while running Norwid script"
    body = error
    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['From'] = os.getenv('SMTP_LOGIN')
    message['To'] = os.getenv('ERROR_RECIPIENT')
    message.attach(MIMEText(body, 'plain'))
    # send email to yourself
    send_email(message)

def send_email(message):
    with smtplib.SMTP(os.getenv('SMTP_SERVER'), os.getenv('SMTP_PORT')) as server:
        server.starttls()
        server.login(os.getenv('SMTP_LOGIN'), os.getenv('SMTP_PASSWORD'))
        server.sendmail(os.getenv('SMTP_LOGIN'), message['To'], message.as_string())
    print('Message sent')


if __name__ == '__main__':
    check_requirements()
    check_heartbeat()