@echo off
echo ========================================
echo Updating project from GitHub...
echo ========================================
cd /d D:\Cortana
git pull origin main

echo ========================================
echo Starting backend with Poetry...
echo ========================================
cd backend
start cmd /k "poetry install && poetry run uvicorn app.main:app --reload"
cd ..

echo ========================================
echo Starting frontend with npm...
echo ========================================
cd frontend
start cmd /k "npm install && npm run dev"
cd ..

echo ========================================
echo Project started successfully!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo ========================================
