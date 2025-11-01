"""
Streamlit application for AI Job Filter Agent.
"""
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from datetime import datetime
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
    if 'filter_history' not in st.session_state:
        st.session_state.filter_history = []
    if 'saved_filters' not in st.session_state:
        st.session_state.saved_filters = {}
    
    # Sidebar for data loading
    with st.sidebar:
        st.header("📁 Data Loading")
        
        # Quick reset button in sidebar
        if st.button("🔄 Reset Filters", help="Quick reset all filters", use_container_width=True, key="sidebar_reset"):
            if 'filtered_data' in st.session_state:
                st.session_state.filtered_data = None
            if 'load_filter_config' in st.session_state:
                del st.session_state['load_filter_config']
            st.success("✅ Filters reset!")
            st.rerun()
        
        st.divider()
        
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
    
    # Quick actions row
    action_col1, action_col2, action_col3 = st.columns(3)
    
    with action_col1:
        if st.button("🔄 Reset All Filters", help="Clear all filters and reset to defaults", use_container_width=True):
            # Clear filter-related session state
            if 'filtered_data' in st.session_state:
                st.session_state.filtered_data = None
            st.success("✅ Filters reset! Clear the form to reset all filter values.")
            st.rerun()
    
    with action_col2:
        if st.button("💾 Save Current Filters", help="Save current filter configuration for later use", use_container_width=True):
            st.session_state['save_filter_prompt'] = True
            st.rerun()
    
    with action_col3:
        if st.button("📜 Load Saved Filters", help="Load a previously saved filter configuration", use_container_width=True):
            st.session_state['load_filter_prompt'] = True
            st.rerun()
    
    st.divider()
    
    # Saved filters and history section
    if st.session_state.get('save_filter_prompt', False):
        with st.expander("💾 Save Filter Configuration", expanded=True):
            filter_name = st.text_input("Filter Name", placeholder="e.g., 'Senior Data Engineer', 'Remote Entry Level'")
            if st.button("Save", key="save_filter_btn"):
                if filter_name:
                    # We'll save after form submission, for now just mark it
                    st.session_state['filter_to_save'] = filter_name
                    st.session_state['save_filter_prompt'] = False
                    st.success(f"✅ Filter configuration will be saved as '{filter_name}' after you apply filters.")
                else:
                    st.error("Please enter a filter name")
    
    if st.session_state.get('load_filter_prompt', False) and st.session_state.saved_filters:
        with st.expander("📜 Load Saved Filters", expanded=True):
            if st.session_state.saved_filters:
                selected_filter = st.selectbox(
                    "Select saved filter",
                    options=list(st.session_state.saved_filters.keys()),
                    help="Choose a previously saved filter configuration to load"
                )
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Load", key="load_filter_btn"):
                        # Load the saved filter
                        saved = st.session_state.saved_filters[selected_filter]
                        st.session_state['load_filter_config'] = saved
                        st.session_state['load_filter_prompt'] = False
                        st.success(f"✅ Loaded '{selected_filter}' - configure filters and click Apply")
                        st.rerun()
                with col2:
                    if st.button("Delete", key="delete_filter_btn"):
                        del st.session_state.saved_filters[selected_filter]
                        st.success(f"✅ Deleted '{selected_filter}'")
                        st.rerun()
            else:
                st.info("No saved filters yet. Save your current filters to get started!")
                st.session_state['load_filter_prompt'] = False
    
    # Show filter history (last 5 applications)
    if st.session_state.filter_history:
        with st.expander("📋 Recent Filter History", expanded=False):
            for i, history_item in enumerate(reversed(st.session_state.filter_history[-5:]), 1):
                timestamp = history_item.get('timestamp', 'Unknown')
                jobs_found = history_item.get('jobs_found', 0)
                keywords = history_item.get('keywords', {})
                title_kw = keywords.get('title', [])
                skills_kw = keywords.get('skills', [])
                
                hist_col1, hist_col2 = st.columns([3, 1])
                with hist_col1:
                    st.write(f"**{i}. {timestamp}** - Found {jobs_found} jobs")
                    if title_kw:
                        st.caption(f"Title: {', '.join(title_kw[:3])}{'...' if len(title_kw) > 3 else ''}")
                    if skills_kw:
                        st.caption(f"Skills: {', '.join(skills_kw[:3])}{'...' if len(skills_kw) > 3 else ''}")
                with hist_col2:
                    if st.button("🔄 Reload", key=f"reload_history_{i}", use_container_width=True):
                        st.session_state['load_filter_config'] = history_item.get('config', {})
                        st.success(f"✅ Loaded filter from {timestamp}")
                        st.rerun()
    
    st.divider()
    
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
                # Load saved filter if available
                saved_company = st.session_state.get('load_filter_config', {}).get('company_categories', [])
                company_categories = st.multiselect(
                    "Company Category",
                    options=st.session_state.filter_options["Company Category"],
                    default=saved_company if saved_company else [],
                    help="Select company categories to include"
                )
            else:
                company_categories = []
            
            # Overall Job Category
            if "Overall Job Category" in st.session_state.filter_options:
                saved_overall = st.session_state.get('load_filter_config', {}).get('overall_job_categories', [])
                overall_job_categories = st.multiselect(
                    "Overall Job Category",
                    options=st.session_state.filter_options["Overall Job Category"],
                    default=saved_overall if saved_overall else [],
                    help="Select overall job categories to include"
                )
            else:
                overall_job_categories = []
            
            # Job Category
            if "Job Category" in st.session_state.filter_options:
                saved_job = st.session_state.get('load_filter_config', {}).get('job_categories', [])
                job_categories = st.multiselect(
                    "Job Category",
                    options=st.session_state.filter_options["Job Category"],
                    default=saved_job if saved_job else [],
                    help="Select specific job categories to include"
                )
            else:
                job_categories = []
            
            # Location Type
            if "Location Type" in st.session_state.filter_options:
                saved_location = st.session_state.get('load_filter_config', {}).get('location_types', [])
                location_types = st.multiselect(
                    "Location Type",
                    options=st.session_state.filter_options["Location Type"],
                    default=saved_location if saved_location else [],
                    help="Select work location types"
                )
            else:
                location_types = []
            
            # Job Type
            if "JobType" in st.session_state.filter_options:
                saved_jobtype = st.session_state.get('load_filter_config', {}).get('job_types', [])
                job_types = st.multiselect(
                    "Job Type",
                    options=st.session_state.filter_options["JobType"],
                    default=saved_jobtype if saved_jobtype else [],
                    help="Select employment types"
                )
            else:
                job_types = []
        
        with col2:
            st.subheader("Keyword & Range Filters")
            
            # Title Keywords
            # Load saved filter if available
            saved_title_kw = st.session_state.get('load_filter_config', {}).get('title_keywords', [])
            saved_title_kw_text = '\n'.join(saved_title_kw) if saved_title_kw else ""
            title_keywords_input = st.text_area(
                "Title Keywords",
                value=saved_title_kw_text,
                help="Enter keywords to search in job titles. Each line or comma-separated phrase will be treated as a single keyword. Spaces within keywords are preserved (e.g., 'data science' is one keyword). Use commas or new lines to separate multiple keywords. Multi-word phrases are matched intelligently.",
                height=100,
                placeholder="data science\nmachine learning\nor: python, java, cloud engineer"
            )
            # Parse keywords: split by newline first, then by comma, preserving spaces
            title_keywords = []
            if title_keywords_input:
                # Split by newlines first
                lines = title_keywords_input.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Then split by comma within each line
                        for kw in line.split(','):
                            kw = kw.strip()
                            if kw:
                                title_keywords.append(kw)
            
            # Show parsed keywords preview
            if title_keywords:
                with st.expander("📋 Title Keywords Preview", expanded=False):
                    for i, kw in enumerate(title_keywords, 1):
                        st.text(f"{i}. '{kw}'")
                    st.caption(f"Total: {len(title_keywords)} keyword(s)")
            
            # Skills Keywords
            # Load saved filter if available
            saved_skills_kw = st.session_state.get('load_filter_config', {}).get('skills_keywords', [])
            saved_skills_kw_text = '\n'.join(saved_skills_kw) if saved_skills_kw else ""
            skills_keywords_input = st.text_area(
                "Skills Keywords",
                value=saved_skills_kw_text,
                help="Enter skills to search for. Each line or comma-separated phrase will be treated as a single keyword. Spaces within keywords are preserved (e.g., 'machine learning' is one keyword). Use commas or new lines to separate multiple keywords. Multi-word phrases are matched intelligently.",
                height=100,
                placeholder="machine learning\npython programming\nor: aws, docker, kubernetes"
            )
            # Parse keywords: split by newline first, then by comma, preserving spaces
            skills_keywords = []
            if skills_keywords_input:
                # Split by newlines first
                lines = skills_keywords_input.split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        # Then split by comma within each line
                        for kw in line.split(','):
                            kw = kw.strip()
                            if kw:
                                skills_keywords.append(kw)
            
            # Show parsed keywords preview
            if skills_keywords:
                with st.expander("📋 Skills Keywords Preview", expanded=False):
                    for i, kw in enumerate(skills_keywords, 1):
                        st.text(f"{i}. '{kw}'")
                    st.caption(f"Total: {len(skills_keywords)} keyword(s)")
            
            # Experience Range
            st.subheader("Experience Range")
            saved_exp = st.session_state.get('load_filter_config', {}).get('experience_range', {})
            exp_col1, exp_col2 = st.columns(2)
            with exp_col1:
                min_experience = st.number_input(
                    "Min Experience (years)", 
                    min_value=0, 
                    value=saved_exp.get('min') if saved_exp else None, 
                    step=1
                )
            with exp_col2:
                max_experience = st.number_input(
                    "Max Experience (years)", 
                    min_value=0, 
                    value=saved_exp.get('max') if saved_exp else None, 
                    step=1
                )
            
            # Salary Range
            st.subheader("Salary Range")
            saved_sal = st.session_state.get('load_filter_config', {}).get('salary_range', {})
            sal_col1, sal_col2 = st.columns(2)
            with sal_col1:
                min_salary = st.number_input(
                    "Min Salary", 
                    min_value=0, 
                    value=saved_sal.get('min') if saved_sal else None, 
                    step=1000
                )
            with sal_col2:
                max_salary = st.number_input(
                    "Max Salary", 
                    min_value=0, 
                    value=saved_sal.get('max') if saved_sal else None, 
                    step=1000
                )
        
        # Fuzzy Matching Thresholds
        st.subheader("🔍 Fuzzy Matching Thresholds")
        saved_thresholds = st.session_state.get('load_filter_config', {}).get('thresholds', {})
        col1, col2, col3 = st.columns(3)
        
        with col1:
            title_threshold = st.slider(
                "Title Match Threshold",
                min_value=0, 
                max_value=100, 
                value=saved_thresholds.get('title', FUZZY_MATCH_THRESHOLDS["title"]),
                help="Higher = stricter matching for job titles"
            )
        
        with col2:
            skills_threshold = st.slider(
                "Skills Match Threshold",
                min_value=0, 
                max_value=100, 
                value=saved_thresholds.get('skills', FUZZY_MATCH_THRESHOLDS["skills"]),
                help="Higher = stricter matching for skills"
            )
        
        with col3:
            geography_threshold = st.slider(
                "Geography Match Threshold",
                min_value=0, 
                max_value=100, 
                value=saved_thresholds.get('geography', FUZZY_MATCH_THRESHOLDS["geography"]),
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
        
        # Full filter config for saving
        full_filter_config = {
            **filters,
            "thresholds": thresholds
        }
        
        # Apply filters
        job_filter = JobFilter(thresholds)
        filtered_df = job_filter.apply_filters(st.session_state.raw_data, filters)
        
        # Store results
        st.session_state.filtered_data = filtered_df
        st.session_state.filter_summary = job_filter.get_filter_summary()
        
        # Save to history
        history_entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "jobs_found": len(filtered_df),
            "keywords": {
                "title": title_keywords,
                "skills": skills_keywords
            },
            "config": full_filter_config
        }
        st.session_state.filter_history.append(history_entry)
        
        # Save filter if requested
        if st.session_state.get('filter_to_save'):
            filter_name = st.session_state['filter_to_save']
            st.session_state.saved_filters[filter_name] = full_filter_config
            st.session_state['filter_to_save'] = None
            st.success(f"✅ Filter configuration saved as '{filter_name}'!")
        
        # Clear load filter config after use
        if 'load_filter_config' in st.session_state:
            del st.session_state['load_filter_config']
        
        # Show detailed feedback
        if len(filtered_df) == 0:
            st.warning("⚠️ No jobs found matching your criteria. Try:")
            st.markdown("""
            - **Lower the fuzzy matching thresholds** (especially Title and Skills)
            - **Check keyword spelling** - Use the preview to verify parsed keywords
            - **Remove some filters** to broaden the search
            - **Use partial keywords** - e.g., 'data' instead of 'data science' if threshold is high
            """)
        else:
            st.success(f"✅ Applied filters! Found {len(filtered_df)} matching jobs")
            
            # Show which keywords matched
            if title_keywords or skills_keywords:
                with st.expander("🔍 Keyword Matching Info", expanded=False):
                    if title_keywords:
                        st.write("**Title Keywords Used:**", ", ".join([f"'{kw}'" for kw in title_keywords]))
                    if skills_keywords:
                        st.write("**Skills Keywords Used:**", ", ".join([f"'{kw}'" for kw in skills_keywords]))
                    st.caption(f"Match threshold: Title={title_threshold}%, Skills={skills_threshold}%")
        
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
    
    # Sorting and display options
    sort_col1, sort_col2, sort_col3 = st.columns(3)
    
    with sort_col1:
        sort_by = st.selectbox(
            "Sort by",
            options=["Match Score", "Company", "Title", "Min Salary", "Max Salary", "Activated Date"],
            index=0 if any("match_score" in col for col in st.session_state.filtered_data.columns) else 2
        )
    
    with sort_col2:
        sort_order = st.selectbox(
            "Order",
            options=["Descending", "Ascending"],
            index=0
        )
    
    with sort_col3:
        results_per_page = st.selectbox(
            "Results per page",
            options=[25, 50, 100, "All"],
            index=1
        )
    
    # Apply sorting
    sorted_df = st.session_state.filtered_data.copy()
    if sort_by == "Match Score":
        match_score_cols = [col for col in sorted_df.columns if "match_score" in col]
        if match_score_cols:
            # Use the first match score column found
            sort_column = match_score_cols[0]
            ascending = (sort_order == "Ascending")
            sorted_df = sorted_df.sort_values(by=sort_column, ascending=ascending)
    elif sort_by == "Company" and "Company" in sorted_df.columns:
        ascending = (sort_order == "Ascending")
        sorted_df = sorted_df.sort_values(by="Company", ascending=ascending, na_position='last')
    elif sort_by == "Title" and "Title" in sorted_df.columns:
        ascending = (sort_order == "Ascending")
        sorted_df = sorted_df.sort_values(by="Title", ascending=ascending, na_position='last')
    elif sort_by == "Min Salary" and "Min Salary" in sorted_df.columns:
        ascending = (sort_order == "Ascending")
        sorted_df = sorted_df.sort_values(by="Min Salary", ascending=ascending, na_position='last')
    elif sort_by == "Max Salary" and "Max Salary" in sorted_df.columns:
        ascending = (sort_order == "Ascending")
        sorted_df = sorted_df.sort_values(by="Max Salary", ascending=ascending, na_position='last')
    elif sort_by == "Activated Date" and "Activated Date" in sorted_df.columns:
        ascending = (sort_order == "Ascending")
        sorted_df = sorted_df.sort_values(by="Activated Date", ascending=ascending, na_position='last')
    
    # Apply pagination
    if results_per_page != "All":
        page_size = results_per_page
        total_pages = (len(sorted_df) + page_size - 1) // page_size
        if total_pages > 1:
            page_num = st.number_input(f"Page (1-{total_pages})", min_value=1, max_value=total_pages, value=1, step=1)
            start_idx = (page_num - 1) * page_size
            end_idx = start_idx + page_size
            sorted_df = sorted_df.iloc[start_idx:end_idx]
            st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(st.session_state.filtered_data))} of {len(st.session_state.filtered_data)} results")
    
    # Display options
    display_cols = st.multiselect(
        "Select columns to display",
        options=st.session_state.filtered_data.columns.tolist(),
        default=["Company", "Title", "Location Type", "Country", "City", "Job Link"]
    )
    
    if display_cols:
        # Check if match score columns exist and add them if they do
        available_cols = list(st.session_state.filtered_data.columns)
        match_score_cols = [col for col in available_cols if 'match_score' in col]
        
        # Show match scores if available
        if match_score_cols:
            with st.expander("📊 Match Scores", expanded=False):
                for col in match_score_cols:
                    scores = sorted_df[col]
                    avg_score = scores.mean()
                    max_score = scores.max()
                    st.metric(f"{col.replace('_match_score', '').title()} Match", 
                             f"{avg_score:.1f}% avg", 
                             f"{max_score:.0f}% max")
        
        # Create display dataframe from sorted data
        display_df_sorted = sorted_df[display_cols].copy()
        
        # Add match scores to display if available and not already included
        for col in match_score_cols:
            if col not in display_cols:
                display_df_sorted[col] = sorted_df[col]
        
        st.dataframe(
            display_df_sorted,
            width='stretch',
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
        # Use bar chart instead of pie chart (Streamlit doesn't have pie_chart)
        st.bar_chart(location_df.set_index("Location Type"))
    
    # Missing data analysis
    if "missing_data" in summary:
        st.subheader("📊 Missing Data Analysis")
        missing_df = pd.DataFrame(
            [(col, info["count"], info["percentage"]) for col, info in summary["missing_data"].items()],
            columns=["Column", "Missing Count", "Missing Percentage"]
        )
        st.dataframe(missing_df, width='stretch')


if __name__ == "__main__":
    main() 