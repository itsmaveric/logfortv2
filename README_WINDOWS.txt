================================================================================
                     LAST MILE TRACKING - Windows Desktop App
================================================================================

QUICK START:
1. Double-click "LastMileTracking.exe" to launch
2. The application will start automatically in your default browser
3. Begin monitoring log files immediately

FEATURES:
✓ Standalone Windows executable - no installation required
✓ Automatic log file monitoring (log_tracktrace.log, .log.1 to .log.10)
✓ Beautiful status timeline visualization
✓ Complete offline functionality with SQLite database
✓ Production-ready parsing for large log files

FILE LOCATIONS:
- App Data: %APPDATA%\LastMileTracking\
- Database: %APPDATA%\LastMileTracking\tracking.db
- Uploads: %APPDATA%\LastMileTracking\uploads\
- Logs: %APPDATA%\LastMileTracking\logs\

MONITORING SETUP:
1. Click "Folder Settings" in the app
2. Add your log file directories
3. Files named "log_tracktrace" with extensions .log, .log.1 to .log.10 will be monitored
4. Supports timestamped patterns like: log_tracktrace.log_1757956433358.1

NETWORK FOLDERS:
✓ Supports UNC paths (\\server\share\logs)
✓ Mapped network drives (Z:\logs)
✓ Local folders (C:\logs)

SYSTEM REQUIREMENTS:
- Windows 10/11 (64-bit)
- 50MB free disk space
- Network access for monitored folders

SUPPORT:
- The app creates diagnostic logs in %APPDATA%\LastMileTracking\logs\
- If issues occur, check the logs folder for error details

SECURITY:
- All data stored locally on your machine
- No internet connection required after initial setup
- No external data transmission

VERSION: 1.0
BUILD DATE: September 2025