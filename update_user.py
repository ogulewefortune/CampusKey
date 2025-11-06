# Shebang line: Tells the system to use Python 3 interpreter when script is executed directly
#!/usr/bin/env python3

# Python docstring: Multi-line string documenting what this script does
"""
Script to update user account with email
"""

# Python import statement: Imports the Flask app instance from app.py
# Needed to access Flask application context for database operations
from app import app

# Python import statement: Imports User model and db instance from models.py
# User is the database model representing a user account
# db is the SQLAlchemy database instance for database operations
from models import User, db

# Python comment: Marks the user information configuration section
# User information
# Python variable: Stores the email address for the user account
# This email will be used for sending verification codes
email = "fogulewe@lakeheadu.ca"

# Python variable: Stores the username for the user account
# Inline comment explains this can be changed to a different username if preferred
username = "fortune"  # You can change this if you prefer a different username

# Python context manager: Creates Flask application context
# Required to access database and models outside of Flask request handlers
with app.app_context():
    # Python comment: Marks the user existence check section
    # Check if user exists
    # Database query: Searches for user with matching username in database
    # .filter_by() filters records, .first() returns first match or None
    user = User.query.filter_by(username=username).first()
    
    # Python conditional: Checks if user was not found (None means user doesn't exist)
    if not user:
        # Python comment: Marks the user creation section
        # Create new user
        # Python object creation: Creates new User instance with provided data
        # User() constructor creates a new user object (not yet saved to database)
        user = User(
            username=username,  # Sets the username field
            email=email,         # Sets the email field
            role='student'      # Sets the role field (can be 'admin' or 'professor')
        )
        # Database operation: Adds new user object to database session
        # db.session.add() stages the object for insertion (not yet committed)
        db.session.add(user)
        # Python print statement: Outputs success message with checkmark emoji
        # f-string formatting inserts username variable into the message
        print(f"✓ Created new user: {username}")
    else:
        # Python else clause: Executes if user already exists
        # Python comment: Marks the user update section
        # Update existing user
        # Python attribute assignment: Updates email field of existing user object
        # Changes are tracked by SQLAlchemy and will be saved on commit
        user.email = email
        # Python print statement: Outputs update confirmation message
        print(f"✓ Updated user: {username}")
    
    # Database operation: Commits all pending changes to database
    # db.session.commit() saves all staged changes (adds/updates) permanently
    # This is when the database is actually modified
    db.session.commit()
    
    # Python print statement: Outputs blank line for spacing
    print(f"\nUser Details:")
    # Python print statement: Displays username from user object
    # Accesses username attribute from the User model instance
    print(f"  Username: {user.username}")
    # Python print statement: Displays email from user object
    print(f"  Email: {user.email}")
    # Python print statement: Displays role from user object
    print(f"  Role: {user.role}")
    # Python print statement: Outputs success message with checkmark
    print(f"\n✓ You can now use this account to log in!")
    # Python print statement: Outputs instructions header
    print(f"\nTo get email verification codes:")
    # Python print statement: Step 1 - Navigate to application URL
    print(f"  1. Go to http://localhost:5001")
    # Python print statement: Step 2 - Enter username
    print(f"  2. Enter username: {username}")
    # Python print statement: Step 3 - Enter email address
    print(f"  3. Enter email: {email}")
    # Python print statement: Step 4 - Click send code button
    print(f"  4. Click 'Send Code'")
    # Python print statement: Step 5 - Check for verification code
    print(f"  5. Check your email or terminal for the verification code")
