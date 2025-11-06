#!/usr/bin/env python3
"""
Database migration script to update existing database with new schema
Run this once to update existing databases
"""
from app import app
from models import db

with app.app_context():
    print("Updating database schema...")
    db.create_all()
    print(" Database schema updated successfully!")
    print("\nNew features added:")
    print("  - Phone number field for users")
    print("  - SMS verification code table")

