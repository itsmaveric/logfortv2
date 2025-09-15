#!/usr/bin/env python3
"""
Test script for desktop configuration system
"""
import os
import tempfile
from pathlib import Path
from desktop_app_fixed import DesktopConfig

def test_desktop_config():
    """Test the desktop configuration system"""
    # Create temporary config directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Override APPDATA for testing
        original_appdata = os.environ.get('APPDATA')
        os.environ['APPDATA'] = temp_dir
        
        try:
            # Create config instance
            config = DesktopConfig()
            
            print("✅ Desktop configuration system test:")
            print(f"   Config directory: {config.config_dir}")
            print(f"   Database file: {config.db_file}")
            print(f"   Uploads directory: {config.uploads_dir}")
            print(f"   Logs directory: {config.logs_dir}")
            
            # Test directories were created
            assert config.config_dir.exists(), "Config directory should exist"
            assert config.uploads_dir.exists(), "Uploads directory should exist"
            assert config.logs_dir.exists(), "Logs directory should exist"
            print("✅ All directories created successfully")
            
            # Test configuration defaults
            assert config.config['port'] == 5000, "Default port should be 5000"
            assert config.config['host'] == '127.0.0.1', "Default host should be localhost"
            assert config.config['first_run'] == True, "Should be first run"
            assert config.config['admin_password_hash'] is None, "No password hash initially"
            print("✅ Default configuration values correct")
            
            # Test password setting
            test_password = "secure_test_password_123"
            config.set_admin_password(test_password)
            
            assert config.config['admin_password_hash'] is not None, "Password hash should be set"
            assert config.config['first_run'] == False, "Should no longer be first run"
            assert config.verify_admin_password(test_password), "Password verification should work"
            assert not config.verify_admin_password("wrong_password"), "Wrong password should fail"
            print("✅ Password hashing and verification working")
            
            # Test config persistence
            config.save_config()
            assert config.config_file.exists(), "Config file should be saved"
            
            # Load new instance to test persistence
            config2 = DesktopConfig()
            assert config2.verify_admin_password(test_password), "Password should persist"
            assert config2.config['first_run'] == False, "First run flag should persist"
            print("✅ Configuration persistence working")
            
            print("\n🎉 All desktop configuration tests passed!")
            
        finally:
            # Restore original APPDATA
            if original_appdata:
                os.environ['APPDATA'] = original_appdata
            else:
                os.environ.pop('APPDATA', None)

if __name__ == '__main__':
    test_desktop_config()