"""
Unit tests for database module
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import pandas as pd
from src.database import DatabaseManager, load_query_from_file


class TestDatabaseManager:
    """Test cases for DatabaseManager"""
    
    @patch('src.database.pymysql.connect')
    def test_connect_success(self, mock_connect):
        """Test successful database connection"""
        mock_connect.return_value = MagicMock()
        
        db = DatabaseManager()
        result = db.connect()
        
        assert result is True
        assert db.connection is not None
        mock_connect.assert_called_once()
    
    @patch('src.database.pymysql.connect')
    def test_connect_failure(self, mock_connect):
        """Test failed database connection"""
        mock_connect.side_effect = Exception("Connection failed")
        
        db = DatabaseManager()
        result = db.connect()
        
        assert result is False
        assert db.connection is None
    
    @patch('src.database.pd.read_sql')
    def test_execute_query_success(self, mock_read_sql):
        """Test successful query execution"""
        # Mock DataFrame
        expected_df = pd.DataFrame({'id': [1, 2], 'name': ['Alice', 'Bob']})
        mock_read_sql.return_value = expected_df
        
        db = DatabaseManager()
        db.connection = MagicMock()
        db.connection.open = True
        
        result = db.execute_query("SELECT * FROM users")
        
        assert result is not None
        assert len(result) == 2
        mock_read_sql.assert_called_once()
    
    def test_load_query_from_file(self, tmp_path):
        """Test loading query from file"""
        # Create temporary SQL file
        query_file = tmp_path / "test.sql"
        query_content = "SELECT * FROM test_table"
        query_file.write_text(query_content)
        
        result = load_query_from_file(str(query_file))
        
        assert result == query_content
