# accounts/utils.py
import random
from django.core.mail import send_mail
from django.conf import settings

def send_email_otp(email):
    # Generate a random 6-digit code
    otp = str(random.randint(100000, 999999))
    
    # Send the email
    subject = 'Verify your new email address'
    message = f'Your verification code is: {otp}. It will expire in 10 minutes.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    
    send_mail(subject, message, email_from, recipient_list)
    return otp
