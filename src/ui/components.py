"""
UI components for Streamlit interface.
"""
import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional


def create_filter_section(title: str, options: List[str], key: str) -> List[str]:
    """
    Create a filter section with multiselect.
    
    Args:
        title: Section title
        options: Available options
        key: Unique key for the component
        
    Returns:
        List of selected options
    """
    st.subheader(title)
    selected = st.multiselect(
        f"Select {title.lower()}",
        options=options,
        key=key
    )
    return selected


def create_range_section(title: str, min_key: str, max_key: str) -> Dict[str, Optional[int]]:
    """
    Create a range filter section.
    
    Args:
        title: Section title
        min_key: Key for minimum value
        max_key: Key for maximum value
        
    Returns:
        Dictionary with min and max values
    """
    st.subheader(title)
    col1, col2 = st.columns(2)
    
    with col1:
        min_val = st.number_input("Min", min_value=0, value=None, step=1, key=min_key)
    
    with col2:
        max_val = st.number_input("Max", min_value=0, value=None, step=1, key=max_key)
    
    return {"min": min_val, "max": max_val}


def create_keyword_input(title: str, key: str) -> List[str]:
    """
    Create a keyword input section.
    
    Args:
        title: Section title
        key: Unique key for the component
        
    Returns:
        List of keywords
    """
    st.subheader(title)
    keywords_text = st.text_input(
        f"Enter {title.lower()} (comma-separated)",
        key=key,
        help=f"Enter {title.lower()} separated by commas"
    )
    
    if keywords_text:
        keywords = [kw.strip() for kw in keywords_text.split(",") if kw.strip()]
        return keywords
    return []


def create_threshold_slider(title: str, default_value: int, key: str) -> int:
    """
    Create a threshold slider.
    
    Args:
        title: Slider title
        default_value: Default threshold value
        key: Unique key for the component
        
    Returns:
        Selected threshold value
    """
    return st.slider(
        title,
        min_value=0,
        max_value=100,
        value=default_value,
        key=key,
        help=f"Higher values = stricter matching for {title.lower()}"
    )


def display_filter_summary(filter_results: Dict[str, Any]):
    """
    Display filter application summary.
    
    Args:
        filter_results: Results from filter application
    """
    st.subheader("📊 Filter Summary")
    
    if not filter_results:
        st.info("No filters applied yet")
        return
    
    # Create summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Jobs", filter_results.get("total_jobs", 0))
    
    with col2:
        st.metric("Filtered Jobs", filter_results.get("filtered_jobs", 0))
    
    with col3:
        reduction = filter_results.get("reduction_percentage", 0)
        st.metric("Reduction", f"{reduction}%")
    
    with col4:
        if filter_results.get("total_jobs", 0) > 0:
            match_rate = (filter_results.get("filtered_jobs", 0) / filter_results.get("total_jobs", 1)) * 100
            st.metric("Match Rate", f"{match_rate:.1f}%")
    
    # Show detailed filter results
    st.subheader("🔍 Filter Details")
    
    filter_details = filter_results.get("filter_results", {})
    if filter_details:
        for filter_name, details in filter_details.items():
            if details.get("applied", False):
                with st.expander(f"📋 {filter_name.replace('_', ' ').title()}"):
                    st.write(f"**Jobs before:** {details.get('jobs_before', 0)}")
                    st.write(f"**Jobs after:** {details.get('jobs_after', 0)}")
                    
                    if "categories" in details:
                        st.write(f"**Categories:** {', '.join(details['categories'])}")
                    
                    if "keywords" in details:
                        st.write(f"**Keywords:** {', '.join(details['keywords'])}")
                    
                    if "threshold" in details:
                        st.write(f"**Threshold:** {details['threshold']}%")


def display_data_table(df: pd.DataFrame, title: str = "Data Table"):
    """
    Display data in a table format.
    
    Args:
        df: DataFrame to display
        title: Table title
    """
    st.subheader(title)
    
    if df is None or df.empty:
        st.info("No data to display")
        return
    
    # Column selection
    available_cols = df.columns.tolist()
    default_cols = ["Company", "Title", "Location Type", "Country", "City", "Job Link"]
    
    # Filter default columns to only include those that exist
    default_cols = [col for col in default_cols if col in available_cols]
    
    selected_cols = st.multiselect(
        "Select columns to display",
        options=available_cols,
        default=default_cols
    )
    
    if selected_cols:
        st.dataframe(
            df[selected_cols],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Please select at least one column to display")


def create_download_section(df: pd.DataFrame, filename_prefix: str = "data"):
    """
    Create download section for data export.
    
    Args:
        df: DataFrame to download
        filename_prefix: Prefix for the filename
    """
    st.subheader("📥 Download Data")
    
    if df is None or df.empty:
        st.info("No data available for download")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"Download {filename_prefix.title()} (CSV)"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Click to download CSV",
                data=csv,
                file_name=f"{filename_prefix}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button(f"Download {filename_prefix.title()} (Excel)"):
            # Note: This would require openpyxl dependency
            st.info("Excel download not implemented yet")


def display_error_message(error: str, title: str = "❌ Error"):
    """
    Display error message in a consistent format.
    
    Args:
        error: Error message
        title: Error title
    """
    st.error(f"{title}: {error}")


def display_success_message(message: str, title: str = "✅ Success"):
    """
    Display success message in a consistent format.
    
    Args:
        message: Success message
        title: Success title
    """
    st.success(f"{title}: {message}")


def display_info_message(message: str, title: str = "ℹ️ Info"):
    """
    Display info message in a consistent format.
    
    Args:
        message: Info message
        title: Info title
    """
    st.info(f"{title}: {message}")


def create_progress_bar(title: str, total: int, current: int):
    """
    Create a progress bar.
    
    Args:
        title: Progress bar title
        total: Total number of items
        current: Current progress
    """
    if total > 0:
        progress = current / total
        st.progress(progress)
        st.write(f"{title}: {current}/{total} ({progress:.1%})") 