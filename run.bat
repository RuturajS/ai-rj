
@echo off
echo Starting AI Assistant (using venv)...

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r requirements.txt

echo Running Assistant...
python main.py

pause
