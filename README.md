#  CAMPUSKEY

Secure University Access System with Multi-Factor Authentication

## Features

- **SMS-based OTP authentication** - Receive verification codes via SMS
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

## SMS Authentication

### Testing Mode (Default)

By default, SMS codes are printed to the console instead of being sent via SMS. This is perfect for development:

1. Enter your username and phone number on the login page
2. Click "Send Code"
3. Check your terminal/console where Flask is running - you'll see the code printed there
4. Enter the code to log in

### Production Setup with Twilio

To enable real SMS sending:

1. Sign up for Twilio (https://www.twilio.com)
2. Get your credentials: Account SID, Auth Token, and Phone Number
3. Set environment variables:
   ```bash
   export TWILIO_ACCOUNT_SID="your_account_sid"
   export TWILIO_AUTH_TOKEN="your_auth_token"
   export TWILIO_PHONE_NUMBER="+1234567890"
   ```
4. Restart the application

**Phone Number Format:** Use E.164 format (e.g., `+1234567890`)

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

