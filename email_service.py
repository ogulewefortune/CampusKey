import random
import string
from datetime import datetime, timedelta
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header


def generate_verification_code():
    """Generate a random 6-digit code"""
    return ''.join(random.choices(string.digits, k=6))


def send_email_code(email_address, code, username):
    """
    Send verification code via email.
    Uses SMTP if configured, otherwise prints to console for testing.
    """
    # Email configuration from environment variables
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_username = os.environ.get('SMTP_USERNAME')
    smtp_password = os.environ.get('SMTP_PASSWORD', '').replace('\xa0', ' ').strip()  # Fix non-breaking spaces
    from_email = os.environ.get('FROM_EMAIL', smtp_username)
    
    subject = "CAMPUSKEY Verification Code"
    
    # HTML email template matching Google style
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
    
    # Plain text version for email clients that don't support HTML
    text_body = f"""Dear CAMPUSKEY User,

We received a request to access your CAMPUSKEY Account {email_address} through your email address. Your CAMPUSKEY verification code is:

{code}

If you did not request this code, it is possible that someone else is trying to access the CAMPUSKEY Account {email_address}. Do not forward or give this code to anyone.

Sincerely yours,
The CAMPUSKEY Security Team

---
This email can't receive replies. For more information, visit the CAMPUSKEY Help Center.
        """
    
    # If SMTP is configured, try to send email
    if smtp_username and smtp_password:
        try:
            print(f"\n Attempting to send email...")
            print(f"   From: {from_email}")
            print(f"   To: {email_address}")
            print(f"   Server: {smtp_server}:{smtp_port}")
            
            msg = MIMEMultipart('alternative')
            msg['From'] = from_email
            msg['To'] = email_address
            msg['Subject'] = Header(subject, 'utf-8')
            
            # Add both plain text and HTML versions
            part1 = MIMEText(text_body, 'plain', 'utf-8')
            part2 = MIMEText(html_body, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            server = smtplib.SMTP(smtp_server, smtp_port, timeout=10)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            result = server.sendmail(from_email, [email_address], text)
            server.quit()
            
            if result:
                error_msg = f"Email send failed: {result}"
                print(f" {error_msg}")
                raise Exception(error_msg)
            else:
                print(f" Email sent successfully to {email_address}")
                return True
        except smtplib.SMTPException as e:
            error_msg = f"SMTP error: {e}"
            print(f" {error_msg}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"Email sending failed: {e}"
            print(f" {error_msg}")
            import traceback
            print(f"   Traceback: {traceback.format_exc()}")
            raise Exception(error_msg)
    
    # Fallback: Print to console for testing
    print("\n" + "="*50)
    print(f" EMAIL CODE (Testing Mode)")
    print(f"To: {email_address}")
    print(f"Subject: {subject}")
    print(f"Code: {code}")
    print(f"\nPlain Text Message:\n{text_body}")
    print("="*50 + "\n")
    
    return True

