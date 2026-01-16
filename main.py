#!/usr/bin/env python3
"""
ClipForge - Free Professional Video Editor
Main entry point
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QFile, QTextStream
from PyQt6.QtGui import QFont, QFontDatabase

from config import APP_NAME, APP_VERSION, ASSETS_DIR
from ui.main_window import MainWindow


def load_fonts():
    """Load custom fonts"""
    fonts_dir = ASSETS_DIR / "fonts"
    if fonts_dir.exists():
        for font_file in fonts_dir.glob("*.ttf"):
            QFontDatabase.addApplicationFont(str(font_file))


def load_stylesheet(app: QApplication):
    """Load the application stylesheet"""
    style_path = os.path.join(os.path.dirname(__file__), "ui", "styles.qss")
    if os.path.exists(style_path):
        with open(style_path, 'r') as f:
            app.setStyleSheet(f.read())


def main():
    """Main application entry point"""
    # Enable high DPI scaling
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)
    app.setOrganizationName("ClipForge")
    
    # Set default font
    font = QFont("Inter", 10)
    font.setStyleHint(QFont.StyleHint.SansSerif)
    app.setFont(font)
    
    # Load custom fonts
    load_fonts()
    
    # Load stylesheet
    load_stylesheet(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
