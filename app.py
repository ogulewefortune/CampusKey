from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
import pyotp
import os
from datetime import datetime, timedelta


from config import Config
from models import db, User, EmailVerificationCode, Course, Grade
from email_service import generate_verification_code, send_email_code
from auth import log_login_attempt, role_required, admin_required, verify_user_role, get_user_role


app = Flask(__name__)
app.config.from_object(Config)


# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.context_processor
def inject_user():
    """Make current_user available to all templates"""
    from flask_login import current_user
    return dict(current_user=current_user)


def create_sample_data():
    """Create demo users and sample data if none exist"""
    if not User.query.first():
        users = [
            User(username='admin', role='admin'),
            User(username='professor', role='professor'),
            User(username='student', role='student'),
        ]
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        # Create sample courses
        prof = User.query.filter_by(username='professor').first()
        if prof:
            courses = [
                Course(code='CS101', name='Introduction to Computer Science', professor_id=prof.id),
                Course(code='MATH201', name='Calculus I', professor_id=prof.id),
            ]
            for course in courses:
                db.session.add(course)
            db.session.commit()
            
            # Create sample grades
            student = User.query.filter_by(username='student').first()
            if student:
                cs101 = Course.query.filter_by(code='CS101').first()
                math201 = Course.query.filter_by(code='MATH201').first()
                if cs101 and math201:
                    grades = [
                        Grade(student_id=student.id, course_id=cs101.id, grade_value='A+', percentage=97.5, professor_id=prof.id),
                        Grade(student_id=student.id, course_id=math201.id, grade_value='B', percentage=85.0, professor_id=prof.id),
                    ]
                    for grade in grades:
                        db.session.add(grade)
                    db.session.commit()


# Routes
@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        otp_code = request.form.get('otp_code')
        email = request.form.get('email')
        
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return render_template('login.html', error='User not found')
        
        # Verify email code if email was used
        if email:
            verification = EmailVerificationCode.query.filter_by(
                username=username,
                email=email,
                code=otp_code,
                used=False
            ).first()
            
            if verification and verification.expires_at > datetime.utcnow():
                # Mark code as used
                verification.used = True
                db.session.commit()
                
                login_user(user)
                log_login_attempt(username, 'email', 'success', user.id)
                session['auth_method'] = 'email'
                session['login_time'] = datetime.utcnow().isoformat()
                session['user_role'] = user.role  # Store role in session
                
                # Redirect to role-specific dashboard
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'professor':
                    return redirect(url_for('professor_dashboard'))
                else:
                    return redirect(url_for('student_dashboard'))
            else:
                log_login_attempt(username, 'email', 'failed')
                return render_template('login.html', error='Invalid or expired verification code')
        else:
            # Fallback to TOTP if no email
            if user and user.verify_otp(otp_code):
                login_user(user)
                log_login_attempt(username, 'otp', 'success', user.id)
                session['auth_method'] = 'otp'
                session['login_time'] = datetime.utcnow().isoformat()
                session['user_role'] = user.role  # Store role in session
                
                # Redirect to role-specific dashboard
                if user.role == 'admin':
                    return redirect(url_for('admin_dashboard'))
                elif user.role == 'professor':
                    return redirect(url_for('professor_dashboard'))
                else:
                    return redirect(url_for('student_dashboard'))
            else:
                log_login_attempt(username, 'otp', 'failed')
                return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@app.route('/api/send-email-code', methods=['POST'])
def send_email_code_route():
    """API endpoint to send email verification code"""
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    
    if not username or not email:
        return jsonify({'success': False, 'error': 'Username and email are required'}), 400
    
    # Check if user exists
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Remove email validation - send to any email entered in the form
    # The email will be sent to the email address provided in the form input
    
    # Generate verification code
    code = generate_verification_code()
    expires_at = datetime.utcnow() + timedelta(minutes=10)
    
    # Save verification code with the email from the form
    verification = EmailVerificationCode(
        username=username,
        email=email,  # Use the email from the form input
        code=code,
        expires_at=expires_at
    )
    db.session.add(verification)
    db.session.commit()
    
    # Send email to the email address entered in the form
    try:
        result = send_email_code(email, code, username)  # Send to the email from form input
        if result:
            return jsonify({'success': True, 'message': f'Code sent successfully to {email}'})
        else:
            return jsonify({'success': False, 'error': 'Email service returned False'}), 500
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"❌ Error sending email: {error_details}")
        return jsonify({'success': False, 'error': f'Failed to send email: {str(e)}'}), 500


@app.route('/api/biometric-login', methods=['POST'])
def biometric_login():
    """Simulated biometric authentication"""
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'success': False, 'error': 'Username is required'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Simulate biometric authentication (always succeeds for demo)
    login_user(user)
    log_login_attempt(username, 'biometric', 'success', user.id)
    session['auth_method'] = 'biometric'
    session['login_time'] = datetime.utcnow().isoformat()
    session['user_role'] = user.role  # Store role in session
    
    # Determine redirect URL based on role
    if user.role == 'admin':
        redirect_url = url_for('admin_dashboard')
    elif user.role == 'professor':
        redirect_url = url_for('professor_dashboard')
    else:
        redirect_url = url_for('student_dashboard')
    
    return jsonify({'success': True, 'message': 'Biometric authentication successful', 'redirect': redirect_url})


@app.route('/api/rfid-login', methods=['POST'])
def rfid_login():
    """Simulated RFID card authentication"""
    data = request.get_json()
    username = data.get('username')
    
    if not username:
        return jsonify({'success': False, 'error': 'Username is required'}), 400
    
    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404
    
    # Simulate RFID authentication (always succeeds for demo)
    login_user(user)
    log_login_attempt(username, 'rfid', 'success', user.id)
    session['auth_method'] = 'rfid'
    session['login_time'] = datetime.utcnow().isoformat()
    session['user_role'] = user.role  # Store role in session
    
    # Determine redirect URL based on role
    if user.role == 'admin':
        redirect_url = url_for('admin_dashboard')
    elif user.role == 'professor':
        redirect_url = url_for('professor_dashboard')
    else:
        redirect_url = url_for('student_dashboard')
    
    return jsonify({'success': True, 'message': 'RFID authentication successful', 'redirect': redirect_url})


@app.route('/dashboard')
@login_required
def dashboard():
    """Redirect to role-specific dashboard"""
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif current_user.role == 'professor':
        return redirect(url_for('professor_dashboard'))
    else:
        return redirect(url_for('student_dashboard'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard - only accessible to admin username"""
    if current_user.username != 'admin' or current_user.role != 'admin':
        return "Access Denied. Only admin username can access this page.", 403
    
    user_data = {
        'username': current_user.username,
        'role': current_user.role,
        'login_time': session.get('login_time', 'Now')
    }
    
    # Admin can see all login attempts
    from models import LoginAttempt
    user_data['total_logins'] = LoginAttempt.query.filter_by(status='success').count()
    user_data['recent_logins'] = LoginAttempt.query.filter_by(status='success').order_by(LoginAttempt.timestamp.desc()).limit(5).all()
    user_data['total_users'] = User.query.count()
    
    return render_template('dashboards/admin_dashboard.html', data=user_data)


@app.route('/professor/dashboard')
@login_required
@role_required('professor')
def professor_dashboard():
    """Professor dashboard"""
    user_data = {
        'username': current_user.username,
        'role': current_user.role,
        'login_time': session.get('login_time', 'Now')
    }
    
    # Professor's courses and students
    user_data['courses'] = Course.query.filter_by(professor_id=current_user.id).all()
    user_data['total_students'] = db.session.query(Grade.student_id).filter_by(professor_id=current_user.id).distinct().count()
    user_data['recent_grades'] = Grade.query.filter_by(professor_id=current_user.id).order_by(Grade.created_at.desc()).limit(5).all()
    
    return render_template('dashboards/professor_dashboard.html', data=user_data)


@app.route('/student/dashboard')
@login_required
@role_required('student')
def student_dashboard():
    """Student dashboard"""
    user_data = {
        'username': current_user.username,
        'role': current_user.role,
        'login_time': session.get('login_time', 'Now')
    }
    
    # Student's grades and courses
    user_data['grades'] = Grade.query.filter_by(student_id=current_user.id).all()
    user_data['courses'] = [grade.course for grade in user_data['grades']]
    user_data['gpa'] = sum([g.percentage for g in user_data['grades']]) / len(user_data['grades']) if user_data['grades'] else 0
    user_data['recent_grades'] = user_data['grades'][:5] if user_data['grades'] else []
    
    return render_template('dashboards/student_dashboard.html', data=user_data)


@app.route('/admin')
@login_required
def admin():
    """Admin panel - only accessible to admin users with username 'admin'"""
    if current_user.username != 'admin' or current_user.role != 'admin':
        return "Access Denied. Only admin username can access this page.", 403
    users = User.query.all()
    from models import LoginAttempt
    all_logins = LoginAttempt.query.filter_by(status='success').order_by(LoginAttempt.timestamp.desc()).limit(100).all()
    return render_template('admin.html', users=users, login_logs=all_logins)


@app.route('/admin/manage-users')
@login_required
def manage_users():
    """Manage users - add, edit, delete (admin only)"""
    if current_user.username != 'admin' or current_user.role != 'admin':
        return "Access Denied", 403
    users = User.query.all()
    return render_template('manage_users.html', users=users)


@app.route('/admin/add-user', methods=['POST'])
@login_required
def add_user():
    """Add new user (admin only)"""
    if current_user.username != 'admin' or current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    data = request.get_json()
    username = data.get('username')
    role = data.get('role', 'student')
    
    if User.query.filter_by(username=username).first():
        return jsonify({'success': False, 'error': 'Username already exists'}), 400
    
    # Email is not stored - only username is used for authentication
    user = User(username=username, role=role)
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'User {username} created successfully'})


@app.route('/admin/edit-user/<int:user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    """Edit user (admin only)"""
    if current_user.username != 'admin' or current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Email is not stored - only role can be updated
    if 'role' in data:
        user.role = data['role']
    
    db.session.commit()
    return jsonify({'success': True, 'message': f'User {user.username} updated successfully'})


@app.route('/admin/delete-user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete user (admin only)"""
    if current_user.username != 'admin' or current_user.role != 'admin':
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    if user_id == current_user.id:
        return jsonify({'success': False, 'error': 'Cannot delete your own account'}), 400
    
    user = User.query.get_or_404(user_id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'User {username} deleted successfully'})


@app.route('/admin/login-logs')
@login_required
def login_logs():
    """View all login logs (admin only)"""
    if current_user.username != 'admin' or current_user.role != 'admin':
        return "Access Denied", 403
    from models import LoginAttempt
    logs = LoginAttempt.query.order_by(LoginAttempt.timestamp.desc()).limit(200).all()
    return render_template('login_logs.html', logs=logs)


@app.route('/admin/grades')
@login_required
def admin_grades():
    """Admin grades management (admin only)"""
    if current_user.username != 'admin' or current_user.role != 'admin':
        return "Access Denied", 403
    grades = Grade.query.order_by(Grade.created_at.desc()).all()
    courses = Course.query.all()
    students = User.query.filter_by(role='student').all()
    return render_template('admin_grades.html', grades=grades, courses=courses, students=students)


@app.route('/professor/courses')
@login_required
@role_required('professor')
def professor_courses():
    """Professor's courses management"""
    courses = Course.query.filter_by(professor_id=current_user.id).all()
    return render_template('professor_courses.html', courses=courses)


@app.route('/professor/add-course', methods=['POST'])
@login_required
@role_required('professor')
def add_course():
    """Add new course (professor only)"""
    data = request.get_json()
    code = data.get('code')
    name = data.get('name')
    
    if Course.query.filter_by(code=code).first():
        return jsonify({'success': False, 'error': 'Course code already exists'}), 400
    
    course = Course(code=code, name=name, professor_id=current_user.id)
    db.session.add(course)
    db.session.commit()
    
    return jsonify({'success': True, 'message': f'Course {code} created successfully'})


@app.route('/professor/give-grades')
@login_required
@role_required('professor')
def give_grades():
    """Give grades to students (professor only)"""
    courses = Course.query.filter_by(professor_id=current_user.id).all()
    students = User.query.filter_by(role='student').all()
    grades = Grade.query.filter_by(professor_id=current_user.id).order_by(Grade.created_at.desc()).all()
    return render_template('give_grades.html', courses=courses, students=students, grades=grades)


@app.route('/professor/submit-grade', methods=['POST'])
@login_required
@role_required('professor')
def submit_grade():
    """Submit a grade (professor only)"""
    data = request.get_json()
    student_id = data.get('student_id')
    course_id = data.get('course_id')
    grade_value = data.get('grade_value')
    percentage = data.get('percentage')
    
    # Verify course belongs to professor
    course = Course.query.get_or_404(course_id)
    if course.professor_id != current_user.id:
        return jsonify({'success': False, 'error': 'Access Denied'}), 403
    
    # Check if grade exists, update or create
    existing_grade = Grade.query.filter_by(student_id=student_id, course_id=course_id).first()
    if existing_grade:
        existing_grade.grade_value = grade_value
        existing_grade.percentage = percentage
        existing_grade.updated_at = datetime.utcnow()
    else:
        grade = Grade(
            student_id=student_id,
            course_id=course_id,
            grade_value=grade_value,
            percentage=percentage,
            professor_id=current_user.id
        )
        db.session.add(grade)
    
    db.session.commit()
    return jsonify({'success': True, 'message': 'Grade submitted successfully'})


@app.route('/student/grades')
@login_required
@role_required('student')
def student_grades():
    """View grades (student only)"""
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    gpa = sum([g.percentage for g in grades]) / len(grades) if grades else 0
    return render_template('student_grades.html', grades=grades, gpa=gpa)


@app.route('/student/courses')
@login_required
@role_required('student')
def student_courses():
    """View enrolled courses (student only)"""
    grades = Grade.query.filter_by(student_id=current_user.id).all()
    courses = [grade.course for grade in grades]
    return render_template('student_courses.html', courses=courses)


@app.route('/report-issue')
@login_required
def report_issue():
    """Report an issue page"""
    return render_template('report_issue.html')


@app.route('/security-guidelines')
@login_required
def security_guidelines():
    """Security guidelines page"""
    return render_template('security_guidelines.html')


@app.route('/recent-activity')
@login_required
def recent_activity():
    """Recent activity page"""
    from models import LoginAttempt
    from flask import request
    from datetime import datetime
    
    # Get recent login attempts
    recent_attempts = LoginAttempt.query.filter_by(user_id=current_user.id).order_by(LoginAttempt.timestamp.desc()).limit(20).all()
    
    # Add current session info
    current_session = {
        'method': session.get('auth_method', 'unknown'),
        'ip_address': request.remote_addr,
        'timestamp': datetime.utcnow(),
        'status': 'success',
        'user_agent': request.headers.get('User-Agent', 'Unknown')
    }
    
    return render_template('recent_activity.html', 
                        activities=recent_attempts,
                        current_session=current_session)


@app.route('/device-security')
@login_required
def device_security():
    """Device security page"""
    from auth import get_active_sessions
    active_sessions = get_active_sessions()
    user_sessions = [s for s in active_sessions if s.user_id == current_user.id]
    
    return render_template('device_security.html', devices=user_sessions)


@app.route('/account-protection')
@login_required
def account_protection():
    """Account protection level page"""
    return render_template('account_protection.html')


@app.route('/access-history')
@login_required
def access_history():
    """View access history page"""
    from auth import get_active_sessions
    from models import LoginAttempt
    
    login_attempts = LoginAttempt.query.filter_by(user_id=current_user.id).order_by(LoginAttempt.timestamp.desc()).limit(50).all()
    active_sessions = get_active_sessions()
    user_sessions = [s for s in active_sessions if s.user_id == current_user.id]
    
    return render_template('access_history.html', 
                        login_attempts=login_attempts,
                        active_sessions=user_sessions)


@app.route('/generate-code')
@login_required
def generate_code():
    """Generate random passcode page"""
    return render_template('generate_code.html')


@app.route('/api/generate-passcode', methods=['POST'])
@login_required
def generate_passcode_api():
    """API endpoint to generate a random passcode"""
    import secrets
    import string
    
    data = request.get_json()
    length = data.get('length', 12)
    include_symbols = data.get('include_symbols', False)
    
    # Generate random passcode
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    passcode = ''.join(secrets.choice(characters) for _ in range(length))
    
    return jsonify({
        'success': True,
        'passcode': passcode,
        'length': length,
        'timestamp': datetime.utcnow().isoformat()
    })


@app.route('/verify-role')
@login_required
def verify_role():
    """API endpoint to verify user's role"""
    return jsonify({
        'username': current_user.username,
        'role': current_user.role,
        'is_admin': current_user.role == 'admin',
        'is_professor': current_user.role == 'professor',
        'is_student': current_user.role == 'student'
    })


@app.route('/api/check-role/<username>')
@login_required
def check_role(username):
    """API endpoint to check a user's role by username (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Access denied. Admin only.'}), 403
    
    role = get_user_role(username)
    if role:
        return jsonify({
            'username': username,
            'role': role,
            'exists': True
        })
    else:
        return jsonify({
            'username': username,
            'exists': False
        }), 404




@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


# API Routes
@app.route('/api/user-info')
@login_required
def user_info():
    return jsonify({
        'username': current_user.username,
        'role': current_user.role,
        'email': current_user.email
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_sample_data()
    
    port = int(os.environ.get("PORT", 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

