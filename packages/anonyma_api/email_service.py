"""
Email Service

Handles sending transactional emails using SMTP.
Supports welcome emails, quota warnings, and notifications.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

from anonyma_core.logging_config import get_logger

logger = get_logger(__name__)


class EmailService:
    """
    Email service for sending transactional emails.
    """

    def __init__(self):
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.from_email = os.getenv('SMTP_FROM_EMAIL', self.smtp_username)
        self.from_name = os.getenv('SMTP_FROM_NAME', 'Anonyma')
        self.enabled = bool(self.smtp_username and self.smtp_password)

        if not self.enabled:
            logger.warning("Email service not configured - emails will not be sent")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: Optional[str] = None
    ) -> bool:
        """
        Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_body: HTML email body
            text_body: Plain text email body (optional)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.enabled:
            logger.warning(f"Email not sent to {to_email} - service not configured")
            return False

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            msg['Subject'] = subject

            # Attach text and HTML parts
            if text_body:
                msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_welcome_email(self, email: str, username: str, role: str) -> bool:
        """
        Send welcome email to new user.
        """
        subject = "Welcome to Anonyma!"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">🔒 Welcome to Anonyma!</h1>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px;">Hi <strong>{username}</strong>,</p>

                <p>Thank you for joining Anonyma! Your account has been created successfully.</p>

                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Your Account Details</h3>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Plan:</strong> {role.capitalize()} {'🎯' if role == 'demo' else '⭐' if role == 'premium' else '👑'}</p>
                    <p><strong>Daily Limit:</strong> {
                        '999,999' if role == 'admin' else
                        '1,000' if role == 'premium' else
                        '50'
                    } requests</p>
                </div>

                <h3>What's Next?</h3>
                <ul>
                    <li>Explore text anonymization features</li>
                    <li>Process documents (PDF, Word, Excel, etc.)</li>
                    <li>Configure your settings</li>
                    {'<li>Consider upgrading to Premium for higher limits</li>' if role == 'demo' else ''}
                </ul>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost')}"
                       style="display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Get Started
                    </a>
                </div>

                <p style="color: #666; font-size: 14px; margin-top: 30px;">
                    Need help? Reply to this email or check our documentation.
                </p>

                <p style="color: #666; font-size: 14px;">
                    Best regards,<br>
                    The Anonyma Team
                </p>
            </div>

            <div style="text-align: center; padding: 20px; color: #999; font-size: 12px;">
                <p>© {datetime.now().year} Anonyma. All rights reserved.</p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Welcome to Anonyma!

        Hi {username},

        Thank you for joining Anonyma! Your account has been created successfully.

        Your Account Details:
        - Email: {email}
        - Plan: {role.capitalize()}
        - Daily Limit: {'999,999' if role == 'admin' else '1,000' if role == 'premium' else '50'} requests

        What's Next?
        - Explore text anonymization features
        - Process documents (PDF, Word, Excel, etc.)
        - Configure your settings

        Visit: {os.getenv('FRONTEND_URL', 'http://localhost')}

        Best regards,
        The Anonyma Team
        """

        return self.send_email(email, subject, html_body, text_body)

    def send_quota_warning_email(
        self, email: str, username: str, daily_used: int, daily_limit: int, percentage: int
    ) -> bool:
        """
        Send quota warning email when user is close to limit.
        """
        subject = f"Anonyma Quota Alert: {percentage}% Used"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #fef3c7; padding: 20px; border-left: 4px solid #f59e0b; border-radius: 8px;">
                <h2 style="color: #92400e; margin-top: 0;">⚠️ Quota Warning</h2>

                <p>Hi <strong>{username}</strong>,</p>

                <p>You've used <strong>{percentage}%</strong> of your daily quota.</p>

                <div style="background: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <p style="margin: 5px 0;"><strong>Used:</strong> {daily_used:,} requests</p>
                    <p style="margin: 5px 0;"><strong>Limit:</strong> {daily_limit:,} requests</p>
                    <p style="margin: 5px 0;"><strong>Remaining:</strong> {daily_limit - daily_used:,} requests</p>
                </div>

                <p>Your quota will reset at midnight UTC.</p>

                <p style="margin-top: 20px;">
                    <strong>Need more requests?</strong> Consider upgrading to Premium for 1,000 requests per day.
                </p>

                <div style="text-align: center; margin: 20px 0;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost')}/pricing"
                       style="display: inline-block; padding: 10px 25px; background: #667eea; color: white; text-decoration: none; border-radius: 5px;">
                        View Plans
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Anonyma Quota Alert

        Hi {username},

        You've used {percentage}% of your daily quota.

        Current Usage:
        - Used: {daily_used:,} requests
        - Limit: {daily_limit:,} requests
        - Remaining: {daily_limit - daily_used:,} requests

        Your quota will reset at midnight UTC.

        Need more requests? Upgrade to Premium for 1,000 requests per day.

        Visit: {os.getenv('FRONTEND_URL', 'http://localhost')}/pricing
        """

        return self.send_email(email, subject, html_body, text_body)

    def send_upgrade_confirmation_email(self, email: str, username: str, new_role: str) -> bool:
        """
        Send confirmation email after upgrade.
        """
        subject = f"Welcome to Anonyma {new_role.capitalize()}! 🎉"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0;">🎉 Upgrade Successful!</h1>
            </div>

            <div style="background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px;">
                <p style="font-size: 16px;">Hi <strong>{username}</strong>,</p>

                <p>Congratulations! Your account has been successfully upgraded to <strong>{new_role.capitalize()}</strong>.</p>

                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0;">Your New Benefits</h3>
                    <ul style="padding-left: 20px;">
                        {'<li>Unlimited requests</li>' if new_role == 'admin' else
                         '<li>1,000 requests per day</li>' if new_role == 'premium' else
                         '<li>50 requests per day</li>'}
                        {'<li>10,000 requests per month</li>' if new_role == 'premium' else ''}
                        <li>All anonymization modes</li>
                        <li>All document formats</li>
                        {'<li>Priority support</li>' if new_role == 'premium' else ''}
                        {'<li>Advanced analytics</li>' if new_role == 'premium' else ''}
                    </ul>
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost')}"
                       style="display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Start Using Your New Plan
                    </a>
                </div>

                <p style="color: #666; font-size: 14px;">
                    Thank you for choosing Anonyma!
                </p>
            </div>
        </body>
        </html>
        """

        text_body = f"""
        Upgrade Successful!

        Hi {username},

        Congratulations! Your account has been upgraded to {new_role.capitalize()}.

        Your New Benefits:
        - {'Unlimited' if new_role == 'admin' else '1,000' if new_role == 'premium' else '50'} requests per day
        - All anonymization modes
        - All document formats
        {'- Priority support' if new_role == 'premium' else ''}

        Visit: {os.getenv('FRONTEND_URL', 'http://localhost')}

        Thank you for choosing Anonyma!
        """

        return self.send_email(email, subject, html_body, text_body)

    def send_new_user_notification_to_admin(
        self, admin_email: str, new_user_email: str, new_user_username: str, role: str
    ) -> bool:
        """
        Notify admin when new user registers.
        """
        subject = f"New User Registration: {new_user_username}"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: #eff6ff; padding: 20px; border-left: 4px solid #3b82f6; border-radius: 8px;">
                <h2 style="color: #1e40af; margin-top: 0;">👤 New User Registration</h2>

                <p>A new user has registered on Anonyma.</p>

                <div style="background: white; padding: 15px; border-radius: 6px; margin: 15px 0;">
                    <p style="margin: 5px 0;"><strong>Username:</strong> {new_user_username}</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> {new_user_email}</p>
                    <p style="margin: 5px 0;"><strong>Role:</strong> {role.capitalize()}</p>
                    <p style="margin: 5px 0;"><strong>Registered:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                </div>

                <div style="text-align: center; margin: 20px 0;">
                    <a href="{os.getenv('FRONTEND_URL', 'http://localhost')}/admin"
                       style="display: inline-block; padding: 10px 25px; background: #667eea; color: white; text-decoration: none; border-radius: 5px;">
                        View in Admin Dashboard
                    </a>
                </div>
            </div>
        </body>
        </html>
        """

        return self.send_email(admin_email, subject, html_body)


# Global email service instance
email_service = EmailService()
