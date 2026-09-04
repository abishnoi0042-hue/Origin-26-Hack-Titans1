@echo off
echo ===================================================
echo Launching AeroHealth AI (Backend + Frontend)...
echo ===================================================

start "AeroHealth AI - Backend (Port 8000)" cmd /k "cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 2 >nul
start "AeroHealth AI - Frontend (Port 5173)" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting!
echo Frontend: http://localhost:5173
echo Backend Docs: http://localhost:8000/docs
echo.
pause
