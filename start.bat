@echo off
chcp 1251 >nul

echo ======================================================
echo     TMS - Test Management System
echo ======================================================
echo.

REM Load variables from .env
for /f "tokens=2 delims==" %%a in ('findstr "APP_PORT" .env') do set APP_PORT=%%a
if "%APP_PORT%"=="" set APP_PORT=8000

for /f "tokens=2 delims==" %%a in ('findstr "DB_USER" .env') do set DB_USER=%%a
if "%DB_USER%"=="" set DB_USER=postgres

for /f "tokens=2 delims==" %%a in ('findstr "DB_NAME" .env') do set DB_NAME=%%a
if "%DB_NAME%"=="" set DB_NAME=tms_db

echo App port: %APP_PORT%
echo DB user: %DB_USER%
echo.

echo 1. Stopping old containers...
docker-compose down -v

echo 2. Building and starting...
docker-compose up -d --build

echo 3. Waiting for database to start...
timeout /t 15 /nobreak >nul

echo 4. Creating tables...
docker-compose exec app python -c "
from app.db.database import init_db
init_db()
"

echo 5. Adding statuses...
docker-compose exec db psql -U %DB_USER% -d %DB_NAME% -c "
DELETE FROM statuses WHERE name IN ('passed', 'failed', 'skipped', 'pending');
INSERT INTO statuses (name) VALUES ('passed'), ('failed'), ('skipped'), ('pending');
"

echo.
echo ======================================================
echo     READY!
echo     http://localhost:%APP_PORT%
echo     http://localhost:%APP_PORT%/docs
echo ======================================================
pause