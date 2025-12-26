"""
Configuration loader for Schedule DB query
Loads and validates environment variables from .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Database Configuration
    DB_TYPE = os.getenv('DB_TYPE', 'mysql')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', '3306'))
    DB_NAME = os.getenv('DB_NAME', '')
    DB_USER = os.getenv('DB_USER', '')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    
    # Email Configuration
    EMAIL_ENABLED = os.getenv('EMAIL_ENABLED', 'true').lower() == 'true'
    SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USE_TLS = os.getenv('SMTP_USE_TLS', 'true').lower() == 'true'
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    EMAIL_FROM = os.getenv('EMAIL_FROM', '')
    EMAIL_TO = os.getenv('EMAIL_TO', '').split(',') if os.getenv('EMAIL_TO') else []
    EMAIL_CC = os.getenv('EMAIL_CC', '').split(',') if os.getenv('EMAIL_CC') else []
    EMAIL_BCC = os.getenv('EMAIL_BCC', '').split(',') if os.getenv('EMAIL_BCC') else []
    
    # Schedule Configuration
    SCHEDULE_ENABLED = os.getenv('SCHEDULE_ENABLED', 'true').lower() == 'true'
    SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', '08:00').split(',') if os.getenv('SCHEDULE_TIME') else ['08:00']
    SCHEDULE_TIME = [time.strip() for time in SCHEDULE_TIME]  # Clean whitespace
    SCHEDULE_TIMEZONE = os.getenv('SCHEDULE_TIMEZONE', 'Asia/Shanghai')
    SCHEDULE_DAYS = os.getenv('SCHEDULE_DAYS', 'MON,TUE,WED,THU,FRI').split(',')
    SCHEDULE_DAYS = [day.strip() for day in SCHEDULE_DAYS]  # Clean whitespace
    
    # Query Configuration
    SQL_QUERY_FILE = os.getenv('SQL_QUERY_FILE', './config/queries.sql')
    
    # Export Configuration
    OUTPUT_DIR = os.getenv('OUTPUT_DIR', './output/snapshots')
    FILE_PREFIX = os.getenv('FILE_PREFIX', 'member_snapshot')
    FILE_RETENTION_DAYS = int(os.getenv('FILE_RETENTION_DAYS', '30'))
    CSV_ENCODING = os.getenv('CSV_ENCODING', 'utf-8')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', './logs/app.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB default
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))  # Keep 5 backup files
    
    @classmethod
    def validate(cls):
        """Validate required settings"""
        required_fields = [
            ('DB_HOST', cls.DB_HOST),
            ('DB_NAME', cls.DB_NAME),
            ('DB_USER', cls.DB_USER),
            ('DB_PASSWORD', cls.DB_PASSWORD),
        ]
        
        missing_fields = [field for field, value in required_fields if not value]
        
        if missing_fields:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_fields)}")
        
        # Only validate email settings if email is enabled
        if cls.EMAIL_ENABLED:
            email_required_fields = [
                ('SMTP_USERNAME', cls.SMTP_USERNAME),
                ('SMTP_PASSWORD', cls.SMTP_PASSWORD),
                ('EMAIL_FROM', cls.EMAIL_FROM),
            ]
            
            missing_email_fields = [field for field, value in email_required_fields if not value]
            
            if missing_email_fields:
                raise ValueError(f"Missing required email environment variables: {', '.join(missing_email_fields)}")
            
            if not cls.EMAIL_TO:
                raise ValueError("At least one EMAIL_TO recipient is required when EMAIL_ENABLED=true")
        
        return True
    
    @classmethod
    def ensure_directories(cls):
        """Ensure required directories exist"""
        Path(cls.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        Path(cls.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)


# Create settings instance
settings = Settings()
