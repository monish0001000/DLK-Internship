@echo off
echo Setting up EDRLite Environment...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt

echo.
echo ==============================================================
echo   EDRLite Platform is Starting...
echo   Open your browser to: http://127.0.0.1:5000
echo   Default Login: admin / EDRLite@2024
echo.
echo   Note: Real osquery mode is active. Ensure 'osqueryi'
echo   is installed and accessible in your system PATH.
echo ==============================================================
python app.py
pause
