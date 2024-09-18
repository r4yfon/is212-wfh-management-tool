@echo off
setlocal
set "FLASK_DIR=%CD%"

wt.exe -w myWindow nt -p "Command Prompt" -d "%FLASK_DIR%" --title "employee.py" -- cmd /c "set FLASK_APP=employee.py && set FLASK_ENV=development && flask run --port 5000"

wt.exe -w myWindow nt -p "Command Prompt" -d "%FLASK_DIR%" --title "request.py" -- cmd /c "set FLASK_APP=request.py && set FLASK_ENV=development && flask run --port 5001"

wt.exe -w myWindow nt -p "Command Prompt" -d "%FLASK_DIR%" --title "request_dates.py" -- cmd /c "set FLASK_APP=request_dates.py && set FLASK_ENV=development && flask run --port 5002"

wt.exe -w myWindow nt -p "Command Prompt" -d "%FLASK_DIR%" --title "view_schedule.py" -- cmd /c "set FLASK_APP=view_schedule.py && set FLASK_ENV=development && flask run --port 5100"