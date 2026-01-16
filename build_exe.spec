# -*- mode: python ; coding: utf-8 -*-
"""
ClipForge - PyInstaller Build Configuration
Build a single executable file

Usage:
  pyinstaller build_exe.spec

Output:
  dist/ClipForge.exe (Windows)
  dist/ClipForge.app (macOS)
"""

import sys
import os

# Get the project root
project_root = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# Collect all source files
a = Analysis(
    ['main.py'],
    pathex=[project_root],
    binaries=[],
    datas=[
        # Include stylesheets
        ('ui/styles.qss', 'ui'),
        # Include assets folder
        ('assets', 'assets'),
        # Include effects
        ('effects', 'effects'),
    ],
    hiddenimports=[
        'PyQt6',
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'PIL',
        'PIL.Image',
        'numpy',
        'json',
        'sqlite3',
        'urllib.request',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'scipy',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Create PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Single executable configuration
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ClipForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Compress with UPX
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window (GUI app)
    disable_windowed_traceback=False,
    argv_emulation=True,  # macOS compatibility
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico' if sys.platform == 'win32' else 'assets/icons/app_icon.icns',
)

# macOS App Bundle (only on macOS)
if sys.platform == 'darwin':
    app = BUNDLE(
        exe,
        name='ClipForge.app',
        icon='assets/icons/app_icon.icns',
        bundle_identifier='com.clipforge.videoeditor',
        info_plist={
            'CFBundleName': 'ClipForge',
            'CFBundleDisplayName': 'ClipForge Video Editor',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
            'NSRequiresAquaSystemAppearance': False,  # Support dark mode
        },
    )
