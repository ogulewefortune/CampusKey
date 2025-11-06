#!/usr/bin/env python3
"""
Helper script to display OTP codes for demo users
Run this script to get the current OTP codes for testing
"""
import pyotp
from app import app
from models import User, db

with app.app_context():
    print("\n" + "="*50)
    print(" CAMPUSKEY - OTP Codes for Demo Users")
    print("="*50 + "\n")
    
    users = User.query.all()
    
    if not users:
        print("No users found. Please run the app first to create sample users.")
    else:
        for user in users:
            totp = pyotp.TOTP(user.otp_secret)
            current_code = totp.now()
            print(f"Username: {user.username:15} | Role: {user.role:10} | OTP: {current_code}")
            print(f"Email:    {user.email}")
            print(f"Secret:   {user.otp_secret}")
            print("-" * 50)
    
    print("\n💡 Tip: OTP codes refresh every 30 seconds")
    print("   Use these codes to log in at http://localhost:5001\n")

