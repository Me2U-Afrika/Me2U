# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
from Me2U.settings import SENDGRID_API_KEY
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# message = Mail(
#     from_email='me2uafrika@gmail.com',
#     to_emails='danielmakori0@gmail.com',
#     subject='Sending with Twilio SendGrid is Fun',
#     html_content='<strong>and easy to do anywhere, even with Python</strong>')
# try:
#     sg = SendGridAPIClient(SENDGRID_API_KEY)
#     response = sg.send(message)
#     print(response.status_code)
#     print(response.body)
#     print(response.headers)
# except Exception as e:
#     print(str(e))

from django.core.mail import send_mail

send_mail("Your Subject", "This is a simple text email body.",
          "me2uafrika@gmail.com", ["danielmakori0@gmail.com"])
