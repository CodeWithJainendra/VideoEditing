"""
Media Browser Panel - Shows imported media files with thumbnails
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem,
    QTabWidget, QFileDialog, QFrame, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QPixmap, QDrag

from config import VIDEO_FORMATS, AUDIO_FORMATS, IMAGE_FORMATS, TEMP_DIR
from core.project import Project
from core.clip import VideoClip, AudioClip, ImageClip


class MediaThumbnailWidget(QFrame):
    """Single media item with thumbnail"""
    double_clicked = pyqtSignal(str)
    
    def __init__(self, file_path: str, thumbnail: QPixmap = None, parent=None):
        super().__init__(parent)
        self.file_path = file_path
        self.thumbnail = thumbnail
        self.setMinimumSize(100, 90)
        self.setMaximumSize(120, 110)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("MediaThumbnailWidget { background-color: #252525; border-radius: 8px; } MediaThumbnailWidget:hover { background-color: #333; }")
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        thumb_label = QLabel()
        thumb_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        thumb_label.setMinimumHeight(60)
        if self.thumbnail:
            scaled = self.thumbnail.scaled(80, 60, Qt.AspectRatioMode.KeepAspectRatio)
            thumb_label.setPixmap(scaled)
        else:
            ext = os.path.splitext(self.file_path)[1].lower()
            icon = "🎬" if ext in VIDEO_FORMATS else "🎵" if ext in AUDIO_FORMATS else "🖼️"
            thumb_label.setText(icon)
            thumb_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(thumb_label)
        name = os.path.basename(self.file_path)[:14]
        name_label = QLabel(name)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #a1a1aa; font-size: 10px;")
        layout.addWidget(name_label)
    
    def mouseDoubleClickEvent(self, e): self.double_clicked.emit(self.file_path)
    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.file_path)
            drag.setMimeData(mime)
            drag.exec(Qt.DropAction.CopyAction)


class MediaBrowser(QWidget):
    """Media browser panel"""
    media_added = pyqtSignal(str)
    clip_dropped = pyqtSignal(object, str, int)
    
    def __init__(self, project: Project, ffmpeg=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.ffmpeg = ffmpeg
        self.media_files = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        header = QHBoxLayout()
        title = QLabel("Media")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #a1a1aa;")
        header.addWidget(title)
        header.addStretch()
        import_btn = QPushButton("+ Import")
        import_btn.setObjectName("primaryButton")
        import_btn.clicked.connect(self._import_media)
        header.addWidget(import_btn)
        layout.addLayout(header)
        
        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        self.container_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        scroll = QScrollArea()
        scroll.setWidget(self.container)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        layout.addWidget(scroll)
    
    def set_project(self, project: Project):
        self.project = project
        self._clear()
        for f in self.project.media_files: self.add_media_file(f)
    
    def _clear(self):
        self.media_files.clear()
        while self.container_layout.count(): 
            w = self.container_layout.takeAt(0).widget()
            if w: w.deleteLater()
    
    def _import_media(self):
        fmts = VIDEO_FORMATS + AUDIO_FORMATS + IMAGE_FORMATS
        files, _ = QFileDialog.getOpenFileNames(self, "Import", "", f"Media (*{' *'.join(fmts)})")
        for f in files: self.add_media_file(f)
    
    def add_media_file(self, path: str):
        if not os.path.exists(path) or path in self.media_files: return
        self.media_files.append(path)
        thumb = self._gen_thumb(path)
        w = MediaThumbnailWidget(path, thumb)
        w.double_clicked.connect(self._on_dbl_click)
        self.container_layout.addWidget(w)
        self.project.add_media_file(path)
        self.media_added.emit(path)
    
    def _gen_thumb(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in IMAGE_FORMATS: return QPixmap(path)
        if ext in VIDEO_FORMATS and self.ffmpeg:
            tmp = str(TEMP_DIR / f"th_{os.path.basename(path)}.jpg")
            if self.ffmpeg.generate_thumbnail(path, tmp): return QPixmap(tmp)
        return None
    
    def _on_dbl_click(self, path):
        ext = os.path.splitext(path)[1].lower()
        if ext in VIDEO_FORMATS:
            d = self.ffmpeg.get_duration(path) if self.ffmpeg else 10
            clip = VideoClip(source_path=path, duration=d, original_duration=d)
            self.clip_dropped.emit(clip, "video", 0)
        elif ext in AUDIO_FORMATS:
            d = self.ffmpeg.get_duration(path) if self.ffmpeg else 10
            clip = AudioClip(source_path=path, duration=d, original_duration=d)
            self.clip_dropped.emit(clip, "audio", 0)
        elif ext in IMAGE_FORMATS:
            clip = ImageClip(source_path=path, duration=5)
            self.clip_dropped.emit(clip, "video", 0)
