"""
Emailer module for Schedule DB Query
Handles email composition and sending with attachments
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import List, Optional
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)


class EmailSender:
    """Handles email composition and sending"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.use_tls = settings.SMTP_USE_TLS
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        self.from_address = settings.EMAIL_FROM
        self.to_addresses = settings.EMAIL_TO
        self.cc_addresses = settings.EMAIL_CC
        self.bcc_addresses = settings.EMAIL_BCC
    
    def create_message(
        self,
        subject: str,
        body: str,
        attachments: Optional[List[Path]] = None,
        html: bool = False
    ) -> MIMEMultipart:
        """
        Create email message with optional attachments
        
        Args:
            subject: Email subject
            body: Email body text
            attachments: List of file paths to attach
            html: If True, body is treated as HTML
            
        Returns:
            MIMEMultipart message object
        """
        message = MIMEMultipart()
        message['From'] = self.from_address
        message['To'] = ', '.join(self.to_addresses)
        
        if self.cc_addresses:
            message['Cc'] = ', '.join(self.cc_addresses)
        
        message['Subject'] = subject
        
        # Add body
        body_type = 'html' if html else 'plain'
        message.attach(MIMEText(body, body_type))
        
        # Add attachments
        if attachments:
            for filepath in attachments:
                try:
                    with open(filepath, 'rb') as f:
                        attachment = MIMEApplication(f.read(), Name=filepath.name)
                        attachment['Content-Disposition'] = f'attachment; filename="{filepath.name}"'
                        message.attach(attachment)
                        logger.debug(f"Attached file: {filepath.name}")
                except Exception as e:
                    logger.error(f"Error attaching file {filepath}: {str(e)}")
        
        return message
    
    def send_email(
        self,
        subject: str,
        body: str,
        attachments: Optional[List[Path]] = None,
        html: bool = False,
        retry_count: int = 3
    ) -> bool:
        """
        Send email with optional attachments
        
        Args:
            subject: Email subject
            body: Email body text
            attachments: List of file paths to attach
            html: If True, body is treated as HTML
            retry_count: Number of retry attempts on failure
            
        Returns:
            True if email sent successfully, False otherwise
        """
        for attempt in range(retry_count):
            try:
                logger.info(f"Sending email (attempt {attempt + 1}/{retry_count})")
                logger.info(f"To: {', '.join(self.to_addresses)}")
                logger.info(f"Subject: {subject}")
                
                # Create message
                message = self.create_message(subject, body, attachments, html)
                
                # Get all recipients
                all_recipients = self.to_addresses + self.cc_addresses + self.bcc_addresses
                
                # Connect to SMTP server
                if self.use_tls:
                    server = smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30)
                    server.starttls()
                else:
                    server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, timeout=30)
                
                # Login
                server.login(self.username, self.password)
                
                # Send email
                server.send_message(message, self.from_address, all_recipients)
                
                # Close connection
                server.quit()
                
                logger.info("Email sent successfully")
                return True
                
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP authentication failed: {str(e)}")
                return False  # Don't retry auth errors
                
            except Exception as e:
                logger.error(f"Error sending email (attempt {attempt + 1}/{retry_count}): {str(e)}")
                
                if attempt < retry_count - 1:
                    logger.info("Retrying...")
                else:
                    logger.error("All retry attempts failed")
                    return False
        
        return False
    
    def send_snapshot_report(
        self,
        csv_filepath: Path,
        row_count: int,
        execution_time: float
    ) -> bool:
        """
        Send schedule db query report email
        
        Args:
            csv_filepath: Path to CSV file to attach
            row_count: Number of rows in the snapshot
            execution_time: Query execution time in seconds
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"Schedule DB query Report - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
<html>
<body>
<h2>Schedule DB query</h2>
<p>The scheduled query has been completed successfully.</p>

<h3>Summary:</h3>
<ul>
    <li><strong>Execution Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
    <li><strong>Total Records:</strong> {row_count:,}</li>
    <li><strong>Execution Time:</strong> {execution_time:.2f} seconds</li>
    <li><strong>File Name:</strong> {csv_filepath.name}</li>
    <li><strong>File Size:</strong> {csv_filepath.stat().st_size:,} bytes</li>
</ul>

<p>Please find the attached CSV file with the complete schedule DB query data.</p>

<hr>
<p style="color: #666; font-size: 12px;">
This is an automated email from Schedule DB Query System.<br>
For questions or issues, please contact the system administrator.
</p>
</body>
</html>
        """
        
        return self.send_email(
            subject=subject,
            body=body,
            attachments=[csv_filepath],
            html=True
        )
    
    def send_error_notification(self, error_message: str, error_details: str = "") -> bool:
        """
        Send error notification email
        
        Args:
            error_message: Brief error description
            error_details: Detailed error information
            
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = f"⚠️ Schedule DB query Error - {datetime.now().strftime('%Y-%m-%d')}"
        
        body = f"""
<html>
<body>
<h2 style="color: #d9534f;">Schedule DB query Error</h2>
<p>An error occurred during the scheduled schedule db query execution.</p>

<h3>Error Details:</h3>
<div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; border-left: 4px solid #d9534f;">
    <strong>Error:</strong> {error_message}
</div>

{f'<pre style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto;">{error_details}</pre>' if error_details else ''}

<p><strong>Timestamp:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>

<hr>
<p style="color: #666; font-size: 12px;">
This is an automated error notification from Schedule DB Query System.<br>
Please investigate and resolve the issue as soon as possible.
</p>
</body>
</html>
        """
        
        return self.send_email(
            subject=subject,
            body=body,
            html=True
        )
    
    def send_test_email(self) -> bool:
        """
        Send a test email to verify configuration
        
        Returns:
            True if email sent successfully, False otherwise
        """
        subject = "Test Email - Schedule DB Query"
        body = f"""
<html>
<body>
<h2>Test Email</h2>
<p>This is a test email from Schedule DB Query system.</p>
<p><strong>Sent at:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<p>If you received this email, your email configuration is working correctly.</p>
</body>
</html>
        """
        
        return self.send_email(
            subject=subject,
            body=body,
            html=True
        )
