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


# Python import statement: Imports Config class from config.py module
# Config contains all Flask application configuration settings
from config import Config

# Python import statement: Imports database models and SQLAlchemy instance from models.py
# db: SQLAlchemy database instance for database operations
# User: Database model representing user accounts
# EmailVerificationCode: Database model for storing email verification codes
# Course: Database model representing academic courses
# Grade: Database model representing student grades
from models import db, User, EmailVerificationCode, Course, Grade

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
from auth import log_login_attempt, role_required, admin_required, verify_user_role, get_user_role, normalize_username, get_est_time


# Python variable: Creates Flask application instance
# Flask(__name__) initializes Flask app, __name__ tells Flask where to find templates/static files
app = Flask(__name__)

# Python method call: Loads configuration from Config class
# app.config.from_object() applies all settings from Config class to Flask app
app.config.from_object(Config)


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
            # verification exists AND expiration time is in the future (EST timezone)
            # Get current time in EST (as naive datetime for comparison with database)
            current_time_est = get_est_time()
            # Convert to naive datetime for comparison (SQLite stores naive datetimes)
            current_time_naive = current_time_est.replace(tzinfo=None)
            
            if verification:
                # expires_at from database is naive datetime (SQLite doesn't store timezone)
                # Compare both as naive datetimes (both should be in EST)
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
                    # Python dictionary assignment: Stores authentication method in session
                    # session['auth_method'] stores how user logged in (email, otp, biometric, etc.)
                    session['auth_method'] = 'email'
                    # Python dictionary assignment: Stores login timestamp in session (EST timezone)
                    # get_est_time().isoformat() creates ISO format timestamp string
                    session['login_time'] = get_est_time().isoformat()
                    # Python dictionary assignment: Stores user role in session
                    # session['user_role'] stores role for quick access without database query
                    session['user_role'] = user.role  # Store role in session
                    
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
                # Python dictionary assignment: Stores OTP auth method in session
                session['auth_method'] = 'otp'
                # Python dictionary assignment: Stores login timestamp (EST timezone)
                session['login_time'] = get_est_time().isoformat()
                # Python dictionary assignment: Stores user role
                session['user_role'] = user.role  # Store role in session
                
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
    # Python variable: Calculates code expiration time (10 minutes from now) in EST
    # get_est_time() gets current EST time, timedelta(minutes=10) adds 10 minutes
    # Convert to naive datetime for database storage (SQLite doesn't store timezone)
    expires_at_aware = get_est_time() + timedelta(minutes=10)
    expires_at = expires_at_aware.replace(tzinfo=None)  # Store as naive datetime
    
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
    # Send email to the email address entered in the form
    # Python try block: Attempts to send email, catches exceptions
    try:
        # Python function call: Sends verification code via email
        # send_email_code() sends email or prints to console if SMTP not configured
        result = send_email_code(email, code, username)  # Send to the email from form input
        # Python conditional: Checks if email was sent successfully
        if result:
            # Python return statement: Returns JSON success response
            # f-string formats message with email address
            return jsonify({'success': True, 'message': f'Code sent successfully to {email}'})
        # Python else clause: Executes if email service returned False
        else:
            # Python return statement: Returns JSON error response with 500 status code
            # 500 = Internal Server Error (email service failed)
            return jsonify({'success': False, 'error': 'Email service returned False'}), 500
    # Python except clause: Catches any exceptions during email sending
    except Exception as e:
        # Python import statement: Imports traceback module for error details
        import traceback
        # Python variable: Gets formatted error traceback as string
        error_details = traceback.format_exc()
        # Python print statement: Outputs error details to console for debugging
        print(f"❌ Error sending email: {error_details}")
        # Python return statement: Returns JSON error response with error message
        # str(e) converts exception to string for JSON response
        return jsonify({'success': False, 'error': f'Failed to send email: {str(e)}'}), 500


# Python decorator: Registers API route for biometric authentication
# '/api/biometric-login' is the API endpoint URL
# methods=['POST'] restricts to POST requests only
@app.route('/api/biometric-login', methods=['POST'])
# Python function definition: Biometric login API endpoint handler
def biometric_login():
    # Python docstring: Documents that this is simulated biometric authentication
    """Simulated biometric authentication"""
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
        log_login_attempt(username, 'biometric', 'failed', user_id=None)
        # Python return statement: Returns JSON error response with 404 status code
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Python comment: Marks simulated authentication section
    # Simulate biometric authentication (always succeeds for demo)
    # Python function call: Logs in the user (simulated success)
    login_user(user)
    # Python function call: Records successful biometric login attempt
    log_login_attempt(username, 'biometric', 'success', user.id)
    # Python dictionary assignment: Stores biometric auth method in session
    session['auth_method'] = 'biometric'
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
    # Includes success message and redirect URL for frontend to use
    return jsonify({'success': True, 'message': 'Biometric authentication successful', 'redirect': redirect_url})


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


# Python conditional: Checks if script is being run directly (not imported as module)
# __name__ == '__main__' is True when script is executed directly
if __name__ == '__main__':
    # Python context manager: Creates Flask application context
    # app.app_context() is required for database operations outside request handlers
    with app.app_context():
        # Python method call: Creates all database tables defined in models
        # db.create_all() reads model definitions and creates missing tables
        db.create_all()
        # Python function call: Creates sample users and data if database is empty
        create_sample_data()
    
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
