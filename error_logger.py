#!/usr/bin/env python3
"""
Custom Error Logger for Last Mile Tracking System
Provides centralized error logging with file rotation and easy access
"""

import os
import logging
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class ErrorLogger:
    """Custom error logger with file rotation and structured logging."""
    
    def __init__(self, log_dir=None, max_bytes=10485760, backup_count=5):
        """
        Initialize the error logger.
        
        Args:
            log_dir (str): Directory to store log files (default: logs/)
            max_bytes (int): Maximum file size before rotation (default: 10MB)
            backup_count (int): Number of backup files to keep (default: 5)
        """
        self.log_dir = Path(log_dir) if log_dir else Path('logs')
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure main error logger
        self.logger = logging.getLogger('last_mile_errors')
        self.logger.setLevel(logging.ERROR)
        
        # Clear existing handlers to avoid duplicates
        self.logger.handlers.clear()
        
        # Create error log file path
        error_log_file = self.log_dir / 'last_mile_errors.log'
        
        # Create rotating file handler
        file_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        
        # Create detailed formatter
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(module)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        # Also create a console handler for immediate feedback
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.ERROR)
        console_formatter = logging.Formatter('ERROR: %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # Set up application-specific logger
        self.app_logger = logging.getLogger('last_mile_app')
        self.app_logger.setLevel(logging.INFO)
        
        # Create app log file
        app_log_file = self.log_dir / 'last_mile_app.log'
        app_handler = RotatingFileHandler(
            app_log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        app_handler.setFormatter(formatter)
        self.app_logger.addHandler(app_handler)
    
    def log_error(self, message, exception=None, context=None):
        """
        Log an error with optional exception details and context.
        
        Args:
            message (str): Error message
            exception (Exception): Optional exception object
            context (dict): Optional context information
        """
        error_msg = f"{message}"
        
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            error_msg += f" | Context: {context_str}"
        
        if exception:
            error_msg += f" | Exception: {str(exception)}"
            self.logger.exception(error_msg)
        else:
            self.logger.error(error_msg)
    
    def log_critical(self, message, exception=None, context=None):
        """Log a critical error that might require immediate attention."""
        error_msg = f"CRITICAL: {message}"
        
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            error_msg += f" | Context: {context_str}"
        
        if exception:
            error_msg += f" | Exception: {str(exception)}"
            self.logger.critical(error_msg)
        else:
            self.logger.critical(error_msg)
    
    def log_warning(self, message, context=None):
        """Log a warning message."""
        warning_msg = f"WARNING: {message}"
        
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            warning_msg += f" | Context: {context_str}"
        
        # Use app logger for warnings
        self.app_logger.warning(warning_msg)
    
    def log_info(self, message, context=None):
        """Log an informational message."""
        info_msg = message
        
        if context:
            context_str = " | ".join([f"{k}={v}" for k, v in context.items()])
            info_msg += f" | Context: {context_str}"
        
        self.app_logger.info(info_msg)
    
    def log_file_processing_error(self, filename, error_message, exception=None):
        """Specialized logging for file processing errors."""
        context = {
            'filename': filename,
            'operation': 'file_processing'
        }
        self.log_error(f"File processing failed: {error_message}", exception, context)
    
    def log_database_error(self, operation, error_message, exception=None):
        """Specialized logging for database errors."""
        context = {
            'operation': operation,
            'component': 'database'
        }
        self.log_error(f"Database error: {error_message}", exception, context)
    
    def log_monitoring_error(self, folder_path, error_message, exception=None):
        """Specialized logging for folder monitoring errors."""
        context = {
            'folder_path': folder_path,
            'operation': 'folder_monitoring'
        }
        self.log_error(f"Monitoring error: {error_message}", exception, context)
    
    def get_log_files(self):
        """Get list of available log files."""
        log_files = []
        
        # Get error log files
        error_logs = list(self.log_dir.glob('last_mile_errors.log*'))
        error_logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Get app log files
        app_logs = list(self.log_dir.glob('last_mile_app.log*'))
        app_logs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for log_file in error_logs + app_logs:
            if log_file.exists():
                stat = log_file.stat()
                log_files.append({
                    'name': log_file.name,
                    'path': str(log_file),
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime)
                })
        
        return log_files
    
    def read_recent_errors(self, lines=50):
        """Read recent error entries from the log file."""
        error_log_file = self.log_dir / 'last_mile_errors.log'
        
        if not error_log_file.exists():
            return []
        
        try:
            with open(error_log_file, 'r') as f:
                all_lines = f.readlines()
                return all_lines[-lines:]
        except Exception as e:
            return [f"Error reading log file: {str(e)}"]


# Global error logger instance
_error_logger = None

def get_error_logger():
    """Get the global error logger instance."""
    global _error_logger
    if _error_logger is None:
        # Determine log directory based on environment
        if os.environ.get('DESKTOP_MODE', 'false').lower() == 'true':
            # Desktop mode: use local logs directory
            log_dir = 'logs'
        else:
            # Web mode: use system temp directory
            log_dir = '/tmp/last_mile_logs'
        
        _error_logger = ErrorLogger(log_dir=log_dir)
    return _error_logger

# Convenience functions for easy use throughout the application
def log_error(message, exception=None, context=None):
    """Quick error logging function."""
    get_error_logger().log_error(message, exception, context)

def log_critical(message, exception=None, context=None):
    """Quick critical error logging function."""
    get_error_logger().log_critical(message, exception, context)

def log_warning(message, context=None):
    """Quick warning logging function."""
    get_error_logger().log_warning(message, context)

def log_info(message, context=None):
    """Quick info logging function."""
    get_error_logger().log_info(message, context)

def log_file_error(filename, error_message, exception=None):
    """Quick file processing error logging."""
    get_error_logger().log_file_processing_error(filename, error_message, exception)

def log_db_error(operation, error_message, exception=None):
    """Quick database error logging."""
    get_error_logger().log_database_error(operation, error_message, exception)

def log_monitor_error(folder_path, error_message, exception=None):
    """Quick monitoring error logging."""
    get_error_logger().log_monitoring_error(folder_path, error_message, exception)

# Example usage demonstration (for testing)
if __name__ == "__main__":
    # Test the error logger
    log_info("Application started", {'version': '1.0', 'mode': 'test'})
    log_warning("This is a test warning", {'component': 'test'})
    log_error("This is a test error", context={'test_id': 123})
    
    try:
        raise ValueError("Test exception")
    except Exception as e:
        log_critical("Critical test error", exception=e, context={'test': True})
    
    print("Error logging test completed. Check logs/ directory for output.")