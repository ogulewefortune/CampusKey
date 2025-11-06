#  CAMPUSKEY

Secure University Access System with Multi-Factor Authentication

## Features

- **Email-based OTP authentication** - Receive verification codes via email
- OTP-based authentication (TOTP authenticator apps)
- Role-based access control (Admin, Professor, Student)
- Session management
- Login attempt tracking
- Modern, responsive UI

## Quick Start

### 1. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Application

```bash
python app.py
```

### 4. Access Application

Open your browser and go to: `http://localhost:5001`

Note: Port 5001 is used because macOS AirPlay uses port 5000.

## Demo Users

The system creates sample users automatically:

- **Admin**: username: `admin`, email: `admin@campuskey.edu`
- **Professor**: username: `professor`, email: `prof@campuskey.edu`
- **Student**: username: `student`, email: `student@campuskey.edu`

## Email Authentication

### How It Works

1. Enter your username and email address on the login page
2. Click "Send Code"
3. Check your email or terminal/console where Flask is running - you'll see the code printed there
4. Enter the code to log in

**Note:** In development mode, verification codes are printed to the console. Configure email settings in `email_service.py` for production email sending.

## Getting TOTP Codes

For TOTP authenticator app codes, use the helper script:

```bash
python get_otp_codes.py
```

## Project Structure

```
campuskey/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── models.py           # Database models
├── auth.py             # Authentication utilities
├── requirements.txt    # Python dependencies
├── runtime.txt         # Python version for deployment
├── static/            # Static files (CSS, JS, images)
└── templates/         # HTML templates
```

## Deployment

For deployment on Render or similar platforms:

1. Set environment variables:
   - `SECRET_KEY`: A secure secret key
   - `DATABASE_URL`: PostgreSQL connection string (if using PostgreSQL)

2. The application will automatically detect the platform and configure accordingly.

## Security Notes

- Change the default `SECRET_KEY` in production
- Use environment variables for sensitive data
- Enable HTTPS in production
- Regularly rotate OTP secrets

