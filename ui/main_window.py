"""
Main Application Window
The primary window with all panels and menus
"""
import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QSplitter, QToolBar, QStatusBar, QMenuBar, QMenu,
    QFileDialog, QMessageBox, QLabel, QProgressBar,
    QDockWidget, QApplication, QDialog, QDialogButtonBox,
    QFormLayout, QComboBox, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QAction, QIcon, QKeySequence, QFont

from config import APP_NAME, APP_VERSION, VIDEO_FORMATS, AUDIO_FORMATS, IMAGE_FORMATS, EXPORT_PRESETS
from core.project import Project
from core.ffmpeg_engine import FFmpegEngine
from core.exporter import Exporter, ExportSettings
from .preview import PreviewPanel
from .timeline import TimelineWidget
from .media_browser import MediaBrowser
from .properties import PropertiesPanel
from .ai_panel import AIPanel


class MainWindow(QMainWindow):
    """
    Main application window
    Contains all panels: media browser, preview, timeline, properties
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize project
        self.project = Project.new()
        
        # Initialize FFmpeg
        try:
            self.ffmpeg = FFmpegEngine()
        except RuntimeError as e:
            QMessageBox.critical(self, "Error", str(e))
            self.ffmpeg = None
        
        # Setup window
        self.setWindowTitle(f"{APP_NAME} - {self.project.name}")
        self.setMinimumSize(1400, 800)
        self.resize(1600, 900)
        
        # Setup UI
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_status_bar()
        
        # Connect signals
        self._connect_signals()
        
        # Show welcome
        self.statusBar().showMessage("Welcome to ClipForge! Import media to get started.", 5000)
    
    def _setup_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu("&File")
        
        new_action = QAction("&New Project", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self.new_project)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open Project...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self.open_project)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        # Import Media
        import_media = QAction("📁 &Import Media...", self)
        import_media.setShortcut(QKeySequence("Ctrl+I"))
        import_media.triggered.connect(self.import_media)
        file_menu.addAction(import_media)
        
        # Import Folder (for Filmora/CapCut exported media)
        import_folder = QAction("📂 Import &Folder...", self)
        import_folder.setToolTip("Import all media from a folder (e.g., exported from Filmora/CapCut)")
        import_folder.triggered.connect(self.import_folder)
        file_menu.addAction(import_folder)
        
        file_menu.addSeparator()
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self.save_project)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence("Ctrl+Shift+S"))
        save_as_action.triggered.connect(self.save_project_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        import_action = QAction("&Import Media...", self)
        import_action.setShortcut(QKeySequence("Ctrl+I"))
        import_action.triggered.connect(self.import_media)
        file_menu.addAction(import_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("&Export Video...", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.triggered.connect(self.show_export_dialog)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        quit_action = QAction("&Quit", self)
        quit_action.setShortcut(QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.StandardKey.Undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.StandardKey.Redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_clip)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        edit_menu.addAction(paste_action)
        
        delete_action = QAction("&Delete", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        split_action = QAction("&Split at Playhead", self)
        split_action.setShortcut(QKeySequence("S"))
        split_action.triggered.connect(self.split_at_playhead)
        edit_menu.addAction(split_action)
        
        # View Menu
        view_menu = menubar.addMenu("&View")
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("&Fit to Window", self)
        zoom_fit_action.setShortcut(QKeySequence("Ctrl+0"))
        view_menu.addAction(zoom_fit_action)
        
        # Settings Menu (NEW!)
        settings_menu = menubar.addMenu("⚙️ &Settings")
        
        api_keys_action = QAction("🔑 &API Keys (Gemini, ElevenLabs)...", self)
        api_keys_action.setToolTip("Configure AI API keys")
        api_keys_action.triggered.connect(self.show_api_settings)
        settings_menu.addAction(api_keys_action)
        
        settings_menu.addSeparator()
        
        project_settings = QAction("📊 &Project Settings...", self)
        project_settings.triggered.connect(self.show_project_settings)
        settings_menu.addAction(project_settings)
        
        # Help Menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About ClipForge", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        shortcuts_action = QAction("&Keyboard Shortcuts", self)
        shortcuts_action.setShortcut(QKeySequence("Ctrl+/"))
        help_menu.addAction(shortcuts_action)
    
    def _setup_toolbar(self):
        """Create main toolbar"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(24, 24))
        self.addToolBar(toolbar)
        
        # Import button
        import_btn = QAction("📁 Import", self)
        import_btn.setToolTip("Import Media (Ctrl+I)")
        import_btn.triggered.connect(self.import_media)
        toolbar.addAction(import_btn)
        
        toolbar.addSeparator()
        
        # Playback controls
        play_btn = QAction("▶️ Play", self)
        play_btn.setToolTip("Play/Pause (Space)")
        play_btn.triggered.connect(self.toggle_play)
        toolbar.addAction(play_btn)
        self.play_action = play_btn
        
        stop_btn = QAction("⏹️ Stop", self)
        stop_btn.setToolTip("Stop")
        stop_btn.triggered.connect(self.stop_playback)
        toolbar.addAction(stop_btn)
        
        toolbar.addSeparator()
        
        # Edit tools
        cut_btn = QAction("✂️ Cut", self)
        cut_btn.setToolTip("Split at Playhead (S)")
        cut_btn.triggered.connect(self.split_at_playhead)
        toolbar.addAction(cut_btn)
        
        trim_btn = QAction("📐 Trim", self)
        trim_btn.setToolTip("Trim Mode")
        toolbar.addAction(trim_btn)
        
        toolbar.addSeparator()
        
        # Add elements
        text_btn = QAction("📝 Text", self)
        text_btn.setToolTip("Add Text Overlay")
        text_btn.triggered.connect(self.add_text)
        toolbar.addAction(text_btn)
        
        audio_btn = QAction("🎵 Music", self)
        audio_btn.setToolTip("Add Background Music")
        audio_btn.triggered.connect(self.add_audio)
        toolbar.addAction(audio_btn)
        
        toolbar.addSeparator()
        
        # AI Tools
        ai_btn = QAction("🤖 AI Script", self)
        ai_btn.setToolTip("Generate AI Script")
        toolbar.addAction(ai_btn)
        
        toolbar.addSeparator()
        
        # Export
        export_btn = QAction("📤 Export", self)
        export_btn.setToolTip("Export Video (Ctrl+E)")
        export_btn.triggered.connect(self.show_export_dialog)
        toolbar.addAction(export_btn)
    
    def _setup_central_widget(self):
        """Create central widget with all panels"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main splitter (vertical - top panels and timeline)
        main_splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Top section splitter (horizontal - media, preview, properties, AI)
        top_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Media Browser (left panel)
        self.media_browser = MediaBrowser(self.project, self.ffmpeg)
        self.media_browser.setObjectName("mediaBrowser")
        self.media_browser.setMinimumWidth(220)
        top_splitter.addWidget(self.media_browser)
        
        # Preview Panel (center)
        self.preview_panel = PreviewPanel(self.project, self.ffmpeg)
        self.preview_panel.setObjectName("previewPanel")
        self.preview_panel.setMinimumWidth(400)
        top_splitter.addWidget(self.preview_panel)
        
        # Properties Panel (right of preview)
        self.properties_panel = PropertiesPanel(self.project)
        self.properties_panel.setObjectName("propertiesPanel")
        self.properties_panel.setMinimumWidth(220)
        top_splitter.addWidget(self.properties_panel)
        
        # AI Panel (far right) - NEW!
        self.ai_panel = AIPanel()
        self.ai_panel.setObjectName("aiPanel")
        self.ai_panel.setMinimumWidth(280)
        self.ai_panel.asset_generated.connect(self._on_ai_asset_generated)
        top_splitter.addWidget(self.ai_panel)
        
        # Set initial sizes
        top_splitter.setSizes([220, 550, 220, 300])
        
        main_splitter.addWidget(top_splitter)
        
        # Timeline (bottom panel)
        self.timeline = TimelineWidget(self.project, self.ffmpeg)
        self.timeline.setObjectName("timelinePanel")
        self.timeline.setMinimumHeight(200)
        main_splitter.addWidget(self.timeline)
        
        # Set initial sizes
        main_splitter.setSizes([500, 300])
        
        layout.addWidget(main_splitter)
    
    def _setup_status_bar(self):
        """Create status bar"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Project duration label
        self.duration_label = QLabel("Duration: 0:00:00")
        status_bar.addPermanentWidget(self.duration_label)
        
        # Resolution label
        self.resolution_label = QLabel("1920 x 1080")
        status_bar.addPermanentWidget(self.resolution_label)
        
        # FPS label
        self.fps_label = QLabel("30 fps")
        status_bar.addPermanentWidget(self.fps_label)
    
    def _connect_signals(self):
        """Connect widget signals"""
        # Media browser -> Timeline
        self.media_browser.media_added.connect(self.on_media_added)
        self.media_browser.clip_dropped.connect(self.timeline.add_clip)
        
        # Timeline -> Preview
        self.timeline.playhead_changed.connect(self.preview_panel.seek_to)
        self.timeline.clip_selected.connect(self.on_clip_selected)
        
        # Properties changes
        self.properties_panel.property_changed.connect(self.on_property_changed)
        
        # Update duration periodically
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_status)
        self.update_timer.start(500)
    
    # ================== File Operations ==================
    
    def new_project(self):
        """Create new project"""
        reply = QMessageBox.question(
            self, "New Project",
            "Create a new project? Unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project = Project.new()
            self.media_browser.set_project(self.project)
            self.timeline.set_project(self.project)
            self.preview_panel.set_project(self.project)
            self.properties_panel.set_project(self.project)
            self.setWindowTitle(f"{APP_NAME} - {self.project.name}")
            self.statusBar().showMessage("New project created", 3000)
    
    def open_project(self):
        """Open existing project"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Project",
            "", "ClipForge Project (*.cfproj)"
        )
        
        if file_path:
            project = Project.load(file_path)
            if project:
                self.project = project
                self.media_browser.set_project(self.project)
                self.timeline.set_project(self.project)
                self.preview_panel.set_project(self.project)
                self.properties_panel.set_project(self.project)
                self.setWindowTitle(f"{APP_NAME} - {self.project.name}")
                self.statusBar().showMessage(f"Opened: {file_path}", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to open project")
    
    def import_folder(self):
        """Import all media files from a folder (e.g., from Filmora/CapCut export)"""
        folder_path = QFileDialog.getExistingDirectory(
            self, "Select Folder to Import",
            os.path.expanduser("~"),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            # Collect all media files
            from config import VIDEO_FORMATS, AUDIO_FORMATS, IMAGE_FORMATS
            all_formats = VIDEO_FORMATS + AUDIO_FORMATS + IMAGE_FORMATS
            
            imported_count = 0
            
            # Walk through folder and subfolders
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    ext = os.path.splitext(file)[1].lower()
                    if ext in all_formats:
                        file_path = os.path.join(root, file)
                        self.media_browser.add_media_file(file_path)
                        imported_count += 1
            
            if imported_count > 0:
                QMessageBox.information(
                    self, "Import Complete",
                    f"✅ Imported {imported_count} media file(s)!\n\n"
                    f"📁 From: {folder_path}\n\n"
                    f"💡 Tip: Double-click media to add to timeline."
                )
                self.statusBar().showMessage(f"Imported {imported_count} files from folder", 5000)
            else:
                QMessageBox.warning(
                    self, "No Media Found",
                    f"No supported media files found in:\n{folder_path}\n\n"
                    f"Supported formats:\n"
                    f"• Video: MP4, MOV, AVI, MKV, WebM\n"
                    f"• Audio: MP3, WAV, AAC, OGG\n"
                    f"• Image: JPG, PNG, GIF, BMP"
                )
    
    def save_project(self):
        """Save current project"""
        if self.project.path:
            if self.project.save():
                self.statusBar().showMessage("Project saved", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to save project")
        else:
            self.save_project_as()
    
    def save_project_as(self):
        """Save project with new name"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Project",
            f"{self.project.name}.cfproj",
            "ClipForge Project (*.cfproj)"
        )
        
        if file_path:
            if self.project.save(file_path):
                self.setWindowTitle(f"{APP_NAME} - {self.project.name}")
                self.statusBar().showMessage(f"Saved: {file_path}", 3000)
            else:
                QMessageBox.warning(self, "Error", "Failed to save project")
    
    def import_media(self):
        """Import media files"""
        all_formats = VIDEO_FORMATS + AUDIO_FORMATS + IMAGE_FORMATS
        filter_str = "Media Files (*" + " *".join(all_formats) + ")"
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "Import Media",
            "", filter_str
        )
        
        for file_path in files:
            self.media_browser.add_media_file(file_path)
        
        if files:
            self.statusBar().showMessage(f"Imported {len(files)} file(s)", 3000)
    
    # ================== Edit Operations ==================
    
    def cut_clip(self):
        """Cut selected clip"""
        # Implementation for cutting clips
        pass
    
    def delete_selected(self):
        """Delete selected clips"""
        self.timeline.delete_selected()
    
    def split_at_playhead(self):
        """Split clip at playhead position"""
        self.timeline.split_at_playhead()
    
    # ================== View Operations ==================
    
    def zoom_in(self):
        """Zoom in timeline"""
        self.timeline.zoom_in()
    
    def zoom_out(self):
        """Zoom out timeline"""
        self.timeline.zoom_out()
    
    # ================== Playback Operations ==================
    
    def toggle_play(self):
        """Toggle play/pause"""
        if self.preview_panel.is_playing:
            self.preview_panel.pause()
            self.play_action.setText("▶️ Play")
        else:
            self.preview_panel.play()
            self.play_action.setText("⏸️ Pause")
    
    def stop_playback(self):
        """Stop playback"""
        self.preview_panel.stop()
        self.play_action.setText("▶️ Play")
    
    # ================== Add Elements ==================
    
    def add_text(self):
        """Add text overlay"""
        from .dialogs import TextDialog
        dialog = TextDialog(self)
        if dialog.exec():
            text_clip = dialog.get_text_clip()
            self.project.add_clip(text_clip, "overlay")
            self.timeline.refresh()
    
    def add_audio(self):
        """Add background audio"""
        filter_str = "Audio Files (*" + " *".join(AUDIO_FORMATS) + ")"
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Add Audio",
            "", filter_str
        )
        
        if file_path:
            self.media_browser.add_media_file(file_path)
    
    # ================== Export ==================
    
    def show_export_dialog(self):
        """Show export dialog"""
        dialog = ExportDialog(self, self.project)
        if dialog.exec():
            settings = dialog.get_settings()
            self.export_video(settings)
    
    def export_video(self, settings: ExportSettings):
        """Export video with given settings"""
        exporter = Exporter(self.project)
        
        # Show progress dialog
        progress_dialog = ExportProgressDialog(self)
        
        def on_progress(percentage: float, message: str):
            progress_dialog.update_progress(percentage, message)
        
        exporter.set_progress_callback(on_progress)
        
        # Start export in background (simplified - should use QThread)
        progress_dialog.show()
        success = exporter.export(settings)
        progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self, "Export Complete",
                f"Video exported successfully to:\n{settings.output_path}"
            )
        else:
            QMessageBox.warning(self, "Export Failed", "Failed to export video")
    
    # ================== Event Handlers ==================
    
    def on_media_added(self, file_path: str):
        """Handle media file added"""
        self.project.add_media_file(file_path)
    
    def on_clip_selected(self, clip_id: str):
        """Handle clip selection"""
        clip = self.project.get_clip(clip_id)
        if clip:
            self.properties_panel.show_clip_properties(clip)
    
    def on_property_changed(self, clip_id: str, prop: str, value):
        """Handle property change"""
        clip = self.project.get_clip(clip_id)
        if clip and hasattr(clip, prop):
            setattr(clip, prop, value)
            self.timeline.refresh()
            self.preview_panel.refresh()
    
    def _on_ai_asset_generated(self, file_path: str):
        """Handle AI-generated asset (voiceover, etc.)"""
        self.media_browser.add_media_file(file_path)
        self.statusBar().showMessage(f"AI asset added: {file_path}", 3000)
    
    def show_api_settings(self):
        """Show API Keys configuration dialog"""
        from .ai_panel import AISettingsDialog
        from core.ai_services import AIConfig
        
        config = AIConfig.load()
        dialog = AISettingsDialog(config, self)
        if dialog.exec():
            new_config = dialog.get_config()
            new_config.save()
            
            # Update AI panel if exists
            if hasattr(self, 'ai_panel'):
                self.ai_panel.ai.update_config(new_config)
            
            QMessageBox.information(
                self, "Settings Saved",
                "✅ API keys saved successfully!\n\n"
                "Your AI features are now ready to use."
            )
    
    def show_project_settings(self):
        """Show project settings dialog"""
        dialog = ProjectSettingsDialog(self.project, self)
        if dialog.exec():
            # Update project settings
            self.project.settings.resolution = dialog.get_resolution()
            self.project.settings.fps = dialog.get_fps()
            self.update_status()
            self.statusBar().showMessage("Project settings updated", 3000)
    
    def update_status(self):
        """Update status bar"""
        duration = self.project.duration
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        self.duration_label.setText(f"Duration: {hours}:{minutes:02d}:{seconds:02d}")
        
        res = self.project.settings.resolution
        self.resolution_label.setText(f"{res[0]} x {res[1]}")
        self.fps_label.setText(f"{self.project.settings.fps:.0f} fps")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, f"About {APP_NAME}",
            f"<h2>{APP_NAME}</h2>"
            f"<p>Version {APP_VERSION}</p>"
            f"<p>A free, powerful video editor with no watermarks.</p>"
            f"<p>Built with Python, PyQt6, and FFmpeg.</p>"
            f"<br>"
            f"<p><b>Features:</b></p>"
            f"<ul>"
            f"<li>Timeline-based editing</li>"
            f"<li>Cut, trim, split clips</li>"
            f"<li>Text overlays</li>"
            f"<li>Background music</li>"
            f"<li>Transitions</li>"
            f"<li>Export to MP4 (no watermark!)</li>"
            f"</ul>"
        )
    
    def closeEvent(self, event):
        """Handle window close"""
        reply = QMessageBox.question(
            self, "Quit",
            "Are you sure you want to quit? Unsaved changes will be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            event.accept()
        else:
            event.ignore()


class ExportDialog(QDialog):
    """Enhanced Export settings dialog with multiple formats"""
    
    # Supported export formats
    FORMATS = {
        'mp4': {'name': 'MP4 (H.264)', 'ext': '.mp4', 'codec': 'libx264', 'audio': 'aac'},
        'mov': {'name': 'MOV (QuickTime)', 'ext': '.mov', 'codec': 'libx264', 'audio': 'aac'},
        'avi': {'name': 'AVI', 'ext': '.avi', 'codec': 'libxvid', 'audio': 'mp3'},
        'mkv': {'name': 'MKV (Matroska)', 'ext': '.mkv', 'codec': 'libx264', 'audio': 'aac'},
        'webm': {'name': 'WebM (VP9)', 'ext': '.webm', 'codec': 'libvpx-vp9', 'audio': 'libopus'},
        'gif': {'name': 'GIF (Animated)', 'ext': '.gif', 'codec': 'gif', 'audio': None},
        'mp3': {'name': 'MP3 (Audio Only)', 'ext': '.mp3', 'codec': None, 'audio': 'libmp3lame'},
        'wav': {'name': 'WAV (Audio Only)', 'ext': '.wav', 'codec': None, 'audio': 'pcm_s16le'},
    }
    
    def __init__(self, parent, project: Project):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Export Video")
        self.setMinimumWidth(500)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        
        # Title
        title = QLabel("📤 Export Your Video")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(title)
        
        # Form
        form = QFormLayout()
        form.setSpacing(12)
        
        # Filename
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.project.name)
        self.name_edit.setPlaceholderText("Enter filename...")
        form.addRow("📝 Filename:", self.name_edit)
        
        # Format dropdown
        self.format_combo = QComboBox()
        for key, fmt in self.FORMATS.items():
            self.format_combo.addItem(f"{fmt['name']} ({fmt['ext']})", key)
        self.format_combo.currentIndexChanged.connect(self._on_format_changed)
        form.addRow("🎞️ Format:", self.format_combo)
        
        # Quality preset
        self.preset_combo = QComboBox()
        for key, preset in EXPORT_PRESETS.items():
            self.preset_combo.addItem(preset['name'], key)
        self.preset_combo.setCurrentIndex(1)  # Full HD default
        form.addRow("📊 Quality:", self.preset_combo)
        
        # Output location
        path_layout = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Select save location...")
        self.path_edit.setReadOnly(True)
        browse_btn = QPushButton("📁 Browse...")
        browse_btn.clicked.connect(self._browse_output)
        path_layout.addWidget(self.path_edit, stretch=1)
        path_layout.addWidget(browse_btn)
        form.addRow("💾 Save to:", path_layout)
        
        layout.addLayout(form)
        
        # Preview of full path
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("color: #71717a; font-size: 11px; padding: 8px; background: #1a1a1a; border-radius: 4px;")
        self.preview_label.setWordWrap(True)
        layout.addWidget(self.preview_label)
        
        # Update preview on changes
        self.name_edit.textChanged.connect(self._update_preview)
        self.format_combo.currentIndexChanged.connect(self._update_preview)
        self.path_edit.textChanged.connect(self._update_preview)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        export_btn = QPushButton("🚀 Export")
        export_btn.setObjectName("primaryButton")
        export_btn.setMinimumWidth(120)
        export_btn.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        
        self._update_preview()
    
    def _on_format_changed(self):
        """Handle format change"""
        fmt_key = self.format_combo.currentData()
        fmt = self.FORMATS[fmt_key]
        
        # Disable quality for audio-only formats
        is_video = fmt['codec'] is not None and fmt_key not in ['mp3', 'wav']
        self.preset_combo.setEnabled(is_video)
        
        self._update_preview()
    
    def _browse_output(self):
        """Browse for save location"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Save Location",
            os.path.expanduser("~")
        )
        if folder:
            self.path_edit.setText(folder)
    
    def _update_preview(self):
        """Update the full path preview"""
        folder = self.path_edit.text() or "~/Videos"
        name = self.name_edit.text() or "untitled"
        fmt_key = self.format_combo.currentData()
        ext = self.FORMATS.get(fmt_key, {}).get('ext', '.mp4')
        
        full_path = os.path.join(folder, f"{name}{ext}")
        self.preview_label.setText(f"📄 Output: {full_path}")
    
    def _validate_and_accept(self):
        """Validate inputs before accepting"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please enter a filename!")
            return
        if not self.path_edit.text().strip():
            QMessageBox.warning(self, "Error", "Please select a save location!")
            return
        self.accept()
    
    def get_output_path(self) -> str:
        """Get full output path"""
        folder = self.path_edit.text()
        name = self.name_edit.text()
        fmt_key = self.format_combo.currentData()
        ext = self.FORMATS[fmt_key]['ext']
        return os.path.join(folder, f"{name}{ext}")
    
    def get_settings(self) -> ExportSettings:
        """Get export settings"""
        preset_key = self.preset_combo.currentData()
        preset = EXPORT_PRESETS[preset_key]
        fmt_key = self.format_combo.currentData()
        fmt = self.FORMATS[fmt_key]
        
        return ExportSettings(
            output_path=self.get_output_path(),
            resolution=preset['resolution'],
            fps=preset['fps'],
            bitrate=preset['bitrate'],
            codec=fmt['codec'] or preset['codec'],
            audio_codec=fmt['audio'] or 'aac'
        )


class ExportProgressDialog(QDialog):
    """Export progress dialog"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Exporting...")
        self.setMinimumWidth(400)
        self.setModal(True)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        self.status_label = QLabel("Preparing export...")
        layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        layout.addWidget(self.progress_bar)
    
    def update_progress(self, percentage: float, message: str):
        self.progress_bar.setValue(int(percentage))
        self.status_label.setText(message)
        QApplication.processEvents()


class ProjectSettingsDialog(QDialog):
    """Project settings dialog"""
    
    RESOLUTIONS = [
        ("720p (HD)", (1280, 720)),
        ("1080p (Full HD)", (1920, 1080)),
        ("1440p (2K)", (2560, 1440)),
        ("2160p (4K)", (3840, 2160)),
    ]
    
    FPS_OPTIONS = [24, 25, 30, 50, 60]
    
    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        self.setWindowTitle("Project Settings")
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        title = QLabel("📊 Project Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        form = QFormLayout()
        
        # Resolution
        self.res_combo = QComboBox()
        for name, res in self.RESOLUTIONS:
            self.res_combo.addItem(name, res)
        # Set current
        current_res = self.project.settings.resolution
        for i, (_, res) in enumerate(self.RESOLUTIONS):
            if res == current_res:
                self.res_combo.setCurrentIndex(i)
                break
        form.addRow("Resolution:", self.res_combo)
        
        # FPS
        self.fps_combo = QComboBox()
        for fps in self.FPS_OPTIONS:
            self.fps_combo.addItem(f"{fps} fps", fps)
        current_fps = int(self.project.settings.fps)
        if current_fps in self.FPS_OPTIONS:
            self.fps_combo.setCurrentIndex(self.FPS_OPTIONS.index(current_fps))
        form.addRow("Frame Rate:", self.fps_combo)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | 
            QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_resolution(self):
        return self.res_combo.currentData()
    
    def get_fps(self):
        return float(self.fps_combo.currentData())
