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
import time

# Import our modules
from src.core.data_processor import DataProcessor
from src.core.job_filter import JobFilter
from src.core.job_tagger import JobTagger
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
    if 'job_tagger' not in st.session_state:
        st.session_state.job_tagger = JobTagger()
    
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
            
            # Tagged jobs count
            tagged_count = st.session_state.job_tagger.get_tagged_count()
            if tagged_count > 0:
                st.divider()
                st.metric("⭐ Tagged Jobs", tagged_count)
                if st.button("View Tagged Jobs", use_container_width=True, key="sidebar_view_tagged"):
                    st.session_state['goto_tagged_tab'] = True
    
    # Main content area
    if st.session_state.data_loaded:
        # Create tabs
        tagged_count = st.session_state.job_tagger.get_tagged_count()
        tab_label = f"⭐ Tagged Jobs ({tagged_count})" if tagged_count > 0 else "⭐ Tagged Jobs"
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 Filter Configuration", "📊 Results", "📈 Data Analysis", tab_label])
        
        with tab1:
            show_filter_configuration()
        
        with tab2:
            show_results()
        
        with tab3:
            show_data_analysis()
        
        with tab4:
            show_tagged_jobs()
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
            
            # Filter By Tag
            st.divider()
            tagger = st.session_state.job_tagger
            
            # Get all available tags from all jobs
            all_tags = set()
            for job_id, tags in tagger.job_tags.items():
                all_tags.update(tags)
            available_tags = sorted(list(all_tags))
            
            if available_tags:
                saved_tags = st.session_state.get('load_filter_config', {}).get('tags', [])
                selected_tags = st.multiselect(
                    "🏷️ Filter By Tag",
                    options=available_tags,
                    default=saved_tags if saved_tags else [],
                    help="Filter to show only jobs with selected tags. Jobs matching ANY selected tag will be shown."
                )
            else:
                selected_tags = []
                st.info("No tags available. Tag jobs in the Results tab to filter by tags.")
        
        with col2:
            st.subheader("Keyword & Range Filters")
            
            # Title Keywords
            # Load saved filter if available
            saved_title_kw = st.session_state.get('load_filter_config', {}).get('title_keywords', [])
            saved_title_kw_text = '\n'.join(saved_title_kw) if saved_title_kw else ""
            title_keywords_input = st.text_area(
                "Title Keywords",
                value=saved_title_kw_text,
                help="Enter keywords to search in job titles. Each line or comma-separated phrase will be treated as a single keyword. Spaces within keywords are preserved (e.g., 'data science' is one keyword). Use commas or new lines to separate multiple keywords. Multiple keywords use OR logic - jobs matching ANY keyword will be included.",
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
                help="Enter skills to search for. Each line or comma-separated phrase will be treated as a single keyword. Spaces within keywords are preserved (e.g., 'machine learning' is one keyword). Use commas or new lines to separate multiple keywords. Multiple keywords use OR logic - jobs matching ANY keyword will be included.",
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
                title_threshold, skills_threshold, geography_threshold,
                selected_tags
            )


def apply_filters(company_categories, overall_job_categories, job_categories,
                 location_types, job_types, title_keywords, skills_keywords,
                 min_experience, max_experience, min_salary, max_salary,
                 title_threshold, skills_threshold, geography_threshold,
                 selected_tags=None):
    """Apply filters to the data."""
    try:
        # Ensure job_id exists in raw_data (needed for tag filtering)
        if 'job_id' not in st.session_state.raw_data.columns:
            from src.core.data_processor import DataProcessor
            processor = DataProcessor()
            st.session_state.raw_data = processor.add_job_ids(st.session_state.raw_data)
        
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
            },
            "tags": selected_tags or []
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
        
        # Apply filters (pass tag_checker for tag filtering)
        job_filter = JobFilter(thresholds)
        tagger = st.session_state.job_tagger
        filtered_df = job_filter.apply_filters(st.session_state.raw_data, filters, tag_checker=tagger)
        
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
        
        # Add row numbers for quick selection
        if 'job_id' in sorted_df.columns:
            # Reset index to get sequential row numbers after sorting/pagination
            display_df_sorted = display_df_sorted.reset_index(drop=True)
            display_df_sorted['#'] = range(1, len(display_df_sorted) + 1)
            
            tagger = st.session_state.job_tagger
            display_df_sorted['⭐ Tagged'] = sorted_df.reset_index(drop=True)['job_id'].astype(str).apply(
                lambda x: '✅' if tagger.is_tagged(x) else ''
            )
            # Reorder to show row number and tag column first
            cols = ['#', '⭐ Tagged'] + [c for c in display_df_sorted.columns if c not in ['#', '⭐ Tagged']]
            display_df_sorted = display_df_sorted[cols]
            
            # Store mapping of row number to job_id for quick selection
            # Important: display_df_sorted has been reset_index, so idx matches row numbers
            row_to_job_id = {}
            sorted_df_reset = sorted_df.reset_index(drop=True)
            for idx, row_num in enumerate(display_df_sorted['#']):
                job_id = str(sorted_df_reset.iloc[idx]['job_id'])
                row_to_job_id[row_num] = job_id
            st.session_state['row_to_job_id'] = row_to_job_id
        
        # Use interactive dataframe with row selection (if supported)
        selected_job_id_from_table = None
        try:
            # Try newer Streamlit API with selection
            selected_rows = st.dataframe(
                display_df_sorted,
                hide_index=True,
                selection_mode="single-row",
                on_select="rerun",
                key="results_dataframe"
            )
            
            # Handle selection based on Streamlit version - only if row mapping exists
            if selected_rows and 'row_to_job_id' in st.session_state:
                # Newer API: selection is returned as dict
                if isinstance(selected_rows, dict) and 'selection' in selected_rows:
                    selected_indices = selected_rows['selection'].get('rows', [])
                    if selected_indices and len(display_df_sorted) > 0:
                        try:
                            selected_row_num = display_df_sorted.iloc[selected_indices[0]]['#']
                            selected_job_id_from_table = st.session_state['row_to_job_id'].get(selected_row_num)
                        except (IndexError, KeyError):
                            pass
                # Check session state for selection (alternative API)
                elif 'results_dataframe' in st.session_state:
                    df_state = st.session_state['results_dataframe']
                    if isinstance(df_state, dict) and 'selection' in df_state:
                        selected_indices = df_state['selection'].get('rows', [])
                        if selected_indices and len(display_df_sorted) > 0:
                            try:
                                selected_row_num = display_df_sorted.iloc[selected_indices[0]]['#']
                                selected_job_id_from_table = st.session_state['row_to_job_id'].get(selected_row_num)
                            except (IndexError, KeyError):
                                pass
        except TypeError:
            # Fallback: selection_mode not supported in this Streamlit version
            st.dataframe(
                display_df_sorted,
                hide_index=True
            )
        except Exception as e:
            # Other errors - use basic dataframe
            st.dataframe(
                display_df_sorted,
                hide_index=True
            )
            app_logger.debug(f"Dataframe selection error: {e}")
        
        # Tagging controls section
        if 'job_id' in sorted_df.columns:
            st.divider()
            st.subheader("🏷️ Tag Jobs for Application")
            
            tag_control_col1, tag_control_col2, tag_control_col3 = st.columns(3)
            
            with tag_control_col1:
                st.write("**Tag/Untag a Job:**")
                st.caption("💡 Tip: Click a row in the table above to auto-select it here!")
                
                # Quick select by row number
                quick_row_col1, quick_row_col2 = st.columns([2, 1])
                with quick_row_col1:
                    max_row = len(sorted_df)
                    # Get current quick row selection from session state, or default to None
                    current_quick_row = st.session_state.get('quick_row_input', None)
                    quick_row = st.number_input(
                        "Quick select by row #",
                        min_value=1,
                        max_value=max_row,
                        value=current_quick_row if current_quick_row else 1,
                        key="quick_row_select",
                        help=f"Enter a row number (1-{max_row}) to quickly select that job, then click 'Select'"
                    )
                    # Store the input value
                    st.session_state['quick_row_input'] = quick_row
                
                with quick_row_col2:
                    if st.button("Select", key="quick_select_btn", use_container_width=True):
                        row_to_job_map = st.session_state.get('row_to_job_id', {})
                        if quick_row and quick_row in row_to_job_map:
                            selected_job_id = row_to_job_map[quick_row]
                            st.session_state['selected_job_from_row'] = selected_job_id
                            st.session_state['last_selected_job_id'] = selected_job_id
                            st.session_state['force_selectbox_update'] = True
                            # Clear the selectbox key to force it to use new index
                            if 'tag_job_select' in st.session_state:
                                del st.session_state['tag_job_select']
                            # Force rerun to update selectbox
                            st.rerun()
                        elif quick_row:
                            st.warning(f"⚠️ Row {quick_row} not found in current results (max: {max_row})")
                            st.write(f"Debug: Available rows: {list(row_to_job_map.keys())[:10]}...")  # Show first 10
                        else:
                            st.warning("⚠️ Please enter a valid row number")
                
                # Create selectbox for tagging
                # Use reset_index to match row numbering with display_df_sorted
                job_options = []
                job_id_to_display = {}
                sorted_df_reset = sorted_df.reset_index(drop=True)
                for idx, (_, row) in enumerate(sorted_df_reset.iterrows()):
                    job_id = str(row.get('job_id', ''))
                    title = str(row.get('Title', 'Unknown'))[:60]
                    company = str(row.get('Company', 'Unknown'))[:30]
                    if job_id:
                        display_text = f"{company} - {title}"
                        job_options.append((job_id, display_text))
                        job_id_to_display[job_id] = display_text
                
                if job_options:
                    # Determine default selection: from table click, from quick row, or previous selection
                    default_index = 0
                    
                    # Priority: table selection > quick row selection > previous selection
                    # selected_job_id_from_table is set above from dataframe selection
                    default_job_id = None
                    
                    if selected_job_id_from_table and selected_job_id_from_table in [opt[0] for opt in job_options]:
                        default_job_id = selected_job_id_from_table
                        # Store for persistence across reruns
                        st.session_state['last_selected_job_id'] = selected_job_id_from_table
                    elif st.session_state.get('selected_job_from_row'):
                        candidate_job_id = st.session_state['selected_job_from_row']
                        if candidate_job_id in [opt[0] for opt in job_options]:
                            default_job_id = candidate_job_id
                            st.session_state['last_selected_job_id'] = default_job_id
                            # Show confirmation
                            st.info(f"✅ Selecting job from row {st.session_state.get('quick_row_input', '?')}")
                        # Don't delete yet - let selectbox use it first
                    elif st.session_state.get('last_selected_job_id') and st.session_state['last_selected_job_id'] in [opt[0] for opt in job_options]:
                        default_job_id = st.session_state['last_selected_job_id']
                    
                    # Fallback to first option if no valid selection
                    if default_job_id is None:
                        default_job_id = job_options[0][0]
                    
                    # Find index of default job
                    default_index = next((i for i, opt in enumerate(job_options) if opt[0] == default_job_id), 0)
                    
                    # Create a unique key that changes when we force update
                    selectbox_key = "tag_job_select"
                    if st.session_state.get('force_selectbox_update', False):
                        # Use a timestamp-based key to force new widget
                        import time
                        selectbox_key = f"tag_job_select_{int(time.time() * 1000)}"
                        del st.session_state['force_selectbox_update']
                    
                    # Clear selected_job_from_row after we've determined the index
                    if 'selected_job_from_row' in st.session_state:
                        del st.session_state['selected_job_from_row']
                    
                    selected_job = st.selectbox(
                        "Select a job to tag/untag",
                        options=[opt[0] for opt in job_options],
                        format_func=lambda x: job_id_to_display.get(x, x),
                        index=default_index,
                        key=selectbox_key
                    )
                    
                    if selected_job:
                        tagger = st.session_state.job_tagger
                        is_tagged = tagger.is_tagged(selected_job)
                        if is_tagged:
                            if st.button("❌ Untag Job", key="untag_btn", use_container_width=True):
                                tagger.untag_job(selected_job)
                                st.success("✅ Job untagged!")
                                st.rerun()
                        else:
                            if st.button("⭐ Tag Job", key="tag_btn", use_container_width=True):
                                tagger.tag_job(selected_job)
                                st.success("✅ Job tagged! View in 'Tagged Jobs' tab.")
                                st.rerun()
            
            with tag_control_col2:
                st.write("**Stats:**")
                tagger = st.session_state.job_tagger
                tagged_in_results = sum(1 for job_id in sorted_df['job_id'].astype(str) if tagger.is_tagged(job_id))
                st.metric("Tagged in Results", tagged_in_results)
                st.caption(f"Total tagged: {tagger.get_tagged_count()}")
                if tagged_in_results > 0:
                    if st.button("📋 View All Tagged", key="view_tagged_btn", use_container_width=True):
                        st.info("Go to the '⭐ Tagged Jobs' tab to see all tagged jobs")
            
            with tag_control_col3:
                st.write("**Export Tagged:**")
                if tagged_in_results > 0:
                    tagged_jobs = sorted_df[sorted_df['job_id'].astype(str).isin(tagger.get_tagged_job_ids())]
                    csv = tagged_jobs.to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download {tagged_in_results} Tagged",
                        data=csv,
                        file_name=f"tagged_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                else:
                    st.info("No tagged jobs in current results")
    
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


def show_tagged_jobs():
    """Show tagged jobs for application."""
    st.header("⭐ Tagged Jobs - Ready to Apply")
    
    tagger = st.session_state.job_tagger
    tagged_count = tagger.get_tagged_count()
    
    if tagged_count == 0:
        st.info("No jobs tagged yet. Tag jobs from the Results tab to track jobs you want to apply for.")
        st.markdown("""
        **How to tag jobs:**
        1. Go to the **📊 Results** tab
        2. Apply filters to find jobs you're interested in
        3. Use the tagging controls to mark jobs you want to apply for
        4. Tagged jobs will appear here for easy access
        """)
        return
    
    # Summary stats
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tagged Jobs", tagged_count)
    with col2:
        if st.button("🔄 Refresh from Current Data", use_container_width=True):
            st.rerun()
    with col3:
        if st.button("🗑️ Clear All Tags", use_container_width=True, help="Remove all tags"):
            if st.session_state.get('confirm_clear_tags', False):
                tagger.clear_all_tags()
                st.success("✅ All tags cleared!")
                st.session_state['confirm_clear_tags'] = False
                st.rerun()
            else:
                st.session_state['confirm_clear_tags'] = True
                st.warning("⚠️ Click again to confirm clearing all tags")
                st.rerun()
    
    # Get tagged jobs from current data
    if not st.session_state.data_loaded or st.session_state.raw_data is None:
        st.warning("Please load data first to view tagged jobs")
        return
    
    tagged_ids = tagger.get_tagged_job_ids()
    raw_data = st.session_state.raw_data
    
    # Filter to only tagged jobs
    if 'job_id' in raw_data.columns:
        tagged_df = raw_data[raw_data['job_id'].astype(str).isin(tagged_ids)].copy()
        
        if len(tagged_df) == 0:
            st.warning("Tagged jobs not found in current dataset. They may be from a different CSV file.")
            st.info(f"You have {tagged_count} jobs tagged, but they're not in the currently loaded data.")
            return
        
        # Add tag date and note columns
        tagged_df['Tagged Date'] = tagged_df['job_id'].astype(str).apply(
            lambda x: (tagger.tag_dates.get(x, '')[:10] if tagger.tag_dates.get(x, '') else 'Unknown')
        )
        tagged_df['Note'] = tagged_df['job_id'].astype(str).apply(
            lambda x: tagger.tag_notes.get(x, '') if x in tagger.tag_notes else ''
        )
        
        st.success(f"Found {len(tagged_df)} tagged jobs in current dataset")
        
        # Sorting
        sort_col1, sort_col2 = st.columns(2)
        with sort_col1:
            sort_by_tagged = st.selectbox(
                "Sort by",
                options=["Tagged Date", "Company", "Title", "Min Salary", "Max Salary"],
                key="tagged_sort"
            )
        with sort_col2:
            sort_order_tagged = st.selectbox(
                "Order",
                options=["Descending", "Ascending"],
                index=0,
                key="tagged_order"
            )
        
        # Apply sorting
        sorted_tagged = tagged_df.copy()
        ascending_tagged = (sort_order_tagged == "Ascending")
        if sort_by_tagged == "Tagged Date":
            sorted_tagged = sorted_tagged.sort_values(by="Tagged Date", ascending=ascending_tagged, na_position='last')
        elif sort_by_tagged in sorted_tagged.columns:
            sorted_tagged = sorted_tagged.sort_values(by=sort_by_tagged, ascending=ascending_tagged, na_position='last')
        
        # Display columns
        default_tagged_cols = ["Company", "Title", "Location Type", "Country", "City", "Min Salary", "Max Salary", "Job Link", "Tagged Date"]
        available_tagged_cols = [c for c in sorted_tagged.columns if c not in ['Note']]
        
        display_tagged_cols = st.multiselect(
            "Select columns to display",
            options=available_tagged_cols,
            default=default_tagged_cols,
            key="tagged_display_cols"
        )
        
        if display_tagged_cols:
            # Show tag notes if any
            jobs_with_notes = sorted_tagged[sorted_tagged['Note'].str.strip() != '']
            if len(jobs_with_notes) > 0:
                with st.expander(f"📝 Jobs with Notes ({len(jobs_with_notes)})", expanded=False):
                    for idx, row in jobs_with_notes.iterrows():
                        st.write(f"**{row.get('Company', 'Unknown')} - {row.get('Title', 'Unknown')}**")
                        st.caption(row['Note'])
                        st.divider()
            
            display_tagged_df = sorted_tagged[display_tagged_cols].copy()
            
            st.dataframe(
                display_tagged_df,
                hide_index=True
            )
            
            # Individual job actions
            st.subheader("🔧 Manage Tagged Jobs")
            
            job_action_col1, job_action_col2 = st.columns(2)
            
            with job_action_col1:
                st.write("**Untag a Job:**")
                untag_options = []
                for idx, row in sorted_tagged.iterrows():
                    job_id = str(row.get('job_id', ''))
                    title = str(row.get('Title', 'Unknown'))
                    company = str(row.get('Company', 'Unknown'))
                    if job_id:
                        untag_options.append((job_id, f"{company} - {title[:50]}"))
                
                if untag_options:
                    selected_untag = st.selectbox(
                        "Select job to untag",
                        options=[opt[0] for opt in untag_options],
                        format_func=lambda x: next((opt[1] for opt in untag_options if opt[0] == x), x),
                        key="untag_select"
                    )
                    
                    if st.button("❌ Untag Selected Job", key="untag_selected", use_container_width=True):
                        tagger.untag_job(selected_untag)
                        st.success("✅ Job untagged!")
                        st.rerun()
            
            with job_action_col2:
                st.write("**Export Options:**")
                # Export all tagged
                csv_all = sorted_tagged.to_csv(index=False)
                st.download_button(
                    label=f"📥 Download All Tagged ({len(sorted_tagged)})",
                    data=csv_all,
                    file_name=f"all_tagged_jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
                
                # Export selected columns only
                if display_tagged_cols:
                    csv_selected = sorted_tagged[display_tagged_cols].to_csv(index=False)
                    st.download_button(
                        label=f"📥 Download Selected Columns",
                        data=csv_selected,
                        file_name=f"tagged_jobs_selected_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
    else:
        st.warning("Job IDs not found in data. Cannot display tagged jobs.")


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
        st.dataframe(missing_df)


if __name__ == "__main__":
    main() 