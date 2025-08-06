"""
Tests for DataProcessor module.
"""
import pytest
import pandas as pd
import tempfile
import os
from src.core.data_processor import DataProcessor


class TestDataProcessor:
    """Test cases for DataProcessor class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.data_processor = DataProcessor()
        
        # Create sample data
        self.sample_data = pd.DataFrame({
            "Company Category": ["Gaming Company", "Tech Company"],
            "Company": ["Cloud Imperium Games", "Google"],
            "Overall Job Category": ["Engineering", "Engineering"],
            "Job Category": ["DevOps", "Software Engineer"],
            "Title": ["Azure Cloud Engineer", "Python Developer"],
            "Min Experience": [2, 3],
            "Max Experience": [5, 7],
            "Country": ["Netherlands", "United States"],
            "State": ["North Holland", "California"],
            "City": ["Amsterdam", "Mountain View"],
            "Location Type": ["On Site", "Remote"],
            "JobType": ["Full Time", "Full Time"],
            "Job Link": ["https://example1.com", "https://example2.com"],
            "Activated Date": ["02 Aug 2025", "03 Aug 2025"],
            "Skills": ["Agile Development, AWS, Azure", "Python, Django, React"],
            "Min Salary": [50000, 80000],
            "Max Salary": [80000, 120000]
        })
    
    def test_generate_job_id(self):
        """Test job ID generation."""
        job_row = {
            "Company": "Cloud Imperium Games",
            "Title": "Azure Cloud Engineer",
            "City": "Amsterdam"
        }
        
        job_id = self.data_processor.generate_job_id(job_row)
        
        assert isinstance(job_id, str)
        assert len(job_id) == 12
        assert job_id.isalnum()
    
    def test_add_job_ids(self):
        """Test adding job IDs to DataFrame."""
        df_with_ids = self.data_processor.add_job_ids(self.sample_data)
        
        assert "job_id" in df_with_ids.columns
        assert len(df_with_ids) == len(self.sample_data)
        assert all(df_with_ids["job_id"].str.len() == 12)
    
    def test_analyze_filter_options(self):
        """Test filter options analysis."""
        filter_options = self.data_processor.analyze_filter_options(self.sample_data)
        
        assert isinstance(filter_options, dict)
        assert "Company Category" in filter_options
        assert "Location Type" in filter_options
        assert len(filter_options["Company Category"]) == 2
        assert len(filter_options["Location Type"]) == 2
    
    def test_get_data_summary(self):
        """Test data summary generation."""
        summary = self.data_processor.get_data_summary(self.sample_data)
        
        assert isinstance(summary, dict)
        assert summary["total_jobs"] == 2
        assert "columns" in summary
        assert "missing_data" in summary
    
    def test_save_and_load_csv(self):
        """Test CSV save and load functionality."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_file = f.name
        
        try:
            # Save data
            success = self.data_processor.save_csv_data(self.sample_data, temp_file)
            assert success
            
            # Load data
            loaded_data = self.data_processor.load_csv_data(temp_file)
            assert loaded_data is not None
            assert len(loaded_data) == len(self.sample_data)
            assert list(loaded_data.columns) == list(self.sample_data.columns)
        
        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def test_load_invalid_csv(self):
        """Test loading invalid CSV file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("invalid,csv,data\n")
            temp_file = f.name
        
        try:
            result = self.data_processor.load_csv_data(temp_file)
            assert result is None
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file) 