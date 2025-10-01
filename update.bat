@echo off
REM QFIL Downloader - Container Update Script for Windows
REM Usage: update.bat [quick|clean|rolling]

setlocal enabledelayedexpansion

set "UPDATE_TYPE=%1"
if "%UPDATE_TYPE%"=="" set "UPDATE_TYPE=quick"

echo 🔄 QFIL Downloader Container Update
echo Update type: %UPDATE_TYPE%
echo ==================================

if "%UPDATE_TYPE%"=="quick" goto quick
if "%UPDATE_TYPE%"=="clean" goto clean
if "%UPDATE_TYPE%"=="rolling" goto rolling

echo ❌ Invalid update type: %UPDATE_TYPE%
echo Valid options: quick, clean, rolling
exit /b 1

:quick
echo 📦 Performing quick update (code changes only)...

REM Backup current projects.json if it exists
if exist "projects.json" (
    echo 💾 Backing up projects.json...
    for /f "tokens=1-4 delims=/ " %%i in ('date /t') do set mydate=%%l%%j%%k
    for /f "tokens=1-2 delims=: " %%i in ('time /t') do set mytime=%%i%%j
    copy projects.json "projects.json.backup.!mydate!_!mytime!"
)

echo 🛑 Stopping containers...
docker-compose down

echo 🔨 Building new image...
docker-compose build --no-cache

echo 🚀 Starting updated containers...
docker-compose up -d

echo ⏳ Waiting for health check...
timeout /t 15 /nobreak > nul

echo 🔍 Checking container status...
docker-compose ps
goto end

:clean
echo 🧹 Performing clean update (removes all data)...

REM Backup projects.json
if exist "projects.json" (
    echo 💾 Backing up projects.json...
    for /f "tokens=1-4 delims=/ " %%i in ('date /t') do set mydate=%%l%%j%%k
    for /f "tokens=1-2 delims=: " %%i in ('time /t') do set mytime=%%i%%j
    copy projects.json "projects.json.backup.!mydate!_!mytime!"
)

echo 🛑 Stopping and removing containers...
docker-compose down --volumes --remove-orphans

echo 🗑️ Removing old images...
docker image prune -f
docker volume prune -f

echo 🔨 Building fresh image...
docker-compose build --no-cache --pull

echo 🚀 Starting fresh containers...
docker-compose up -d

echo ⏳ Waiting for health check...
timeout /t 20 /nobreak > nul

echo 🔍 Checking container status...
docker-compose ps
goto end

:rolling
echo 🔄 Performing rolling update (zero downtime)...

echo 🔨 Building new image...
docker-compose build --no-cache

echo 📈 Scaling up with new version...
docker-compose up -d --scale qfil-downloader=2 --no-recreate

echo ⏳ Waiting for new container to be healthy...
timeout /t 30 /nobreak > nul

echo 📉 Scaling down to single instance...
docker-compose up -d --scale qfil-downloader=1

echo 🔍 Final status check...
docker-compose ps
goto end

:end
echo.
echo ✅ Update completed successfully!
echo 🌐 Application available at: http://localhost:5000
echo 📊 View logs with: docker-compose logs -f
echo 🔧 Manage projects at: http://localhost:5000/manage

REM Health check
echo.
echo 🏥 Performing health check...
curl -f -s http://localhost:5000/ > nul 2>&1
if %errorlevel%==0 (
    echo ✅ Health check passed - Application is running correctly
) else (
    echo ❌ Health check failed - Please check logs with: docker-compose logs
    exit /b 1
)

endlocal