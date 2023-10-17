@echo off

echo Installing required packages...
pip install -r data_record_tool/requirements.txt

if errorlevel 1 (
    echo Error: Failed to install required packages.
    exit /b 1
)

echo Packages installed successfully.

echo Running the Python script...
python data_record_tool/record_tool.py

pause
