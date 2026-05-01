# restaurants/verify.py
from django.conf import settings
from twilio.rest import Client

client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

def send_verification(phone_number):
    # Sends a 4-6 digit code to the phone number
    verification = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
        .verifications.create(to=phone_number, channel='sms')
    return verification.status

def check_verification(phone_number, code):
    # Checks if the user's entered code matches
    try:
        check = client.verify.v2.services(settings.TWILIO_VERIFY_SERVICE_SID) \
            .verification_checks.create(to=phone_number, code=code)
        return check.status == 'approved'
    except Exception:
        return False
