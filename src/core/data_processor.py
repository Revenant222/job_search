"""
Data processing module for AI Job Filter Agent.
"""
import os
import hashlib
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
from config.settings import CSV_ENCODING, CSV_DELIMITER, OUTPUT_COLUMNS
from src.utils.logger import app_logger
from src.utils.validators import validate_csv_file, validate_job_data


class DataProcessor:
    """
    Handles data processing operations for job filtering.
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize DataProcessor.
        
        Args:
            data_dir: Directory for data files
        """
        self.data_dir = data_dir
        self.csv_source_dir = os.path.join(data_dir, "csv_source")
        self.csv_output_dir = os.path.join(data_dir, "csv_output")
        
        # Ensure directories exist
        os.makedirs(self.csv_source_dir, exist_ok=True)
        os.makedirs(self.csv_output_dir, exist_ok=True)
        
        self.logger = app_logger
    
    def load_csv_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        Load data from CSV file.
        
        Args:
            file_path: Path to CSV file
            
        Returns:
            DataFrame with job data or None if loading fails
        """
        try:
            if not validate_csv_file(file_path):
                self.logger.error(f"Invalid CSV file: {file_path}")
                return None
            
            # Load CSV with specified encoding and delimiter
            df = pd.read_csv(
                file_path,
                encoding=CSV_ENCODING,
                delimiter=CSV_DELIMITER,
                low_memory=False
            )
            
            # Validate the loaded data
            validation_result = validate_job_data(df)
            if not validation_result["is_valid"]:
                self.logger.error(f"Data validation failed: {validation_result['errors']}")
                return None
            
            if validation_result["warnings"]:
                self.logger.warning(f"Data validation warnings: {validation_result['warnings']}")
            
            self.logger.info(f"Successfully loaded {len(df)} jobs from {file_path}")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading CSV file {file_path}: {str(e)}")
            return None
    
    def save_csv_data(self, df: pd.DataFrame, file_path: str) -> bool:
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            file_path: Path to save the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save DataFrame to CSV
            df.to_csv(
                file_path,
                index=False,
                encoding=CSV_ENCODING,
                sep=CSV_DELIMITER
            )
            
            self.logger.info(f"Successfully saved {len(df)} jobs to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving CSV file {file_path}: {str(e)}")
            return False
    
    def generate_job_id(self, job_row: Dict[str, Any]) -> str:
        """
        Create unique identifier for a job.
        
        Args:
            job_row: Job data as dictionary
            
        Returns:
            Unique job ID
        """
        # Use stable fields for ID generation
        company = str(job_row.get("Company", "")).lower().strip()
        title = str(job_row.get("Title", "")).lower().strip()
        location = str(job_row.get("City", "")).lower().strip()
        
        # Create stable key
        stable_key = f"{company}|{title}|{location}"
        
        # Generate hash
        job_hash = hashlib.md5(stable_key.encode()).hexdigest()[:12]
        
        return job_hash
    
    def add_job_ids(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add job IDs to DataFrame.
        
        Args:
            df: DataFrame with job data
            
        Returns:
            DataFrame with job IDs added
        """
        if df is None or df.empty:
            return df
        
        # Convert DataFrame to list of dictionaries for processing
        jobs_list = df.to_dict('records')
        
        # Add job IDs
        for job in jobs_list:
            job['job_id'] = self.generate_job_id(job)
        
        # Convert back to DataFrame
        result_df = pd.DataFrame(jobs_list)
        
        self.logger.info(f"Added job IDs to {len(result_df)} jobs")
        return result_df
    
    def analyze_filter_options(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Extract unique values for filter option generation.
        
        Args:
            df: DataFrame with job data
            
        Returns:
            Dictionary with filter options for each field
        """
        if df is None or df.empty:
            return {}
        
        filter_options = {}
        
        # Categorical fields for multi-select filters
        categorical_fields = [
            "Company Category", "Overall Job Category", "Job Category", "Location Type"
        ]
        
        for field in categorical_fields:
            if field in df.columns:
                # Get unique values, remove NaN, sort
                unique_values = df[field].dropna().unique()
                unique_values = [str(val).strip() for val in unique_values if str(val).strip()]
                unique_values = sorted(list(set(unique_values)))
                filter_options[field] = unique_values
        
        # Geographic fields
        geographic_fields = ["Country", "State", "City"]
        for field in geographic_fields:
            if field in df.columns:
                unique_values = df[field].dropna().unique()
                unique_values = [str(val).strip() for val in unique_values if str(val).strip()]
                unique_values = sorted(list(set(unique_values)))
                filter_options[field] = unique_values
        
        # Job type field
        if "JobType" in df.columns:
            unique_values = df["JobType"].dropna().unique()
            unique_values = [str(val).strip() for val in unique_values if str(val).strip()]
            unique_values = sorted(list(set(unique_values)))
            filter_options["JobType"] = unique_values
        
        # Skills analysis
        if "Skills" in df.columns:
            all_skills = []
            for skills_str in df["Skills"].dropna():
                if isinstance(skills_str, str):
                    # Split by comma and clean
                    skills = [skill.strip() for skill in skills_str.split(",") if skill.strip()]
                    all_skills.extend(skills)
            
            # Get unique skills
            unique_skills = sorted(list(set(all_skills)))
            filter_options["Skills"] = unique_skills
        
        # Experience range analysis
        if "Min Experience" in df.columns:
            min_exp_values = df["Min Experience"].dropna()
            if not min_exp_values.empty:
                try:
                    min_exp_values = pd.to_numeric(min_exp_values, errors='coerce')
                    min_exp_values = min_exp_values.dropna()
                    if not min_exp_values.empty:
                        filter_options["Min Experience"] = {
                            "min": int(min_exp_values.min()),
                            "max": int(min_exp_values.max())
                        }
                except Exception as e:
                    self.logger.warning(f"Error processing Min Experience: {e}")
        
        if "Max Experience" in df.columns:
            max_exp_values = df["Max Experience"].dropna()
            if not max_exp_values.empty:
                try:
                    max_exp_values = pd.to_numeric(max_exp_values, errors='coerce')
                    max_exp_values = max_exp_values.dropna()
                    if not max_exp_values.empty:
                        filter_options["Max Experience"] = {
                            "min": int(max_exp_values.min()),
                            "max": int(max_exp_values.max())
                        }
                except Exception as e:
                    self.logger.warning(f"Error processing Max Experience: {e}")
        
        # Salary range analysis
        if "Min Salary" in df.columns:
            min_salary_values = df["Min Salary"].dropna()
            if not min_salary_values.empty:
                try:
                    min_salary_values = pd.to_numeric(min_salary_values, errors='coerce')
                    min_salary_values = min_salary_values.dropna()
                    if not min_salary_values.empty:
                        filter_options["Min Salary"] = {
                            "min": int(min_salary_values.min()),
                            "max": int(min_salary_values.max())
                        }
                except Exception as e:
                    self.logger.warning(f"Error processing Min Salary: {e}")
        
        if "Max Salary" in df.columns:
            max_salary_values = df["Max Salary"].dropna()
            if not max_salary_values.empty:
                try:
                    max_salary_values = pd.to_numeric(max_salary_values, errors='coerce')
                    max_salary_values = max_salary_values.dropna()
                    if not max_salary_values.empty:
                        filter_options["Max Salary"] = {
                            "min": int(max_salary_values.min()),
                            "max": int(max_salary_values.max())
                        }
                except Exception as e:
                    self.logger.warning(f"Error processing Max Salary: {e}")
        
        self.logger.info(f"Generated filter options for {len(filter_options)} fields")
        return filter_options
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Get summary statistics for the dataset.
        
        Args:
            df: DataFrame with job data
            
        Returns:
            Dictionary with summary statistics
        """
        if df is None or df.empty:
            return {"total_jobs": 0}
        
        summary = {
            "total_jobs": len(df),
            "columns": list(df.columns),
            "missing_data": {}
        }
        
        # Calculate missing data percentages
        for column in df.columns:
            missing_count = df[column].isna().sum()
            missing_percentage = (missing_count / len(df)) * 100
            summary["missing_data"][column] = {
                "count": missing_count,
                "percentage": round(missing_percentage, 2)
            }
        
        # Geographic distribution
        if "Country" in df.columns:
            country_counts = df["Country"].value_counts().head(10).to_dict()
            summary["top_countries"] = country_counts
        
        # Job category distribution
        if "Job Category" in df.columns:
            category_counts = df["Job Category"].value_counts().head(10).to_dict()
            summary["top_categories"] = category_counts
        
        # Location type distribution
        if "Location Type" in df.columns:
            location_counts = df["Location Type"].value_counts().to_dict()
            summary["location_types"] = location_counts
        
        return summary
    
    def cache_data_with_timestamp(self, df: pd.DataFrame, source_name: str) -> str:
        """
        Cache data with timestamp for avoiding redundant processing.
        
        Args:
            df: DataFrame to cache
            source_name: Name of the data source
            
        Returns:
            Path to cached file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{source_name}_{timestamp}.csv"
        file_path = os.path.join(self.csv_source_dir, filename)
        
        if self.save_csv_data(df, file_path):
            self.logger.info(f"Cached data to {file_path}")
            return file_path
        else:
            self.logger.error(f"Failed to cache data to {file_path}")
            return "" 