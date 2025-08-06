"""
Page components for Streamlit interface.
"""
import streamlit as st
import pandas as pd
from typing import Dict, Any, Optional
from src.ui.components import (
    display_filter_summary, display_data_table, create_download_section,
    display_error_message, display_success_message, display_info_message
)


def show_welcome_page():
    """Show welcome page with project information."""
    st.title("🔍 AI Job Filter Agent")
    st.markdown("Filter and analyze job listings with intelligent fuzzy matching")
    
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
    
    # Show features
    st.subheader("🚀 Features")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Smart Filtering**
        - Multi-criteria filtering
        - Fuzzy matching for titles and skills
        - Geographic filtering
        - Experience and salary ranges
        
        **📊 Data Analysis**
        - Job distribution analysis
        - Missing data insights
        - Geographic trends
        - Category breakdowns
        """)
    
    with col2:
        st.markdown("""
        **🔍 Fuzzy Matching**
        - Configurable thresholds
        - Intelligent keyword matching
        - Location similarity scoring
        - Skills extraction
        
        **📥 Export Options**
        - CSV download
        - Filtered results export
        - Data analysis reports
        - Custom column selection
        """)


def show_filter_page():
    """Show filter configuration page."""
    st.header("🎯 Filter Configuration")
    
    if not st.session_state.get('data_loaded', False):
        st.warning("Please load data first")
        return
    
    # This will be implemented in the main streamlit_app.py
    st.info("Filter configuration interface will be shown here")


def show_results_page():
    """Show results page."""
    st.header("📊 Filtering Results")
    
    if st.session_state.get('filtered_data') is None:
        st.info("Apply filters to see results")
        return
    
    # Show summary
    if hasattr(st.session_state, 'filter_summary'):
        display_filter_summary(st.session_state.filter_summary)
    
    # Show detailed results
    display_data_table(
        st.session_state.filtered_data,
        "Matching Jobs"
    )
    
    # Download options
    create_download_section(
        st.session_state.filtered_data,
        "filtered_jobs"
    )


def show_analysis_page():
    """Show data analysis page."""
    st.header("📈 Data Analysis")
    
    if not st.session_state.get('data_loaded', False):
        st.info("Please load data first")
        return
    
    summary = st.session_state.get('data_summary', {})
    
    # Basic statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Jobs", summary.get("total_jobs", 0))
    
    with col2:
        st.metric("Columns", len(summary.get("columns", [])))
    
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


def show_settings_page():
    """Show settings page."""
    st.header("⚙️ Settings")
    
    st.subheader("Fuzzy Matching Thresholds")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        title_threshold = st.slider(
            "Title Match Threshold",
            min_value=0, max_value=100, value=85,
            help="Higher = stricter matching for job titles"
        )
    
    with col2:
        skills_threshold = st.slider(
            "Skills Match Threshold",
            min_value=0, max_value=100, value=70,
            help="Higher = stricter matching for skills"
        )
    
    with col3:
        geography_threshold = st.slider(
            "Geography Match Threshold",
            min_value=0, max_value=100, value=80,
            help="Higher = stricter matching for locations"
        )
    
    # Save settings
    if st.button("Save Settings"):
        st.session_state.fuzzy_thresholds = {
            "title": title_threshold,
            "skills": skills_threshold,
            "geography": geography_threshold
        }
        display_success_message("Settings saved successfully!")
    
    # Show current settings
    if hasattr(st.session_state, 'fuzzy_thresholds'):
        st.subheader("Current Settings")
        st.json(st.session_state.fuzzy_thresholds)


def show_help_page():
    """Show help and documentation page."""
    st.header("❓ Help & Documentation")
    
    st.subheader("Getting Started")
    st.markdown("""
    1. **Upload Data**: Use the sidebar to upload your CSV file with job data
    2. **Configure Filters**: Go to the Filter Configuration tab to set up your filters
    3. **Apply Filters**: Click 'Apply Filters' to process your data
    4. **View Results**: Check the Results tab to see matching jobs
    5. **Analyze Data**: Use the Data Analysis tab for insights
    6. **Export Results**: Download your filtered data as CSV
    """)
    
    st.subheader("Filter Types")
    
    with st.expander("Categorical Filters"):
        st.markdown("""
        - **Company Category**: Filter by type of company
        - **Job Category**: Filter by specific job categories
        - **Location Type**: Filter by work location (Remote, On-site, Hybrid)
        - **Job Type**: Filter by employment type (Full-time, Part-time, Contract)
        """)
    
    with st.expander("Keyword Filters"):
        st.markdown("""
        - **Title Keywords**: Search for specific words in job titles
        - **Skills Keywords**: Search for required skills
        - Uses fuzzy matching for flexible searching
        """)
    
    with st.expander("Range Filters"):
        st.markdown("""
        - **Experience Range**: Filter by years of experience
        - **Salary Range**: Filter by salary expectations
        - Leave empty to include all values
        """)
    
    with st.expander("Fuzzy Matching"):
        st.markdown("""
        - **Title Threshold**: How strict to be with job title matching (0-100)
        - **Skills Threshold**: How strict to be with skills matching (0-100)
        - **Geography Threshold**: How strict to be with location matching (0-100)
        - Higher values = stricter matching
        """)
    
    st.subheader("Troubleshooting")
    
    with st.expander("Common Issues"):
        st.markdown("""
        **No results found**: Try lowering your fuzzy matching thresholds or using fewer filters
        
        **Data not loading**: Check that your CSV file has the expected column structure
        
        **Slow performance**: Large datasets may take time to process. Consider using more specific filters.
        """)
    
    st.subheader("Data Format")
    st.markdown("""
    Your CSV file should have these columns:
    - Company Category, Company, Overall Job Category, Job Category
    - Title, Min Experience, Max Experience
    - Country, State, City, Location Type, JobType
    - Job Link, Activated Date, Skills, Min Salary, Max Salary
    """) 