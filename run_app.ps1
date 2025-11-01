# Quick start script for Job Search Application
# Run this script to launch the Streamlit app

Write-Host "Starting Job Search Application..." -ForegroundColor Green

# Activate virtual environment and run Streamlit
& .\.venv\Scripts\Activate.ps1
streamlit run src\streamlit_app.py

