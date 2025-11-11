# Python import statement: Imports random module for generating random numbers
# Used to create random verification codes
import random

# Python import statement: Imports string module for string constants
# string.digits provides '0123456789' for generating numeric codes
import string

# Python import statement: Imports datetime and timedelta classes from datetime module
# datetime: Used for creating timestamps
# timedelta: Used for calculating time differences (e.g., code expiration)
from datetime import datetime, timedelta

# Python import statement: Imports os module for accessing environment variables
# Used to read SMTP configuration from system environment variables
import os

# Python import statement: Imports smtplib module for sending emails via SMTP protocol
# smtplib provides SMTP client functionality to send emails
import smtplib

# Python import statement: Imports MIMEText class for creating plain text email messages
# MIMEText is used to create email body content
from email.mime.text import MIMEText

# Python import statement: Imports MIMEMultipart class for creating multipart email messages
# MIMEMultipart allows combining HTML and plain text versions in one email
from email.mime.multipart import MIMEMultipart

# Python import statement: Imports Header class for properly encoding email headers
# Header handles UTF-8 encoding for non-ASCII characters in email subjects
from email.header import Header


# Python function definition: Function to generate a random 6-digit verification code
def generate_verification_code():
    # Python docstring: Documents what the function does
    """Generate a random 6-digit code"""
    # Python return statement: Returns a string of 6 random digits
    # random.choices() selects 6 random digits from string.digits
    # ''.join() concatenates the selected digits into a single string
    return ''.join(random.choices(string.digits, k=6))


# Python function definition: Function to send verification code via email
# Parameters: email_address (recipient), code (verification code), username (for personalization)
def send_email_code(email_address, code, username):
    # Python docstring: Documents function purpose and behavior
    """
    Send verification code via email.
    Uses SMTP if configured, otherwise prints to console for testing.
    """
    # Python comment: Marks email configuration section
    # Email configuration from environment variables
    # Python variable: Gets SMTP server address from environment variable
    # os.environ.get() reads env var with fallback to Gmail's SMTP server
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    
    # Python variable: Gets SMTP port number from environment variable
    # int() converts string to integer, defaults to 587 (TLS port)
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    
    # Python variable: Gets SMTP username (email address) from environment variable
    # None if not set - used to check if email is configured
    smtp_username = os.environ.get('SMTP_USERNAME')
    
    # Python variable: Gets SMTP password from environment variable
    # .replace('\xa0', ' ') removes non-breaking spaces that can cause login issues
    # .strip() removes leading/trailing whitespace
    smtp_password = os.environ.get('SMTP_PASSWORD', '').replace('\xa0', ' ').strip()  # Fix non-breaking spaces
    
    # Python variable: Gets sender email address from environment variable
    # Falls back to smtp_username if FROM_EMAIL not set
    from_email = os.environ.get('FROM_EMAIL', smtp_username)
    
    # Python variable: Sets email subject line
    # This appears in the recipient's email client
    subject = "CAMPUSKEY Verification Code"
    
    # Python comment: Marks HTML email template section
    # HTML email template matching Google style
    # Python f-string: Multi-line string with variable interpolation
    # f""" allows embedding {variables} in the HTML template
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Google Sans', Roboto, Arial, sans-serif; background-color: #202124; color: #e8eaed;">
        <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #202124; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="600" cellpadding="0" cellspacing="0" style="background-color: #202124; max-width: 600px;">
                        <!-- Blue Banner Header -->
                        <tr>
                            <td style="background-color: #1a73e8; padding: 24px 32px; text-align: center;">
                                <h1 style="margin: 0; color: #ffffff; font-size: 22px; font-weight: 400; letter-spacing: 0.25px;">CAMPUSKEY Verification Code</h1>
                            </td>
                        </tr>
                        
                        <!-- Email Body -->
                        <tr>
                            <td style="background-color: #202124; padding: 32px; color: #e8eaed; font-size: 14px; line-height: 20px;">
                                <p style="margin: 0 0 16px 0; color: #e8eaed;">Dear CAMPUSKEY User,</p>
                                
                                <p style="margin: 0 0 16px 0; color: #e8eaed;">
                                    We received a request to access your CAMPUSKEY Account
                                    <span style="color: #8ab4f8; text-decoration: underline;">{email_address}</span>
                                    through your email address. Your CAMPUSKEY verification code is:
                                </p>
                                
                                <!-- Verification Code Display -->
                                <div style="margin: 24px 0; text-align: center;">
                                    <div style="font-size: 36px; font-weight: 400; color: #e8eaed; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                                        {code}
                                    </div>
                                </div>
                                
                                <p style="margin: 16px 0; color: #e8eaed;">
                                    If you did not request this code, it is possible that someone else is trying to access the CAMPUSKEY Account
                                    <span style="color: #8ab4f8; text-decoration: underline;">{email_address}</span>.
                                    Do not forward or give this code to anyone.
                                </p>
                                
                                <p style="margin: 24px 0 0 0; color: #e8eaed;">Sincerely yours,</p>
                                <p style="margin: 4px 0 0 0; color: #e8eaed;">The CAMPUSKEY Security Team</p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding: 16px 32px; text-align: center;">
                                <p style="margin: 0; color: #9aa0a6; font-size: 12px; line-height: 16px;">
                                    This email can't receive replies. For more information, visit the
                                    <a href="#" style="color: #8ab4f8; text-decoration: underline;">CAMPUSKEY Help Center</a>.
                                </p>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    # Python comment: Marks plain text email version section
    # Plain text version for email clients that don't support HTML
    # Python f-string: Multi-line plain text email template
    # Plain text ensures email is readable even if HTML rendering fails
    text_body = f"""Dear CAMPUSKEY User,

We received a request to access your CAMPUSKEY Account {email_address} through your email address. Your CAMPUSKEY verification code is:

{code}

If you did not request this code, it is possible that someone else is trying to access the CAMPUSKEY Account {email_address}. Do not forward or give this code to anyone.

Sincerely yours,
The CAMPUSKEY Security Team

---
This email can't receive replies. For more information, visit the CAMPUSKEY Help Center.
        """
    
    # Python comment: Marks SMTP email sending section
    # If SMTP is configured, try to send email
    # Python conditional: Checks if both username and password are configured
    if smtp_username and smtp_password:
        # Python try block: Attempts to send email, catches exceptions
        try:
            # Python print statement: Outputs status message to console
            print(f"\n Attempting to send email...")
            # Python print statement: Displays sender email address
            print(f"   From: {from_email}")
            # Python print statement: Displays recipient email address
            print(f"   To: {email_address}")
            # Python print statement: Displays SMTP server and port
            print(f"   Server: {smtp_server}:{smtp_port}")
            
            # Python object creation: Creates multipart email message
            # 'alternative' allows both HTML and plain text versions
            msg = MIMEMultipart('alternative')
            # Python attribute assignment: Sets sender email address
            msg['From'] = from_email
            # Python attribute assignment: Sets recipient email address
            msg['To'] = email_address
            # Python attribute assignment: Sets email subject with UTF-8 encoding
            # Header() ensures proper encoding for special characters
            msg['Subject'] = Header(subject, 'utf-8')
            
            # Python comment: Marks email body attachment section
            # Add both plain text and HTML versions
            # Python object creation: Creates plain text email part
            # MIMEText() creates email body with specified content type and encoding
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            # Python object creation: Creates HTML email part
            part2 = MIMEText(html_body, 'html', 'utf-8')
            
            # Python method call: Attaches plain text version to email message
            msg.attach(part1)
            # Python method call: Attaches HTML version to email message
            msg.attach(part2)
            
            # Python object creation: Creates SMTP connection to email server
            # Try SSL connection first (port 465), then fall back to TLS (port 587)
            # This handles Render's network restrictions better
            server = None
            connection_error = None
            
            # Try connecting with the configured port
            try:
                if smtp_port == 465:
                    # Python object creation: Creates SSL SMTP connection for port 465
                    # smtplib.SMTP_SSL() creates encrypted connection directly
                    # timeout=10 sets 10-second timeout for connection (faster failure on cloud)
                    server = smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=10)
                    # Python method call: Authenticates with SMTP server using credentials
                    # login() sends username and password to server
                    server.login(smtp_username, smtp_password)
                else:
                    # Python object creation: Creates SMTP connection for TLS (port 587)
                    # smtplib.SMTP() connects to SMTP server on specified port
                    # timeout=10 sets 10-second timeout for connection (faster failure on cloud)
                    server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
                    # Python method call: Starts TLS encryption for secure connection
                    # starttls() upgrades connection to encrypted TLS
                    server.starttls()
                    # Python method call: Authenticates with SMTP server using credentials
                    # login() sends username and password to server
                    server.login(smtp_username, smtp_password)
            except (OSError, ConnectionError, TimeoutError, smtplib.SMTPException) as e:
                # Python comment: Catches network connection errors
                # If TLS port 587 fails, try SSL port 465 as fallback
                connection_error = e
                error_msg = str(e)
                print(f" Connection error on port {smtp_port}: {error_msg}")
                
                if smtp_port == 587:
                    # Python print statement: Logs fallback attempt
                    print(f" TLS connection failed, trying SSL on port 465...")
                    try:
                        # Python object creation: Retry with SSL connection
                        server = smtplib.SMTP_SSL(smtp_server, 465, timeout=10)
                        print(f" SSL connection established, authenticating...")
                        server.login(smtp_username, smtp_password)
                        # Python print statement: Logs successful fallback
                        print(f" SSL connection successful on port 465")
                    except Exception as ssl_error:
                        # Python raise statement: Re-raises with both errors
                        ssl_error_msg = str(ssl_error)
                        print(f" SSL fallback also failed: {ssl_error_msg}")
                        raise Exception(f"Both TLS (port 587) and SSL (port 465) connections failed. TLS error: {e}, SSL error: {ssl_error}")
                else:
                    # Python raise statement: Re-raises original error if not port 587
                    print(f" Connection failed on port {smtp_port}: {error_msg}")
                    raise
            # Python method call: Converts email message to string format
            # as_string() serializes the MIME message for sending
            text = msg.as_string()
            # Python method call: Sends email to recipient
            # sendmail() sends the email and returns dictionary of failed recipients
            # Empty dictionary {} means success, non-empty means some failures
            result = server.sendmail(from_email, [email_address], text)
            # Python method call: Closes SMTP connection
            # quit() properly closes the connection to the server
            server.quit()
            
            # Python conditional: Checks if email sending failed
            # result is empty dict {} on success, non-empty dict on failure
            if result:
                # Python variable: Creates error message string
                # f-string formats error message with result details
                error_msg = f"Email send failed: {result}"
                # Python print statement: Outputs error message
                print(f" {error_msg}")
                # Python raise statement: Raises exception to stop execution
                raise Exception(error_msg)
            else:
                # Python else clause: Executes if email sent successfully
                # Python print statement: Outputs success message
                print(f" Email sent successfully to {email_address}")
                # Python return statement: Returns True to indicate success
                return True
        # Python except clause: Catches SMTP-specific exceptions
        except smtplib.SMTPAuthenticationError as e:
            # Python variable: Creates error message with exception details
            error_msg = f"SMTP Authentication failed: {e}. Check your SMTP_USERNAME and SMTP_PASSWORD. For Gmail, make sure you're using an App Password, not your regular password."
            # Python print statement: Outputs error message
            print(f" {error_msg}")
            # Python import statement: Imports traceback module for error details
            import traceback
            # Python print statement: Outputs full error traceback
            print(f"   Traceback: {traceback.format_exc()}")
            # Python raise statement: Re-raises exception with custom message
            raise Exception(error_msg)
        except smtplib.SMTPException as e:
            # Python variable: Creates error message with exception details
            error_msg = f"SMTP error: {e}"
            # Python print statement: Outputs error message
            print(f" {error_msg}")
            # Python import statement: Imports traceback module for error details
            import traceback
            # Python print statement: Outputs full error traceback
            # format_exc() returns formatted stack trace as string
            print(f"   Traceback: {traceback.format_exc()}")
            # Python raise statement: Re-raises exception with custom message
            raise Exception(error_msg)
        # Python except clause: Catches all other exceptions
        except Exception as e:
            # Python variable: Creates generic error message
            error_msg = f"Email sending failed: {e}"
            # Python print statement: Outputs error message
            print(f" {error_msg}")
            # Python import statement: Imports traceback module
            import traceback
            # Python print statement: Outputs full error traceback
            print(f"   Traceback: {traceback.format_exc()}")
            # Python raise statement: Re-raises exception with custom message
            raise Exception(error_msg)
    
    # Python comment: Marks fallback console output section
    # Fallback: Print to console for testing
    # Python print statement: Outputs separator line (50 equal signs)
    print("\n" + "="*50)
    # Python print statement: Outputs header indicating testing mode
    print(f" EMAIL CODE (Testing Mode)")
    # Python print statement: Displays recipient email address
    print(f"To: {email_address}")
    # Python print statement: Displays email subject
    print(f"Subject: {subject}")
    # Python print statement: Displays verification code
    print(f"Code: {code}")
    # Python print statement: Outputs blank line and plain text message
    print(f"\nPlain Text Message:\n{text_body}")
    # Python print statement: Outputs closing separator line
    print("="*50 + "\n")
    
    # Python return statement: Returns True to indicate function completed
    # Even in testing mode, function returns success
    return True
