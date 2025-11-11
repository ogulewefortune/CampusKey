#!/bin/bash
# Start CAMPUSKEY server with email configuration

cd "$(dirname "$0")"

# Load email configuration
source email_config.sh

# Use port 465 for SSL (more reliable)
export SMTP_PORT=465

# Enable Flask debug mode
export FLASK_DEBUG=True

# Activate virtual environment and start server
source venv/bin/activate
python app.py

