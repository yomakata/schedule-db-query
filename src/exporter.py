"""
Exporter module for Schedule DB query
Handles CSV file export and file management
"""
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class CSVExporter:
    """Handles CSV export and file management"""
    
    def __init__(self, file_prefix: Optional[str] = None):
        """
        Initialize CSV Exporter
        
        Args:
            file_prefix: Optional custom prefix for output files. 
                        If None, uses FILE_PREFIX from settings.
        """
        self.output_dir = Path(settings.OUTPUT_DIR)
        self.file_prefix = file_prefix if file_prefix is not None else settings.FILE_PREFIX
        self.encoding = settings.CSV_ENCODING
        self.retention_days = settings.FILE_RETENTION_DAYS
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_filename(self) -> str:
        """
        Generate timestamped filename for CSV export
        
        Returns:
            Filename string (e.g., 'member_snapshot_2025-12-22_143000.csv')
        """
        timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
        filename = f"{self.file_prefix}_{timestamp}.csv"
        return filename
    
    def export_to_csv(self, dataframe: pd.DataFrame, filename: Optional[str] = None) -> Optional[Path]:
        """
        Export DataFrame to CSV file
        
        Args:
            dataframe: pandas DataFrame to export
            filename: Optional custom filename. If None, auto-generates timestamp filename
            
        Returns:
            Path to exported file, or None if error
        """
        try:
            if dataframe is None or dataframe.empty:
                logger.warning("Cannot export empty DataFrame")
                return None
            
            # Generate filename if not provided
            if filename is None:
                filename = self.generate_filename()
            
            filepath = self.output_dir / filename
            
            logger.info(f"Exporting {len(dataframe)} rows to {filepath}")
            
            # Export to CSV
            dataframe.to_csv(
                filepath,
                index=False,
                encoding=self.encoding,
                date_format='%Y-%m-%d %H:%M:%S'
            )
            
            # Verify file was created
            if filepath.exists():
                file_size = filepath.stat().st_size
                logger.info(f"CSV file exported successfully: {filepath} ({file_size} bytes)")
                return filepath
            else:
                logger.error("CSV file was not created")
                return None
                
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return None
    
    def cleanup_old_files(self) -> int:
        """
        Remove CSV files older than retention period
        
        Returns:
            Number of files deleted
        """
        try:
            if self.retention_days <= 0:
                logger.info("File cleanup disabled (retention_days <= 0)")
                return 0
            
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            deleted_count = 0
            
            logger.info(f"Cleaning up files older than {self.retention_days} days")
            
            # Find all CSV files in output directory
            for filepath in self.output_dir.glob(f"{self.file_prefix}*.csv"):
                try:
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                    
                    if file_mtime < cutoff_date:
                        logger.info(f"Deleting old file: {filepath.name}")
                        filepath.unlink()
                        deleted_count += 1
                        
                except Exception as e:
                    logger.error(f"Error deleting file {filepath}: {str(e)}")
            
            if deleted_count > 0:
                logger.info(f"Deleted {deleted_count} old file(s)")
            else:
                logger.info("No old files to delete")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")
            return 0
    
    def get_file_count(self) -> int:
        """
        Get count of CSV files in output directory
        
        Returns:
            Number of CSV files
        """
        try:
            count = len(list(self.output_dir.glob(f"{self.file_prefix}*.csv")))
            return count
        except Exception as e:
            logger.error(f"Error counting files: {str(e)}")
            return 0
    
    def get_latest_file(self) -> Optional[Path]:
        """
        Get the most recently created CSV file
        
        Returns:
            Path to latest file, or None if no files exist
        """
        try:
            files = list(self.output_dir.glob(f"{self.file_prefix}*.csv"))
            if not files:
                return None
            
            # Sort by modification time, newest first
            latest_file = max(files, key=lambda p: p.stat().st_mtime)
            return latest_file
            
        except Exception as e:
            logger.error(f"Error getting latest file: {str(e)}")
            return None
