#!/usr/bin/env python3
"""
Last Mile Tracking System - Desktop Application
Minimal, stable version without REMOTE_DEBUGGING_PORT issues
"""

import os
import sys
import json
import threading
import time
import logging
import secrets
from pathlib import Path

# Set minimal environment variables - avoid problematic ones
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['PYWEBVIEW_LOG'] = '0'

# Import dependencies with error handling
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
            'admin_password_hash': None,
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
        self._setup_environment()
    
    def _setup_environment(self):
        """Setup environment variables for the Flask application"""
        os.environ['DATABASE_URL'] = self.config.config['database_url']
        os.environ['SESSION_SECRET'] = self.config.config['secret_key']
        os.environ['DESKTOP_MODE'] = 'true'
        os.environ['UPLOADS_FOLDER'] = str(self.config.uploads_dir)
        os.environ['LOGS_FOLDER'] = str(self.config.logs_dir)
        
        # Set admin password hash if available
        if self.config.config.get('admin_password_hash'):
            os.environ['ADMIN_PASSWORD_HASH'] = self.config.config['admin_password_hash']
    
    def _start_server(self):
        """Start the Flask server in a separate thread"""
        try:
            from app import app
            self.flask_app = app
            
            app.config['UPLOAD_FOLDER'] = str(self.config.uploads_dir)
            app.config['LOGS_FOLDER'] = str(self.config.logs_dir)
            
            host = self.config.config['host']
            port = self.config.config['port']
            
            logger.info(f"Starting server on {host}:{port}")
            serve(app, host=host, port=port, threads=6)
            
        except Exception as e:
            logger.error(f"Server error: {e}")
            self.running = False
    
    def _wait_for_server(self):
        """Wait for server to start"""
        import requests
        url = f"http://{self.config.config['host']}:{self.config.config['port']}"
        
        for attempt in range(30):
            try:
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    logger.info("Server started successfully")
                    return True
            except:
                time.sleep(0.5)
        
        logger.error("Server failed to start within timeout")
        return False
    
    def _open_browser_fallback(self):
        """Open application in default browser as fallback"""
        import webbrowser
        url = f"http://{self.config.config['host']}:{self.config.config['port']}"
        logger.info(f"Opening {url} in default browser")
        webbrowser.open(url)
        print(f"\nLast Mile Tracking is now running at: {url}")
        print("Press Ctrl+C to stop the application.")
        
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Application stopped by user")
    
    def run(self):
        """Main application entry point"""
        try:
            logger.info(f"Starting {self.config.app_name}...")
            self.running = True
            
            # Start Flask server
            self.server_thread = threading.Thread(target=self._start_server, daemon=True)
            self.server_thread.start()
            
            # Wait for server to start
            if not self._wait_for_server():
                logger.error("Failed to start server")
                return
            
            # Try webview first, fallback to browser
            url = f"http://{self.config.config['host']}:{self.config.config['port']}"
            
            try:
                # Minimal webview configuration
                window = webview.create_window(
                    title=self.config.app_name,
                    url=url,
                    width=1200,
                    height=800,
                    resizable=True
                )
                
                # Start webview with minimal options
                webview.start(debug=False)
                
            except Exception as webview_error:
                logger.warning(f"WebView failed: {webview_error}")
                logger.info("Falling back to browser mode")
                self._open_browser_fallback()
            
        except Exception as e:
            logger.error(f"Application error: {e}")
            sys.exit(1)
        finally:
            self.running = False
            self.config.save_config()


def main():
    """Main entry point"""
    try:
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