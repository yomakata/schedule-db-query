"""
Unit tests for exporter module
"""
import pytest
from pathlib import Path
import pandas as pd
from src.exporter import CSVExporter


class TestCSVExporter:
    """Test cases for CSVExporter"""
    
    def test_generate_filename(self):
        """Test filename generation"""
        exporter = CSVExporter()
        filename = exporter.generate_filename()
        
        assert filename.startswith(exporter.file_prefix)
        assert filename.endswith('.csv')
        assert '_' in filename  # Should contain timestamp separator
    
    def test_export_to_csv(self, tmp_path):
        """Test CSV export"""
        # Create test DataFrame
        df = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie']
        })
        
        # Create exporter with temp directory
        exporter = CSVExporter()
        exporter.output_dir = tmp_path
        
        # Export
        result = exporter.export_to_csv(df, 'test.csv')
        
        assert result is not None
        assert result.exists()
        assert result.name == 'test.csv'
        
        # Verify content
        df_read = pd.read_csv(result)
        assert len(df_read) == 3
        assert list(df_read.columns) == ['id', 'name']
    
    def test_export_empty_dataframe(self, tmp_path):
        """Test exporting empty DataFrame"""
        df = pd.DataFrame()
        
        exporter = CSVExporter()
        exporter.output_dir = tmp_path
        
        result = exporter.export_to_csv(df)
        
        assert result is None
    
    def test_get_file_count(self, tmp_path):
        """Test file counting"""
        exporter = CSVExporter()
        exporter.output_dir = tmp_path
        
        # Create some test files
        (tmp_path / f"{exporter.file_prefix}_1.csv").touch()
        (tmp_path / f"{exporter.file_prefix}_2.csv").touch()
        (tmp_path / "other_file.csv").touch()
        
        count = exporter.get_file_count()
        
        assert count == 2  # Only files matching the prefix
