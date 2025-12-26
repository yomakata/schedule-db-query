"""
Database module for Schedule DB Query
Handles database connections and query execution using SQLAlchemy
"""
import logging
import pandas as pd
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

# Import SQLAlchemy
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    logger.error("SQLAlchemy not installed. Install with: pip install SQLAlchemy")

# Import database drivers based on availability (for SQLAlchemy)
try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    logger.warning("pymysql not installed. MySQL support disabled.")

try:
    import psycopg2
    POSTGRESQL_AVAILABLE = True
except ImportError:
    POSTGRESQL_AVAILABLE = False
    logger.warning("psycopg2 not installed. PostgreSQL support disabled.")

try:
    import pyodbc
    SQLSERVER_AVAILABLE = True
except ImportError:
    SQLSERVER_AVAILABLE = False
    logger.warning("pyodbc not installed. SQL Server support disabled.")


class DatabaseManager:
    """Manages database connections and query execution using SQLAlchemy"""
    
    def __init__(self):
        self.engine: Optional[Engine] = None
        self.db_type = settings.DB_TYPE
        self.host = settings.DB_HOST
        self.port = settings.DB_PORT
        self.database = settings.DB_NAME
        self.user = settings.DB_USER
        self.password = settings.DB_PASSWORD
    
    def connect(self) -> bool:
        """
        Establish database connection using SQLAlchemy
        Returns True if successful, False otherwise
        """
        try:
            if not SQLALCHEMY_AVAILABLE:
                raise ImportError("SQLAlchemy not installed. Install with: pip install SQLAlchemy")
            
            logger.info(f"Connecting to {self.db_type} database at {self.host}:{self.port}")
            
            # Build SQLAlchemy connection URL based on database type
            if self.db_type.lower() == 'mysql':
                if not MYSQL_AVAILABLE:
                    raise ImportError("pymysql not installed. Install with: pip install pymysql")
                
                # MySQL connection URL: mysql+pymysql://user:password@host:port/database
                connection_url = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?charset=utf8mb4"
            
            elif self.db_type.lower() == 'postgresql':
                if not POSTGRESQL_AVAILABLE:
                    raise ImportError("psycopg2 not installed. Install with: pip install psycopg2-binary")
                
                # PostgreSQL connection URL: postgresql://user:password@host:port/database
                connection_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            
            elif self.db_type.lower() == 'sqlserver':
                if not SQLSERVER_AVAILABLE:
                    raise ImportError("pyodbc not installed. Install with: pip install pyodbc")
                
                # SQL Server connection URL: mssql+pyodbc://user:password@host:port/database?driver=ODBC+Driver+17+for+SQL+Server
                connection_url = f"mssql+pyodbc://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"
            
            else:
                raise ValueError(f"Unsupported database type: '{self.db_type}'. Supported types: mysql, postgresql, sqlserver")
            
            # Create SQLAlchemy engine
            self.engine = create_engine(
                connection_url,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=False,          # Set to True for SQL query logging
                connect_args={'connect_timeout': 30}
            )
            
            # Test the connection
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            logger.info("Database connection established successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to database: {str(e)}")
            return False
    
    def disconnect(self):
        """Close database connection"""
        if self.engine:
            try:
                self.engine.dispose()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
    
    def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """
        Execute SQL query and return results as pandas DataFrame using SQLAlchemy
        
        Args:
            query: SQL query string
            
        Returns:
            pandas DataFrame with query results, or None if error
        """
        try:
            # Check if engine is valid
            if not self.engine:
                logger.warning("Database engine not initialized, attempting to connect")
                if not self.connect():
                    return None
            
            logger.info("Executing SQL query...")
            logger.debug(f"Query: {query[:200]}...")  # Log first 200 chars
            
            # Execute query and load into DataFrame using SQLAlchemy engine
            # This eliminates the pandas UserWarning about DBAPI2 connections
            df = pd.read_sql(query, self.engine)
            
            row_count = len(df)
            logger.info(f"Query executed successfully. Retrieved {row_count} rows")
            
            return df
            
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test database connection
        Returns True if connection is successful, False otherwise
        """
        try:
            if self.connect():
                # Execute simple test query
                test_query = "SELECT 1 as test"
                result = self.execute_query(test_query)
                self.disconnect()
                
                if result is not None and len(result) > 0:
                    logger.info("Database connection test successful")
                    return True
            
            logger.error("Database connection test failed")
            return False
            
        except Exception as e:
            logger.error(f"Database connection test error: {str(e)}")
            return False
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


def load_query_from_file(filepath: str) -> str:
    """
    Load SQL query from file
    
    Args:
        filepath: Path to SQL file
        
    Returns:
        SQL query string
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            query = f.read()
        logger.info(f"Loaded query from {filepath}")
        return query
    except Exception as e:
        logger.error(f"Error loading query from file: {str(e)}")
        raise
