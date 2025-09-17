@echo off
REM Last Mile Tracking - Windows Build Script
echo ============================================
echo   Building Last Mile Tracking for Windows
echo ============================================

echo.
echo [1/6] Installing required packages...
pip install pyinstaller pywebview waitress flask flask-sqlalchemy werkzeug

echo.
echo [2/6] Cleaning previous builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"
if exist "desktop_app.spec" del "desktop_app.spec"

echo.
echo [3/6] Creating PyInstaller spec file...
pyi-makespec --onefile --windowed --name "LastMileTracking" desktop_app_fixed.py

echo.
echo [4/6] Modifying spec file for complete packaging...
python modify_spec.py

echo.
echo [5/6] Building executable with PyInstaller...
pyinstaller --clean LastMileTracking.spec

echo.
echo [6/6] Creating portable distribution...
if not exist "dist\LastMileTracking_Portable" mkdir "dist\LastMileTracking_Portable"
copy "dist\LastMileTracking.exe" "dist\LastMileTracking_Portable\"
copy "README_WINDOWS.txt" "dist\LastMileTracking_Portable\"

echo.
echo ============================================
echo   Build Complete!
echo ============================================
echo.
echo Your Windows application is ready:
echo   Location: dist\LastMileTracking_Portable\
echo   Executable: LastMileTracking.exe
echo.
echo To run: Double-click LastMileTracking.exe
echo.
pause