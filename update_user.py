#!/usr/bin/env python3
"""
Script to update user account with email
"""
from app import app
from models import User, db

# User information
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
            role='student'  # Change to 'admin' or 'professor' if needed
        )
        db.session.add(user)
        print(f"✓ Created new user: {username}")
    else:
        # Update existing user
        user.email = email
        print(f"✓ Updated user: {username}")
    
    db.session.commit()
    
    print(f"\nUser Details:")
    print(f"  Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Role: {user.role}")
    print(f"\n✓ You can now use this account to log in!")
    print(f"\nTo get email verification codes:")
    print(f"  1. Go to http://localhost:5001")
    print(f"  2. Enter username: {username}")
    print(f"  3. Enter email: {email}")
    print(f"  4. Click 'Send Code'")
    print(f"  5. Check your email or terminal for the verification code")

