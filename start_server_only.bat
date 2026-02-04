@echo off
setlocal

echo Installing Python dependencies...
if exist venv (
    echo Virtual environment found
) else (
    echo Creating virtual environment...
    python -m venv venv
)

call venv\Scripts\activate.bat
pip install -r requirements.txt

echo Starting FastAPI server...
python server.py