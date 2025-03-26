@echo off
echo Starting Policy Hub Application...

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Start Django server in a new window
start cmd /k "python manage.py runserver"

:: Wait for server to start (5 seconds)
timeout /t 5 /nobreak

:: Open default browser
start http://127.0.0.1:8000/

echo Application started! You can close this window.