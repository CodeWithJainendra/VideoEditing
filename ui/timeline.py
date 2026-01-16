"""
Timeline Widget
Visual timeline for video editing with tracks and clips
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QFrame, QSlider, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize, QTimer
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, 
    QMouseEvent, QPaintEvent, QLinearGradient
)

from config import COLORS, TRACK_HEIGHT, PIXELS_PER_SECOND
from core.project import Project
from core.clip import Clip, VideoClip, AudioClip, ImageClip, TextClip, ClipType


class TimelineClipItem(QWidget):
    """Visual representation of a clip on timeline"""
    
    clicked = pyqtSignal(str)  # clip_id
    moved = pyqtSignal(str, float)  # clip_id, new_start_time
    resized = pyqtSignal(str, float)  # clip_id, new_duration
    
    def __init__(self, clip: Clip, pixels_per_second: float = PIXELS_PER_SECOND, parent=None):
        super().__init__(parent)
        self.clip = clip
        self.pps = pixels_per_second
        self.selected = False
        self.dragging = False
        self.resizing = False
        self.drag_start_x = 0
        self.original_start = 0
        
        self._update_geometry()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)
    
    def _update_geometry(self):
        """Update widget size based on clip properties"""
        x = int(self.clip.start_time * self.pps)
        width = int(self.clip.duration * self.pps)
        self.setGeometry(x, 0, max(width, 20), TRACK_HEIGHT - 8)
    
    def set_pixels_per_second(self, pps: float):
        """Update zoom level"""
        self.pps = pps
        self._update_geometry()
    
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Get color based on clip type
        if self.clip.clip_type == ClipType.VIDEO:
            color1 = QColor(COLORS['timeline_video'])
            color2 = QColor('#4f46e5')
        elif self.clip.clip_type == ClipType.AUDIO:
            color1 = QColor(COLORS['timeline_audio'])
            color2 = QColor('#059669')
        elif self.clip.clip_type == ClipType.IMAGE:
            color1 = QColor(COLORS['timeline_image'])
            color2 = QColor('#d97706')
        else:
            color1 = QColor(COLORS['timeline_text'])
            color2 = QColor('#db2777')
        
        # Gradient background
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)
        
        # Draw clip background
        painter.setBrush(QBrush(gradient))
        if self.selected:
            painter.setPen(QPen(QColor('#ffffff'), 2))
        else:
            painter.setPen(QPen(color1.lighter(130), 1))
        
        painter.drawRoundedRect(rect.adjusted(1, 1, -1, -1), 4, 4)
        
        # Draw clip name
        painter.setPen(QColor('#ffffff'))
        font = QFont('Inter', 9)
        font.setBold(True)
        painter.setFont(font)
        text_rect = rect.adjusted(8, 4, -8, -4)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, 
                        self.clip.name[:20])
        
        # Draw duration at bottom right
        duration_str = f"{self.clip.duration:.1f}s"
        font.setBold(False)
        font.setPointSize(8)
        painter.setFont(font)
        painter.setPen(QColor(255, 255, 255, 180))
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom,
                        duration_str)
        
        # Draw resize handles
        if self.selected:
            painter.setBrush(QColor('#ffffff'))
            painter.setPen(Qt.PenStyle.NoPen)
            # Left handle
            painter.drawRoundedRect(0, rect.height()//2 - 10, 4, 20, 2, 2)
            # Right handle
            painter.drawRoundedRect(rect.width() - 4, rect.height()//2 - 10, 4, 20, 2, 2)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.clip.id)
            self.selected = True
            self.update()
            
            # Check if clicking on resize handle
            if event.position().x() < 8:
                self.resizing = True
                self.resize_left = True
            elif event.position().x() > self.width() - 8:
                self.resizing = True
                self.resize_left = False
            else:
                self.dragging = True
            
            self.drag_start_x = event.position().x()
            self.original_start = self.clip.start_time
            self.original_duration = self.clip.duration
    
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            delta_x = event.position().x() - self.drag_start_x
            delta_time = delta_x / self.pps
            new_start = max(0, self.original_start + delta_time)
            self.clip.start_time = new_start
            self._update_geometry()
        elif self.resizing:
            delta_x = event.position().x() - self.drag_start_x
            delta_time = delta_x / self.pps
            
            if self.resize_left:
                new_start = max(0, self.original_start + delta_time)
                new_duration = self.original_duration - (new_start - self.original_start)
                if new_duration > 0.1:
                    self.clip.start_time = new_start
                    self.clip.duration = new_duration
            else:
                new_duration = max(0.1, self.original_duration + delta_time)
                self.clip.duration = new_duration
            
            self._update_geometry()
        else:
            # Update cursor for resize handles
            if event.position().x() < 8 or event.position().x() > self.width() - 8:
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            else:
                self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.dragging:
            self.moved.emit(self.clip.id, self.clip.start_time)
        elif self.resizing:
            self.resized.emit(self.clip.id, self.clip.duration)
        
        self.dragging = False
        self.resizing = False
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        split_action = menu.addAction("Split at Playhead")
        delete_action = menu.addAction("Delete")
        menu.addSeparator()
        duplicate_action = menu.addAction("Duplicate")
        properties_action = menu.addAction("Properties...")
        
        action = menu.exec(event.globalPos())
        
        if action == delete_action:
            self.parent().parent().remove_clip(self.clip.id)


class TimelineTrack(QFrame):
    """A single track on the timeline"""
    
    clip_clicked = pyqtSignal(str)
    
    def __init__(self, name: str, track_type: str = "video", parent=None):
        super().__init__(parent)
        self.name = name
        self.track_type = track_type
        self.clips: list[TimelineClipItem] = []
        self.pps = PIXELS_PER_SECOND
        
        self.setMinimumHeight(TRACK_HEIGHT)
        self.setMaximumHeight(TRACK_HEIGHT)
        self.setStyleSheet("""
            TimelineTrack {
                background-color: #1a1a1a;
                border-bottom: 1px solid #252525;
            }
        """)
    
    def add_clip(self, clip: Clip):
        """Add a clip to the track"""
        clip_item = TimelineClipItem(clip, self.pps, self)
        clip_item.clicked.connect(self.clip_clicked.emit)
        clip_item.show()
        self.clips.append(clip_item)
    
    def remove_clip(self, clip_id: str):
        """Remove a clip from track"""
        for clip_item in self.clips:
            if clip_item.clip.id == clip_id:
                clip_item.deleteLater()
                self.clips.remove(clip_item)
                break
    
    def clear(self):
        """Clear all clips"""
        for clip_item in self.clips:
            clip_item.deleteLater()
        self.clips.clear()
    
    def set_zoom(self, pps: float):
        """Update zoom level"""
        self.pps = pps
        for clip_item in self.clips:
            clip_item.set_pixels_per_second(pps)
    
    def deselect_all(self):
        """Deselect all clips"""
        for clip_item in self.clips:
            clip_item.selected = False
            clip_item.update()
    
    def get_clip_at(self, time: float) -> Clip | None:
        """Get clip at specific time"""
        for clip_item in self.clips:
            if clip_item.clip.start_time <= time < clip_item.clip.end_time:
                return clip_item.clip
        return None


class TimelineRuler(QWidget):
    """Time ruler showing time markers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.pps = PIXELS_PER_SECOND
        self.duration = 60  # Total timeline duration in seconds
        self.setMinimumHeight(30)
        self.setMaximumHeight(30)
    
    def set_zoom(self, pps: float):
        self.pps = pps
        self.update()
    
    def set_duration(self, duration: float):
        self.duration = max(60, duration + 30)  # Add padding
        self.setMinimumWidth(int(self.duration * self.pps))
        self.update()
    
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        
        # Background
        painter.fillRect(rect, QColor('#0a0a0a'))
        
        # Draw time markers
        painter.setPen(QColor('#71717a'))
        font = QFont('Inter', 9)
        painter.setFont(font)
        
        # Calculate interval based on zoom
        if self.pps < 20:
            major_interval = 10  # Every 10 seconds
        elif self.pps < 50:
            major_interval = 5  # Every 5 seconds
        else:
            major_interval = 1  # Every second
        
        for sec in range(0, int(self.duration) + 1):
            x = int(sec * self.pps)
            
            if sec % major_interval == 0:
                # Major tick
                painter.setPen(QColor('#71717a'))
                painter.drawLine(x, rect.height() - 10, x, rect.height())
                
                # Time label
                minutes = sec // 60
                seconds = sec % 60
                time_str = f"{minutes}:{seconds:02d}"
                painter.drawText(x + 4, rect.height() - 14, time_str)
            else:
                # Minor tick
                painter.setPen(QColor('#3f3f46'))
                painter.drawLine(x, rect.height() - 5, x, rect.height())


class PlayheadWidget(QWidget):
    """Playhead indicator"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.position = 0  # In seconds
        self.pps = PIXELS_PER_SECOND
        self.setFixedWidth(2)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
    
    def set_position(self, seconds: float):
        self.position = seconds
        self.move(int(seconds * self.pps), 0)
    
    def set_zoom(self, pps: float):
        self.pps = pps
        self.move(int(self.position * self.pps), 0)
    
    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor('#ef4444'))


class TimelineWidget(QWidget):
    """Main timeline widget with all tracks"""
    
    playhead_changed = pyqtSignal(float)  # seconds
    clip_selected = pyqtSignal(str)  # clip_id
    
    def __init__(self, project: Project, ffmpeg=None, parent=None):
        super().__init__(parent)
        self.project = project
        self.ffmpeg = ffmpeg
        self.pps = PIXELS_PER_SECOND
        self.playhead_position = 0
        self.selected_clip_id = None
        
        self._setup_ui()
        self._refresh_tracks()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Top controls bar
        controls = QHBoxLayout()
        controls.setContentsMargins(8, 8, 8, 8)
        
        # Zoom controls
        zoom_label = QLabel("Zoom:")
        zoom_label.setStyleSheet("color: #71717a;")
        controls.addWidget(zoom_label)
        
        zoom_slider = QSlider(Qt.Orientation.Horizontal)
        zoom_slider.setRange(10, 200)
        zoom_slider.setValue(50)
        zoom_slider.setMaximumWidth(150)
        zoom_slider.valueChanged.connect(self._on_zoom_changed)
        controls.addWidget(zoom_slider)
        
        controls.addStretch()
        
        # Time display
        self.time_label = QLabel("0:00:00 / 0:00:00")
        self.time_label.setStyleSheet("color: #a1a1aa; font-family: monospace;")
        controls.addWidget(self.time_label)
        
        layout.addLayout(controls)
        
        # Scrollable timeline area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scroll_area.setStyleSheet("QScrollArea { border: none; background-color: #0a0a0a; }")
        
        # Timeline content
        self.timeline_content = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_content)
        self.timeline_layout.setContentsMargins(0, 0, 0, 0)
        self.timeline_layout.setSpacing(0)
        
        # Ruler
        self.ruler = TimelineRuler()
        self.timeline_layout.addWidget(self.ruler)
        
        # Track container
        self.track_container = QWidget()
        self.track_layout = QVBoxLayout(self.track_container)
        self.track_layout.setContentsMargins(0, 0, 0, 0)
        self.track_layout.setSpacing(0)
        
        # Video tracks
        self.video_tracks: list[TimelineTrack] = []
        for i in range(3):
            track = TimelineTrack(f"Video {i+1}", "video")
            track.clip_clicked.connect(self._on_clip_clicked)
            self.video_tracks.append(track)
            self.track_layout.addWidget(track)
        
        # Audio tracks
        self.audio_tracks: list[TimelineTrack] = []
        for i in range(2):
            track = TimelineTrack(f"Audio {i+1}", "audio")
            track.clip_clicked.connect(self._on_clip_clicked)
            self.audio_tracks.append(track)
            self.track_layout.addWidget(track)
        
        self.track_layout.addStretch()
        
        self.timeline_layout.addWidget(self.track_container)
        
        scroll_area.setWidget(self.timeline_content)
        layout.addWidget(scroll_area)
        
        # Playhead (overlayed)
        self.playhead = PlayheadWidget(self.track_container)
        self.playhead.resize(2, 400)
        self.playhead.show()
    
    def _on_zoom_changed(self, value: int):
        """Handle zoom slider change"""
        self.pps = value
        self.ruler.set_zoom(value)
        self.playhead.set_zoom(value)
        
        for track in self.video_tracks + self.audio_tracks:
            track.set_zoom(value)
    
    def _on_clip_clicked(self, clip_id: str):
        """Handle clip click"""
        # Deselect all clips
        for track in self.video_tracks + self.audio_tracks:
            track.deselect_all()
        
        self.selected_clip_id = clip_id
        self.clip_selected.emit(clip_id)
    
    def set_project(self, project: Project):
        """Update project reference"""
        self.project = project
        self._refresh_tracks()
    
    def _refresh_tracks(self):
        """Refresh all tracks from project"""
        # Clear tracks
        for track in self.video_tracks:
            track.clear()
        for track in self.audio_tracks:
            track.clear()
        
        # Add video clips
        for i, track_clips in enumerate(self.project.video_tracks):
            if i < len(self.video_tracks):
                for clip in track_clips:
                    self.video_tracks[i].add_clip(clip)
        
        # Add audio clips
        for i, track_clips in enumerate(self.project.audio_tracks):
            if i < len(self.audio_tracks):
                for clip in track_clips:
                    self.audio_tracks[i].add_clip(clip)
        
        # Update ruler
        self.ruler.set_duration(self.project.duration)
    
    def add_clip(self, clip: Clip, track_type: str = "video", track_index: int = 0):
        """Add a clip to timeline"""
        self.project.add_clip(clip, track_type, track_index)
        self._refresh_tracks()
    
    def remove_clip(self, clip_id: str):
        """Remove a clip from timeline"""
        self.project.remove_clip(clip_id)
        self._refresh_tracks()
    
    def delete_selected(self):
        """Delete selected clip"""
        if self.selected_clip_id:
            self.remove_clip(self.selected_clip_id)
            self.selected_clip_id = None
    
    def split_at_playhead(self):
        """Split clip at current playhead position"""
        time = self.playhead_position
        
        for track in self.video_tracks + self.audio_tracks:
            clip = track.get_clip_at(time)
            if clip:
                # Split logic here
                pass
    
    def set_playhead(self, seconds: float):
        """Set playhead position"""
        self.playhead_position = seconds
        self.playhead.set_position(seconds)
        self.playhead_changed.emit(seconds)
        self._update_time_display()
    
    def _update_time_display(self):
        """Update time label"""
        current = self.playhead_position
        total = self.project.duration
        
        def format_time(s):
            m, s = divmod(int(s), 60)
            h, m = divmod(m, 60)
            return f"{h}:{m:02d}:{s:02d}"
        
        self.time_label.setText(f"{format_time(current)} / {format_time(total)}")
    
    def zoom_in(self):
        """Increase zoom"""
        self.pps = min(200, self.pps + 10)
        self._on_zoom_changed(self.pps)
    
    def zoom_out(self):
        """Decrease zoom"""
        self.pps = max(10, self.pps - 10)
        self._on_zoom_changed(self.pps)
    
    def refresh(self):
        """Refresh timeline display"""
        self._refresh_tracks()
    
    def mousePressEvent(self, event: QMouseEvent):
        """Click on timeline to move playhead"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Calculate time from click position
            x = event.position().x()
            time = x / self.pps
            self.set_playhead(max(0, time))
