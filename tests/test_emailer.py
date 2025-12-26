"""
Unit tests for emailer module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from src.emailer import EmailSender


class TestEmailSender:
    """Test cases for EmailSender"""
    
    def test_create_message(self):
        """Test email message creation"""
        emailer = EmailSender()
        
        message = emailer.create_message(
            subject="Test Subject",
            body="Test Body",
            html=False
        )
        
        assert message['Subject'] == "Test Subject"
        assert message['From'] == emailer.from_address
        assert message['To'] == ', '.join(emailer.to_addresses)
    
    @patch('src.emailer.smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        # Mock SMTP server
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        emailer = EmailSender()
        
        result = emailer.send_email(
            subject="Test",
            body="Test body",
            retry_count=1
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('src.emailer.smtplib.SMTP')
    def test_send_email_with_attachment(self, mock_smtp, tmp_path):
        """Test sending email with attachment"""
        # Create temporary file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content")
        
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        emailer = EmailSender()
        
        result = emailer.send_email(
            subject="Test",
            body="Test body",
            attachments=[test_file],
            retry_count=1
        )
        
        assert result is True
    
    def test_send_test_email(self):
        """Test send_test_email method"""
        emailer = EmailSender()
        
        with patch.object(emailer, 'send_email') as mock_send:
            mock_send.return_value = True
            
            result = emailer.send_test_email()
            
            assert result is True
            mock_send.assert_called_once()
            
            # Check that it was called with correct parameters
            call_args = mock_send.call_args
            assert 'Test Email' in call_args.kwargs['subject']
            assert call_args.kwargs['html'] is True
