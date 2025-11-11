# ------------------------------------------------------------------------------------
# auth.py
#
# Copyright (c) 2025 CampusKey. All rights reserved
# Description:
# This Python code is part of a software application developed for CampusKey
# University Access System. It includes functionality for authentication utilities
# including login attempt logging, role-based access control, and user management.
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
#    app.py - Main Flask application that uses these authentication utilities
#    models.py - Database models used for authentication
#
# ------------------------------------------------------------------------------------

# Python import statement: Imports Flask request, session, and abort utilities
# request: Access HTTP request data
# session: Server-side session storage
# abort: Raise HTTP exceptions
from flask import request, session, abort

# Python import statement: Imports wraps decorator from functools
# wraps: Preserves function metadata when creating decorators
from functools import wraps

# Python import statement: Imports current_user from Flask-Login
# current_user: Proxy object representing logged-in user
from flask_login import current_user

# Python import statement: Imports database models and db instance
# LoginAttempt: Model for logging login attempts
# ActiveSession: Model for tracking active user sessions
# User: User model for authentication
# db: SQLAlchemy database instance
from models import LoginAttempt, ActiveSession, User, db

# Python import statement: Imports datetime and timedelta classes
# datetime: For creating timestamps
# timedelta: For calculating time differences
from datetime import datetime, timedelta

# Python import statement: Imports pytz module for timezone handling
# pytz: Provides timezone-aware datetime objects
import pytz

# EST timezone constant: US Eastern timezone for logging and time calculations
# EST: Eastern Standard Time timezone object
EST = pytz.timezone('US/Eastern')


def normalize_username(username):
    """
    Normalize username to lowercase.
    This ensures case-insensitive username matching.
    
    Args:
        username: Username string (can be None)
    
    Returns:
        Lowercase username string, or None if input is None
    """
    if username is None:
        return None
    return username.lower().strip()


def get_est_time():
    """
    Get current time in EST timezone.
    
    Returns:
        datetime object in EST timezone
    """
    return datetime.now(EST)


def log_login_attempt(username, method, status, user_id=None):
    """
    Log a login attempt to the database.
    
    Args:
        username: Username that attempted login
        method: Authentication method used ('otp', 'email', 'biometric', 'rfid', 'password')
        status: 'success' or 'failed'
        user_id: User ID if user exists, None for failed attempts with non-existent users
    """
    try:
        # Get IP address and user agent from request if available
        ip_address = request.remote_addr if request else None
        user_agent = request.headers.get('User-Agent') if request else None
        
        # Normalize username to lowercase
        normalized_username = normalize_username(username)
        
        # Create login attempt record using SQLAlchemy
        login_attempt = LoginAttempt(
            username=normalized_username,
            method=method,
            status=status,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=get_est_time()
        )
        
        db.session.add(login_attempt)
        db.session.commit()
    except Exception as e:
        # Log error but don't break the application
        print(f"Error logging login attempt: {e}")
        db.session.rollback()



def track_session_activity(user_id, session_id):
    """
    Track or update active session activity.
    Creates new session if it doesn't exist, or updates last_activity timestamp.
    
    Args:
        user_id: User ID for the session
        session_id: Flask session ID
    """
    try:
        # Check if session exists
        active_session = ActiveSession.query.filter_by(session_id=session_id).first()
        
        if active_session is None:
            # Session does not exist - create new one
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            
            active_session = ActiveSession(
                user_id=user_id,
                session_id=session_id,
                login_time=get_est_time(),
                last_activity=get_est_time(),
                ip_address=ip_address,
                user_agent=user_agent
            )
            db.session.add(active_session)
        else:
            # Session exists - update last_activity timestamp
            active_session.last_activity = get_est_time()
        
        db.session.commit()
    except Exception as e:
        print(f"Error tracking session activity: {e}")
        db.session.rollback()

def get_active_sessions():
    """
    Get all active sessions, removing expired ones.
    Sessions expire after 2 hours of inactivity.
    
    Returns:
        List of ActiveSession objects that are still active
    """
    try:
        # Calculate expiration time (2 hours ago) in EST
        expiration_time = get_est_time() - timedelta(hours=2)
        
        # Find and delete expired sessions
        expired_sessions = ActiveSession.query.filter(
            ActiveSession.last_activity < expiration_time
        ).all()
        
        for session in expired_sessions:
            db.session.delete(session)
        
        db.session.commit()
        
        # Return all remaining active sessions
        return ActiveSession.query.all()
    except Exception as e:
        print(f"Error getting active sessions: {e}")
        db.session.rollback()
        return []

# decorator functions to ensure proper role authentication
def role_required(*roles):
    def decorator(func):
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if not current_user or not current_user.is_authenticated:
                    abort(403)
                if current_user.role not in roles:
                    abort(403)
                return func(*args, **kwargs)
            except AttributeError:
                abort(403)
        return wrapper
    return decorator


def admin_required(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            if not current_user or not current_user.is_authenticated:
                abort(403)
            if current_user.role != 'admin':
                abort(403)
            return func(*args, **kwargs)
        except AttributeError:
            abort(403)
    return wrapper

# checks that user exists and has the expected role
def verify_user_role(username, expected_role):
    """
    Verify that a user exists and has the expected role.
    
    Args:
        username: Username to check
        expected_role: Expected role ('admin', 'professor', 'student')
    
    Returns:
        True if user exists and has expected role, False otherwise
    """
    try:
        # Normalize username to lowercase for case-insensitive lookup
        normalized_username = normalize_username(username)
        user = User.query.filter_by(username=normalized_username).first()
        
        if user is None:
            return False
        
        return user.role == expected_role
    except Exception as e:
        print(f"Error verifying user role: {e}")
        return False

def get_user_role(username):
    """
    Get the role of a user by username.
    
    Args:
        username: Username to look up
    
    Returns:
        User's role string if user exists, None otherwise
    """
    try:
        # Normalize username to lowercase for case-insensitive lookup
        normalized_username = normalize_username(username)
        user = User.query.filter_by(username=normalized_username).first()
        
        if user is None:
            return None
        
        return user.role
    except Exception as e:
        print(f"Error getting user role: {e}")
        return None


