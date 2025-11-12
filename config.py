# ------------------------------------------------------------------------------------
# config.py
#
# Copyright (c) 2025 CampusKey. All rights reserved
# Description:
# This Python code is part of a software application developed for CampusKey
# University Access System. It includes functionality for application configuration
# settings including database connection, secret keys, and environment variables.
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
#    app.py - Main Flask application that uses this configuration
#    models.py - Database models that use database configuration
#
# ------------------------------------------------------------------------------------

# Python import statement: Imports the os module for accessing environment variables
# os.environ allows reading configuration values from system environment variables
# This is a security best practice - keeps sensitive data out of source code
import os


# Python class definition: Config class holds all Flask application configuration settings
# This class is used by Flask's config.from_object() method to load settings
class Config:
    # Class variable: SECRET_KEY is used by Flask for session management and CSRF protection
    # os.environ.get() reads from environment variable, with fallback to default dev key
    # In production, SECRET_KEY should be set as environment variable for security
    SECRET_KEY = os.environ.get('SECRET_KEY', 'campuskey-dev-secret-2025')
    
    # Class variable: DATABASE_URL stores the database connection string
    # Reads from environment variable DATABASE_URL (set by hosting platforms like Render)
    # If not set, defaults to SQLite for local development
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    # Python conditional: Checks if DATABASE_URL exists and uses PostgreSQL protocol
    # Render and other platforms provide PostgreSQL databases with 'postgres://' prefix
    if DATABASE_URL and DATABASE_URL.startswith('postgres'):
        # SQLAlchemy requires 'postgresql://' instead of 'postgres://' (legacy compatibility fix)
        # .replace() converts the URL format to work with SQLAlchemy
        SQLALCHEMY_DATABASE_URI = DATABASE_URL.replace('postgres://', 'postgresql://')
    else:
        # Python else clause: Fallback to SQLite for local development
        # SQLite is a file-based database, perfect for development and testing
        # 'sqlite:///campuskey.db' creates database file in instance/ directory
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///campuskey.db')
    
    # Class variable: Disables SQLAlchemy event system tracking modifications
    # Setting to False improves performance by not tracking every model change
    # This is recommended by Flask-SQLAlchemy documentation for better performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Class variable: Enable connection pooling for PostgreSQL (important for Render)
    # These settings optimize database connections for production use
    # Only apply to PostgreSQL, not SQLite
    if DATABASE_URL and DATABASE_URL.startswith('postgres'):
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 5,           # Number of connections to keep in the pool
            'max_overflow': 10,       # Maximum connections beyond pool_size
            'pool_pre_ping': True,    # Test connections before using them (handles dropped connections)
            'pool_recycle': 3600,      # Recycle connections after 1 hour (prevents stale connections)
            'connect_args': {
                'connect_timeout': 10  # Connection timeout in seconds
            }
        }
    else:
        # No special engine options needed for SQLite
        SQLALCHEMY_ENGINE_OPTIONS = {}