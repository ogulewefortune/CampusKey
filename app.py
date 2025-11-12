# ------------------------------------------------------------------------------------
# app.py
#
# Copyright (c) 2025 CampusKey. All rights reserved
# Description:
# This Python code is part of a software application developed for CampusKey
# University Access System. It includes functionality for web application routes,
# authentication, user management, course management, and WebAuthn biometric
# authentication.
#
# Related Documents:
#    Specification Document
#    Design Document
#
# Disclaimer:
# This code is provided as-is, without any warranty or support. Use it at your
# own risk. The author and CampusKey shall not be liable for any damages or
# issues arising from the use of this code.
#
# File created on 11/11/2025
#
# Associated files:
# ------------------
#    models.py - Database models
#    config.py - Configuration settings
#    auth.py - Authentication utilities
#    email_service.py - Email sending functionality
#
# ------------------------------------------------------------------------------------

# Python import statement: Imports Flask class and utility functions from Flask framework
# Flask: Main application class for creating web application
# render_template: Renders HTML templates with Jinja2
# request: Access HTTP request data (form data, JSON, etc.)
# jsonify: Converts Python dictionaries to JSON responses
# session: Server-side session storage for user data
# redirect: Redirects user to different URL
# url_for: Generates URLs for routes by function name
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

# Python import statement: Imports Flask-Login classes and functions for authentication
# LoginManager: Manages user login sessions
# login_user: Logs in a user and creates session
# logout_user: Logs out current user and clears session
# login_required: Decorator to protect routes requiring authentication
# current_user: Proxy object representing logged-in user
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

# Python import statement: Imports pyotp module for TOTP (Time-based One-Time Password) generation
# Used for two-factor authentication with authenticator apps
import pyotp

# Python import statement: Imports os module for accessing environment variables
# Used to read configuration values like PORT, DATABASE_URL, etc.
import os

# Python import statement: Imports datetime and timedelta classes from datetime module
# datetime: Creates timestamps for database records
# timedelta: Calculates time differences (e.g., code expiration times)
from datetime import datetime, timedelta

# Python import statements for WebAuthn and device fingerprinting
import base64
import json
import hashlib
import secrets
from webauthn import generate_registration_options, verify_registration_response, generate_authentication_options, verify_authentication_response
from webauthn.helpers.structs import PublicKeyCredentialDescriptor, AuthenticatorSelectionCriteria, UserVerificationRequirement, AuthenticatorAttachment, RegistrationCredential, AuthenticatorAttestationResponse, AuthenticationCredential, AuthenticatorAssertionResponse, PublicKeyCredentialType, ResidentKeyRequirement, AuthenticatorTransport
from webauthn.helpers.cose import COSEAlgorithmIdentifier


# Python import statement: Imports Config class from config.py module
# Config contains all Flask application configuration settings
from config import Config

# Python import statement: Imports database models and SQLAlchemy instance from models.py
# db: SQLAlchemy database instance for database operations
# User: Database model representing user accounts
# EmailVerificationCode: Database model for storing email verification codes
# Course: Database model representing academic courses
# Grade: Database model representing student grades
# WebAuthnCredential: Database model for WebAuthn biometric credentials
# DeviceFingerprint: Database model for device fingerprinting
from models import db, User, EmailVerificationCode, Course, Grade, WebAuthnCredential, DeviceFingerprint

# Python import statement: Imports email service functions from email_service.py
# generate_verification_code: Creates random 6-digit verification codes
# send_email_code: Sends verification code via email or prints to console
from email_service import generate_verification_code, send_email_code

# Python import statement: Imports authentication utility functions from auth.py
# log_login_attempt: Records login attempts in database for security tracking
# role_required: Decorator to restrict routes to specific user roles
# admin_required: Decorator to restrict routes to admin users only
# verify_user_role: Checks if user has specific role
# get_user_role: Retrieves user's role from database
# normalize_username: Converts username to lowercase for case-insensitive matching
# get_est_time: Gets current time in EST timezone
# get_utc_time: Gets current time in UTC timezone (timezone-agnostic, works for all users)
from auth import log_login_attempt, role_required, admin_required, verify_user_role, get_user_role, normalize_username, get_est_time, get_utc_time


# Python variable: Creates Flask application instance
# Flask(__name__) initializes Flask app, __name__ tells Flask where to find templates/static files
app = Flask(__name__)

# Python method call: Loads configuration from Config class
# app.config.from_object() applies all settings from Config class to Flask app
app.config.from_object(Config)

# WebAuthn configuration - Get origin URL for WebAuthn (required for security)
# In production (Render), use the Render URL, otherwise use localhost
def get_webauthn_origin():
    """Get the origin URL for WebAuthn based on environment"""
    # Check for Render external URL first
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        # Ensure it has https://
        if not render_url.startswith('http'):
            render_url = 'https://' + render_url
        return render_url
    
    # Check for custom WEBAUTHN_ORIGIN
    custom_origin = os.environ.get('WEBAUTHN_ORIGIN')
    if custom_origin:
        return custom_origin
    
    # Fallback: try to get from request (for development)
    try:
        from flask import has_request_context
        if has_request_context() and request:
            scheme = 'https' if request.is_secure or request.headers.get('X-Forwarded-Proto') == 'https' else 'http'
            return f"{scheme}://{request.host}"
    except:
        pass
    
    # Final fallback
    return 'http://localhost:5001'

# WebAuthn Relying Party configuration
# For Render: Extract domain from RENDER_EXTERNAL_URL or set WEBAUTHN_RP_ID env var
def get_rp_id():
    """Get the Relying Party ID for WebAuthn"""
    # Check for custom RP_ID
    custom_rp_id = os.environ.get('WEBAUTHN_RP_ID')
    if custom_rp_id:
        return custom_rp_id
    
    # Try to extract from Render URL
    render_url = os.environ.get('RENDER_EXTERNAL_URL')
    if render_url:
        # Remove protocol and path, keep only domain
        domain = render_url.replace('https://', '').replace('http://', '').split('/')[0]
        return domain
    
    # Fallback to localhost for development
    return 'localhost'

RP_ID = get_rp_id()
RP_NAME = "CAMPUSKEY"


# Python comment: Marks extension initialization section
# Initialize extensions
# Python method call: Initializes SQLAlchemy database with Flask app
# db.init_app() connects the database instance to this Flask application
db.init_app(app)

# Python variable: Creates LoginManager instance for managing user sessions
# LoginManager handles user authentication state and session management
login_manager = LoginManager()

# Python method call: Initializes LoginManager with Flask app
# login_manager.init_app() connects LoginManager to this Flask application
login_manager.init_app(app)

# Python attribute assignment: Sets the login view route name
# login_view tells Flask-Login where to redirect unauthenticated users
# When user tries to access protected route, redirects to 'login' route
login_manager.login_view = 'login'


# Python decorator: Registers function as Flask-Login user loader callback
# @login_manager.user_loader tells Flask-Login how to load user from session
# This function is called whenever Flask-Login needs to get user object from user_id in session
@login_manager.user_loader
# Python function definition: Function to load user object from user ID
# Parameter: user_id (string) - user ID stored in session
def load_user(user_id):
    # Python return statement: Queries database for user and returns User object
    # User.query.get() retrieves user by primary key (id)
    # int(user_id) converts string ID from session to integer for database query
    return User.query.get(int(user_id))


# Python decorator: Registers function as Flask context processor
# @app.context_processor makes variables available to all templates automatically
# This function runs before every template is rendered
@app.context_processor
# Python function definition: Function to inject variables into template context
def inject_user():
    # Python docstring: Documents what the function does
    """Make current_user available to all templates"""
    # Python import statement: Imports current_user from flask_login
    # current_user is the proxy object representing logged-in user (or AnonymousUser if not logged in)
    from flask_login import current_user
    # Python return statement: Returns dictionary that will be available in all templates
    # dict() creates dictionary with 'current_user' key accessible in templates
    return dict(current_user=current_user)


# Python function definition: Function to create sample/demo data for testing
# Creates admin, professor, and student users with sample courses and grades
def create_sample_data():
    # Python docstring: Documents what the function does
    """Create demo users and sample data if none exist"""
    # Python conditional: Checks if any users exist in database
    # User.query.first() returns first user or None if database is empty
    if not User.query.first():
        # Python variable: Creates list of User objects for demo users
        # Each User() creates a new user instance (not yet saved to database)
        users = [
            # Python object creation: Creates admin user with admin role
            User(username='admin', role='admin'),
            # Python object creation: Creates professor user with professor role
            User(username='professor', role='professor'),
            # Python object creation: Creates student user with student role
            User(username='student', role='student'),
        ]
        # Python for loop: Iterates through each user in the users list
        for user in users:
            # Python method call: Adds user object to database session
            # db.session.add() stages the object for insertion (not yet committed)
            db.session.add(user)
        # Python method call: Commits all staged users to database
        # db.session.commit() saves all users permanently to database
        db.session.commit()
        
        # Python comment: Marks sample courses creation section
        # Create sample courses
        # Python variable: Queries database for professor user
        # .filter_by() filters users by username, .first() returns first match or None
        prof = User.query.filter_by(username='professor').first()
        # Python conditional: Checks if professor user exists
        if prof:
            # Python variable: Creates list of Course objects
            # Each Course() creates a course instance linked to professor
            courses = [
                # Python object creation: Creates CS101 course linked to professor
                Course(code='CS101', name='Introduction to Computer Science', professor_id=prof.id),
                # Python object creation: Creates MATH201 course linked to professor
                Course(code='MATH201', name='Calculus I', professor_id=prof.id),
            ]
            # Python for loop: Iterates through each course
            for course in courses:
                # Python method call: Adds course to database session
                db.session.add(course)
            # Python method call: Commits courses to database
            db.session.commit()
            
            # Python comment: Marks sample grades creation section
            # Create sample grades
            # Python variable: Queries database for student user
            student = User.query.filter_by(username='student').first()
            # Python conditional: Checks if student exists
            if student:
                # Python variable: Queries database for CS101 course
                cs101 = Course.query.filter_by(code='CS101').first()
                # Python variable: Queries database for MATH201 course
                math201 = Course.query.filter_by(code='MATH201').first()
                # Python conditional: Checks if both courses exist
                if cs101 and math201:
                    # Python variable: Creates list of Grade objects
                    # Each Grade() links student, course, grade value, percentage, and professor
                    grades = [
                        # Python object creation: Creates A+ grade for CS101 (97.5%)
                        Grade(student_id=student.id, course_id=cs101.id, grade_value='A+', percentage=97.5, professor_id=prof.id),
                        # Python object creation: Creates B grade for MATH201 (85.0%)
                        Grade(student_id=student.id, course_id=math201.id, grade_value='B', percentage=85.0, professor_id=prof.id),
                    ]
                    # Python for loop: Iterates through each grade
                    for grade in grades:
                        # Python method call: Adds grade to database session
                        db.session.add(grade)
                    # Python method call: Commits grades to database
                    db.session.commit()


# Python comment: Marks the routes section
# Routes
# Python decorator: Registers route handler for root URL '/'
# @app.route() tells Flask which URL should trigger this function
@app.route('/')
# Python function definition: Home page route handler
def home():
    # Python return statement: Redirects user to login page
    # redirect() sends HTTP redirect response
    # url_for('login') generates URL for the 'login' route function
    return redirect(url_for('login'))


# Python decorator: Registers route handler for '/login' URL with GET and POST methods
# methods=['GET', 'POST'] allows both displaying login form and processing form submission
@app.route('/login', methods=['GET', 'POST'])
# Python function definition: Login page route handler
def login():
    # Python conditional: Checks if request method is POST (form submission)
    # request.method contains HTTP method ('GET', 'POST', etc.)
    if request.method == 'POST':
        # Python variable: Gets username from form data
        # request.form.get() retrieves form field value, returns None if not found
        username_input = request.form.get('username')
        # Python variable: Gets OTP verification code from form data
        otp_code = request.form.get('otp_code')
        # Python variable: Gets email address from form data
        email = request.form.get('email')
        
        # Normalize username to lowercase for case-insensitive matching
        username = normalize_username(username_input) if username_input else None
        
        # Python variable: Queries database for user with matching username (case-insensitive)
        # .filter_by() filters users, .first() returns first match or None
        user = User.query.filter_by(username=username).first() if username else None
        
        # Python conditional: Checks if user was not found
        if not user:
            # Log failed login attempt - wrong username
            if username:
                log_login_attempt(username, 'email' if email else 'otp', 'failed', user_id=None)
            # Python return statement: Renders login template with error message
            # render_template() renders HTML template with provided variables
            return render_template('login.html', error='User not found')
        
        # Python comment: Marks email verification code checking section
        # Verify email code if email was used
        # Python conditional: Checks if email was provided in form
        if email:
            # Python variable: Queries database for matching verification code
            # EmailVerificationCode.query.filter_by() searches verification codes
            # Conditions: username matches, email matches, code matches, not used yet
            verification = EmailVerificationCode.query.filter_by(
                username=username,  # Matches username
                email=email,         # Matches email address
                code=otp_code,       # Matches verification code
                used=False           # Code has not been used yet
            ).first()
            
            # Python conditional: Checks if verification code exists and is not expired
            # verification exists AND expiration time is in the future (UTC timezone)
            # Get current time in UTC (as naive datetime for comparison with database)
            # UTC is timezone-agnostic and works correctly for users in any timezone
            current_time_utc = get_utc_time()
            # Convert to naive datetime for comparison (SQLite stores naive datetimes)
            current_time_naive = current_time_utc
            
            if verification:
                # expires_at from database is naive datetime stored in UTC (SQLite doesn't store timezone)
                # Compare both as naive datetimes (both should be in UTC)
                if verification.expires_at > current_time_naive:
                    # Python comment: Marks code usage marking section
                    # Mark code as used
                    # Python attribute assignment: Marks verification code as used
                    # Prevents code from being reused for security
                    verification.used = True
                    # Python method call: Saves code usage status to database
                    db.session.commit()
                    
                    # Python function call: Logs in the user and creates session
                    # login_user() creates Flask-Login session for the user
                    login_user(user)
                    # Python function call: Records successful login attempt in database
                    # log_login_attempt() saves login event for security auditing
                    log_login_attempt(username, 'email', 'success', user.id)
                    # Python function call: Track active session for monitoring
                    # track_session_activity() creates/updates active session record
                    from auth import track_session_activity
                    import hashlib
                    # Generate a unique session ID from Flask session
                    session_id = hashlib.sha256(str(session.get('_id', id(session))).encode()).hexdigest()[:32]
                    track_session_activity(user.id, session_id)
                    # Python dictionary assignment: Stores authentication method in session
                    # session['auth_method'] stores how user logged in (email, otp, biometric, etc.)
                    session['auth_method'] = 'email'
                    # Python dictionary assignment: Stores login timestamp in session (UTC timezone)
                    # get_utc_time().isoformat() creates ISO format timestamp string
                    session['login_time'] = get_utc_time().isoformat()
                    # Python dictionary assignment: Stores user role in session
                    # session['user_role'] stores role for quick access without database query
                    session['user_role'] = user.role  # Store role in session
                    # Python function call: Store device fingerprint for security tracking
                    # This tracks the device and IP address being used
                    try:
                        user_agent = request.headers.get('User-Agent', '')
                        ip_address = request.remote_addr
                        device_info = {}  # Will be collected by JavaScript if available
                        fingerprint_hash = create_device_fingerprint(device_info, user_agent, ip_address)
                        store_device_fingerprint(user.id, fingerprint_hash, device_info, user_agent, ip_address)
                    except Exception as e:
                        print(f"Device fingerprint error: {e}")
                    
                    # Python comment: Marks role-based redirect section
                    # Redirect to role-specific dashboard
                    # Python conditional: Checks if user is admin
                    if user.role == 'admin':
                        # Python return statement: Redirects to admin dashboard
                        return redirect(url_for('admin_dashboard'))
                    # Python elif clause: Checks if user is professor
                    elif user.role == 'professor':
                        # Python return statement: Redirects to professor dashboard
                        return redirect(url_for('professor_dashboard'))
                    # Python else clause: Default case (student)
                    else:
                        # Python return statement: Redirects to student dashboard
                        return redirect(url_for('student_dashboard'))
                else:
                    # Expired verification code
                    log_login_attempt(username, 'email', 'failed', user_id=user.id if user else None)
                    return render_template('login.html', error='Invalid or expired verification code')
            else:
                # Invalid verification code
                log_login_attempt(username, 'email', 'failed', user_id=user.id if user else None)
                return render_template('login.html', error='Invalid or expired verification code')
        # Python else clause: Executes if no email was provided (uses TOTP instead)
        else:
            # Python comment: Marks TOTP fallback authentication section
            # Fallback to TOTP if no email
            # Python conditional: Checks if user exists and OTP code is valid
            # user.verify_otp() validates the TOTP code against user's secret
            if user and user.verify_otp(otp_code):
                # Python function call: Logs in the user
                login_user(user)
                # Python function call: Records successful TOTP login
                log_login_attempt(username, 'otp', 'success', user.id)
                # Python function call: Track active session for monitoring
                from auth import track_session_activity
                import hashlib
                session_id = hashlib.sha256(str(id(session)).encode()).hexdigest()[:32]
                track_session_activity(user.id, session_id)
                # Python dictionary assignment: Stores OTP auth method in session
                session['auth_method'] = 'otp'
                # Python dictionary assignment: Stores login timestamp (UTC timezone)
                session['login_time'] = get_utc_time().isoformat()
                # Python dictionary assignment: Stores user role
                session['user_role'] = user.role  # Store role in session
                # Python function call: Store device fingerprint for security tracking
                try:
                    user_agent = request.headers.get('User-Agent', '')
                    ip_address = request.remote_addr
                    device_info = {}
                    fingerprint_hash = create_device_fingerprint(device_info, user_agent, ip_address)
                    store_device_fingerprint(user.id, fingerprint_hash, device_info, user_agent, ip_address)
                except Exception as e:
                    print(f"Device fingerprint error: {e}")
                
                # Python comment: Marks role-based redirect section
                # Redirect to role-specific dashboard
                # Python conditional: Checks if user is admin
                if user.role == 'admin':
                    # Python return statement: Redirects to admin dashboard
                    return redirect(url_for('admin_dashboard'))
                # Python elif clause: Checks if user is professor
                elif user.role == 'professor':
                    # Python return statement: Redirects to professor dashboard
                    return redirect(url_for('professor_dashboard'))
                # Python else clause: Default case (student)
                else:
                    # Python return statement: Redirects to student dashboard
                    return redirect(url_for('student_dashboard'))
            # Python else clause: Executes if TOTP verification failed
            else:
                # Python function call: Records failed TOTP login attempt (wrong OTP code)
                log_login_attempt(username, 'otp', 'failed', user_id=user.id if user else None)
                # Python return statement: Renders login page with error message
                return render_template('login.html', error='Invalid OTP code')
    
    # Python return statement: Renders login page for GET requests (display form)
    # This executes when user visits /login page (not submitting form)
    return render_template('login.html')


# Python decorator: Registers API route for sending email verification codes
# '/api/send-email-code' is the API endpoint URL
# methods=['POST'] restricts route to POST requests only (API endpoint)
@app.route('/api/send-email-code', methods=['POST'])
# Python function definition: API endpoint handler for sending email codes
def send_email_code_route():
    # Python docstring: Documents what the endpoint does
    """API endpoint to send email verification code"""
    # Python variable: Parses JSON data from request body
    # request.get_json() converts JSON request body to Python dictionary
    data = request.get_json()
    # Python variable: Extracts username from JSON data
    # .get() retrieves value from dictionary, returns None if key doesn't exist
    username = data.get('username')
    # Python variable: Extracts email from JSON data
    email = data.get('email')
    
    # Python conditional: Validates that both username and email are provided
    if not username or not email:
        # Python return statement: Returns JSON error response with 400 status code
        # jsonify() converts Python dict to JSON response
        # 400 = Bad Request (missing required parameters)
        return jsonify({'success': False, 'error': 'Username and email are required'}), 400
    
    # Python comment: Marks user existence check section
    # Check if user exists
    # Normalize username to lowercase for case-insensitive matching
    normalized_username = normalize_username(username)
    # Python variable: Queries database for user with matching username
    user = User.query.filter_by(username=normalized_username).first()
    # Python conditional: Checks if user was not found
    if not user:
        # Python return statement: Returns JSON error response with 404 status code
        # 404 = Not Found (user doesn't exist)
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Python comment: Marks email validation removal note
    # Remove email validation - send to any email entered in the form
    # The email will be sent to the email address provided in the form input
    
    # Python comment: Marks verification code generation section
    # Generate verification code
    # Python variable: Generates random 6-digit verification code
    # generate_verification_code() returns string like '123456'
    code = generate_verification_code()
    # Python variable: Calculates code expiration time (10 minutes from now) in UTC
    # get_utc_time() gets current UTC time, timedelta(minutes=10) adds 10 minutes
    # UTC is timezone-agnostic and works correctly for users in any timezone (Saskatoon, Thunder Bay, etc.)
    # Convert to naive datetime for database storage (SQLite doesn't store timezone)
    expires_at = get_utc_time() + timedelta(minutes=10)  # Store as naive datetime in UTC
    
    # Python comment: Marks verification code storage section
    # Save verification code with the email from the form
    # Python object creation: Creates EmailVerificationCode database record
    verification = EmailVerificationCode(
        username=username,      # Links code to username
        email=email,            # Links code to email address (from form input)
        code=code,              # Stores the 6-digit verification code
        expires_at=expires_at    # Sets expiration timestamp
    )
    # Python method call: Adds verification code to database session
    db.session.add(verification)
    # Python method call: Saves verification code to database
    db.session.commit()
    
    # Python comment: Marks email sending section
    # Check if SendGrid is configured first (works on Render free tier)
    email_service = os.environ.get('EMAIL_SERVICE', '').lower()
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    
    # Check if SMTP is configured before attempting to send
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD', '').strip()
    
    # If neither SendGrid nor SMTP is configured, show code in response
    if (email_service != 'sendgrid' or not sendgrid_api_key) and (not smtp_username or not smtp_password):
        # SMTP not configured - show code in response for testing
        # This allows OTP to work even if email fails (code is shown)
        print(f"[WARNING] EMAIL NOT CONFIGURED - Showing code in response:")
        print(f"   EMAIL_SERVICE: {os.environ.get('EMAIL_SERVICE', 'NOT SET')}")
        print(f"   SENDGRID_API_KEY: {'SET' if sendgrid_api_key else 'NOT SET'}")
        print(f"   SMTP_USERNAME: {'SET' if smtp_username else 'NOT SET'}")
        print(f"   SMTP_PASSWORD: {'SET' if smtp_password else 'NOT SET'}")
        print(f"   SMTP_SERVER: {os.environ.get('SMTP_SERVER', 'NOT SET')}")
        print(f"   SMTP_PORT: {os.environ.get('SMTP_PORT', 'NOT SET')}")
        print(f"   FROM_EMAIL: {os.environ.get('FROM_EMAIL', 'NOT SET')}")
        print(f"   Code for {username}: {code}")
        print(f"   TIP: Add EMAIL_SERVICE=sendgrid and SENDGRID_API_KEY to Render to enable emails!")
        # Still return success but include code in message
        return jsonify({
            'success': True,
            'message': f'Email service not configured. Your verification code is: {code}\n\nTo enable email sending, set SMTP_USERNAME and SMTP_PASSWORD in Render environment variables.\n\nCheck Render logs for configuration details.',
            'code': code,  # Include code in response for testing
            'email_configured': False
        })
    
    # Try to send email synchronously first (with timeout)
    # This ensures we can report actual errors to the user
    import signal
    import threading
    
    email_result = {'status': None, 'error': None, 'success': False}
    
    def send_email_with_timeout():
        """Send email with timeout"""
        try:
            result = send_email_code(email, code, username)
            if result:
                print(f"[SUCCESS] Email sent successfully to {email}")
                email_result['status'] = 'success'
                email_result['success'] = True
            else:
                print(f"[WARNING] Email service returned False for {email}")
                email_result['status'] = 'failed'
                email_result['error'] = 'Email service returned False'
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            # Log detailed error for debugging in Render logs
            print(f"[ERROR] ERROR SENDING EMAIL TO {email}:")
            print(f"   Error: {str(e)}")
            print(f"   Full traceback:")
            print(error_details)
            print(f"   SMTP_SERVER: {os.environ.get('SMTP_SERVER', 'NOT SET')}")
            print(f"   SMTP_PORT: {os.environ.get('SMTP_PORT', 'NOT SET')}")
            print(f"   SMTP_USERNAME: {os.environ.get('SMTP_USERNAME', 'NOT SET')}")
            print(f"   SMTP_PASSWORD: {'SET' if os.environ.get('SMTP_PASSWORD') else 'NOT SET'}")
            print(f"   FROM_EMAIL: {os.environ.get('FROM_EMAIL', 'NOT SET')}")
            email_result['status'] = 'failed'
            email_result['error'] = str(e)
    
    # Send email in thread with 15 second timeout
    email_thread = threading.Thread(target=send_email_with_timeout, daemon=True)
    email_thread.start()
    email_thread.join(timeout=15)  # Wait up to 15 seconds
    
    # Check result
    if email_result['status'] is None:
        # Still sending - return success but note it's in progress
        return jsonify({
            'success': True,
            'message': f'Verification code is being sent to {email}. Please check your inbox and spam folder. If not received within a minute, check Render logs.',
            'warning': 'Email sending is taking longer than expected. Check Render logs if not received.'
        })
    elif email_result['success']:
        # Success!
        print(f"[SUCCESS] Email sent successfully to {email}")
        return jsonify({
            'success': True,
            'message': f'Verification code sent successfully to {email}. Please check your inbox and spam folder.',
            'email_configured': True,
            'email_sent': True
        })
    else:
        # Failed - return error with code so user can still login
        error_msg = email_result['error'] or 'Unknown error'
        print(f"[WARNING] Email failed but code is: {code} (for {username})")
        print(f"   Error details: {error_msg}")
        return jsonify({
            'success': False,
            'error': f'Failed to send email: {error_msg}. Your verification code is: {code}',
            'code': code,  # Include code so user can still login
            'message': f'Email sending failed. Your verification code is: {code}. Please use this code to login. Check Render logs for email errors.',
            'email_configured': True,
            'email_sent': False,
            'email_error': error_msg
        })


# WebAuthn and Device Fingerprinting API Routes

# Helper function to create device fingerprint hash
def create_device_fingerprint(device_info, user_agent, ip_address):
    """Create a hash from device characteristics"""
    fingerprint_string = json.dumps({
        'device_info': device_info,
        'user_agent': user_agent,
        'ip': ip_address
    }, sort_keys=True)
    return hashlib.sha256(fingerprint_string.encode()).hexdigest()

# Helper function to safely decode base64 with padding handling
def safe_b64decode(data):
    """Safely decode base64 string, handling padding issues"""
    if not data:
        return b''
    # If already bytes, return as-is (shouldn't happen, but handle it)
    if isinstance(data, bytes):
        return data
    # Ensure it's a string
    if not isinstance(data, str):
        data = str(data)
    # Add padding if needed
    missing_padding = len(data) % 4
    if missing_padding:
        data += '=' * (4 - missing_padding)
    try:
        return base64.b64decode(data)
    except Exception as e:
        # Try URL-safe base64 if standard fails
        try:
            return base64.urlsafe_b64decode(data)
        except:
            raise ValueError(f"Failed to decode base64: {e}")

# Helper function to serialize WebAuthn registration options
def serialize_registration_options(options):
    """Convert PublicKeyCredentialCreationOptions to dictionary"""
    result = {
        'challenge': base64.b64encode(options.challenge).decode(),
        'rp': {
            'id': options.rp.id,
            'name': options.rp.name
        },
        'user': {
            'id': base64.b64encode(options.user.id).decode(),
            'name': options.user.name,
            'displayName': options.user.display_name or options.user.name
        },
        'pubKeyCredParams': [
            {
                'type': param.type,
                'alg': param.alg.value if hasattr(param.alg, 'value') else int(param.alg)
            }
            for param in options.pub_key_cred_params
        ],
        'timeout': options.timeout,
    }
    
    if options.authenticator_selection:
        authenticator_selection_dict = {
            'userVerification': options.authenticator_selection.user_verification.value if options.authenticator_selection.user_verification else None
        }
        # Add authenticatorAttachment if specified
        if options.authenticator_selection.authenticator_attachment:
            authenticator_selection_dict['authenticatorAttachment'] = options.authenticator_selection.authenticator_attachment.value
        # Add residentKey if specified
        if hasattr(options.authenticator_selection, 'resident_key') and options.authenticator_selection.resident_key:
            authenticator_selection_dict['residentKey'] = options.authenticator_selection.resident_key.value
        elif hasattr(options.authenticator_selection, 'require_resident_key'):
            authenticator_selection_dict['requireResidentKey'] = options.authenticator_selection.require_resident_key
        result['authenticatorSelection'] = authenticator_selection_dict
    
    if options.exclude_credentials:
        result['excludeCredentials'] = [
            {
                'id': base64.b64encode(cred.id).decode(),
                'type': cred.type.value if hasattr(cred.type, 'value') else str(cred.type),
                'transports': [t.value for t in cred.transports] if cred.transports else []
            }
            for cred in options.exclude_credentials
        ]
    
    if options.attestation:
        result['attestation'] = options.attestation.value
    
    return result

# Helper function to serialize WebAuthn authentication options
def serialize_authentication_options(options):
    """Convert PublicKeyCredentialRequestOptions to dictionary"""
    result = {
        'challenge': base64.b64encode(options.challenge).decode(),
        'timeout': options.timeout,
        'rpId': options.rp_id,
        'userVerification': options.user_verification.value if options.user_verification else None
    }
    
    if options.allow_credentials:
        result['allowCredentials'] = [
            {
                'id': base64.b64encode(cred.id).decode(),
                'type': cred.type.value if hasattr(cred.type, 'value') else str(cred.type),
                'transports': [t.value for t in cred.transports] if cred.transports else ['internal']  # Default to internal if not set
            }
            for cred in options.allow_credentials
        ]
    else:
        # Empty allowCredentials means discover all credentials - ensure user verification is required
        # But we prefer to list credentials with internal transport to force platform authenticators
        result['allowCredentials'] = []
    
    return result

# Helper function to store or update device fingerprint
def store_device_fingerprint(user_id, fingerprint_hash, device_info, user_agent, ip_address):
    """Store or update device fingerprint"""
    try:
        fingerprint = DeviceFingerprint.query.filter_by(
            user_id=user_id,
            fingerprint_hash=fingerprint_hash
        ).first()
        
        if fingerprint:
            # Update last seen timestamp
            fingerprint.last_seen_at = get_est_time()
            fingerprint.device_info = json.dumps(device_info) if device_info else None
        else:
            # Create new fingerprint
            fingerprint = DeviceFingerprint(
                user_id=user_id,
                fingerprint_hash=fingerprint_hash,
                device_info=json.dumps(device_info) if device_info else None,
                user_agent=user_agent,
                ip_address=ip_address,
                is_trusted=False  # New devices start as untrusted
            )
            db.session.add(fingerprint)
        
        db.session.commit()
        return fingerprint
    except Exception as e:
        print(f"Error storing device fingerprint: {e}")
        db.session.rollback()
        return None


# WebAuthn Registration - Start registration process
@app.route('/api/webauthn/register/begin', methods=['POST'])
@login_required
def webauthn_register_begin():
    """Start WebAuthn registration process"""
    try:
        username = normalize_username(current_user.username)
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get existing credentials for this user
        existing_credentials = WebAuthnCredential.query.filter_by(user_id=user.id).all()
        existing_credential_ids = [safe_b64decode(cred.credential_id) for cred in existing_credentials]
        
        # Generate registration options
        origin = get_webauthn_origin()
        registration_options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=user.username,  # Library expects string, not bytes
            user_name=user.username,
            user_display_name=user.username,
            exclude_credentials=[
                PublicKeyCredentialDescriptor(id=cred_id) for cred_id in existing_credential_ids
            ],
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.PLATFORM,  # Require platform authenticators (Face ID, Touch ID)
                user_verification=UserVerificationRequirement.REQUIRED,
                resident_key=ResidentKeyRequirement.PREFERRED  # Prefer resident keys for better UX
            ),
        )
        
        # Store challenge in session
        session['webauthn_challenge'] = base64.b64encode(registration_options.challenge).decode()
        session['webauthn_user_id'] = user.id
        
        return jsonify({
            'success': True,
            'options': serialize_registration_options(registration_options)
        })
    except Exception as e:
        print(f"WebAuthn registration begin error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# WebAuthn Registration - Complete registration
@app.route('/api/webauthn/register/complete', methods=['POST'])
@login_required
def webauthn_register_complete():
    """Complete WebAuthn registration"""
    try:
        data = request.get_json()
        credential = data.get('credential')
        device_name = data.get('device_name', 'Unknown Device')
        
        if not credential:
            return jsonify({'success': False, 'error': 'Credential data required'}), 400
        
        # Get challenge from session
        challenge = session.get('webauthn_challenge')
        user_id = session.get('webauthn_user_id')
        
        if not challenge or not user_id:
            return jsonify({'success': False, 'error': 'Registration session expired'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Convert dictionary credential to RegistrationCredential object
        # JavaScript sends: {id, rawId (base64), response: {clientDataJSON (base64), attestationObject (base64)}, type}
        credential_obj = RegistrationCredential(
            id=credential.get('id'),
            raw_id=safe_b64decode(credential.get('rawId')),
            response=AuthenticatorAttestationResponse(
                client_data_json=safe_b64decode(credential['response']['clientDataJSON']),
                attestation_object=safe_b64decode(credential['response']['attestationObject'])
            ),
            type=PublicKeyCredentialType.PUBLIC_KEY
        )
        
        # Verify registration response
        origin = get_webauthn_origin()
        verification = verify_registration_response(
            credential=credential_obj,
            expected_challenge=safe_b64decode(challenge),
            expected_origin=origin,
            expected_rp_id=RP_ID,
        )
        
        # Convert credential_public_key to JSON-serializable format
        # The public key may contain bytes that need to be converted to base64 strings
        def convert_bytes_to_base64(obj):
            """Recursively convert bytes to base64 strings for JSON serialization"""
            if isinstance(obj, bytes):
                return base64.b64encode(obj).decode()
            elif isinstance(obj, dict):
                return {k: convert_bytes_to_base64(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_bytes_to_base64(item) for item in obj]
            else:
                return obj
        
        public_key_serializable = convert_bytes_to_base64(verification.credential_public_key)
        
        # Store credential in database
        # Store the base64-encoded credential_id (required for WebAuthn verification)
        credential_record = WebAuthnCredential(
            user_id=user.id,
            credential_id=base64.b64encode(verification.credential_id).decode(),  # Store as base64 string
            public_key=json.dumps(public_key_serializable),
            counter=verification.sign_count,
            device_name=device_name
        )
        
        db.session.add(credential_record)
        db.session.commit()
        
        # Clear session
        session.pop('webauthn_challenge', None)
        session.pop('webauthn_user_id', None)
        
        return jsonify({
            'success': True,
            'message': 'Biometric credential registered successfully'
        })
    except Exception as e:
        print(f"WebAuthn registration complete error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# WebAuthn Authentication - Start authentication
@app.route('/api/webauthn/authenticate/begin', methods=['POST'])
def webauthn_authenticate_begin():
    """Start WebAuthn authentication"""
    try:
        data = request.get_json()
        username_input = data.get('username')
        
        if not username_input:
            return jsonify({'success': False, 'error': 'Username is required'}), 400
        
        username = normalize_username(username_input)
        user = User.query.filter_by(username=username).first()
        
        if not user:
            log_login_attempt(username, 'biometric', 'failed', user_id=None)
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Get user's credentials
        credentials = WebAuthnCredential.query.filter_by(user_id=user.id).all()
        if not credentials:
            return jsonify({
                'success': False, 
                'error': 'No biometric credentials registered for your account. Please log in with username/password and register your biometric in the dashboard first.'
            }), 404
        
        # Prepare credential descriptors with platform transport hint
        # Include all user's credentials with platform transport to force platform authenticator use
        # This ensures the browser uses Face ID/Touch ID instead of showing QR code options
        allow_credentials = []
        for cred in credentials:
            try:
                cred_id_bytes = safe_b64decode(cred.credential_id)
                allow_credentials.append(
                    PublicKeyCredentialDescriptor(
                        id=cred_id_bytes,
                        transports=[AuthenticatorTransport.INTERNAL]  # Force internal/platform authenticator
                    )
                )
            except Exception as e:
                print(f"Error processing credential {cred.id}: {e}")
                continue
        
        # If no credentials found, use empty list (shouldn't happen, but handle it)
        # Empty list with userVerification=required should still prefer platform authenticators
        
        # Generate authentication options
        # Set timeout to force prompt (not auto-confirm)
        # Require explicit user verification (biometric confirmation)
        origin = get_webauthn_origin()
        authentication_options = generate_authentication_options(
            rp_id=RP_ID,
            allow_credentials=allow_credentials if allow_credentials else None,  # None means discover all, but we prefer to list them
            user_verification=UserVerificationRequirement.REQUIRED,  # Require biometric confirmation
            timeout=60000,  # 60 second timeout to ensure prompt appears
        )
        
        # Store challenge and user info in session
        session['webauthn_challenge'] = base64.b64encode(authentication_options.challenge).decode()
        session['webauthn_user_id'] = user.id
        
        return jsonify({
            'success': True,
            'options': serialize_authentication_options(authentication_options)
        })
    except Exception as e:
        print(f"WebAuthn authenticate begin error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


# WebAuthn Authentication - Complete authentication
@app.route('/api/webauthn/authenticate/complete', methods=['POST'])
def webauthn_authenticate_complete():
    """Complete WebAuthn authentication"""
    try:
        data = request.get_json()
        credential = data.get('credential')
        device_info = data.get('device_info', {})
        
        if not credential:
            return jsonify({'success': False, 'error': 'Credential data required'}), 400
        
        # Get challenge and user from session
        challenge = session.get('webauthn_challenge')
        user_id = session.get('webauthn_user_id')
        
        if not challenge or not user_id:
            return jsonify({'success': False, 'error': 'Authentication session expired'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Find the credential using the browser's credential ID
        # The browser sends the credential ID that was registered
        credential_id_b64 = credential.get('id')
        raw_id_data = credential.get('rawId')
        if not raw_id_data:
            return jsonify({'success': False, 'error': 'Missing rawId in credential data'}), 400
        # Ensure raw_id_data is a string before decoding
        credential_raw_id = safe_b64decode(str(raw_id_data))
        
        # Try to find credential by matching the raw credential ID bytes
        # Handle both base64-stored and integer-stored credential IDs
        credential_record = None
        for cred in WebAuthnCredential.query.filter_by(user_id=user.id).all():
            try:
                # Try base64 decode first (new format)
                stored_id_bytes = safe_b64decode(cred.credential_id)
                if stored_id_bytes == credential_raw_id:
                    credential_record = cred
                    break
            except:
                # If that fails, try integer format (old format)
                try:
                    stored_int = int(cred.credential_id)
                    # Convert integer to bytes - the integer was created from first 8 bytes
                    # So we need to check if the first 8 bytes of credential_raw_id match
                    stored_bytes_8 = stored_int.to_bytes(8, byteorder='big', signed=False)
                    if len(credential_raw_id) >= 8:
                        if stored_bytes_8 == credential_raw_id[:8]:
                            credential_record = cred
                            break
                    # Also try matching the full length if it fits
                    if len(credential_raw_id) <= 8:
                        if stored_bytes_8[:len(credential_raw_id)] == credential_raw_id:
                            credential_record = cred
                            break
                except Exception as e:
                    print(f"Error matching integer credential: {e}")
                    pass
        
        if not credential_record:
            # Log for debugging
            print(f"Credential lookup failed for user {user.id}")
            print(f"Browser credential rawId length: {len(credential_raw_id)}")
            print(f"Browser credential rawId (first 20 bytes): {credential_raw_id[:20]}")
            stored_creds = WebAuthnCredential.query.filter_by(user_id=user.id).all()
            for sc in stored_creds:
                print(f"Stored credential_id: {sc.credential_id} (type: {type(sc.credential_id).__name__})")
            log_login_attempt(user.username, 'biometric', 'failed', user.id)
            return jsonify({'success': False, 'error': 'Invalid credential - credential not found for this user'}), 401
        
        # Convert dictionary credential to AuthenticationCredential object
        # JavaScript sends: {id, rawId (base64), response: {clientDataJSON, authenticatorData, signature, userHandle (all base64)}, type}
        # Use already-decoded credential_raw_id instead of decoding again
        response_data = credential.get('response', {})
        if not response_data:
            return jsonify({'success': False, 'error': 'Missing response data in credential'}), 400
        
        # Ensure all response data is properly decoded from base64 to bytes
        client_data_json = response_data.get('clientDataJSON', '')
        authenticator_data = response_data.get('authenticatorData', '')
        signature = response_data.get('signature', '')
        user_handle = response_data.get('userHandle')
        
        # Convert strings to bytes using base64 decode
        client_data_bytes = safe_b64decode(str(client_data_json)) if client_data_json else b''
        authenticator_data_bytes = safe_b64decode(str(authenticator_data)) if authenticator_data else b''
        signature_bytes = safe_b64decode(str(signature)) if signature else b''
        user_handle_bytes = safe_b64decode(str(user_handle)) if user_handle else None
        
        credential_obj = AuthenticationCredential(
            id=credential.get('id'),
            raw_id=credential_raw_id,  # Already decoded above as bytes
            response=AuthenticatorAssertionResponse(
                client_data_json=client_data_bytes,
                authenticator_data=authenticator_data_bytes,
                signature=signature_bytes,
                user_handle=user_handle_bytes
            ),
            type=PublicKeyCredentialType.PUBLIC_KEY
        )
        
        # Verify authentication response
        origin = get_webauthn_origin()
        public_key_dict = json.loads(credential_record.public_key)
        
        # Convert base64 strings back to bytes in the public key
        # The public key was stored with bytes converted to base64 strings
        # COSE key format: values can be int, str (base64), or bytes
        def convert_base64_to_bytes(obj):
            """Recursively convert base64 strings back to bytes"""
            if isinstance(obj, bytes):
                # Already bytes, return as-is
                return obj
            elif isinstance(obj, str):
                # Try to decode as base64 - if it fails, return as-is (might be a regular string)
                try:
                    decoded = safe_b64decode(obj)
                    # Only return decoded if it looks like binary data (not a regular string)
                    # Base64-encoded bytes typically decode to non-printable characters
                    if len(decoded) > 0:
                        return decoded
                    return obj
                except (ValueError, TypeError):
                    # Not base64, return as string
                    return obj
            elif isinstance(obj, dict):
                return {k: convert_base64_to_bytes(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_base64_to_bytes(item) for item in obj]
            else:
                # int, float, None, etc. - return as-is
                return obj
        
        public_key = convert_base64_to_bytes(public_key_dict)
        
        # Ensure challenge is bytes - it's stored as base64 string in session
        if isinstance(challenge, bytes):
            expected_challenge_bytes = challenge
        elif isinstance(challenge, str):
            # Challenge is stored as base64 string, decode to bytes
            expected_challenge_bytes = safe_b64decode(challenge)
        else:
            # Convert to string first, then decode
            expected_challenge_bytes = safe_b64decode(str(challenge))
        
        verification = verify_authentication_response(
            credential=credential_obj,
            expected_challenge=expected_challenge_bytes,
            expected_origin=origin,
            expected_rp_id=RP_ID,
            credential_public_key=public_key,
            credential_current_sign_count=credential_record.counter,
        )
        
        # Update credential counter and last used
        credential_record.counter = verification.new_sign_count
        credential_record.last_used_at = get_est_time()
        db.session.commit()
        
        # Store device fingerprint
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        fingerprint_hash = create_device_fingerprint(device_info, user_agent, ip_address)
        store_device_fingerprint(user.id, fingerprint_hash, device_info, user_agent, ip_address)
        
        # Log in the user
        login_user(user, remember=True)  # Use remember=True to persist session
        log_login_attempt(user.username, 'biometric', 'success', user.id)
        # Python function call: Track active session for monitoring
        from auth import track_session_activity
        import hashlib
        session_id = hashlib.sha256(str(id(session)).encode()).hexdigest()[:32]
        track_session_activity(user.id, session_id)
        session['auth_method'] = 'biometric'
        session['login_time'] = get_utc_time().isoformat()
        session['user_role'] = user.role
        
        # Clear WebAuthn challenge session (but keep user logged in)
        session.pop('webauthn_challenge', None)
        session.pop('webauthn_user_id', None)
        
        # Commit session changes
        session.permanent = True
        
        # Determine redirect URL
        if user.role == 'admin':
            redirect_url = url_for('admin_dashboard')
        elif user.role == 'professor':
            redirect_url = url_for('professor_dashboard')
        else:
            redirect_url = url_for('student_dashboard')
        
        print(f"Biometric login successful for user {user.username}, redirecting to {redirect_url}")
        
        return jsonify({
            'success': True,
            'message': 'Biometric authentication successful',
            'redirect': redirect_url
        })
    except Exception as e:
        print(f"WebAuthn authenticate complete error: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        username = session.get('webauthn_user_id')
        if username:
            user = User.query.get(username)
            if user:
                log_login_attempt(user.username, 'biometric', 'failed', user.id)
        return jsonify({'success': False, 'error': str(e)}), 500


# Device Fingerprint API - Store fingerprint
@app.route('/api/device-fingerprint', methods=['POST'])
@login_required
def store_fingerprint():
    """Store device fingerprint for current user"""
    try:
        data = request.get_json()
        device_info = data.get('device_info', {})
        
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        fingerprint_hash = create_device_fingerprint(device_info, user_agent, ip_address)
        fingerprint = store_device_fingerprint(
            current_user.id,
            fingerprint_hash,
            device_info,
            user_agent,
            ip_address
        )
        
        if fingerprint:
            return jsonify({
                'success': True,
                'fingerprint_id': fingerprint.id,
                'is_trusted': fingerprint.is_trusted
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to store fingerprint'}), 500
    except Exception as e:
        print(f"Device fingerprint error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Legacy biometric login endpoint (kept for backward compatibility)
@app.route('/api/biometric-login', methods=['POST'])
def biometric_login():
    """Legacy endpoint - redirects to WebAuthn"""
    return jsonify({
        'success': False,
        'error': 'Please use WebAuthn authentication endpoints',
        'message': 'Use /api/webauthn/authenticate/begin to start authentication'
    }), 400


# Python decorator: Registers API route for RFID card authentication
# '/api/rfid-login' is the API endpoint URL
# methods=['POST'] restricts to POST requests only
@app.route('/api/rfid-login', methods=['POST'])
# Python function definition: RFID login API endpoint handler
def rfid_login():
    # Python docstring: Documents that this is simulated RFID authentication
    """Simulated RFID card authentication"""
    # Python variable: Parses JSON data from request body
    data = request.get_json()
    # Python variable: Extracts username from JSON data
    username_input = data.get('username')
    
    # Python conditional: Validates username is provided
    if not username_input:
        # Python return statement: Returns JSON error response with 400 status code
        return jsonify({'success': False, 'error': 'Username is required'}), 400
    
    # Normalize username to lowercase for case-insensitive matching
    username = normalize_username(username_input)
    
    # Python variable: Queries database for user with matching username
    user = User.query.filter_by(username=username).first()
    # Python conditional: Checks if user was not found
    if not user:
        # Log failed login attempt - wrong username
        log_login_attempt(username, 'rfid', 'failed', user_id=None)
        # Python return statement: Returns JSON error response with 404 status code
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Python comment: Marks simulated authentication section
    # Simulate RFID authentication (always succeeds for demo)
    # Python function call: Logs in the user (simulated success)
    login_user(user)
    # Python function call: Records successful RFID login attempt
    log_login_attempt(username, 'rfid', 'success', user.id)
    # Python dictionary assignment: Stores RFID auth method in session
    session['auth_method'] = 'rfid'
    # Python dictionary assignment: Stores login timestamp (EST timezone)
    session['login_time'] = get_est_time().isoformat()
    # Python dictionary assignment: Stores user role in session
    session['user_role'] = user.role  # Store role in session
    
    # Python comment: Marks redirect URL determination section
    # Determine redirect URL based on role
    # Python conditional: Checks if user is admin
    if user.role == 'admin':
        # Python variable: Generates URL for admin dashboard
        redirect_url = url_for('admin_dashboard')
    # Python elif clause: Checks if user is professor
    elif user.role == 'professor':
        # Python variable: Generates URL for professor dashboard
        redirect_url = url_for('professor_dashboard')
    # Python else clause: Default case (student)
    else:
        # Python variable: Generates URL for student dashboard
        redirect_url = url_for('student_dashboard')
    
    # Python return statement: Returns JSON success response with redirect URL
    return jsonify({'success': True, 'message': 'RFID authentication successful', 'redirect': redirect_url})


# Python decorator: Registers route handler for '/dashboard' URL
# @login_required decorator ensures user must be logged in to access this route
@app.route('/dashboard')
# Python decorator: Requires user to be authenticated before accessing route
# If not logged in, redirects to login page (defined in login_manager.login_view)
@login_required
# Python function definition: Dashboard route handler (redirects to role-specific dashboard)
def dashboard():
    # Python docstring: Documents what the function does
    """Redirect to role-specific dashboard"""
    # Python conditional: Checks if current user's role is admin
    # current_user is provided by Flask-Login, represents logged-in user
    if current_user.role == 'admin':
        # Python return statement: Redirects to admin dashboard
        return redirect(url_for('admin_dashboard'))
    # Python elif clause: Checks if current user's role is professor
    elif current_user.role == 'professor':
        # Python return statement: Redirects to professor dashboard
        return redirect(url_for('professor_dashboard'))
    # Python else clause: Default case (student or other roles)
    else:
        # Python return statement: Redirects to student dashboard
        return redirect(url_for('student_dashboard'))


# Python decorator: Registers route handler for '/admin/dashboard' URL
@app.route('/admin/dashboard')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Admin dashboard route handler
def admin_dashboard():
    # Python docstring: Documents access restrictions
    """Admin dashboard - only accessible to admin username"""
    # Python conditional: Checks if user is not admin username or not admin role
    # Double check ensures only specific admin user can access
    if current_user.username != 'admin' or current_user.role != 'admin':
        # Python return statement: Returns 403 Forbidden error message
        # 403 status code indicates access denied
        return "Access Denied. Only admin username can access this page.", 403
    
    # Python variable: Creates dictionary with user data for template
    # Dictionary will be passed to template for display
    user_data = {
        'username': current_user.username,           # Gets username from current user
        'role': current_user.role,                    # Gets role from current user
        'login_time': session.get('login_time', 'Now') # Gets login time from session, defaults to 'Now'
    }
    
    # Python comment: Marks login statistics section
    # Admin can see all login attempts
    # Python import statement: Imports LoginAttempt model from models module
    from models import LoginAttempt
    # Python dictionary assignment: Counts total successful logins
    # LoginAttempt.query.filter_by() filters by status, .count() returns total count
    user_data['total_logins'] = LoginAttempt.query.filter_by(status='success').count()
    # Python dictionary assignment: Gets 5 most recent successful logins
    # .order_by() sorts by timestamp descending, .limit(5) gets top 5 results
    user_data['recent_logins'] = LoginAttempt.query.filter_by(status='success').order_by(LoginAttempt.timestamp.desc()).limit(5).all()
    # Python dictionary assignment: Counts total number of users
    # User.query.count() returns total count of all users in database
    user_data['total_users'] = User.query.count()
    
    # Python comment: Marks active sessions section
    # Get all currently active sessions (users who are online)
    # Python import statement: Imports get_active_sessions function from auth module
    from auth import get_active_sessions
    from models import ActiveSession
    # Python dictionary assignment: Gets all active sessions
    # get_active_sessions() returns list of ActiveSession objects for users currently logged in
    active_sessions = get_active_sessions()
    user_data['active_sessions'] = active_sessions
    user_data['active_users_count'] = len(active_sessions)
    
    # Python comment: Marks device fingerprinting section
    # Get device information for active sessions
    # Python dictionary assignment: Gets device fingerprints for active users
    user_data['device_info'] = {}
    for active_session in active_sessions:
        user_id = active_session.user_id
        user = User.query.get(user_id)
        if user:
            # Get most recent device fingerprint for this user
            device = DeviceFingerprint.query.filter_by(user_id=user_id).order_by(DeviceFingerprint.last_seen_at.desc()).first()
            if device:
                user_data['device_info'][user_id] = {
                    'ip_address': device.ip_address,
                    'user_agent': device.user_agent,
                    'last_seen': device.last_seen_at,
                    'is_trusted': device.is_trusted
                }
    
    # Python return statement: Renders admin dashboard template with user data
    # render_template() renders HTML template and passes data dictionary to template
    return render_template('dashboards/admin_dashboard.html', data=user_data)


# Python decorator: Registers route handler for '/professor/dashboard' URL
@app.route('/professor/dashboard')
# Python decorator: Requires user to be authenticated
@login_required
# Python decorator: Restricts access to users with 'professor' role only
# @role_required('professor') ensures only professors can access this route
@role_required('professor')
# Python function definition: Professor dashboard route handler
def professor_dashboard():
    # Python docstring: Documents what the function does
    """Professor dashboard"""
    # Python variable: Creates dictionary with user data for template
    user_data = {
        'username': current_user.username,           # Gets username
        'role': current_user.role,                    # Gets role
        'login_time': session.get('login_time', 'Now') # Gets login time from session
    }
    
    # Python comment: Marks professor-specific data section
    # Professor's courses and students
    # Python dictionary assignment: Gets all courses taught by this professor
    # Course.query.filter_by() filters courses by professor_id matching current user's ID
    user_data['courses'] = Course.query.filter_by(professor_id=current_user.id).all()
    # Python dictionary assignment: Counts unique students taught by this professor
    # db.session.query() creates custom query, .distinct() removes duplicates, .count() returns count
    user_data['total_students'] = db.session.query(Grade.student_id).filter_by(professor_id=current_user.id).distinct().count()
    # Python dictionary assignment: Gets 5 most recent grades given by this professor
    # Grade.query.filter_by() filters by professor_id, .order_by() sorts by creation date descending
    user_data['recent_grades'] = Grade.query.filter_by(professor_id=current_user.id).order_by(Grade.created_at.desc()).limit(5).all()
    
    # Python return statement: Renders professor dashboard template with user data
    return render_template('dashboards/professor_dashboard.html', data=user_data)


# Python decorator: Registers route handler for '/student/dashboard' URL
@app.route('/student/dashboard')
# Python decorator: Requires user to be authenticated
@login_required
# Python decorator: Restricts access to users with 'student' role only
@role_required('student')
# Python function definition: Student dashboard route handler
def student_dashboard():
    # Python docstring: Documents what the function does
    """Student dashboard"""
    # Python variable: Creates dictionary with user data for template
    user_data = {
        'username': current_user.username,           # Gets username
        'role': current_user.role,                    # Gets role
        'login_time': session.get('login_time', 'Now') # Gets login time from session
    }
    
    # Python comment: Marks student-specific data section
    # Student's grades and courses
    # Python dictionary assignment: Gets all grades for this student
    # Grade.query.filter_by() filters grades by student_id matching current user's ID
    user_data['grades'] = Grade.query.filter_by(student_id=current_user.id).all()
    # Python dictionary assignment: Extracts courses from grades list
    # List comprehension: [grade.course for grade in ...] gets course object from each grade
    user_data['courses'] = [grade.course for grade in user_data['grades']]
    # Python dictionary assignment: Calculates GPA (Grade Point Average)
    # sum() adds all percentages, divides by count, defaults to 0 if no grades exist
    user_data['gpa'] = sum([g.percentage for g in user_data['grades']]) / len(user_data['grades']) if user_data['grades'] else 0
    # Python dictionary assignment: Gets 5 most recent grades
    # List slicing [:5] gets first 5 items, or empty list if no grades exist
    user_data['recent_grades'] = user_data['grades'][:5] if user_data['grades'] else []
    
    # Python return statement: Renders student dashboard template with user data
    return render_template('dashboards/student_dashboard.html', data=user_data)


# Python decorator: Registers route handler for '/admin' URL
@app.route('/admin')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Admin panel route handler
def admin():
    # Python docstring: Documents access restrictions
    """Admin panel - only accessible to admin users with username 'admin'"""
    # Python conditional: Checks if user is not admin username or not admin role
    if current_user.username != 'admin' or current_user.role != 'admin':
        # Python return statement: Returns 403 Forbidden error
        return "Access Denied. Only admin username can access this page.", 403
    # Python variable: Queries database for all users
    # User.query.all() returns list of all User objects in database
    users = User.query.all()
    # Python import statement: Imports LoginAttempt model
    from models import LoginAttempt
    # Python variable: Gets 100 most recent successful login attempts
    # .filter_by() filters by status, .order_by() sorts by timestamp descending, .limit(100) gets top 100
    all_logins = LoginAttempt.query.filter_by(status='success').order_by(LoginAttempt.timestamp.desc()).limit(100).all()
    # Python return statement: Renders admin template with users and login logs
    return render_template('admin.html', users=users, login_logs=all_logins)


# Python decorator: Registers route handler for '/admin/manage-users' URL
@app.route('/admin/manage-users')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: User management page route handler
def manage_users():
    # Python docstring: Documents what the function does
    """Manage users - add, edit, delete (admin only)"""
    # Python conditional: Checks if user is not admin
    if current_user.username != 'admin' or current_user.role != 'admin':
        # Python return statement: Returns 403 Forbidden error
        return "Access Denied", 403
    # Python variable: Gets all users from database
    users = User.query.all()
    # Python return statement: Renders user management template
    return render_template('manage_users.html', users=users)


# Python decorator: Registers API route for adding new users
# '/admin/add-user' is the API endpoint URL
# methods=['POST'] restricts to POST requests only
@app.route('/admin/add-user', methods=['POST'])
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Add user API endpoint handler
def add_user():
    # Python docstring: Documents access restrictions
    """Add new user (admin only)"""
    # Python conditional: Checks if user is not admin
    if current_user.username != 'admin' or current_user.role != 'admin':
        # Python return statement: Returns JSON error response with 403 status code
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    # Python variable: Parses JSON data from request body
    data = request.get_json()
    # Python variable: Extracts username from JSON data
    username_input = data.get('username')
    # Python variable: Extracts role from JSON data, defaults to 'student' if not provided
    role = data.get('role', 'student')
    
    # Normalize username to lowercase for case-insensitive matching
    username = normalize_username(username_input) if username_input else None
    
    if not username:
        return jsonify({'success': False, 'error': 'Username is required'}), 400
    
    # Python conditional: Checks if username already exists in database
    if User.query.filter_by(username=username).first():
        # Python return statement: Returns JSON error response with 400 status code
        # 400 = Bad Request (username already exists)
        return jsonify({'success': False, 'error': 'Username already exists'}), 400
    
    # Python comment: Marks user creation section
    # Email is not stored - only username is used for authentication
    # Python object creation: Creates new User instance
    user = User(username=username, role=role)
    # Python method call: Adds user to database session
    db.session.add(user)
    # Python method call: Saves user to database
    db.session.commit()
    
    # Python return statement: Returns JSON success response
    # f-string formats message with username
    return jsonify({'success': True, 'message': f'User {username} created successfully'})


# Python decorator: Registers API route for editing users
# '/admin/edit-user/<int:user_id>' is the API endpoint with user_id parameter
# <int:user_id> extracts user_id from URL and converts to integer
@app.route('/admin/edit-user/<int:user_id>', methods=['POST'])
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Edit user API endpoint handler
# Parameter: user_id (integer) - ID of user to edit, extracted from URL
def edit_user(user_id):
    # Python docstring: Documents access restrictions
    """Edit user (admin only)"""
    # Python conditional: Checks if user is not admin
    if current_user.username != 'admin' or current_user.role != 'admin':
        # Python return statement: Returns JSON error response with 403 status code
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    # Python variable: Queries database for user by ID, returns 404 if not found
    # .get_or_404() retrieves user or automatically returns 404 error if doesn't exist
    user = User.query.get_or_404(user_id)
    # Python variable: Parses JSON data from request body
    data = request.get_json()
    
    # Python comment: Marks user update section
    # Email is not stored - only role can be updated
    # Python conditional: Checks if 'role' key exists in JSON data
    if 'role' in data:
        # Python attribute assignment: Updates user's role
        user.role = data['role']
    
    # Python method call: Saves changes to database
    db.session.commit()
    # Python return statement: Returns JSON success response
    return jsonify({'success': True, 'message': f'User {user.username} updated successfully'})


# Python decorator: Registers API route for deleting users
# '/admin/delete-user/<int:user_id>' is the API endpoint with user_id parameter
@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Delete user API endpoint handler
# Parameter: user_id (integer) - ID of user to delete
def delete_user(user_id):
    # Python docstring: Documents access restrictions
    """Delete user (admin only)"""
    # Python conditional: Checks if user is not admin
    if current_user.username != 'admin' or current_user.role != 'admin':
        # Python return statement: Returns JSON error response with 403 status code
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    # Python conditional: Prevents user from deleting their own account
    # Security check: Prevents accidental self-deletion
    if user_id == current_user.id:
        # Python return statement: Returns JSON error response with 400 status code
        return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
    
    # Python variable: Queries database for user by ID, returns 404 if not found
    user = User.query.get_or_404(user_id)
    # Python variable: Stores username before deletion (for success message)
    username = user.username
    # Python method call: Marks user for deletion in database session
    # db.session.delete() stages user for deletion (not yet committed)
    db.session.delete(user)
    # Python method call: Permanently deletes user from database
    db.session.commit()
    
    # Python return statement: Returns JSON success response
    return jsonify({'success': True, 'message': f'User {username} deleted successfully'})


# Python decorator: Registers route handler for '/admin/login-logs' URL
@app.route('/admin/login-logs')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Login logs page route handler
def login_logs():
    # Python docstring: Documents access restrictions
    """View all login logs (admin only)"""
    # Python conditional: Checks if user is not admin
    if current_user.username != 'admin' or current_user.role != 'admin':
        # Python return statement: Returns 403 Forbidden error
        return "Access Denied", 403
    # Python import statement: Imports LoginAttempt model
    from models import LoginAttempt
    # Python variable: Gets 200 most recent login attempts from database
    # .order_by() sorts by timestamp descending, .limit(200) gets top 200 results
    logs = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).limit(200).all()
    # Python return statement: Renders login logs template with logs data
    return render_template('login_logs.html', logs=logs)


# Python decorator: Registers route handler for '/admin/grades' URL
@app.route('/admin/grades')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Admin grades management page route handler
def admin_grades():
    # Python docstring: Documents access restrictions
    """Admin grades management (admin only)"""
    # Python conditional: Checks if user is not admin
    if current_user.username != 'admin' or current_user.role != 'admin':
        # Python return statement: Returns 403 Forbidden error
        return "Access Denied", 403
    # Python variable: Gets all grades ordered by creation date (newest first)
    # .order_by() sorts by created_at descending
    grades = Grade.query.order_by(Grade.created_at.desc()).all()
    # Python variable: Gets all courses from database
    courses = Course.query.all()
    # Python variable: Gets all users with 'student' role
    # .filter_by() filters users by role='student'
    students = User.query.filter_by(role='student').all()
    # Python return statement: Renders admin grades template with grades, courses, and students
    return render_template('admin_grades.html', grades=grades, courses=courses, students=students)


# Python decorator: Registers route handler for '/professor/courses' URL
@app.route('/professor/courses')
# Python decorator: Requires user to be authenticated
@login_required
# Python decorator: Restricts access to users with 'professor' role only
@role_required('professor')
# Python function definition: Professor courses page route handler
def professor_courses():
    # Python docstring: Documents what the function does
    """Professor's courses management"""
    # Python variable: Gets all courses taught by current professor
    # Course.query.filter_by() filters courses by professor_id matching current user's ID
    courses = Course.query.filter_by(professor_id=current_user.id).all()
    # Python return statement: Renders professor courses template with courses data
    return render_template('professor_courses.html', courses=courses)


# Python decorator: Registers API route for adding courses
# '/professor/add-course' is the API endpoint URL
# methods=['POST'] restricts to POST requests only
@app.route('/professor/add-course', methods=['POST'])
# Python decorator: Requires user to be authenticated
@login_required
# Python decorator: Restricts access to users with 'professor' role only
@role_required('professor')
# Python function definition: Add course API endpoint handler
def add_course():
    # Python docstring: Documents access restrictions
    """Add new course (professor only)"""
    # Python variable: Parses JSON data from request body
    data = request.get_json()
    # Python variable: Extracts course code from JSON data
    code = data.get('code')
    # Python variable: Extracts course name from JSON data
    name = data.get('name')
    
    # Python conditional: Checks if course code already exists
    if Course.query.filter_by(code=code).first():
        # Python return statement: Returns JSON error response with 400 status code
        return jsonify({'success': False, 'error': 'Course code already exists'}), 400
    
    # Python object creation: Creates new Course instance
    # Links course to current professor via professor_id
    course = Course(code=code, name=name, professor_id=current_user.id)
    # Python method call: Adds course to database session
    db.session.add(course)
    # Python method call: Saves course to database
    db.session.commit()
    
    # Python return statement: Returns JSON success response
    return jsonify({'success': True, 'message': f'Course {code} created successfully'})


# Python decorator: Registers route handler for '/professor/give-grades' URL
@app.route('/professor/give-grades')
# Python decorator: Requires user to be authenticated
@login_required
# Python decorator: Restricts access to users with 'professor' role only
@role_required('professor')
# Python function definition: Give grades page route handler
def give_grades():
    # Python docstring: Documents what the function does
    """Give grades to students (professor only)"""
    # Python variable: Gets all courses taught by current professor
    courses = Course.query.filter_by(professor_id=current_user.id).all()
    # Python variable: Gets all users with 'student' role
    students = User.query.filter_by(role='student').all()
    # Python variable: Gets all grades given by current professor, ordered by creation date
    grades = Grade.query.filter_by(professor_id=current_user.id).order_by(Grade.created_at.desc()).all()
    # Python return statement: Renders give grades template with courses, students, and grades
    return render_template('give_grades.html', courses=courses, students=students, grades=grades)


# Python decorator: Registers API route for submitting grades
# '/professor/submit-grade' is the API endpoint URL
# methods=['POST'] restricts to POST requests only
@app.route('/professor/submit-grade', methods=['POST'])
# Python decorator: Requires user to be authenticated
@login_required
# Python decorator: Restricts access to users with 'professor' role only
@role_required('professor')
# Python function definition: Submit grade API endpoint handler
def submit_grade():
    # Python docstring: Documents access restrictions
    """Submit a grade (professor only)"""
    # Python variable: Parses JSON data from request body
    data = request.get_json()
    # Python variable: Extracts student ID from JSON data
    student_id = data.get('student_id')
    # Python variable: Extracts course ID from JSON data
    course_id = data.get('course_id')
    # Python variable: Extracts grade value (A+, A, B, etc.) from JSON data
    grade_value = data.get('grade_value')
    # Python variable: Extracts percentage score (0-100) from JSON data
    percentage = data.get('percentage')
    
    # Python comment: Marks course ownership verification section
    # Verify course belongs to professor
    # Python variable: Queries database for course by ID, returns 404 if not found
    course = Course.query.get_or_404(course_id)
    # Python conditional: Checks if course doesn't belong to current professor
    if course.professor_id != current_user.id:
        # Python return statement: Returns JSON error response with 403 status code
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    # Python comment: Marks grade update/create section
    # Check if grade exists, update or create
    # Python variable: Queries database for existing grade for this student and course
    existing_grade = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()
    # Python conditional: Checks if grade already exists
    if existing_grade:
        # Python attribute assignment: Updates grade value
        existing_grade.grade_value = grade_value
        # Python attribute assignment: Updates percentage score
        existing_grade.percentage = percentage
        # Python attribute assignment: Updates timestamp to current time
        existing_grade.updated_at = get_est_time()
    # Python else clause: Executes if grade doesn't exist (create new)
    else:
        # Python object creation: Creates new Grade instance
        grade = Grade(
            student_id=student_id,      # Links grade to student
            course_id=course_id,         # Links grade to course
            grade_value=grade_value,     # Sets letter grade
            percentage=percentage,       # Sets percentage score
            professor_id=current_user.id # Links grade to professor
        )
        # Python method call: Adds new grade to database session
        db.session.add(grade)
    
    # Python method call: Saves grade changes to database
    db.session.commit()
    # Python return statement: Returns JSON success response
    return jsonify({'success': True, 'message': 'Grade submitted successfully'})


# Python decorator: Registers route handler for '/student/grades' URL
@app.route('/student/grades')
# Python decorator: Requires user to be authenticated
@login_required
# Python decorator: Restricts access to users with 'student' role only
@role_required('student')
# Python function definition: Student grades page route handler
def student_grades():
    # Python docstring: Documents what the function does
    """View grades (student only)"""
    # Python variable: Gets all grades for current student
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    # Python variable: Calculates GPA (Grade Point Average)
    # sum() adds all percentages, divides by count, defaults to 0 if no grades
    gpa = sum([g.percentage for g in grades]) / len(grades) if grades else 0
    # Python return statement: Renders student grades template with grades and GPA
    return render_template('student_grades.html', grades=grades, gpa=gpa)


# Python decorator: Registers route handler for '/student/courses' URL
@app.route('/student/courses')
# Python decorator: Requires user to be authenticated
@login_required
# Python decorator: Restricts access to users with 'student' role only
@role_required('student')
# Python function definition: Student courses page route handler
def student_courses():
    # Python docstring: Documents what the function does
    """View enrolled courses (student only)"""
    # Python variable: Gets all grades for current student
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    # Python variable: Extracts courses from grades list using list comprehension
    # [grade.course for grade in grades] gets course object from each grade
    courses = [grade.course for grade in grades]
    # Python return statement: Renders student courses template with courses data
    return render_template('student_courses.html', courses=courses)


# Python decorator: Registers route handler for '/report-issue' URL
@app.route('/report-issue')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Report issue page route handler
def report_issue():
    # Python docstring: Documents what the function does
    """Report an issue page"""
    # Python return statement: Renders report issue template
    return render_template('report_issue.html')


# Python decorator: Registers route handler for '/security-guidelines' URL
@app.route('/security-guidelines')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Security guidelines page route handler
def security_guidelines():
    # Python docstring: Documents what the function does
    """Security guidelines page"""
    # Python return statement: Renders security guidelines template
    return render_template('security_guidelines.html')


# Python decorator: Registers route handler for '/recent-activity' URL
@app.route('/recent-activity')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Recent activity page route handler
def recent_activity():
    # Python docstring: Documents what the function does
    """Recent activity page"""
    # Python import statement: Imports LoginAttempt model from models module
    from models import LoginAttempt
    # Python import statement: Imports request object from flask module
    # Already imported at top, but re-imported here for clarity
    from flask import request
    # Python import statement: Imports datetime class
    # Already imported at top, but re-imported here for clarity
    from datetime import datetime
    
    # Python comment: Marks login attempts retrieval section
    # Get recent login attempts
    # Python variable: Gets 20 most recent login attempts for current user
    # .filter_by() filters by user_id, .order_by() sorts by timestamp descending, .limit(20) gets top 20
    recent_attempts = LoginAttempt.query.filter_by(user_id=current_user.id).order_by(LoginAttempt.timestamp.desc()).limit(20).all()
    
    # Python comment: Marks current session info section
    # Add current session info
    # Python variable: Creates dictionary with current session information
    current_session = {
        'method': session.get('auth_method', 'unknown'),              # Gets auth method from session
        'ip_address': request.remote_addr,                             # Gets client IP address
        'timestamp': get_est_time(),                                 # Gets current EST timestamp
        'status': 'success',                                            # Sets status as success
        'user_agent': request.headers.get('User-Agent', 'Unknown')     # Gets browser user agent string
    }
    
    # Python return statement: Renders recent activity template with activities and current session
    return render_template('recent_activity.html', 
                        activities=recent_attempts,
                        current_session=current_session)


# Python decorator: Registers route handler for '/device-security' URL
@app.route('/device-security')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Device security page route handler
def device_security():
    # Python docstring: Documents what the function does
    """Device security page"""
    # Python import statement: Imports get_active_sessions function from auth module
    from auth import get_active_sessions
    # Python variable: Gets all active sessions from authentication system
    active_sessions = get_active_sessions()
    # Python variable: Filters active sessions to only current user's sessions
    # List comprehension: [s for s in ... if ...] filters sessions by user_id
    user_sessions = [s for s in active_sessions if s.user_id == current_user.id]
    
    # Python return statement: Renders device security template with user's devices
    return render_template('device_security.html', devices=user_sessions)


# Python decorator: Registers route handler for '/account-protection' URL
@app.route('/account-protection')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Account protection page route handler
def account_protection():
    # Python docstring: Documents what the function does
    """Account protection level page"""
    # Python return statement: Renders account protection template
    return render_template('account_protection.html')


# Python decorator: Registers route handler for '/access-history' URL
@app.route('/access-history')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Access history page route handler
def access_history():
    # Python docstring: Documents what the function does
    """View access history page"""
    # Python import statement: Imports get_active_sessions function from auth module
    from auth import get_active_sessions
    # Python import statement: Imports LoginAttempt model from models module
    from models import LoginAttempt
    
    # Python variable: Gets 50 most recent login attempts for current user
    # .filter_by() filters by user_id, .order_by() sorts by timestamp descending, .limit(50) gets top 50
    login_attempts = LoginAttempt.query.filter_by(user_id=current_user.id).order_by(LoginAttempt.timestamp.desc()).limit(50).all()
    # Python variable: Gets all active sessions
    active_sessions = get_active_sessions()
    # Python variable: Filters active sessions to only current user's sessions
    user_sessions = [s for s in active_sessions if s.user_id == current_user.id]
    
    # Python return statement: Renders access history template with login attempts and active sessions
    return render_template('access_history.html', 
                        login_attempts=login_attempts,
                        active_sessions=user_sessions)


# Python decorator: Registers route handler for '/generate-code' URL
@app.route('/generate-code')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Generate code page route handler
def generate_code():
    # Python docstring: Documents what the function does
    """Generate random passcode page"""
    # Python return statement: Renders generate code template
    return render_template('generate_code.html')


# Python decorator: Registers API route for generating passcodes
# '/api/generate-passcode' is the API endpoint URL
# methods=['POST'] restricts to POST requests only
@app.route('/api/generate-passcode', methods=['POST'])
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Generate passcode API endpoint handler
def generate_passcode_api():
    # Python docstring: Documents what the endpoint does
    """API endpoint to generate a random passcode"""
    # Python import statement: Imports secrets module for cryptographically secure random generation
    # secrets is more secure than random for generating passwords/codes
    import secrets
    # Python import statement: Imports string module for character sets
    import string
    
    # Python variable: Parses JSON data from request body
    data = request.get_json()
    # Python variable: Extracts passcode length from JSON data, defaults to 12 if not provided
    length = data.get('length', 12)
    # Python variable: Extracts include_symbols flag from JSON data, defaults to False
    include_symbols = data.get('include_symbols', False)
    
    # Python comment: Marks character set definition section
    # Generate random passcode
    # Python variable: Creates character set with letters and digits
    # string.ascii_letters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    # string.digits = '0123456789'
    characters = string.ascii_letters + string.digits
    # Python conditional: Checks if symbols should be included
    if include_symbols:
        # Python string concatenation: Adds special symbols to character set
        characters += '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    # Python variable: Generates random passcode using cryptographically secure random selection
    # secrets.choice() selects random character from set, repeated 'length' times
    # ''.join() concatenates selected characters into single string
    passcode = ''.join(secrets.choice(characters) for _ in range(length))
    
    # Python return statement: Returns JSON response with generated passcode
    return jsonify({
        'success': True,                        # Indicates operation succeeded
        'passcode': passcode,                   # The generated passcode string
        'length': length,                       # Length of generated passcode
        'timestamp': get_est_time().isoformat() # ISO format timestamp of generation (EST)
    })


# Python decorator: Registers API route for verifying user role
# '/verify-role' is the API endpoint URL
@app.route('/verify-role')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Verify role API endpoint handler
def verify_role():
    # Python docstring: Documents what the endpoint does
    """API endpoint to verify user's role"""
    # Python return statement: Returns JSON response with user role information
    return jsonify({
        'username': current_user.username,                    # Gets username from current user
        'role': current_user.role,                            # Gets role from current user
        'is_admin': current_user.role == 'admin',            # Boolean: True if admin
        'is_professor': current_user.role == 'professor',    # Boolean: True if professor
        'is_student': current_user.role == 'student'         # Boolean: True if student
    })


# Python decorator: Registers API route for checking user role by username
# '/api/check-role/<username>' is the API endpoint with username parameter
# <username> extracts username from URL as string
@app.route('/api/check-role/<username>')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: Check role API endpoint handler
# Parameter: username (string) - Username to check, extracted from URL
def check_role(username):
    # Python docstring: Documents access restrictions
    """API endpoint to check a user's role by username (admin only)"""
    # Python conditional: Checks if current user is not admin
    if current_user.role != 'admin':
        # Python return statement: Returns JSON error response with 403 status code
        return jsonify({'error': 'Access denied. Admin only.'}), 403
    
    # Python variable: Gets user's role from database using helper function
    # get_user_role() queries database and returns role string or None
    role = get_user_role(username)
    # Python conditional: Checks if user exists (role is not None)
    if role:
        # Python return statement: Returns JSON response with user role information
        return jsonify({
            'username': username,      # Username that was checked
            'role': role,              # User's role (admin, professor, or student)
            'exists': True             # Boolean: User exists in database
        })
    # Python else clause: Executes if user doesn't exist
    else:
        # Python return statement: Returns JSON response with 404 status code
        return jsonify({
            'username': username,      # Username that was checked
            'exists': False            # Boolean: User does not exist
        }), 404




# Python decorator: Registers route handler for '/register-biometric' URL
@app.route('/register-biometric')
@login_required
def register_biometric():
    """Page for registering biometric credentials"""
    # Get user's existing credentials
    credentials = WebAuthnCredential.query.filter_by(user_id=current_user.id).all()
    return render_template('register_biometric.html', credentials=credentials)


# Python decorator: Registers route handler for '/logout' URL
@app.route('/logout')
# Python function definition: Logout route handler (no login_required - logout should work for all)
def logout():
    # Python function call: Logs out current user and clears session
    # logout_user() removes user from Flask-Login session
    logout_user()
    # Python return statement: Redirects user to login page after logout
    return redirect(url_for('login'))


# Python comment: Marks API routes section
# API Routes
# Python decorator: Registers API route for getting user information
# '/api/user-info' is the API endpoint URL
@app.route('/api/user-info')
# Python decorator: Requires user to be authenticated
@login_required
# Python function definition: User info API endpoint handler
def user_info():
    # Python return statement: Returns JSON response with current user's information
    return jsonify({
        'username': current_user.username,  # Gets username from current user
        'role': current_user.role,        # Gets role from current user
        'email': current_user.email       # Gets email from current user
    })


# Initialize database lazily (only when first request comes in)
# This speeds up cold starts on Render free tier
def initialize_database():
    """Initialize database tables and sample data"""
    try:
        with app.app_context():
            # Create all database tables defined in models
            db.create_all()
            # Create sample users and data if database is empty
            create_sample_data()
    except Exception as e:
        # Log error but don't crash - database might already exist
        print(f"Database initialization note: {e}")

# Track if database has been initialized
_db_initialized = False

# Initialize database on first request (lazy initialization for faster cold starts)
@app.before_request
def ensure_database_initialized():
    """Ensure database is initialized before handling requests"""
    global _db_initialized
    if not _db_initialized:
        initialize_database()
        _db_initialized = True
    
    # Track session activity for authenticated users (updates last_activity timestamp)
    if current_user.is_authenticated:
        try:
            from auth import track_session_activity
            import hashlib
            # Generate session ID from Flask session
            session_id = hashlib.sha256(str(id(session)).encode()).hexdigest()[:32]
            track_session_activity(current_user.id, session_id)
        except Exception as e:
            # Don't break the request if session tracking fails
            pass

# Check email configuration endpoint (GET - no auth needed for debugging)
@app.route('/api/check-email-config', methods=['GET'])
def check_email_config():
    """Check if email configuration is set up correctly"""
    # Check SendGrid configuration (preferred for Render free tier)
    email_service = os.environ.get('EMAIL_SERVICE', '').lower()
    sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
    sendgrid_configured = email_service == 'sendgrid' and sendgrid_api_key is not None
    
    # Check SMTP configuration (fallback)
    smtp_server = os.environ.get('SMTP_SERVER', 'NOT SET')
    smtp_port = os.environ.get('SMTP_PORT', 'NOT SET')
    smtp_username = os.environ.get('SMTP_USERNAME', 'NOT SET')
    smtp_password = 'SET' if os.environ.get('SMTP_PASSWORD') else 'NOT SET'
    from_email = os.environ.get('FROM_EMAIL', 'NOT SET')
    
    smtp_configured = all([
        smtp_server != 'NOT SET',
        smtp_port != 'NOT SET',
        smtp_username != 'NOT SET',
        smtp_password == 'SET',
        from_email != 'NOT SET'
    ])
    
    # Overall configuration status (either SendGrid or SMTP)
    configured = sendgrid_configured or smtp_configured
    
    return jsonify({
        # SendGrid configuration
        'EMAIL_SERVICE': email_service if email_service else 'NOT SET',
        'SENDGRID_API_KEY': 'SET' if sendgrid_api_key else 'NOT SET',
        'sendgrid_configured': sendgrid_configured,
        # SMTP configuration
        'SMTP_SERVER': smtp_server,
        'SMTP_PORT': smtp_port,
        'SMTP_USERNAME': smtp_username,
        'SMTP_PASSWORD': smtp_password,
        'FROM_EMAIL': from_email,
        'smtp_configured': smtp_configured,
        # Overall status
        'configured': configured,
        'preferred_method': 'SendGrid' if sendgrid_configured else ('SMTP' if smtp_configured else 'None')
    })

# Test endpoint to verify email configuration (for debugging)
@app.route('/api/test-email', methods=['POST'])
def test_email():
    """Test email sending configuration (supports both SendGrid and SMTP)"""
    try:
        data = request.get_json()
        test_email_address = data.get('email', 'test@example.com')
        
        # Check SendGrid configuration
        email_service = os.environ.get('EMAIL_SERVICE', '').lower()
        sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        sendgrid_configured = email_service == 'sendgrid' and sendgrid_api_key is not None
        
        # Check SMTP configuration
        smtp_server = os.environ.get('SMTP_SERVER', 'NOT SET')
        smtp_port = os.environ.get('SMTP_PORT', 'NOT SET')
        smtp_username = os.environ.get('SMTP_USERNAME', 'NOT SET')
        smtp_password = 'SET' if os.environ.get('SMTP_PASSWORD') else 'NOT SET'
        from_email = os.environ.get('FROM_EMAIL', 'NOT SET')
        
        smtp_configured = all([
            smtp_username != 'NOT SET',
            smtp_password == 'SET'
        ])
        
        config_status = {
            # SendGrid config
            'EMAIL_SERVICE': email_service if email_service else 'NOT SET',
            'SENDGRID_API_KEY': 'SET' if sendgrid_api_key else 'NOT SET',
            'sendgrid_configured': sendgrid_configured,
            # SMTP config
            'SMTP_SERVER': smtp_server,
            'SMTP_PORT': smtp_port,
            'SMTP_USERNAME': smtp_username,
            'SMTP_PASSWORD': smtp_password,
            'FROM_EMAIL': from_email,
            'smtp_configured': smtp_configured
        }
        
        # Try to send a test email (send_email_code handles SendGrid/SMTP automatically)
        if sendgrid_configured or smtp_configured:
            try:
                result = send_email_code(test_email_address, '123456', 'test_user')
                method_used = 'SendGrid' if sendgrid_configured else 'SMTP'
                return jsonify({
                    'success': True,
                    'message': f'Test email sent successfully via {method_used}!',
                    'method_used': method_used,
                    'config': config_status,
                    'test_email': test_email_address
                })
            except Exception as e:
                import traceback
                error_traceback = traceback.format_exc()
                print(f"[ERROR] TEST EMAIL FAILED:")
                print(f"   Error: {str(e)}")
                print(f"   Traceback: {error_traceback}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to send test email: {str(e)}',
                    'error_details': error_traceback,
                    'config': config_status,
                    'test_email': test_email_address
                }), 500
        else:
            return jsonify({
                'success': False,
                'error': 'Email not configured - need either SendGrid (EMAIL_SERVICE=sendgrid + SENDGRID_API_KEY) or SMTP (SMTP_USERNAME + SMTP_PASSWORD)',
                'config': config_status,
                'tip': 'For Render free tier, use SendGrid: Set EMAIL_SERVICE=sendgrid and SENDGRID_API_KEY'
            }), 400
            
    except Exception as e:
        import traceback
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


# Python conditional: Checks if script is being run directly (not imported as module)
# __name__ == '__main__' is True when script is executed directly
# This block only runs when using Flask dev server, not with gunicorn
if __name__ == '__main__':
    # Python variable: Gets port number from environment variable, defaults to 5001
    # os.environ.get() reads PORT env var, int() converts to integer, 5001 is default
    # Port 5001 is used because macOS AirPlay uses port 5000
    port = int(os.environ.get("PORT", 5001))
    # Python method call: Starts Flask development server
    # app.run() starts the web server
    # host='0.0.0.0' allows connections from any network interface
    # port=port uses the port number from environment or default
    # debug mode: Only enable in development (not in production)
    debug_mode = os.environ.get("FLASK_DEBUG", "False").lower() == "true"
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
