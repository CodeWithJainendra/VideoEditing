"""
Video Preview Panel
Displays video preview with playback controls
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSlider, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont

from config import PREVIEW_RESOLUTION, TEMP_DIR
from core.project import Project


class VideoDisplayWidget(QWidget):
    """Widget for displaying video frames"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pixmap = None
        self.setMinimumSize(320, 180)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet("background-color: #000000; border-radius: 8px;")
    
    def set_frame(self, image: QImage):
        """Display an image frame"""
        self.pixmap = QPixmap.fromImage(image)
        self.update()
    
    def set_pixmap(self, pixmap: QPixmap):
        """Display a pixmap"""
        self.pixmap = pixmap
        self.update()
    
    def clear(self):
        """Clear the display"""
        self.pixmap = None
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Background
        painter.fillRect(rect, QColor('#000000'))
        
        if self.pixmap:
            # Scale pixmap to fit while maintaining aspect ratio
            scaled = self.pixmap.scaled(
                rect.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            
            # Center the image
            x = (rect.width() - scaled.width()) // 2
            y = (rect.height() - scaled.height()) // 2
            painter.drawPixmap(x, y, scaled)
        else:
            # Show placeholder
            painter.setPen(QColor('#3f3f46'))
            font = QFont('Inter', 14)
            painter.setFont(font)
            painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "No Preview")
            
            # Draw play icon
            painter.setBrush(QColor('#3f3f46'))
            center = rect.center()
            from PyQt6.QtGui import QPolygon
            from PyQt6.QtCore import QPoint
            # Draw triangle play button
            points = [
                QPoint(center.x() - 20, center.y() - 30),
                QPoint(center.x() - 20, center.y() + 30),
                QPoint(center.x() + 30, center.y())
            ]
            painter.drawPolygon(QPolygon(points))


class PreviewPanel(QWidget):
    """Video preview panel with playback controls"""
    
    frame_changed = pyqtSignal(float)  # current time
    
    def __init__(self, project: Project, ffmpeg=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.ffmpeg = ffmpeg
        
        self.is_playing = False
        self.current_time = 0.0
        self.playback_timer = QTimer()
        self.playback_timer.timeout.connect(self._on_playback_tick)
        
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("Preview")
        title.setObjectName("heading")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #a1a1aa;")
        layout.addWidget(title)
        
        # Video display
        self.video_display = VideoDisplayWidget()
        layout.addWidget(self.video_display, stretch=1)
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 1000)
        self.progress_slider.setValue(0)
        self.progress_slider.sliderMoved.connect(self._on_seek)
        layout.addWidget(self.progress_slider)
        
        # Time display
        time_layout = QHBoxLayout()
        self.current_time_label = QLabel("0:00")
        self.current_time_label.setStyleSheet("color: #a1a1aa; font-family: monospace;")
        time_layout.addWidget(self.current_time_label)
        time_layout.addStretch()
        self.duration_label = QLabel("0:00")
        self.duration_label.setStyleSheet("color: #a1a1aa; font-family: monospace;")
        time_layout.addWidget(self.duration_label)
        layout.addLayout(time_layout)
        
        # Playback controls
        controls = QHBoxLayout()
        controls.setSpacing(8)
        
        controls.addStretch()
        
        # Go to start
        start_btn = QPushButton("⏮")
        start_btn.setFixedSize(36, 36)
        start_btn.setToolTip("Go to Start")
        start_btn.clicked.connect(self.go_to_start)
        controls.addWidget(start_btn)
        
        # Previous frame
        prev_btn = QPushButton("⏪")
        prev_btn.setFixedSize(36, 36)
        prev_btn.setToolTip("Previous Frame")
        prev_btn.clicked.connect(self.prev_frame)
        controls.addWidget(prev_btn)
        
        # Play/Pause
        self.play_btn = QPushButton("▶")
        self.play_btn.setFixedSize(48, 48)
        self.play_btn.setObjectName("primaryButton")
        self.play_btn.setToolTip("Play/Pause (Space)")
        self.play_btn.clicked.connect(self.toggle_play)
        controls.addWidget(self.play_btn)
        
        # Next frame
        next_btn = QPushButton("⏩")
        next_btn.setFixedSize(36, 36)
        next_btn.setToolTip("Next Frame")
        next_btn.clicked.connect(self.next_frame)
        controls.addWidget(next_btn)
        
        # Go to end
        end_btn = QPushButton("⏭")
        end_btn.setFixedSize(36, 36)
        end_btn.setToolTip("Go to End")
        end_btn.clicked.connect(self.go_to_end)
        controls.addWidget(end_btn)
        
        controls.addStretch()
        
        layout.addLayout(controls)
        
        # Volume control
        volume_layout = QHBoxLayout()
        volume_label = QLabel("🔊")
        volume_label.setStyleSheet("color: #71717a;")
        volume_layout.addWidget(volume_label)
        
        volume_slider = QSlider(Qt.Orientation.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(100)
        volume_slider.setMaximumWidth(100)
        volume_layout.addWidget(volume_slider)
        
        volume_layout.addStretch()
        layout.addLayout(volume_layout)
    
    def set_project(self, project: Project):
        """Update project reference"""
        self.project = project
        self.current_time = 0
        self._update_display()
    
    def _update_display(self):
        """Update the video display"""
        # Get current frame from project
        if self.project.duration > 0:
            # Update progress slider
            progress = int((self.current_time / self.project.duration) * 1000)
            self.progress_slider.blockSignals(True)
            self.progress_slider.setValue(progress)
            self.progress_slider.blockSignals(False)
            
            # Update time labels
            self._update_time_labels()
            
            # Load and display current frame
            self._load_current_frame()
    
    def _load_current_frame(self):
        """Load the frame at current time"""
        if not self.ffmpeg:
            return
        
        # Find clip at current time
        for track in self.project.video_tracks:
            for clip in track:
                if hasattr(clip, 'source_path') and clip.source_path:
                    if clip.start_time <= self.current_time < clip.end_time:
                        # Calculate position within clip
                        clip_time = self.current_time - clip.start_time + clip.trim_start
                        
                        # Extract frame
                        temp_frame = str(TEMP_DIR / "preview_frame.jpg")
                        success = self.ffmpeg.extract_frame(
                            clip.source_path, 
                            clip_time, 
                            temp_frame,
                            PREVIEW_RESOLUTION
                        )
                        
                        if success and os.path.exists(temp_frame):
                            pixmap = QPixmap(temp_frame)
                            self.video_display.set_pixmap(pixmap)
                            return
        
        # No frame found, clear display
        self.video_display.clear()
    
    def _update_time_labels(self):
        """Update time labels"""
        def format_time(seconds: float) -> str:
            m, s = divmod(int(seconds), 60)
            return f"{m}:{s:02d}"
        
        self.current_time_label.setText(format_time(self.current_time))
        self.duration_label.setText(format_time(self.project.duration))
    
    def _on_seek(self, value: int):
        """Handle seek slider"""
        if self.project.duration > 0:
            self.current_time = (value / 1000) * self.project.duration
            self._update_display()
            self.frame_changed.emit(self.current_time)
    
    def _on_playback_tick(self):
        """Advance playback"""
        fps = self.project.settings.fps
        self.current_time += 1.0 / fps
        
        if self.current_time >= self.project.duration:
            self.stop()
            return
        
        self._update_display()
        self.frame_changed.emit(self.current_time)
    
    def toggle_play(self):
        """Toggle playback"""
        if self.is_playing:
            self.pause()
        else:
            self.play()
    
    def play(self):
        """Start playback"""
        if self.project.duration <= 0:
            return
        
        self.is_playing = True
        self.play_btn.setText("⏸")
        
        fps = self.project.settings.fps
        interval = int(1000 / fps)
        self.playback_timer.start(interval)
    
    def pause(self):
        """Pause playback"""
        self.is_playing = False
        self.play_btn.setText("▶")
        self.playback_timer.stop()
    
    def stop(self):
        """Stop playback and reset"""
        self.pause()
        self.current_time = 0
        self._update_display()
        self.frame_changed.emit(self.current_time)
    
    def go_to_start(self):
        """Go to beginning"""
        self.current_time = 0
        self._update_display()
        self.frame_changed.emit(self.current_time)
    
    def go_to_end(self):
        """Go to end"""
        self.current_time = max(0, self.project.duration - 0.1)
        self._update_display()
        self.frame_changed.emit(self.current_time)
    
    def prev_frame(self):
        """Go to previous frame"""
        fps = self.project.settings.fps
        self.current_time = max(0, self.current_time - 1.0 / fps)
        self._update_display()
        self.frame_changed.emit(self.current_time)
    
    def next_frame(self):
        """Go to next frame"""
        fps = self.project.settings.fps
        self.current_time = min(self.project.duration, self.current_time + 1.0 / fps)
        self._update_display()
        self.frame_changed.emit(self.current_time)
    
    def seek_to(self, seconds: float):
        """Seek to specific time"""
        self.current_time = max(0, min(self.project.duration, seconds))
        self._update_display()
    
    def refresh(self):
        """Refresh display"""
        self._update_display()
