from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime
from config import Config
from models import db, User, AccessLog
from auth import auth_bp

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Admin access required', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('auth.login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', user=user)

@app.route('/history')
@login_required
def history():
    user = User.query.get(session['user_id'])
    logs = AccessLog.query.filter_by(user_id=user.id).order_by(AccessLog.timestamp.desc()).limit(50).all()
    return render_template('history.html', logs=logs)

@app.route('/profile')
@login_required
def profile():
    user = User.query.get(session['user_id'])
    return render_template('profile.html', user=user)

@app.route('/admin')
@admin_required
def admin():
    users = User.query.all()
    logs = AccessLog.query.order_by(AccessLog.timestamp.desc()).limit(100).all()
    return render_template('admin.html', users=users, logs=logs)

@app.route('/biometric')
@login_required
def biometric():
    return render_template('biometric.html')

@app.route('/api/access', methods=['POST'])
@login_required
def record_access():
    data = request.json
    log = AccessLog(
        user_id=session['user_id'],
        access_type=data.get('type', 'unknown'),
        location=data.get('location', 'unknown'),
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

