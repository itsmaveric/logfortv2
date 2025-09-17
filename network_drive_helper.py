"""
Network Drive Helper for Windows UNC Path Access
Provides robust network folder connection and authentication for the Last Mile Tracking system.
"""

import os
import subprocess
import contextlib
import logging
try:
    import win32wnet
    WINDOWS_NETWORK_AVAILABLE = True
except ImportError:
    WINDOWS_NETWORK_AVAILABLE = False
    # Fallback for non-Windows environments
    class win32wnet:
        NETRESOURCE = object
        @staticmethod
        def WNetAddConnection2(*args): raise NotImplementedError("Windows network functions not available")
        @staticmethod
        def WNetCancelConnection2(*args): raise NotImplementedError("Windows network functions not available")  
        @staticmethod
        def WNetGetUniversalName(*args): raise NotImplementedError("Windows network functions not available")
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class NetworkDriveManager:
    """
    Manages Windows network drive connections and UNC path access.
    Handles authentication, connection persistence, and error recovery.
    """
    
    def __init__(self, server: str, share: str, username: Optional[str] = None, 
                 password: Optional[str] = None, domain: Optional[str] = None):
        self.server = server
        self.share = share
        self.username = username
        self.password = password
        self.domain = domain
        self.unc_path = self._normalize_unc_path(server, share)
        
    def _normalize_unc_path(self, server: str, share: str) -> str:
        """Normalize UNC path format"""
        # Remove any existing slashes and rebuild properly
        server = server.strip('\\/')
        share = share.strip('\\/')
        return f'\\\\{server}\\{share}'
    
    def test_connection(self) -> Tuple[bool, str]:
        """
        Test if the network path is accessible.
        Returns (success, message)
        """
        try:
            # First try direct access (if already authenticated)
            if os.path.exists(self.unc_path):
                return True, "Network path accessible"
            
            # If not accessible, try with authentication
            if self.username and self.password:
                return self._test_with_credentials()
            
            return False, "Path not accessible and no credentials provided"
            
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
    
    def _test_with_credentials(self) -> Tuple[bool, str]:
        """Test connection with provided credentials"""
        if not WINDOWS_NETWORK_AVAILABLE:
            return False, "Windows network functions not available on this platform"
        
        try:
            # Try connecting with credentials
            netresource = win32wnet.NETRESOURCE()
            netresource.lpRemoteName = self.unc_path
            
            user = f'{self.domain}\\{self.username}' if self.domain else self.username
            
            win32wnet.WNetAddConnection2(netresource, self.password, user, 0)
            
            # Test if path is now accessible
            if os.path.exists(self.unc_path):
                return True, "Connected successfully with credentials"
            else:
                return False, "Connected but path still not accessible"
                
        except Exception as e:
            return False, f"Authentication failed: {str(e)}"
    
    def connect(self) -> bool:
        """
        Establish connection to the network drive.
        Returns True if successful, False otherwise.
        """
        success, message = self.test_connection()
        if success:
            logger.info(f"Network drive connected: {self.unc_path}")
            return True
        else:
            logger.error(f"Failed to connect to {self.unc_path}: {message}")
            return False
    
    def disconnect(self):
        """Disconnect from the network drive"""
        if not WINDOWS_NETWORK_AVAILABLE:
            logger.warning("Windows network functions not available for disconnect")
            return
            
        try:
            win32wnet.WNetCancelConnection2(self.unc_path, 0, True)
            logger.info(f"Disconnected from {self.unc_path}")
        except Exception as e:
            logger.warning(f"Could not disconnect from {self.unc_path}: {e}")
    
    @contextlib.contextmanager
    def temporary_connection(self):
        """Context manager for temporary network connections"""
        connected = False
        try:
            if not os.path.exists(self.unc_path):
                if self.connect():
                    connected = True
                else:
                    raise ConnectionError(f"Could not connect to {self.unc_path}")
            
            yield self.unc_path
            
        finally:
            if connected:
                self.disconnect()
    
    def list_files(self, pattern: str = "*") -> list:
        """List files in the network folder"""
        try:
            import glob
            search_pattern = os.path.join(self.unc_path, pattern)
            return glob.glob(search_pattern)
        except Exception as e:
            logger.error(f"Error listing files in {self.unc_path}: {e}")
            return []
    
    def get_connection_info(self) -> dict:
        """Get information about the current connection"""
        return {
            'unc_path': self.unc_path,
            'server': self.server,
            'share': self.share,
            'username': self.username,
            'domain': self.domain,
            'accessible': os.path.exists(self.unc_path)
        }


class NetworkFolderValidator:
    """Validates and diagnoses network folder access issues"""
    
    @staticmethod
    def diagnose_path(path: str) -> dict:
        """
        Diagnose common UNC path issues.
        Returns diagnostic information and suggestions.
        """
        result = {
            'path': path,
            'is_unc': False,
            'exists': False,
            'accessible': False,
            'issues': [],
            'suggestions': []
        }
        
        # Check if it's a UNC path
        if path.startswith('\\\\'):
            result['is_unc'] = True
            
            # Parse UNC path
            parts = path.strip('\\').split('\\')
            if len(parts) >= 2:
                result['server'] = parts[0]
                result['share'] = parts[1]
            else:
                result['issues'].append('Invalid UNC path format')
                result['suggestions'].append('Use format: \\\\server\\share\\path')
        
        # Test existence and accessibility
        try:
            result['exists'] = os.path.exists(path)
            if result['exists']:
                try:
                    os.listdir(path)
                    result['accessible'] = True
                except PermissionError:
                    result['issues'].append('Permission denied')
                    result['suggestions'].append('Check network credentials and access rights')
                except Exception as e:
                    result['issues'].append(f'Access error: {e}')
            else:
                result['issues'].append('Path does not exist or is not reachable')
                result['suggestions'].append('Check server name, share name, and network connectivity')
        except Exception as e:
            result['issues'].append(f'Path validation error: {e}')
        
        return result
    
    @staticmethod
    def get_mapped_drives() -> list:
        """Get all currently mapped network drives"""
        drives = []
        for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            drive = f'{letter}:'
            if os.path.exists(drive):
                try:
                    # Try to get the UNC path for this drive
                    unc = win32wnet.WNetGetUniversalName(drive, 1)
                    drives.append({
                        'drive': drive,
                        'unc_path': unc,
                        'type': 'network'
                    })
                except:
                    drives.append({
                        'drive': drive,
                        'unc_path': None,
                        'type': 'local'
                    })
        return [d for d in drives if d['type'] == 'network']


def create_network_drive_manager(folder_path: str, username: str = None, 
                                password: str = None, domain: str = None) -> Optional[NetworkDriveManager]:
    """
    Factory function to create NetworkDriveManager from a folder path.
    Handles both UNC paths and mapped drive letters.
    """
    if not folder_path:
        return None
    
    # If it's a UNC path
    if folder_path.startswith('\\\\'):
        parts = folder_path.strip('\\').split('\\')
        if len(parts) >= 2:
            server = parts[0]
            share = parts[1]
            return NetworkDriveManager(server, share, username, password, domain)
    
    # If it's a drive letter, try to get the UNC path
    elif len(folder_path) >= 2 and folder_path[1] == ':':
        try:
            unc = win32wnet.WNetGetUniversalName(folder_path[:2], 1)
            # Parse the UNC path
            parts = unc.strip('\\').split('\\')
            if len(parts) >= 2:
                server = parts[0]
                share = parts[1]
                return NetworkDriveManager(server, share, username, password, domain)
        except:
            # It's a local drive, no network manager needed
            pass
    
    return None


def test_network_connectivity():
    """Test basic network connectivity and diagnose common issues"""
    print("=== Network Drive Connectivity Test ===")
    
    # Get mapped drives
    mapped = NetworkFolderValidator.get_mapped_drives()
    if mapped:
        print(f"\nMapped Network Drives ({len(mapped)}):")
        for drive in mapped:
            print(f"  {drive['drive']} -> {drive['unc_path']}")
    else:
        print("\nNo mapped network drives found")
    
    # Test a sample UNC path (you can modify this for testing)
    test_path = input("\nEnter UNC path to test (or press Enter to skip): ").strip()
    if test_path:
        result = NetworkFolderValidator.diagnose_path(test_path)
        print(f"\nDiagnosis for {test_path}:")
        print(f"  UNC Path: {result['is_unc']}")
        print(f"  Exists: {result['exists']}")
        print(f"  Accessible: {result['accessible']}")
        
        if result['issues']:
            print("  Issues:")
            for issue in result['issues']:
                print(f"    - {issue}")
        
        if result['suggestions']:
            print("  Suggestions:")
            for suggestion in result['suggestions']:
                print(f"    - {suggestion}")


if __name__ == "__main__":
    test_network_connectivity()