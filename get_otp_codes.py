# Shebang line: Tells the system to use Python 3 interpreter when script is executed directly
#!/usr/bin/env python3

# Python docstring: Multi-line string documenting what this script does
"""
Helper script to display OTP codes for demo users
Run this script to get the current OTP codes for testing
"""

# Python import statement: Imports pyotp module for TOTP (Time-based One-Time Password) generation
# pyotp is used to generate and verify OTP codes from user secrets
import pyotp

# Python import statement: Imports the Flask app instance from app.py
# Needed to access Flask application context for database operations
from app import app

# Python import statement: Imports User model and db instance from models.py
# User model represents user accounts in the database
# db is the SQLAlchemy database instance
from models import User, db

# Python context manager: Creates Flask application context
# Required to access database and models outside of Flask request handlers
with app.app_context():
    # Python print statement: Outputs blank line for spacing
    # String concatenation: Creates separator line with 50 equal signs
    print("\n" + "="*50)
    # Python print statement: Outputs script header/title
    print(" CAMPUSKEY - OTP Codes for Demo Users")
    # Python print statement: Outputs closing separator line
    # String concatenation: Adds newline after separator
    print("="*50 + "\n")
    
    # Database query: Retrieves all users from the database
    # User.query.all() returns a list of all User objects in the database
    users = User.query.all()
    
    # Python conditional: Checks if users list is empty (no users found)
    if not users:
        # Python print statement: Outputs message when no users exist
        # Instructs user to run the app first to create sample users
        print("No users found. Please run the app first to create sample users.")
    else:
        # Python else clause: Executes if users exist
        # Python for loop: Iterates through each user in the users list
        for user in users:
            # Python object creation: Creates TOTP object from user's secret key
            # pyotp.TOTP() generates time-based OTP codes using the user's secret
            # user.otp_secret is the unique secret key stored in the database
            totp = pyotp.TOTP(user.otp_secret)
            # Python method call: Generates current OTP code for this moment in time
            # .now() returns the 6-digit code valid for the current 30-second window
            current_code = totp.now()
            # Python print statement: Displays user information in formatted table
            # f-string with formatting: {user.username:15} pads username to 15 characters
            # {user.role:10} pads role to 10 characters for alignment
            # {current_code} displays the current OTP code
            print(f"Username: {user.username:15} | Role: {user.role:10} | OTP: {current_code}")
            # Python print statement: Displays user's email address
            print(f"Email:    {user.email}")
            # Python print statement: Displays the OTP secret key
            # This secret is used to generate QR codes for authenticator apps
            print(f"Secret:   {user.otp_secret}")
            # Python print statement: Outputs separator line between users
            # String multiplication: Creates line of 50 dashes
            print("-" * 50)
    
    # Python print statement: Outputs blank line for spacing
    # Outputs helpful tip about OTP code refresh interval
    print("\n💡 Tip: OTP codes refresh every 30 seconds")
    # Python print statement: Outputs instruction on where to use the codes
    # Provides URL where users can log in with these codes
    print("   Use these codes to log in at http://localhost:5001\n")
