#!/usr/bin/env python3
"""
Modify PyInstaller spec file to include all necessary files for Last Mile Tracking
"""

spec_template = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_app_fixed.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
        ('favicon.ico', '.'),
    ],
    hiddenimports=[
        'pkg_resources.py2_warn',
        'werkzeug.serving',
        'waitress.server',
        'sqlalchemy.sql.default_comparator',
        'email_validator',
        'flask_sqlalchemy',
        'sqlite3',
        'pathlib',
        'threading',
        'logging.handlers'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='LastMileTracking',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='favicon.ico' if os.path.exists('favicon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
'''

import os

print("Creating enhanced PyInstaller spec file...")

with open('LastMileTracking.spec', 'w') as f:
    f.write(spec_template)

print("✅ Spec file created: LastMileTracking.spec")
print("✅ Included templates, static files, and dependencies")
print("✅ Console window disabled for clean desktop experience")