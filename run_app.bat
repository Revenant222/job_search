@echo off
REM Quick start script for Job Search Application
REM Run this script to launch the Streamlit app

echo Starting Job Search Application...

REM Activate virtual environment and run Streamlit
call .venv\Scripts\activate.bat
streamlit run src\streamlit_app.py

pause

