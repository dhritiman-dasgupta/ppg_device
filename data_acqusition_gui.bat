@echo off

echo Installing required packages...
pip install -r "data_acqusition_tool\requirements.txt"

rem Check if the installation was successful
if errorlevel 1 (
    echo Error: Failed to install required packages.
    exit /b 1
) else (
    echo Packages installed successfully.
)

rem Run the Python application
echo Starting the application...
python "data_acqusition_tool\data_exploration_tool.py"

pause
