#!/usr/bin/env python3
"""
Last Mile Tracking System - Desktop Application
Main entry point for the Windows desktop version
"""

# CRITICAL: Set ALL environment variables FIRST, before any other imports
import os
import sys

# Environment variables that MUST be set before importing pywebview
# Remove REMOTE_DEBUGGING_PORT as it causes Python runtime issues
os.environ.setdefault('PYTHONHTTPSVERIFY', '0')
os.environ.setdefault('WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS', '--disable-web-security --disable-features=VizDisplayCompositor --disable-dev-shm-usage --no-sandbox')
os.environ.setdefault('WEBVIEW2_USER_DATA_FOLDER', os.path.join(os.environ.get('APPDATA', '.'), 'LastMileTracking', 'webview2'))
os.environ.setdefault('PYWEBVIEW_LOG', '0')

# Now safe to import other modules
import json
import threading
import time
import logging
import secrets
from pathlib import Path

# Import pywebview last, after all environment variables are set
try:
    import webview
except ImportError:
    print("Error: pywebview not installed. Run: pip install pywebview")
    sys.exit(1)

try:
    from waitress import serve
except ImportError:
    print("Error: waitress not installed. Run: pip install waitress")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DesktopConfig:
    """Handle desktop application configuration"""
    
    def __init__(self):
        self.app_name = "Last Mile Tracking"
        self.config_dir = Path(os.environ.get('APPDATA', '.')) / 'LastMileTracking'
        self.config_file = self.config_dir / 'config.json'
        self.db_file = self.config_dir / 'tracking.db'
        self.uploads_dir = self.config_dir / 'uploads'
        self.logs_dir = self.config_dir / 'logs'
        
        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        
        self.config = self.load_config()
    
    def load_config(self):
        """Load or create configuration file"""
        default_config = {
            'admin_password_hash': None,  # Will be set on first run
            'port': 5000,
            'host': '127.0.0.1',
            'monitored_folders': [],
            'database_url': f'sqlite:///{self.db_file}',
            'secret_key': self._generate_secret_key(),
            'monitor_interval': 10,
            'auto_start_monitor': False,
            'first_run': True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults for new keys
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config=None):
        """Save configuration to file"""
        if config is None:
            config = self.config
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Configuration saved to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")
    
    def _generate_secret_key(self):
        """Generate a random secret key"""
        return secrets.token_hex(32)
    
    def set_admin_password(self, password):
        """Set admin password with proper hashing"""
        from werkzeug.security import generate_password_hash
        self.config['admin_password_hash'] = generate_password_hash(password)
        self.config['first_run'] = False
        self.save_config()
    
    def verify_admin_password(self, password):
        """Verify admin password"""
        from werkzeug.security import check_password_hash
        if not self.config.get('admin_password_hash'):
            return False
        return check_password_hash(self.config['admin_password_hash'], password)
    
    def is_first_run(self):
        """Check if this is the first run"""
        return self.config.get('first_run', True) or not self.config.get('admin_password_hash')


class DesktopApp:
    """Main desktop application class"""
    
    def __init__(self):
        self.config = DesktopConfig()
        self.server_thread = None
        self.flask_app = None
        self.running = False
        
        # Set environment variables for Flask app
        self._setup_environment()
    
    def _setup_environment(self):
        """Setup environment variables for the Flask application"""
        os.environ['DATABASE_URL'] = self.config.config['database_url']
        os.environ['SESSION_SECRET'] = self.config.config['secret_key']
        os.environ['DESKTOP_MODE'] = 'true'
        os.environ['UPLOADS_FOLDER'] = str(self.config.uploads_dir)
        os.environ['LOGS_FOLDER'] = str(self.config.logs_dir)
        
        # Additional desktop environment setup
        
        # Set admin password hash if available
        if self.config.config.get('admin_password_hash'):
            os.environ['ADMIN_PASSWORD_HASH'] = self.config.config['admin_password_hash']
    
    def _start_server(self):
        """Start the Flask server in a separate thread"""
        try:
            # Import Flask app
            from app import app
            self.flask_app = app
            
            # Configure for desktop use
            app.config['UPLOAD_FOLDER'] = str(self.config.uploads_dir)
            app.config['LOGS_FOLDER'] = str(self.config.logs_dir)
            
            # Start server
            host = self.config.config['host']
            port = self.config.config['port']
            
            logger.info(f"Starting server on {host}:{port}")
            serve(app, host=host, port=port, threads=6)
            
        except Exception as e:
            logger.error(f"Server error: {e}")
            self.running = False
    
    def _create_window(self):
        """Create and configure the main application window"""
        try:
            host = self.config.config['host']
            port = self.config.config['port']
            url = f"http://{host}:{port}"
            
            # Wait for server to start
            import requests
            for attempt in range(30):
                try:
                    response = requests.get(url, timeout=1)
                    if response.status_code == 200:
                        break
                except:
                    time.sleep(0.5)
            else:
                raise Exception("Server failed to start within timeout")
            
            # Create webview window with additional configuration
            window = webview.create_window(
                title=self.config.app_name,
                url=url,
                width=1200,
                height=800,
                min_size=(800, 600),
                resizable=True,
                shadow=True,
                on_top=False,
                text_select=False  # Disable text selection for app-like feel
            )
            
            return window
            
        except Exception as e:
            logger.error(f"Window creation error: {e}")
            return None
    
    def _start_folder_monitor(self):
        """Start the folder monitoring service if enabled"""
        if self.config.config.get('auto_start_monitor', False):
            try:
                # Import and start folder monitor
                from folder_monitor import start_monitor
                
                # Start the global monitor service
                if start_monitor():
                    logger.info("Folder monitoring started successfully")
                else:
                    logger.warning("Folder monitoring already running or failed to start")
                
            except Exception as e:
                logger.error(f"Folder monitor error: {e}")
    
    def _on_window_closing(self):
        """Handle window closing event"""
        logger.info("Application closing...")
        self.shutdown()
    
    def shutdown(self):
        """Gracefully shutdown the application"""
        self.running = False
        
        # Stop folder monitor
        try:
            from folder_monitor import stop_monitor
            stop_monitor()
            logger.info("Folder monitor stopped")
        except Exception as e:
            logger.error(f"Error stopping folder monitor: {e}")
        
        # Save configuration
        self.config.save_config()
        
        logger.info("Application shutdown complete")
    
    def run(self):
        """Main application entry point"""
        try:
            logger.info(f"Starting {self.config.app_name}...")
            self.running = True
            
            # Start Flask server in background thread
            self.server_thread = threading.Thread(target=self._start_server, daemon=True)
            self.server_thread.start()
            
            # Start folder monitoring if enabled
            self._start_folder_monitor()
            
            # Create and show main window
            window = self._create_window()
            if window:
                # Configure webview with safer settings
                webview.settings = {
                    'ALLOW_DOWNLOADS': True,
                    'ALLOW_FILE_URLS': True,
                    'DEBUG': False,
                    'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,
                    'OPEN_DEVTOOLS_IN_DEBUG': False
                }
                
                # Simple webview start - minimal configuration to avoid errors
                try:
                    webview.start(debug=False)
                except Exception as webview_error:
                    logger.error(f"WebView error: {webview_error}")
                    # Open in browser as fallback
                    import webbrowser
                    url = f"http://{self.config.config['host']}:{self.config.config['port']}"
                    webbrowser.open(url)
                    input("Press Enter to exit...")
            
            self.shutdown()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            self.shutdown()
            sys.exit(1)


def main():
    """Main entry point"""
    try:
        # Create and run desktop application
        app = DesktopApp()
        app.run()
        
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()