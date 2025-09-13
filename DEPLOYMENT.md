# REFLIV Desktop Application - Deployment Guide

## Overview
The REFLIV Desktop Application has been successfully converted from a web application to a Windows desktop application using PyWebView and SQLite.

## Architecture Summary
- **GUI Framework**: PyWebView (native Windows webview)
- **Backend**: Flask + Waitress server 
- **Database**: SQLite (embedded, stored in %APPDATA%\REFLIV\)
- **Assets**: Fully vendored (Bootstrap, Chart.js, Font Awesome) for offline operation
- **Security**: Password hashing, session management, secure configuration

## Deployment Instructions

### Prerequisites for Building
Install these dependencies on a Windows machine:
```bash
pip install -r requirements-desktop.txt
```

**Windows Runtime Requirements:**
- Microsoft Edge WebView2 Runtime (usually pre-installed on Windows 10/11)
- If missing, download from: https://developer.microsoft.com/en-us/microsoft-edge/webview2/

### Building the Executable
1. **On Windows development machine:**
   ```bash
   python build_desktop.py
   ```

2. **Manual PyInstaller (if build script fails):**
   ```bash
   pyinstaller --clean refliv_desktop.spec
   ```

### Distribution
The build process creates:
- `dist/REFLIV-Desktop.exe` - Main application executable
- `dist/install.bat` - Windows installer script  
- `dist/README.txt` - User documentation

### Installation Options

#### Option 1: Using Installer (Recommended)
1. Run `install.bat` as Administrator
2. Creates shortcuts on Desktop and Start Menu
3. Installs to `%PROGRAMFILES%\REFLIV\`

#### Option 2: Portable Mode
1. Simply run `REFLIV-Desktop.exe` directly
2. All data stored in `%APPDATA%\REFLIV\`

## File Structure (Post-Installation)
```
%APPDATA%\REFLIV\
├── config.json          # Application configuration
├── tracking.db          # SQLite database
├── uploads/             # File uploads directory
└── logs/                # Application logs
```

## Key Features Preserved
✅ **Folder Monitoring** - Background service with UI controls  
✅ **Analytics Dashboard** - Charts and export functionality  
✅ **File Management** - Upload, tracking, and search  
✅ **Security** - Password protection and encrypted storage  
✅ **Offline Operation** - No internet required  

## Development Mode
For development/testing:
```bash
python run_desktop.py
```

## Building Notes
- **Linux/Replit Limitation**: PyWebView requires Windows for GUI testing
- **Dependencies**: All Flask/SQLAlchemy dependencies aligned for SQLite
- **Size**: Executable ~50-100MB (includes Python runtime + dependencies)
- **Compatibility**: Windows 10+ required

## Next Steps for Production
1. **Test on Windows**: Build and test the executable on Windows machine
2. **Code Signing**: Sign executable for Windows security warnings
3. **Proper Installer**: Consider NSIS/Inno Setup for professional installer
4. **Auto-Updater**: Implement update mechanism if needed

## Troubleshooting
- **Import Errors**: Check hiddenimports in `refliv_desktop.spec`
- **Asset Issues**: Verify templates use `url_for('static', ...)` paths
- **Database**: SQLite files created automatically on first run