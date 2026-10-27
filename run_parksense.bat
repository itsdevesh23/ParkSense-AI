@echo off
echo =======================================================================
echo    ParkSense AI: Federated Multi-Lot Smart Parking Forecasting
echo    Team 4: Devesh Munagala (23BCT0149) ^& Abhinav (23BCT0142)
echo =======================================================================
echo.
echo Starting FastAPI Backend on http://localhost:8000 ...
start "ParkSense AI - Backend (FastAPI)" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo Starting Vite Frontend on http://localhost:5173 ...
start "ParkSense AI - Frontend (React + Vite)" cmd /k "cd frontend && npm run dev"

echo.
echo =======================================================================
echo Both services are booting!
echo   Frontend: http://localhost:5173
echo   Backend:  http://localhost:8000 (Swagger Docs: http://localhost:8000/docs)
echo =======================================================================
pause
