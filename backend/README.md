# CampusKey Backend

Backend API server for CampusKey - Biometric & RFID Authentication System.

## Project Structure

```
backend/
├── main.py                          # Main FastAPI application entry point
├── requirements.txt                 # Python dependencies list
├── campuskey.db                    # SQLite database file (created at runtime)
├── models/                         # Data models and schemas
│   ├── user_models.py              # User-related data models
│   └── auth_models.py              # Authentication-related data models
├── services/                       # Business logic and service layer
│   ├── biometric_service.py        # Face recognition and biometric authentication
│   ├── email_service.py            # Email sending functionality (password recovery)
│   ├── rfid_service.py             # RFID/NFC card reading and validation
│   └── code_generator.py           # One-time code generation for 2FA
└── routes/                         # API route handlers
    ├── auth_routes.py              # Authentication endpoints (login, register, etc.)
    ├── biometric_routes.py          # Biometric authentication endpoints
    └── rfid_routes.py              # RFID authentication endpoints
```

## Setup Instructions

### 1. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Mac/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the backend directory for environment variables:

```env
# Database
DATABASE_URL=sqlite:///./campuskey.db

# JWT Secret Key (generate a secure random string)
SECRET_KEY=your-secret-key-here

# Email Configuration (for password recovery)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Run the Server

```bash
# Run development server
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://0.0.0.0:8000`

## API Endpoints

### Authentication Routes (`/auth`)
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with username/password
- `POST /auth/logout` - Logout current user
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

### Biometric Routes (`/biometric`)
- `POST /biometric/enroll` - Enroll user face for recognition
- `POST /biometric/verify` - Verify user identity using face
- `GET /biometric/status` - Check enrollment status

### RFID Routes (`/rfid`)
- `POST /rfid/register` - Register RFID card for user
- `POST /rfid/verify` - Verify RFID card
- `GET /rfid/cards` - List registered RFID cards

## Database

The application uses SQLite database (`campuskey.db`) which is automatically created on first run.

## Security Features

- JWT token-based authentication
- Password hashing with bcrypt
- Face recognition for biometric authentication
- RFID card validation
- Secure email verification for password recovery

## Development Notes

- Database file (`campuskey.db`) is created automatically
- All sensitive data should be stored in `.env` file
- Use `python-decouple` to load environment variables
- Face recognition models are loaded at startup

## Testing

```bash
# Run tests (when implemented)
pytest

# Run with coverage
pytest --cov=.
```

## Dependencies

See `requirements.txt` for complete list of Python packages required.

---

**Built for Fake University**

