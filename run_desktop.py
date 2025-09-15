#!/usr/bin/env python3
"""
Quick launcher for REFLIV Desktop Application
Use this for development and testing
"""
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    try:
        from desktop_app_fixed import main
        main()
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting desktop application: {e}")
        sys.exit(1)