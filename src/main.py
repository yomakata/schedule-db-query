"""
Main entry point for Schedule DB query
Orchestrates database query, CSV export, and email delivery
"""
import logging
import sys
import time
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from src.database import DatabaseManager, load_query_from_file
from src.exporter import CSVExporter
from src.emailer import EmailSender
from src.scheduler import create_scheduler


def setup_logging():
    """Configure logging for the application with rotation"""
    from logging.handlers import RotatingFileHandler
    
    settings.ensure_directories()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Rotating file handler (rotates when file reaches max size)
    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger


logger = setup_logging()


def execute_snapshot():
    """Main function to execute member snapshot"""
    from datetime import datetime
    start_time = time.time()
    execution_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        logger.info("=" * 80)
        logger.info("Starting Member Snapshot Execution")
        logger.info(f"Execution Time: {execution_timestamp}")
        logger.info("=" * 80)
        
        # Initialize components
        db_manager = DatabaseManager()
        emailer = EmailSender()
        
        # Load SQL query from configured file
        query_file = Path(settings.SQL_QUERY_FILE)
        
        # If relative path, resolve it relative to project root
        if not query_file.is_absolute():
            query_file = Path(__file__).parent.parent / query_file
        
        if not query_file.exists():
            raise FileNotFoundError(f"Query file not found: {query_file}")
        
        logger.info(f"Loading SQL query from: {query_file}")
        query = load_query_from_file(str(query_file))
        
        # Extract query file name (without extension) for output file prefix
        query_file_prefix = query_file.stem  # e.g., "queries" or "sales_report"
        
        # Initialize exporter with query file name as prefix
        exporter = CSVExporter(file_prefix=query_file_prefix)
        
        # Execute query
        logger.info("Step 1: Executing database query...")
        with db_manager:
            df = db_manager.execute_query(query)
        
        if df is None or df.empty:
            logger.warning("Query returned no results")
            if settings.EMAIL_ENABLED:
                emailer.send_error_notification(
                    "No data returned from query",
                    f"The SQL query executed successfully but returned 0 rows.\nQuery file: {query_file}"
                )
            return False
        
        # Export to CSV
        logger.info("Step 2: Exporting data to CSV...")
        csv_file = exporter.export_to_csv(df)
        
        if csv_file is None:
            raise Exception("Failed to export CSV file")
        
        # Cleanup old files
        logger.info("Step 3: Cleaning up old files...")
        deleted_count = exporter.cleanup_old_files()
        
        # Calculate execution time
        execution_time = time.time() - start_time
        
        # Send email if enabled
        email_sent = False
        if settings.EMAIL_ENABLED:
            logger.info("Step 4: Sending email notification...")
            emailer = EmailSender()
            email_sent = emailer.send_snapshot_report(
                csv_filepath=csv_file,
                row_count=len(df),
                execution_time=execution_time
            )
            
            if not email_sent:
                logger.warning("Failed to send email notification")
        else:
            logger.info("Step 4: Email notification skipped (EMAIL_ENABLED=false)")
        
        # Summary
        logger.info("=" * 80)
        logger.info("Snapshot Execution Completed Successfully")
        logger.info(f"  Total rows: {len(df):,}")
        logger.info(f"  CSV file: {csv_file.name}")
        logger.info(f"  File size: {csv_file.stat().st_size:,} bytes")
        logger.info(f"  File path: {csv_file}")
        logger.info(f"  Execution time: {execution_time:.2f} seconds")
        logger.info(f"  Old files deleted: {deleted_count}")
        logger.info(f"  Email enabled: {'Yes' if settings.EMAIL_ENABLED else 'No'}")
        logger.info(f"  Email sent: {'Yes' if email_sent else 'No' if settings.EMAIL_ENABLED else 'N/A'}")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error("=" * 80)
        logger.error("Snapshot Execution Failed")
        logger.error(f"  Error: {str(e)}")
        logger.error(f"  Execution time: {execution_time:.2f} seconds")
        logger.error("=" * 80)
        logger.exception("Full error traceback:")
        
        # Send error notification
        try:
            if settings.EMAIL_ENABLED:
                emailer = EmailSender()
                emailer.send_error_notification(
                    error_message=str(e),
                    error_details=f"Execution time: {execution_time:.2f}s\nCheck log file for details: {settings.LOG_FILE}"
                )
        except Exception as email_error:
            logger.error(f"Failed to send error notification: {str(email_error)}")
        
        return False


def test_database_connection():
    """Test database connection"""
    db_manager = DatabaseManager()
    
    if db_manager.test_connection():
        logger.info("✓ Database connection test passed")
        return True
    else:
        logger.error("✗ Database connection test failed")
        return False


def test_email_sending():
    """Test email sending"""
    if not settings.EMAIL_ENABLED:
        logger.warning("Email is disabled (EMAIL_ENABLED=false)")
        logger.info("Set EMAIL_ENABLED=true in .env to test email")
        return False
    
    logger.info("Testing email configuration...")
    emailer = EmailSender()
    
    if emailer.send_test_email():
        logger.info("✓ Test email sent successfully")
        return True
    else:
        logger.error("✗ Failed to send test email")
        return False


def main():
    """Main entry point with command-line argument handling"""
    parser = argparse.ArgumentParser(
        description='Schedule DB Query - Automated database snapshot to CSV with email delivery'
    )
    
    parser.add_argument(
        '--run-once',
        action='store_true',
        help='Execute snapshot once and exit (no scheduling)'
    )
    
    parser.add_argument(
        '--test-db',
        action='store_true',
        help='Test database connection and exit'
    )
    
    parser.add_argument(
        '--test-email',
        action='store_true',
        help='Send test email and exit'
    )
    
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Run with scheduler (default behavior)'
    )
    
    args = parser.parse_args()
    
    try:
        # Validate settings
        logger.info("=" * 80)
        logger.info("Schedule DB query Service Starting...")
        logger.info("=" * 80)
        logger.info("Validating configuration...")
        settings.validate()
        logger.info("✓ Configuration validated successfully")
        
        # Handle test commands first (before connection test)
        if args.test_db:
            logger.info("Testing database connection...")
            sys.exit(0 if test_database_connection() else 1)
        
        if args.test_email:
            sys.exit(0 if test_email_sending() else 1)
        
        # Test database connection on startup for all other modes
        logger.info("=" * 80)
        logger.info("Testing Database Connection on Startup...")
        logger.info("=" * 80)
        if not test_database_connection():
            logger.error("✗ Database connection test failed. Please check your database configuration.")
            sys.exit(1)
        logger.info("=" * 80)
        
        # Handle run-once mode
        if args.run_once:
            success = execute_snapshot()
            sys.exit(0 if success else 1)
        
        # Default: Run with scheduler
        if not settings.SCHEDULE_ENABLED and not args.schedule:
            logger.warning("Scheduling is disabled in configuration")
            logger.info("Run with --run-once to execute immediately, or enable SCHEDULE_ENABLED in .env")
            sys.exit(1)
        
        scheduler = create_scheduler(execute_snapshot)
        scheduler.run()
        
    except KeyboardInterrupt:
        logger.info("Program interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        logger.exception("Full error traceback:")
        sys.exit(1)


if __name__ == '__main__':
    main()
