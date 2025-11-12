# CAMPUSKEY

**Secure University Access System with Multi-Factor Authentication**

A modern, secure access management system for universities featuring email-based authentication, biometric login, role-based access control, and comprehensive security features.

---

## Features

- **Email-based OTP Authentication** - Secure login via email verification codes
- **Multi-Factor Authentication** - Support for TOTP authenticator apps (Google Authenticator, Authy)
- **Biometric Authentication** - Face ID / Touch ID support via WebAuthn
- **RFID Card Support** - Physical card-based authentication
- **Role-Based Access Control** - Admin, Professor, and Student roles with different permissions
- **Academic Management** - Course management, grade tracking, and student enrollment
- **Security Features** - Login attempt tracking, session management, device fingerprinting
- **Modern UI** - Beautiful, responsive design with glassmorphism effects
- **Timezone-Aware** - Works correctly for users in any timezone (UTC-based)

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CampusKey
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Access the application**
   - Open your browser and navigate to: `http://localhost:5001`
   - Note: Port 5001 is used because macOS AirPlay uses port 5000

---

## Demo Users

The system automatically creates three demo users when you first run the application. You can use any of these to log in:

| Username | Role | Access Level |
|----------|------|--------------|
| `admin` | Admin | Full system access - manage users, view all logs, system administration |
| `professor` | Professor | Manage courses, assign grades to students, view student information |
| `student` | Student | View own grades, enrolled courses, and academic information |

---

## How to Login

### Email-Based Authentication (Recommended)

1. **Enter Username**
   - Type one of the demo usernames: `admin`, `professor`, or `student`

2. **Enter Email Address**
   - Enter any valid email address (e.g., `yourname@example.com`)
   - The email doesn't need to match the username - it's just used to send the verification code

3. **Get Verification Code**
   - Click the **"Send Code"** button
   - **In Development**: The verification code will be printed in your terminal/console where Flask is running
   - **In Production**: The code will be sent to the email address you provided
   - Codes expire after 10 minutes

4. **Enter Code and Login**
   - Enter the 6-digit verification code you received
   - Click **"LOGIN"** button
   - You'll be redirected to your role-specific dashboard

### Alternative Authentication Methods

- **Biometric Login** (Face ID / Touch ID): Click "Face ID / Touch ID" button after entering username
  - Note: You must first register your biometric on the dashboard after logging in with email
  
- **RFID Card**: Click "RFID Card" button after entering username
  - Simulates RFID card authentication for testing

---

## Project Structure

```
CampusKey/
├── app.py                  # Main Flask application and routes
├── config.py               # Application configuration (database, secrets)
├── models.py               # Database models (User, Course, Grade, etc.)
├── auth.py                 # Authentication utilities and security functions
├── email_service.py        # Email sending service (SendGrid, SMTP)
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python version specification
├── Procfile                # Process file for deployment
├── static/                 # Static files
│   ├── css/
│   │   └── style.css      # Modern UI styles
│   └── js/
│       └── webauthn.js    # WebAuthn/biometric authentication
├── templates/              # HTML templates
│   ├── base.html          # Base template
│   ├── login.html         # Login page
│   └── dashboards/        # Role-specific dashboards
│       ├── admin_dashboard.html
│       ├── professor_dashboard.html
│       └── student_dashboard.html
└── instance/              # Database files (created automatically)
    └── campuskey.db       # SQLite database (local development)
```

---

## Key Features Explained

### Role-Based Dashboards

- **Admin Dashboard**: 
  - User management (create, edit, delete users)
  - View all login attempts and security logs
  - System-wide statistics and monitoring

- **Professor Dashboard**:
  - Create and manage courses
  - Assign grades to students
  - View enrolled students and their progress

- **Student Dashboard**:
  - View personal grades and GPA
  - See enrolled courses and course information
  - Access professor contact information

### Security Features

- **Login Attempt Tracking**: All login attempts are logged with IP address, timestamp, and status
- **Session Management**: Active sessions are tracked and expire after 2 hours of inactivity
- **Device Fingerprinting**: Tracks and identifies devices for security monitoring
- **Email Verification**: One-time codes expire after 10 minutes for security
- **UTC Timezone**: All timestamps use UTC to work correctly for users worldwide

---

## Development

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Run the application
python app.py
```

### Database

- **Local Development**: Uses SQLite database (`instance/campuskey.db`)
- **Production**: Automatically uses PostgreSQL when `DATABASE_URL` environment variable is set
- Tables are created automatically on first run
- Sample data (users, courses, grades) is created if database is empty

### Email Configuration

For production email sending, configure these environment variables:

- `EMAIL_SERVICE`: `sendgrid` or `smtp`
- `SENDGRID_API_KEY`: Your SendGrid API key (if using SendGrid)
- `SMTP_USERNAME`: SMTP username (if using SMTP)
- `SMTP_PASSWORD`: SMTP password (if using SMTP)
- `SMTP_HOST`: SMTP server hostname
- `SMTP_PORT`: SMTP server port

**Note**: In development mode, verification codes are printed to the console for easy testing.

---

## Technologies Used

- **Backend**: Flask (Python web framework)
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Flask-Login, WebAuthn, pyotp
- **Frontend**: HTML5, CSS3 (Modern design with glassmorphism)
- **Security**: Cryptography, device fingerprinting, session management

---

## Security Notes

- Change the default `SECRET_KEY` in production (set via `SECRET_KEY` environment variable)
- Use environment variables for all sensitive configuration
- Enable HTTPS in production environments
- Regularly review login attempt logs for suspicious activity
- Verification codes expire after 10 minutes for security

---

## License

This project is part of the CampusKey University Access System.

---

## Contributing

This is a university project. For questions or issues, please contact the development team.

---

## Additional Documentation

- **Deployment Guide**: See `RENDER_DEPLOYMENT.md` for deploying to Render
- **Database Setup**: See `RENDER_DATABASE_SETUP.md` for PostgreSQL configuration
- **Email Configuration**: See `CHECK_EMAIL_CONFIG.md` for email setup details

---

**Made for secure university access management**
