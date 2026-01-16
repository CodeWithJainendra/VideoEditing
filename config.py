"""
ClipForge Configuration
"""
import os
import sys
from pathlib import Path

# App Info
APP_NAME = "ClipForge"
APP_VERSION = "1.0.0"
APP_AUTHOR = "ClipForge Team"

# Detect if running as PyInstaller bundle
def is_bundled():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')

# Paths - Handle both development and bundled execution
if is_bundled():
    # Running as .exe - use temp extraction path for readonly assets
    BUNDLE_DIR = Path(sys._MEIPASS)
    ASSETS_DIR = BUNDLE_DIR / "assets"
    
    # Use user's AppData for writable directories
    if sys.platform == 'win32':
        USER_DATA_DIR = Path(os.environ.get('LOCALAPPDATA', os.path.expanduser('~'))) / "ClipForge"
    else:
        USER_DATA_DIR = Path.home() / ".clipforge"
    
    TEMP_DIR = USER_DATA_DIR / "temp"
    GENERATED_DIR = USER_DATA_DIR / "generated"
else:
    # Running in development
    BASE_DIR = Path(__file__).parent
    ASSETS_DIR = BASE_DIR / "assets"
    USER_DATA_DIR = BASE_DIR
    TEMP_DIR = BASE_DIR / "temp"
    GENERATED_DIR = ASSETS_DIR / "generated"

ICONS_DIR = ASSETS_DIR / "icons"
FONTS_DIR = ASSETS_DIR / "fonts"

# Create necessary directories
for dir_path in [TEMP_DIR, GENERATED_DIR, USER_DATA_DIR]:
    try:
        dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directory {dir_path}: {e}")

# Video Settings
DEFAULT_FPS = 30
DEFAULT_RESOLUTION = (1920, 1080)
PREVIEW_RESOLUTION = (640, 360)

# Timeline Settings
TIMELINE_HEIGHT = 200
TRACK_HEIGHT = 60
PIXELS_PER_SECOND = 50  # Zoom level

# Supported Formats
VIDEO_FORMATS = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.wmv', '.flv']
AUDIO_FORMATS = ['.mp3', '.wav', '.aac', '.ogg', '.m4a', '.flac']
IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff']

# Export Settings
EXPORT_PRESETS = {
    'web_hd': {
        'name': 'Web HD (720p)',
        'resolution': (1280, 720),
        'bitrate': '5M',
        'fps': 30,
        'codec': 'libx264'
    },
    'full_hd': {
        'name': 'Full HD (1080p)',
        'resolution': (1920, 1080),
        'bitrate': '10M',
        'fps': 30,
        'codec': 'libx264'
    },
    'quad_hd': {
        'name': 'Quad HD (1440p)',
        'resolution': (2560, 1440),
        'bitrate': '20M',
        'fps': 30,
        'codec': 'libx264'
    },
    '4k': {
        'name': '4K Ultra HD',
        'resolution': (3840, 2160),
        'bitrate': '40M',
        'fps': 30,
        'codec': 'libx264'
    }
}

# Colors (Modern Dark Theme)
COLORS = {
    'bg_primary': '#0f0f0f',
    'bg_secondary': '#1a1a1a',
    'bg_tertiary': '#252525',
    'accent': '#6366f1',
    'accent_hover': '#818cf8',
    'accent_glow': '#4f46e5',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'text_primary': '#ffffff',
    'text_secondary': '#a1a1aa',
    'text_muted': '#71717a',
    'border': '#3f3f46',
    'timeline_video': '#6366f1',
    'timeline_audio': '#10b981',
    'timeline_image': '#f59e0b',
    'timeline_text': '#ec4899'
}
