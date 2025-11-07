@echo off
REM Test script for delta analysis
REM This tests pulling from Google Sheets and delta comparison

echo Testing Delta Analysis...
echo.

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Run the test script
python scripts\tests\test_delta_analysis.py

pause

