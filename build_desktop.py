#!/usr/bin/env python3
"""
Build script for REFLIV Desktop Application
Creates a standalone Windows executable using PyInstaller
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required build dependencies are installed"""
    try:
        import PyInstaller
        logger.info(f"PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        logger.error("PyInstaller not found. Install with: pip install pyinstaller")
        return False
    
    # Check for required modules
    required_modules = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'sqlalchemy', 
        'pywebview', 'waitress', 'werkzeug', 'requests', 
        'email_validator', 'openpyxl'
    ]
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        logger.error(f"Missing required modules: {missing}")
        return False
    
    return True

def clean_build():
    """Clean previous build artifacts"""
    logger.info("Cleaning previous build artifacts...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dirname in dirs_to_clean:
        if os.path.exists(dirname):
            shutil.rmtree(dirname)
            logger.info(f"Removed {dirname}/")
    
    # Clean spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        logger.info(f"Removed {spec_file}")

def create_pyinstaller_spec():
    """Create PyInstaller spec file"""
    logger.info("Creating PyInstaller spec file...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

# Get the current directory
workpath = os.getcwd()

# Data files to include
datas = [
    ('templates', 'templates'),
    ('static', 'static'),
]

# Hidden imports (modules that PyInstaller might miss)
hiddenimports = [
    'flask',
    'flask_sqlalchemy',
    'flask_login',
    'sqlalchemy',
    'sqlalchemy.sql.default_comparator',
    'sqlalchemy.pool',
    'sqlalchemy.dialects.sqlite',
    'pywebview',
    'waitress',
    'werkzeug',
    'werkzeug.security',
    'requests',
    'email_validator',
    'openpyxl',
    'sqlite3',
    'logging.handlers',
    'datetime',
    'threading',
    'queue',
    'json',
    'pathlib',
    'hashlib',
    'secrets',
    'time',
    'os',
    'sys',
    'platform',
    'dns',
]

# Analysis configuration
a = Analysis(
    ['desktop_app_fixed.py'],
    pathex=[workpath],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'PIL',
        'numpy',
        'pandas',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# Remove duplicate files
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='REFLIV-Desktop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # Disable UPX to avoid build issues
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/icon.ico' if os.path.exists('static/icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
"""
    
    with open('refliv_desktop.spec', 'w') as f:
        f.write(spec_content)
    
    logger.info("Created refliv_desktop.spec")

def create_version_info():
    """Create version info file for Windows executable"""
    logger.info("Creating version info file...")
    
    version_info = """# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'REFLIV'),
        StringStruct(u'FileDescription', u'REFLIV Tracking System - Desktop Application'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'REFLIV-Desktop'),
        StringStruct(u'LegalCopyright', u'Copyright © 2025 REFLIV'),
        StringStruct(u'OriginalFilename', u'REFLIV-Desktop.exe'),
        StringStruct(u'ProductName', u'REFLIV Tracking System'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""
    
    with open('version_info.txt', 'w') as f:
        f.write(version_info)
    
    logger.info("Created version_info.txt")

def build_executable():
    """Build the executable using PyInstaller"""
    logger.info("Building executable with PyInstaller...")
    
    try:
        # Run PyInstaller
        cmd = [sys.executable, '-m', 'PyInstaller', '--clean', 'refliv_desktop.spec']
        
        logger.info(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Build completed successfully!")
            logger.info("Output:")
            for line in result.stdout.split('\n'):
                if line.strip():
                    logger.info(f"  {line}")
        else:
            logger.error("Build failed!")
            logger.error("Error output:")
            for line in result.stderr.split('\n'):
                if line.strip():
                    logger.error(f"  {line}")
            return False
            
    except Exception as e:
        logger.error(f"Build error: {e}")
        return False
    
    return True

def create_installer_script():
    """Create an installer script for the application"""
    logger.info("Creating installer script...")
    
    installer_content = """@echo off
echo REFLIV Desktop Application Installer
echo ====================================
echo.

set "INSTALL_DIR=%PROGRAMFILES%\\REFLIV"
set "APPDATA_DIR=%APPDATA%\\REFLIV"

echo Installing REFLIV Desktop Application...
echo.

:: Create installation directory
if not exist "%INSTALL_DIR%" (
    mkdir "%INSTALL_DIR%"
    echo Created installation directory: %INSTALL_DIR%
)

:: Copy application files
copy "REFLIV-Desktop.exe" "%INSTALL_DIR%\\" > nul
if errorlevel 1 (
    echo Error: Failed to copy application files
    pause
    exit /b 1
)

:: Create desktop shortcut
echo Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\\Desktop\\REFLIV Desktop.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\REFLIV-Desktop.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'REFLIV Tracking System'; $Shortcut.Save()"

:: Create start menu shortcut
echo Creating start menu shortcut...
if not exist "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\REFLIV" (
    mkdir "%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\REFLIV"
)
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\REFLIV\\REFLIV Desktop.lnk'); $Shortcut.TargetPath = '%INSTALL_DIR%\\REFLIV-Desktop.exe'; $Shortcut.WorkingDirectory = '%INSTALL_DIR%'; $Shortcut.Description = 'REFLIV Tracking System'; $Shortcut.Save()"

echo.
echo Installation completed successfully!
echo.
echo Application installed to: %INSTALL_DIR%
echo Configuration will be stored in: %APPDATA_DIR%
echo.
echo You can now run REFLIV Desktop from:
echo - Desktop shortcut
echo - Start Menu ^> REFLIV ^> REFLIV Desktop
echo.
pause
"""
    
    with open('dist/install.bat', 'w') as f:
        f.write(installer_content)
    
    logger.info("Created dist/install.bat")

def create_readme():
    """Create README file for distribution"""
    logger.info("Creating README file...")
    
    readme_content = """# REFLIV Desktop Application

## Overview
REFLIV Desktop is a standalone Windows application for tracking and monitoring log files. It provides a comprehensive dashboard for analytics, file monitoring, and export capabilities.

## Features
- **Offline Operation**: Works completely offline without internet connection
- **Folder Monitoring**: Automatically monitor specified folders for log files
- **Analytics Dashboard**: Interactive charts and data visualization
- **Export Options**: Export data to CSV, Excel, JSON formats
- **Secure**: Password-protected access with encrypted storage
- **Portable**: All data stored in user's AppData directory

## Installation

### Method 1: Using Installer (Recommended)
1. Extract all files to a folder
2. Right-click `install.bat` and select "Run as administrator"
3. Follow the installation prompts
4. Launch from Desktop or Start Menu

### Method 2: Portable Mode
1. Simply run `REFLIV-Desktop.exe` directly
2. All configuration will be stored in `%APPDATA%\\REFLIV\\`

## First Run Setup
1. Launch the application
2. Set an admin password when prompted
3. Configure folder monitoring in the Monitor section
4. Start using the tracking system

## Data Storage
- **Configuration**: `%APPDATA%\\REFLIV\\config.json`
- **Database**: `%APPDATA%\\REFLIV\\tracking.db`
- **Uploads**: `%APPDATA%\\REFLIV\\uploads\\`
- **Logs**: `%APPDATA%\\REFLIV\\logs\\`

## System Requirements
- Windows 10 or later
- 100 MB free disk space
- 512 MB RAM

## Support
For support or questions, please refer to the application documentation.

## Version
Version 1.0.0
Built with PyInstaller
"""
    
    with open('dist/README.txt', 'w') as f:
        f.write(readme_content)
    
    logger.info("Created dist/README.txt")

def main():
    """Main build process"""
    logger.info("Starting REFLIV Desktop build process...")
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Build dependencies not met. Exiting.")
        return False
    
    # Clean previous builds
    clean_build()
    
    # Create build files
    create_pyinstaller_spec()
    create_version_info()
    
    # Build executable
    if not build_executable():
        logger.error("Build failed. Exiting.")
        return False
    
    # Check if executable was created
    exe_path = Path('dist/REFLIV-Desktop.exe')
    if not exe_path.exists():
        logger.error("Executable not found at dist/REFLIV-Desktop.exe")
        return False
    
    # Get file size
    file_size = exe_path.stat().st_size / (1024 * 1024)  # MB
    logger.info(f"Executable created: {exe_path} ({file_size:.1f} MB)")
    
    # Create additional distribution files
    create_installer_script()
    create_readme()
    
    logger.info("Build process completed successfully!")
    logger.info("Distribution files created in dist/ directory:")
    logger.info("  - REFLIV-Desktop.exe (main application)")
    logger.info("  - install.bat (installer script)")
    logger.info("  - README.txt (documentation)")
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)