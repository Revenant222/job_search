"""
Streamlit application for AI Job Filter Agent.
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from typing import Dict, Any, Optional

# Import our modules
from src.core.data_processor import DataProcessor
from src.core.job_filter import JobFilter
from config.settings import FUZZY_MATCH_THRESHOLDS, APPLICATION_STATUS_OPTIONS
from src.utils.logger import app_logger


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="AI Job Filter Agent",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 AI Job Filter Agent")
    st.markdown("Filter and analyze job listings with intelligent fuzzy matching")
    
    # Initialize session state
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False
    if 'filtered_data' not in st.session_state:
        st.session_state.filtered_data = None
    if 'filter_options' not in st.session_state:
        st.session_state.filter_options = {}
    if 'data_summary' not in st.session_state:
        st.session_state.data_summary = {}
    
    # Sidebar for data loading
    with st.sidebar:
        st.header("📁 Data Loading")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload CSV file",
            type=['csv'],
            help="Upload a CSV file with job data"
        )
        
        if uploaded_file is not None:
            if st.button("Load Data"):
                load_data(uploaded_file)
        
        # Data summary
        if st.session_state.data_loaded:
            st.success("✅ Data loaded successfully!")
            st.metric("Total Jobs", st.session_state.data_summary.get("total_jobs", 0))
            
            if st.session_state.filtered_data is not None:
                st.metric("Filtered Jobs", len(st.session_state.filtered_data))
    
    # Main content area
    if st.session_state.data_loaded:
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["🎯 Filter Configuration", "📊 Results", "📈 Data Analysis"])
        
        with tab1:
            show_filter_configuration()
        
        with tab2:
            show_results()
        
        with tab3:
            show_data_analysis()
    else:
        st.info("👆 Please upload a CSV file to get started")
        
        # Show sample data structure
        st.subheader("Expected Data Structure")
        st.markdown("""
        Your CSV file should contain the following columns:
        
        | Column | Description | Example |
        |--------|-------------|---------|
        | Company Category | Type of company | Gaming Company |
        | Company | Company name | Cloud Imperium Games |
        | Overall Job Category | High-level job category | Engineering & Development |
        | Job Category | Specific job category | DevOps |
        | Title | Job title | Azure Cloud Engineer |
        | Min Experience | Minimum years of experience | 2 |
        | Max Experience | Maximum years of experience | 5 |
        | Country | Country | Netherlands |
        | State | State/Province | North Holland |
        | City | City | Amsterdam |
        | Location Type | Work location type | On Site |
        | JobType | Employment type | Full Time |
        | Job Link | URL to job posting | https://... |
        | Activated Date | Date job was posted | 02 Aug 2025 |
        | Skills | Required skills | "Agile Development, AWS, Azure" |
        | Min Salary | Minimum salary | 50000 |
        | Max Salary | Maximum salary | 80000 |
        """)


def load_data(uploaded_file):
    """Load data from uploaded file."""
    try:
        # Create temporary file
        temp_file = f"temp_upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        with open(temp_file, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Load data using DataProcessor
        data_processor = DataProcessor()
        df = data_processor.load_csv_data(temp_file)
        
        if df is not None:
            # Add job IDs
            df = data_processor.add_job_ids(df)
            
            # Store in session state
            st.session_state.raw_data = df
            st.session_state.data_loaded = True
            
            # Generate filter options
            st.session_state.filter_options = data_processor.analyze_filter_options(df)
            
            # Get data summary
            st.session_state.data_summary = data_processor.get_data_summary(df)
            
            # Clean up temp file
            os.remove(temp_file)
            
            st.success(f"Successfully loaded {len(df)} jobs!")
            
        else:
            st.error("Failed to load data. Please check your CSV file format.")
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        app_logger.error(f"Error loading data: {str(e)}")


def show_filter_configuration():
    """Show filter configuration interface."""
    st.header("🎯 Filter Configuration")
    
    if not st.session_state.data_loaded:
        st.warning("Please load data first")
        return
    
    # Initialize JobFilter
    job_filter = JobFilter()
    
    # Create filter form
    with st.form("filter_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Categorical Filters")
            
            # Company Category
            if "Company Category" in st.session_state.filter_options:
                company_categories = st.multiselect(
                    "Company Category",
                    options=st.session_state.filter_options["Company Category"],
                    help="Select company categories to include"
                )
            else:
                company_categories = []
            
            # Overall Job Category
            if "Overall Job Category" in st.session_state.filter_options:
                overall_job_categories = st.multiselect(
                    "Overall Job Category",
                    options=st.session_state.filter_options["Overall Job Category"],
                    help="Select overall job categories to include"
                )
            else:
                overall_job_categories = []
            
            # Job Category
            if "Job Category" in st.session_state.filter_options:
                job_categories = st.multiselect(
                    "Job Category",
                    options=st.session_state.filter_options["Job Category"],
                    help="Select specific job categories to include"
                )
            else:
                job_categories = []
            
            # Location Type
            if "Location Type" in st.session_state.filter_options:
                location_types = st.multiselect(
                    "Location Type",
                    options=st.session_state.filter_options["Location Type"],
                    help="Select work location types"
                )
            else:
                location_types = []
            
            # Job Type
            if "JobType" in st.session_state.filter_options:
                job_types = st.multiselect(
                    "Job Type",
                    options=st.session_state.filter_options["JobType"],
                    help="Select employment types"
                )
            else:
                job_types = []
        
        with col2:
            st.subheader("Keyword & Range Filters")
            
            # Title Keywords
            title_keywords = st.text_input(
                "Title Keywords",
                help="Enter keywords to search in job titles (comma-separated)"
            )
            title_keywords = [kw.strip() for kw in title_keywords.split(",") if kw.strip()] if title_keywords else []
            
            # Skills Keywords
            skills_keywords = st.text_input(
                "Skills Keywords",
                help="Enter skills to search for (comma-separated)"
            )
            skills_keywords = [kw.strip() for kw in skills_keywords.split(",") if kw.strip()] if skills_keywords else []
            
            # Experience Range
            st.subheader("Experience Range")
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                min_experience = st.number_input("Min Experience (years)", min_value=0, value=None, step=1)
            with exp_col2:
                max_experience = st.number_input("Max Experience (years)", min_value=0, value=None, step=1)
            
            # Salary Range
            st.subheader("Salary Range")
            sal_col1, sal_col2 = st.columns(2)
            with sal_col1:
                min_salary = st.number_input("Min Salary", min_value=0, value=None, step=1000)
            with sal_col2:
                max_salary = st.number_input("Max Salary", min_value=0, value=None, step=1000)
        
        # Fuzzy Matching Thresholds
        st.subheader("🔍 Fuzzy Matching Thresholds")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            title_threshold = st.slider(
                "Title Match Threshold",
                min_value=0, max_value=100, value=FUZZY_MATCH_THRESHOLDS["title"],
                help="Higher = stricter matching for job titles"
            )
        
        with col2:
            skills_threshold = st.slider(
                "Skills Match Threshold",
                min_value=0, max_value=100, value=FUZZY_MATCH_THRESHOLDS["skills"],
                help="Higher = stricter matching for skills"
            )
        
        with col3:
            geography_threshold = st.slider(
                "Geography Match Threshold",
                min_value=0, max_value=100, value=FUZZY_MATCH_THRESHOLDS["geography"],
                help="Higher = stricter matching for locations"
            )
        
        # Apply filters button
        if st.form_submit_button("🚀 Apply Filters"):
            apply_filters(
                company_categories, overall_job_categories, job_categories,
                location_types, job_types, title_keywords, skills_keywords,
                min_experience, max_experience, min_salary, max_salary,
                title_threshold, skills_threshold, geography_threshold
            )


def apply_filters(company_categories, overall_job_categories, job_categories,
                 location_types, job_types, title_keywords, skills_keywords,
                 min_experience, max_experience, min_salary, max_salary,
                 title_threshold, skills_threshold, geography_threshold):
    """Apply filters to the data."""
    try:
        # Prepare filter configuration
        filters = {
            "company_categories": company_categories,
            "overall_job_categories": overall_job_categories,
            "job_categories": job_categories,
            "location_types": location_types,
            "job_types": job_types,
            "title_keywords": title_keywords,
            "skills_keywords": skills_keywords,
            "experience_range": {
                "min": min_experience,
                "max": max_experience
            },
            "salary_range": {
                "min": min_salary,
                "max": max_salary
            }
        }
        
        # Update thresholds
        thresholds = {
            "title": title_threshold,
            "skills": skills_threshold,
            "geography": geography_threshold
        }
        
        # Apply filters
        job_filter = JobFilter(thresholds)
        filtered_df = job_filter.apply_filters(st.session_state.raw_data, filters)
        
        # Store results
        st.session_state.filtered_data = filtered_df
        st.session_state.filter_summary = job_filter.get_filter_summary()
        
        st.success(f"✅ Applied filters! Found {len(filtered_df)} matching jobs")
        
    except Exception as e:
        st.error(f"Error applying filters: {str(e)}")
        app_logger.error(f"Error applying filters: {str(e)}")


def show_results():
    """Show filtering results."""
    st.header("📊 Filtering Results")
    
    if st.session_state.filtered_data is None:
        st.info("Apply filters to see results")
        return
    
    # Show summary
    if hasattr(st.session_state, 'filter_summary'):
        summary = st.session_state.filter_summary
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Jobs", summary["total_jobs"])
        with col2:
            st.metric("Filtered Jobs", summary["filtered_jobs"])
        with col3:
            st.metric("Reduction", f"{summary['reduction_percentage']}%")
        with col4:
            st.metric("Match Rate", f"{round((summary['filtered_jobs'] / summary['total_jobs']) * 100, 1)}%")
    
    # Show detailed results
    st.subheader("Matching Jobs")
    
    # Display options
    display_cols = st.multiselect(
        "Select columns to display",
        options=st.session_state.filtered_data.columns.tolist(),
        default=["Company", "Title", "Location Type", "Country", "City", "Job Link"]
    )
    
    if display_cols:
        st.dataframe(
            st.session_state.filtered_data[display_cols],
            use_container_width=True,
            hide_index=True
        )
    
    # Download options
    st.subheader("📥 Download Results")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Download Filtered Data (CSV)"):
            csv = st.session_state.filtered_data.to_csv(index=False)
            st.download_button(
                label="Click to download",
                data=csv,
                file_name=f"filtered_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("Download All Data (CSV)"):
            csv = st.session_state.filtered_data.to_csv(index=False)
            st.download_button(
                label="Click to download",
                data=csv,
                file_name=f"all_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )


def show_data_analysis():
    """Show data analysis and insights."""
    st.header("📈 Data Analysis")
    
    if not st.session_state.data_loaded:
        st.info("Please load data first")
        return
    
    summary = st.session_state.data_summary
    
    # Basic statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Jobs", summary["total_jobs"])
    
    with col2:
        st.metric("Columns", len(summary["columns"]))
    
    with col3:
        if "missing_data" in summary:
            avg_missing = sum(info["percentage"] for info in summary["missing_data"].values()) / len(summary["missing_data"])
            st.metric("Avg Missing Data", f"{avg_missing:.1f}%")
    
    # Geographic distribution
    if "top_countries" in summary:
        st.subheader("🌍 Top Countries")
        countries_df = pd.DataFrame(
            list(summary["top_countries"].items()),
            columns=["Country", "Job Count"]
        )
        st.bar_chart(countries_df.set_index("Country"))
    
    # Job category distribution
    if "top_categories" in summary:
        st.subheader("💼 Top Job Categories")
        categories_df = pd.DataFrame(
            list(summary["top_categories"].items()),
            columns=["Category", "Job Count"]
        )
        st.bar_chart(categories_df.set_index("Category"))
    
    # Location type distribution
    if "location_types" in summary:
        st.subheader("📍 Location Types")
        location_df = pd.DataFrame(
            list(summary["location_types"].items()),
            columns=["Location Type", "Job Count"]
        )
        st.pie_chart(location_df.set_index("Location Type"))
    
    # Missing data analysis
    if "missing_data" in summary:
        st.subheader("📊 Missing Data Analysis")
        missing_df = pd.DataFrame(
            [(col, info["count"], info["percentage"]) for col, info in summary["missing_data"].items()],
            columns=["Column", "Missing Count", "Missing Percentage"]
        )
        st.dataframe(missing_df, use_container_width=True)


if __name__ == "__main__":
    main() 