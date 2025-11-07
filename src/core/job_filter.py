"""
Job filtering module with fuzzy matching capabilities.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from config.settings import FUZZY_MATCH_THRESHOLDS
from src.utils.fuzzy_matcher import (
    fuzzy_match, fuzzy_match_keywords, calculate_title_similarity,
    calculate_location_similarity, clean_text
)
from src.utils.logger import app_logger


class JobFilter:
    """
    Handles job filtering operations with fuzzy matching.
    """
    
    def __init__(self, thresholds: Optional[Dict[str, int]] = None):
        """
        Initialize JobFilter with fuzzy matching thresholds.
        
        Args:
            thresholds: Dictionary of field-specific thresholds
        """
        self.thresholds = thresholds or FUZZY_MATCH_THRESHOLDS.copy()
        self.logger = app_logger
        
        # Track filtering statistics
        self.filter_stats = {
            "total_jobs": 0,
            "filtered_jobs": 0,
            "filter_results": {}
        }
    
    def apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any], tag_checker: Any = None) -> pd.DataFrame:
        """
        Apply all filters to the DataFrame.
        
        Args:
            df: DataFrame with job data
            filters: Dictionary of filter configurations
            
        Returns:
            Filtered DataFrame
        """
        if df is None or df.empty:
            return df
        
        self.filter_stats["total_jobs"] = len(df)
        self.filter_stats["filtered_jobs"] = len(df)
        self.filter_stats["filter_results"] = {}
        
        filtered_df = df.copy()
        
        # Apply each filter type
        if "company_categories" in filters and filters["company_categories"]:
            filtered_df = self.filter_by_categories(
                filtered_df, "Company Category", filters["company_categories"]
            )
        
        if "overall_job_categories" in filters and filters["overall_job_categories"]:
            filtered_df = self.filter_by_categories(
                filtered_df, "Overall Job Category", filters["overall_job_categories"]
            )
        
        if "job_categories" in filters and filters["job_categories"]:
            filtered_df = self.filter_by_categories(
                filtered_df, "Job Category", filters["job_categories"]
            )
        
        if "location_types" in filters and filters["location_types"]:
            filtered_df = self.filter_by_categories(
                filtered_df, "Location Type", filters["location_types"]
            )
        
        if "title_keywords" in filters and filters["title_keywords"]:
            filtered_df = self.filter_by_keywords(
                filtered_df, "Title", filters["title_keywords"],
                self.thresholds.get("title", 85)
            )
        
        if "experience_range" in filters and filters["experience_range"]:
            min_exp = filters["experience_range"].get("min")
            max_exp = filters["experience_range"].get("max")
            filtered_df = self.filter_by_experience_range(
                filtered_df, min_exp, max_exp
            )
        
        if "geography" in filters and filters["geography"]:
            filtered_df = self.filter_by_geography(
                filtered_df, filters["geography"],
                self.thresholds.get("geography", 80)
            )
        
        if "skills_keywords" in filters and filters["skills_keywords"]:
            filtered_df = self.filter_by_skills(
                filtered_df, filters["skills_keywords"],
                self.thresholds.get("skills", 70)
            )
        
        if "salary_range" in filters and filters["salary_range"]:
            min_salary = filters["salary_range"].get("min")
            max_salary = filters["salary_range"].get("max")
            filtered_df = self.filter_by_salary_range(
                filtered_df, min_salary, max_salary
            )
        
        if "job_types" in filters and filters["job_types"]:
            filtered_df = self.filter_by_categories(
                filtered_df, "JobType", filters["job_types"]
            )
        
        if "tags" in filters and filters["tags"]:
            filtered_df = self.filter_by_tags(
                filtered_df, filters["tags"], tag_checker
            )
        
        self.filter_stats["filtered_jobs"] = len(filtered_df)
        self.logger.info(f"Filtered {self.filter_stats['total_jobs']} jobs to {self.filter_stats['filtered_jobs']} jobs")
        
        return filtered_df
    
    def filter_by_categories(self, df: pd.DataFrame, column: str, categories: List[str]) -> pd.DataFrame:
        """
        Filter by exact category matches.
        
        Args:
            df: DataFrame to filter
            column: Column name to filter on
            categories: List of categories to include
            
        Returns:
            Filtered DataFrame
        """
        if column not in df.columns:
            self.logger.warning(f"Column {column} not found in DataFrame")
            return df
        
        # Convert to string and handle NaN values
        df_filtered = df[df[column].astype(str).isin(categories)]
        
        self.filter_stats["filter_results"][f"{column}_categories"] = {
            "applied": True,
            "categories": categories,
            "jobs_before": len(df),
            "jobs_after": len(df_filtered)
        }
        
        return df_filtered
    
    def filter_by_keywords(self, df: pd.DataFrame, column: str, keywords: List[str], threshold: int) -> pd.DataFrame:
        """
        Filter by fuzzy keyword matching.
        
        Uses OR logic: a job matches if ANY of the keywords match.
        
        Args:
            df: DataFrame to filter
            column: Column name to filter on
            keywords: List of keywords to match
            threshold: Fuzzy matching threshold
            
        Returns:
            Filtered DataFrame with match scores
        """
        if column not in df.columns:
            self.logger.warning(f"Column {column} not found in DataFrame")
            return df
        
        # Add match scores column (as float to avoid dtype warnings)
        df_with_scores = df.copy()
        df_with_scores[f"{column}_match_score"] = 0.0
        
        matching_indices = []
        
        for idx, row in df.iterrows():
            text = str(row[column]) if pd.notna(row[column]) else ""
            if text:
                # Find best match score (OR logic: ANY keyword can match)
                best_score = 0
                for keyword in keywords:
                    matches = fuzzy_match_keywords(text, [keyword], threshold)
                    if matches:
                        best_score = max(best_score, matches[0][1])
                
                if best_score > 0:
                    df_with_scores.at[idx, f"{column}_match_score"] = best_score
                    matching_indices.append(idx)
        
        # Filter to only matching rows
        df_filtered = df_with_scores.loc[matching_indices]
        
        self.filter_stats["filter_results"][f"{column}_keywords"] = {
            "applied": True,
            "keywords": keywords,
            "threshold": threshold,
            "jobs_before": len(df),
            "jobs_after": len(df_filtered)
        }
        
        return df_filtered
    
    def filter_by_experience_range(self, df: pd.DataFrame, min_exp: Optional[int], max_exp: Optional[int]) -> pd.DataFrame:
        """
        Filter by experience range.
        
        Args:
            df: DataFrame to filter
            min_exp: Minimum experience years
            max_exp: Maximum experience years
            
        Returns:
            Filtered DataFrame
        """
        df_filtered = df.copy()
        
        # Filter by Min Experience
        if min_exp is not None:
            df_filtered = df_filtered[
                (df_filtered["Min Experience"].isna()) |
                (pd.to_numeric(df_filtered["Min Experience"], errors='coerce') >= min_exp)
            ]
        
        # Filter by Max Experience
        if max_exp is not None:
            df_filtered = df_filtered[
                (df_filtered["Max Experience"].isna()) |
                (pd.to_numeric(df_filtered["Max Experience"], errors='coerce') <= max_exp)
            ]
        
        self.filter_stats["filter_results"]["experience_range"] = {
            "applied": True,
            "min_experience": min_exp,
            "max_experience": max_exp,
            "jobs_before": len(df),
            "jobs_after": len(df_filtered)
        }
        
        return df_filtered
    
    def filter_by_geography(self, df: pd.DataFrame, geography_filters: Dict[str, List[str]], threshold: int) -> pd.DataFrame:
        """
        Filter by geographic criteria with fuzzy matching.
        
        Args:
            df: DataFrame to filter
            geography_filters: Dictionary with country, state, city filters
            threshold: Fuzzy matching threshold
            
        Returns:
            Filtered DataFrame
        """
        df_filtered = df.copy()
        
        # Filter by Country
        if "countries" in geography_filters and geography_filters["countries"]:
            df_filtered = self.filter_by_categories(
                df_filtered, "Country", geography_filters["countries"]
            )
        
        # Filter by State with fuzzy matching
        if "states" in geography_filters and geography_filters["states"]:
            df_filtered = self.filter_by_keywords(
                df_filtered, "State", geography_filters["states"], threshold
            )
        
        # Filter by City with fuzzy matching
        if "cities" in geography_filters and geography_filters["cities"]:
            df_filtered = self.filter_by_keywords(
                df_filtered, "City", geography_filters["cities"], threshold
            )
        
        self.filter_stats["filter_results"]["geography"] = {
            "applied": True,
            "filters": geography_filters,
            "threshold": threshold,
            "jobs_before": len(df),
            "jobs_after": len(df_filtered)
        }
        
        return df_filtered
    
    def filter_by_skills(self, df: pd.DataFrame, skills: List[str], threshold: int) -> pd.DataFrame:
        """
        Filter by skills with fuzzy matching.
        
        Args:
            df: DataFrame to filter
            skills: List of skills to match
            threshold: Fuzzy matching threshold
            
        Returns:
            Filtered DataFrame
        """
        if "Skills" not in df.columns:
            self.logger.warning("Skills column not found in DataFrame")
            return df
        
        df_filtered = df.copy()
        df_filtered["skills_match_score"] = 0.0
        
        matching_indices = []
        
        for idx, row in df.iterrows():
            skills_text = str(row["Skills"]) if pd.notna(row["Skills"]) else ""
            if skills_text:
                # Find best match score for any skill
                best_score = 0
                for skill in skills:
                    matches = fuzzy_match_keywords(skills_text, [skill], threshold)
                    if matches:
                        best_score = max(best_score, matches[0][1])
                
                if best_score > 0:
                    df_filtered.at[idx, "skills_match_score"] = best_score
                    matching_indices.append(idx)
        
        # Filter to only matching rows
        df_filtered = df_filtered.loc[matching_indices]
        
        self.filter_stats["filter_results"]["skills"] = {
            "applied": True,
            "skills": skills,
            "threshold": threshold,
            "jobs_before": len(df),
            "jobs_after": len(df_filtered)
        }
        
        return df_filtered
    
    def filter_by_tags(self, df: pd.DataFrame, selected_tags: List[str], tag_checker: Any = None) -> pd.DataFrame:
        """
        Filter jobs by tags.
        
        Args:
            df: DataFrame to filter (must have 'job_id' column)
            selected_tags: List of tag names to filter by (jobs must have at least one of these tags)
            tag_checker: Object with has_tag(job_id, tag) method (e.g., JobTagger instance)
            
        Returns:
            Filtered DataFrame containing only jobs with at least one of the selected tags
        """
        if not selected_tags:
            return df
        
        if 'job_id' not in df.columns:
            self.logger.warning("Cannot filter by tags: 'job_id' column not found")
            return df
        
        if tag_checker is None:
            self.logger.warning("Cannot filter by tags: no tag_checker provided")
            return df
        
        # Filter to jobs that have at least one of the selected tags
        def has_any_tag(job_id: str) -> bool:
            """Check if job has any of the selected tags."""
            for tag in selected_tags:
                if hasattr(tag_checker, 'has_tag') and tag_checker.has_tag(str(job_id), tag):
                    return True
            return False
        
        # Apply tag filter
        mask = df['job_id'].astype(str).apply(has_any_tag)
        filtered_df = df[mask].copy()
        
        self.logger.info(f"Tag filter ({selected_tags}): {len(df)} -> {len(filtered_df)} jobs")
        return filtered_df
    
    def filter_by_salary_range(self, df: pd.DataFrame, min_salary: Optional[int], max_salary: Optional[int]) -> pd.DataFrame:
        """
        Filter by salary range.
        
        Args:
            df: DataFrame to filter
            min_salary: Minimum salary
            max_salary: Maximum salary
            
        Returns:
            Filtered DataFrame
        """
        df_filtered = df.copy()
        
        # Filter by Min Salary
        if min_salary is not None:
            df_filtered = df_filtered[
                (df_filtered["Min Salary"].isna()) |
                (pd.to_numeric(df_filtered["Min Salary"], errors='coerce') >= min_salary)
            ]
        
        # Filter by Max Salary
        if max_salary is not None:
            df_filtered = df_filtered[
                (df_filtered["Max Salary"].isna()) |
                (pd.to_numeric(df_filtered["Max Salary"], errors='coerce') <= max_salary)
            ]
        
        self.filter_stats["filter_results"]["salary_range"] = {
            "applied": True,
            "min_salary": min_salary,
            "max_salary": max_salary,
            "jobs_before": len(df),
            "jobs_after": len(df_filtered)
        }
        
        return df_filtered
    
    def get_filter_summary(self) -> Dict[str, Any]:
        """
        Get summary of filtering results.
        
        Returns:
            Dictionary with filtering statistics
        """
        return {
            "total_jobs": self.filter_stats["total_jobs"],
            "filtered_jobs": self.filter_stats["filtered_jobs"],
            "reduction_percentage": round(
                ((self.filter_stats["total_jobs"] - self.filter_stats["filtered_jobs"]) / 
                 self.filter_stats["total_jobs"]) * 100, 2
            ) if self.filter_stats["total_jobs"] > 0 else 0,
            "filter_results": self.filter_stats["filter_results"]
        }
    
    def reset_stats(self):
        """Reset filtering statistics."""
        self.filter_stats = {
            "total_jobs": 0,
            "filtered_jobs": 0,
            "filter_results": {}
        } 