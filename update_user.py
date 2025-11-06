#!/usr/bin/env python3
"""
Script to update user account with phone number and email
"""
from app import app
from models import User, db

# User information
phone_number = "+18077098707"  # Formatted with country code (807-709-8707)
email = "fogulewe@lakeheadu.ca"
username = "fortune"  # You can change this if you prefer a different username

with app.app_context():
    # Check if user exists
    user = User.query.filter_by(username=username).first()
    
    if not user:
        # Create new user
        user = User(
            username=username,
            email=email,
            phone_number=phone_number,
            role='student'  # Change to 'admin' or 'professor' if needed
        )
        db.session.add(user)
        print(f"✅ Created new user: {username}")
    else:
        # Update existing user
        user.email = email
        user.phone_number = phone_number
        print(f"✅ Updated user: {username}")
    
    db.session.commit()
    
    print(f"\nUser Details:")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Phone: {user.phone_number}")
    print(f"  Role: {user.role}")
    print(f"\n🎉 You can now use this account to log in!")
    print(f"\nTo get SMS codes:")
    print(f"  1. Go to http://localhost:5001")
    print(f"  2. Enter username: {username}")
    print(f"  3. Enter phone number: {phone_number}")
    print(f"  4. Click 'Send Code'")
    print(f"  5. Check the terminal for the SMS code")

