"""
Validation utilities for AI Job Filter Agent.
"""
import os
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd


def validate_csv_file(file_path: str) -> bool:
    """
    Validate that a CSV file exists and is readable.
    
    Args:
        file_path: Path to CSV file
        
    Returns:
        True if file is valid, False otherwise
    """
    if not file_path or not os.path.exists(file_path):
        return False
    
    try:
        # Try to read the first few lines to validate format
        pd.read_csv(file_path, nrows=5)
        return True
    except Exception:
        return False


def validate_job_data(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate job data structure and content.
    
    Args:
        df: DataFrame containing job data
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "row_count": len(df) if df is not None else 0,
        "missing_columns": [],
        "empty_columns": []
    }
    
    if df is None or df.empty:
        validation_result["is_valid"] = False
        validation_result["errors"].append("DataFrame is empty or None")
        return validation_result
    
    # Expected columns from the technical specification
    expected_columns = [
        "Company Category", "Company", "Overall Job Category", "Job Category",
        "Title", "Min Experience", "Max Experience", "Country", "State", "City",
        "Location Type", "JobType", "Job Link", "Activated Date", "Skills",
        "Min Salary", "Max Salary"
    ]
    
    # Check for missing columns
    missing_columns = [col for col in expected_columns if col not in df.columns]
    if missing_columns:
        validation_result["missing_columns"] = missing_columns
        validation_result["warnings"].append(f"Missing columns: {missing_columns}")
    
    # Check for empty columns
    empty_columns = []
    for col in df.columns:
        if df[col].isna().all() or (df[col].astype(str).str.strip() == "").all():
            empty_columns.append(col)
    
    if empty_columns:
        validation_result["empty_columns"] = empty_columns
        validation_result["warnings"].append(f"Empty columns: {empty_columns}")
    
    # Check for required columns
    required_columns = ["Company", "Title", "Job Link"]
    for col in required_columns:
        if col not in df.columns:
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Required column missing: {col}")
        elif df[col].isna().all():
            validation_result["is_valid"] = False
            validation_result["errors"].append(f"Required column is empty: {col}")
    
    return validation_result


def validate_url(url: str) -> bool:
    """
    Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Basic URL pattern
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(url_pattern.match(url))


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(email_pattern.match(email))


def validate_date_format(date_str: str, format_str: str = "%d %b %Y") -> bool:
    """
    Validate date format.
    
    Args:
        date_str: Date string to validate
        format_str: Expected date format
        
    Returns:
        True if date is valid, False otherwise
    """
    if not date_str or not isinstance(date_str, str):
        return False
    
    try:
        datetime.strptime(date_str, format_str)
        return True
    except ValueError:
        return False


def validate_numeric_range(value: Any, min_val: Optional[float] = None, max_val: Optional[float] = None) -> bool:
    """
    Validate numeric value is within specified range.
    
    Args:
        value: Value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        True if value is valid, False otherwise
    """
    if value is None:
        return True  # Allow None values
    
    try:
        num_value = float(value)
    except (ValueError, TypeError):
        return False
    
    if min_val is not None and num_value < min_val:
        return False
    
    if max_val is not None and num_value > max_val:
        return False
    
    return True


def validate_fuzzy_threshold(threshold: int) -> bool:
    """
    Validate fuzzy matching threshold.
    
    Args:
        threshold: Threshold value to validate
        
    Returns:
        True if threshold is valid, False otherwise
    """
    return isinstance(threshold, int) and 0 <= threshold <= 100


def validate_filter_config(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate filter configuration.
    
    Args:
        filters: Filter configuration dictionary
        
    Returns:
        Dictionary with validation results
    """
    validation_result = {
        "is_valid": True,
        "errors": [],
        "warnings": []
    }
    
    if not filters:
        validation_result["warnings"].append("No filters specified")
        return validation_result
    
    # Validate fuzzy thresholds
    if "fuzzy_thresholds" in filters:
        thresholds = filters["fuzzy_thresholds"]
        for field, threshold in thresholds.items():
            if not validate_fuzzy_threshold(threshold):
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Invalid fuzzy threshold for {field}: {threshold}")
    
    # Validate numeric ranges
    numeric_fields = ["min_experience", "max_experience", "min_salary", "max_salary"]
    for field in numeric_fields:
        if field in filters:
            value = filters[field]
            if value is not None and not validate_numeric_range(value, 0):
                validation_result["is_valid"] = False
                validation_result["errors"].append(f"Invalid numeric value for {field}: {value}")
    
    # Validate salary range logic
    if "min_salary" in filters and "max_salary" in filters:
        min_salary = filters["min_salary"]
        max_salary = filters["max_salary"]
        if (min_salary is not None and max_salary is not None and 
            min_salary > max_salary):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Min salary cannot be greater than max salary")
    
    # Validate experience range logic
    if "min_experience" in filters and "max_experience" in filters:
        min_exp = filters["min_experience"]
        max_exp = filters["max_experience"]
        if (min_exp is not None and max_exp is not None and 
            min_exp > max_exp):
            validation_result["is_valid"] = False
            validation_result["errors"].append("Min experience cannot be greater than max experience")
    
    return validation_result


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    if not filename:
        return "unnamed_file"
    
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        return "unnamed_file"
    
    return sanitized 