"""
Properties Panel - Edit clip properties
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QSpinBox, QDoubleSpinBox, QLineEdit,
    QComboBox, QGroupBox, QFormLayout, QColorDialog,
    QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor

from core.project import Project
from core.clip import Clip, VideoClip, AudioClip, ImageClip, TextClip, ClipType


class PropertiesPanel(QWidget):
    """Panel for editing clip properties"""
    property_changed = pyqtSignal(str, str, object)  # clip_id, property, value
    
    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self.project = project
        self.current_clip = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # Title
        title = QLabel("Properties")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #a1a1aa;")
        layout.addWidget(title)
        
        # No selection message
        self.no_selection = QLabel("Select a clip to edit its properties")
        self.no_selection.setStyleSheet("color: #71717a; padding: 20px;")
        self.no_selection.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.no_selection)
        
        # Clip info group
        self.info_group = QGroupBox("Clip Info")
        info_layout = QFormLayout(self.info_group)
        self.name_edit = QLineEdit()
        self.name_edit.textChanged.connect(lambda v: self._emit_change("name", v))
        info_layout.addRow("Name:", self.name_edit)
        self.type_label = QLabel()
        info_layout.addRow("Type:", self.type_label)
        layout.addWidget(self.info_group)
        self.info_group.hide()
        
        # Timing group
        self.timing_group = QGroupBox("Timing")
        timing_layout = QFormLayout(self.timing_group)
        self.start_spin = QDoubleSpinBox()
        self.start_spin.setRange(0, 9999)
        self.start_spin.setSuffix(" s")
        self.start_spin.valueChanged.connect(lambda v: self._emit_change("start_time", v))
        timing_layout.addRow("Start:", self.start_spin)
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0.1, 9999)
        self.duration_spin.setSuffix(" s")
        self.duration_spin.valueChanged.connect(lambda v: self._emit_change("duration", v))
        timing_layout.addRow("Duration:", self.duration_spin)
        layout.addWidget(self.timing_group)
        self.timing_group.hide()
        
        # Video properties group
        self.video_group = QGroupBox("Video")
        video_layout = QFormLayout(self.video_group)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(lambda v: self._emit_change("opacity", v/100))
        video_layout.addRow("Opacity:", self.opacity_slider)
        self.scale_spin = QDoubleSpinBox()
        self.scale_spin.setRange(0.1, 10)
        self.scale_spin.setValue(1.0)
        self.scale_spin.valueChanged.connect(lambda v: self._emit_change("scale", v))
        video_layout.addRow("Scale:", self.scale_spin)
        layout.addWidget(self.video_group)
        self.video_group.hide()
        
        # Audio properties group
        self.audio_group = QGroupBox("Audio")
        audio_layout = QFormLayout(self.audio_group)
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 200)
        self.volume_slider.setValue(100)
        self.volume_slider.valueChanged.connect(lambda v: self._emit_change("volume", v/100))
        audio_layout.addRow("Volume:", self.volume_slider)
        layout.addWidget(self.audio_group)
        self.audio_group.hide()
        
        # Text properties group
        self.text_group = QGroupBox("Text")
        text_layout = QFormLayout(self.text_group)
        self.text_edit = QLineEdit()
        self.text_edit.textChanged.connect(lambda v: self._emit_change("text", v))
        text_layout.addRow("Text:", self.text_edit)
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 200)
        self.font_size_spin.setValue(48)
        self.font_size_spin.valueChanged.connect(lambda v: self._emit_change("font_size", v))
        text_layout.addRow("Size:", self.font_size_spin)
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self._choose_color)
        text_layout.addRow("Color:", self.color_btn)
        layout.addWidget(self.text_group)
        self.text_group.hide()
        
        layout.addStretch()
    
    def set_project(self, project: Project):
        self.project = project
        self.clear()
    
    def clear(self):
        self.current_clip = None
        self.no_selection.show()
        self.info_group.hide()
        self.timing_group.hide()
        self.video_group.hide()
        self.audio_group.hide()
        self.text_group.hide()
    
    def show_clip_properties(self, clip: Clip):
        self.current_clip = clip
        self.no_selection.hide()
        
        # Update info
        self.info_group.show()
        self.name_edit.setText(clip.name)
        self.type_label.setText(clip.clip_type.value.capitalize())
        
        # Update timing
        self.timing_group.show()
        self.start_spin.setValue(clip.start_time)
        self.duration_spin.setValue(clip.duration)
        
        # Show type-specific properties
        self.video_group.hide()
        self.audio_group.hide()
        self.text_group.hide()
        
        if clip.clip_type == ClipType.VIDEO:
            self.video_group.show()
            self.audio_group.show()
            self.opacity_slider.setValue(int(clip.opacity * 100))
            if hasattr(clip, 'scale'): self.scale_spin.setValue(clip.scale)
            self.volume_slider.setValue(int(clip.volume * 100))
        elif clip.clip_type == ClipType.AUDIO:
            self.audio_group.show()
            self.volume_slider.setValue(int(clip.volume * 100))
        elif clip.clip_type == ClipType.IMAGE:
            self.video_group.show()
            self.opacity_slider.setValue(int(clip.opacity * 100))
            if hasattr(clip, 'scale'): self.scale_spin.setValue(clip.scale)
        elif clip.clip_type == ClipType.TEXT:
            self.text_group.show()
            self.text_edit.setText(clip.text)
            self.font_size_spin.setValue(clip.font_size)
    
    def _emit_change(self, prop: str, value):
        if self.current_clip:
            self.property_changed.emit(self.current_clip.id, prop, value)
    
    def _choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid() and self.current_clip:
            self._emit_change("font_color", color.name())
