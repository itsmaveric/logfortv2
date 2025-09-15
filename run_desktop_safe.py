#!/usr/bin/env python3
"""
REFLIV Desktop - Safe Mode Launcher
Alternative launcher with enhanced error handling and debugging options
"""
import os
import sys
import webbrowser
import time
import subprocess

def set_safe_environment():
    """Set all necessary environment variables for safe PyWebView operation"""
    env_vars = {
        'REMOTE_DEBUGGING_PORT': '0',
        'PYTHONHTTPSVERIFY': '0',
        'WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS': '--disable-web-security --disable-features=VizDisplayCompositor --disable-dev-shm-usage',
        'WEBVIEW2_USER_DATA_FOLDER': os.path.join(os.environ.get('APPDATA', '.'), 'REFLIV', 'webview2'),
        'PYWEBVIEW_LOG': '1',  # Enable logging
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"Set {key}={value}")

def test_imports():
    """Test that all required modules can be imported"""
    modules = ['flask', 'waitress', 'pywebview']
    missing = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module} imported successfully")
        except ImportError as e:
            print(f"✗ {module} import failed: {e}")
            missing.append(module)
    
    return missing

def start_server_only():
    """Start only the Flask server without GUI"""
    try:
        print("\n=== Starting server-only mode ===")
        from desktop_app_fixed import DesktopApp
        
        # Create app but override the run method
        app = DesktopApp()
        app._setup_environment()
        
        print("Starting Flask server...")
        host = app.config.config['host']
        port = app.config.config['port']
        
        # Start server in current thread
        from app import app as flask_app
        from waitress import serve
        
        flask_app.config['UPLOAD_FOLDER'] = str(app.config.uploads_dir)
        flask_app.config['LOGS_FOLDER'] = str(app.config.logs_dir)
        
        print(f"Server starting on http://{host}:{port}")
        print("You can manually open this URL in your browser")
        
        # Optionally open browser
        try:
            webbrowser.open(f"http://{host}:{port}")
        except:
            pass
        
        serve(flask_app, host=host, port=port, threads=6)
        
    except Exception as e:
        print(f"Server startup failed: {e}")
        return False
    
    return True

def try_desktop_mode():
    """Try to start the full desktop application"""
    try:
        print("\n=== Attempting desktop mode ===")
        set_safe_environment()
        
        # Import and run desktop app
        from desktop_app_fixed import main
        main()
        return True
        
    except Exception as e:
        print(f"Desktop mode failed: {e}")
        print("Error details:", str(e))
        return False

def main():
    """Main launcher with fallback options"""
    print("REFLIV Desktop Application - Safe Mode Launcher")
    print("=" * 50)
    
    # Test imports first
    print("\n1. Testing module imports...")
    missing = test_imports()
    
    if missing:
        print(f"\nERROR: Missing modules: {missing}")
        print("Please install them with: pip install " + " ".join(missing))
        return
    
    # Set environment variables
    print("\n2. Setting safe environment variables...")
    set_safe_environment()
    
    # Try desktop mode first
    print("\n3. Trying desktop mode...")
    if try_desktop_mode():
        print("Desktop mode started successfully!")
        return
    
    # Fallback to server-only mode
    print("\n4. Falling back to server-only mode...")
    print("This will start the web server and open your browser")
    
    choice = input("Continue with server-only mode? (y/N): ").lower().strip()
    if choice in ('y', 'yes'):
        start_server_only()
    else:
        print("Launch cancelled.")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nLauncher interrupted by user")
    except Exception as e:
        print(f"\nLauncher error: {e}")
        input("Press Enter to exit...")