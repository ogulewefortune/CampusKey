# ------------------------------------------------------------------------------------
# migrate_db.py
#
# Copyright (c) 2025 CampusKey. All rights reserved
# Description:
# This Python code is part of a software application developed for CampusKey
# University Access System. It includes functionality for database migration
# and schema updates, creating all necessary database tables.
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
#    app.py - Main Flask application that provides application context
#    models.py - Database models that define the schema
#    config.py - Configuration settings for database connection
#
# ------------------------------------------------------------------------------------

# Shebang line: Tells the system to use Python 3 interpreter when script is executed directly
# Allows running script with ./migrate_db.py instead of python3 migrate_db.py
#!/usr/bin/env python3

# Python docstring: Multi-line string documenting what this script does
# Docstrings are used for documentation and help text
"""
Database migration script to update existing database with new schema
Run this once to update existing databases
"""

# Python import statement: Imports the Flask app instance from app.py
# app instance is needed to access Flask application context
from app import app

# Python import statement: Imports db (SQLAlchemy instance) from models.py
# db is the database object that handles all database operations
from models import db

# Python context manager: Creates Flask application context
# app.app_context() is required to access database outside of request handlers
# This allows running database operations in standalone scripts
with app.app_context():
    # Python print statement: Outputs status message to console
    # Informs user that database migration is starting
    print("Updating database schema...")
    
    # Database method: Creates all database tables defined in models
    # db.create_all() reads model definitions and creates missing tables
    # Safe to run multiple times - only creates tables that don't exist
    db.create_all()
    
    # Python print statement: Outputs success message with checkmark emoji
    # Confirms that database schema update completed successfully
    print("✓ Database schema updated successfully!")
