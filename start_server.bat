@echo off
setlocal

echo Building Angular application...
cd ui
if exist node_modules (
    echo node_modules found, skipping npm install
) else (
    echo Installing npm packages...
    npm install
)

echo Building Angular app...
call npx ng build

if %ERRORLEVEL% NEQ 0 (
    echo Angular build failed
    exit /b %ERRORLEVEL%
)

echo Angular build completed successfully
cd ..

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