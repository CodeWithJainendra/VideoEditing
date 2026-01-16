# 🎬 ClipForge - Free Professional Video Editor

A powerful, free video editing software with no watermarks. Built with Python, PyQt6, and FFmpeg.

## ✨ Features

- **Timeline-based editing** - Drag & drop video, audio, and image clips
- **Cut, Trim, Split** - Precise editing tools
- **Text Overlays** - Add styled text to your videos
- **Background Music** - Layer audio tracks
- **Transitions** - Smooth transitions between clips
- **Preview Window** - Real-time preview
- **Export to MP4** - High quality exports with NO watermark
- **Works Offline** - No internet required

## 🚀 Quick Start

### Prerequisites

```bash
# Install Python 3.9+
# Install FFmpeg
brew install ffmpeg  # macOS
# or
choco install ffmpeg  # Windows
```

### Installation

```bash
# Clone/navigate to project
cd VideoEditing

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run the app
python main.py
```

## 📦 Build Executable

### macOS
```bash
pyinstaller --name ClipForge --windowed --icon=assets/icon.icns main.py
```

### Windows
```bash
pyinstaller --name ClipForge --windowed --icon=assets/icon.ico main.py
```

## 📁 Project Structure

```
ClipForge/
├── main.py                 # Entry point
├── requirements.txt        # Dependencies
├── config.py              # App configuration
├── ui/
│   ├── main_window.py     # Main application window
│   ├── timeline.py        # Timeline widget
│   ├── preview.py         # Video preview panel
│   ├── media_browser.py   # Media import panel
│   ├── properties.py      # Properties panel
│   └── styles.qss         # Qt stylesheet
├── core/
│   ├── project.py         # Project management
│   ├── clip.py            # Clip data models
│   ├── ffmpeg_engine.py   # FFmpeg wrapper
│   └── exporter.py        # Export functionality
├── effects/
│   ├── transitions.py     # Transition effects
│   └── text_overlay.py    # Text effects
└── assets/
    ├── icons/             # UI icons
    └── fonts/             # Custom fonts
```

## 🎯 Roadmap

### MVP (Current)
- [x] Basic timeline
- [x] Import media
- [x] Cut/trim/split
- [x] Text overlays
- [x] Audio tracks
- [x] MP4 export

### v2.0 (Planned)
- [ ] Transitions library
- [ ] Filters & effects
- [ ] Keyframe animations
- [ ] 4K support

### v3.0 (Future)
- [ ] GPU acceleration
- [ ] Multi-track audio mixing
- [ ] Color grading
- [ ] Plugin system

## 📄 License

MIT License - Free to use, modify, and distribute.

---
Built with ❤️ by ClipForge Team
