from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    biometric_data = db.Column(db.String(255), nullable=True)
    
    # Relationships
    access_logs = db.relationship('AccessLog', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class AccessLog(db.Model):
    __tablename__ = 'access_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    access_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Boolean, default=True)
    notes = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f'<AccessLog {self.id} - User {self.user_id}>'

