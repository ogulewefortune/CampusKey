import random
import string
from datetime import datetime, timedelta
from flask import current_app
import os

try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False
    print("Twilio not installed. SMS will be printed to console for testing.")


def generate_sms_code():
    """Generate a random 6-digit code"""
    return ''.join(random.choices(string.digits, k=6))


def send_sms_code(phone_number, code):
    """
    Send SMS code to phone number.
    Uses Twilio if configured, otherwise prints to console for testing.
    """
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
    
    message = f"Your CAMPUSKEY verification code is: {code}. Valid for 10 minutes."
    
    # If Twilio is configured, use it
    if TWILIO_AVAILABLE and twilio_account_sid and twilio_auth_token:
        try:
            client = Client(twilio_account_sid, twilio_auth_token)
            client.messages.create(
                body=message,
                from_=twilio_phone_number,
                to=phone_number
            )
            return True
        except Exception as e:
            print(f"Twilio error: {e}")
            # Fall through to console output
    
    # Fallback: Print to console for testing
    print("\n" + "="*50)
    print(f" SMS CODE (Testing Mode)")
    print(f"To: {phone_number}")
    print(f"Code: {code}")
    print(f"Message: {message}")
    print("="*50 + "\n")
    
    return True

