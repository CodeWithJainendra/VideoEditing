"""
Dialog windows for the application
"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QSpinBox, QPushButton,
    QDialogButtonBox, QComboBox, QColorDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.clip import TextClip


class TextDialog(QDialog):
    """Dialog for adding text overlay"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Text")
        self.setMinimumWidth(400)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Enter text...")
        form.addRow("Text:", self.text_edit)
        
        self.font_combo = QComboBox()
        self.font_combo.addItems(["Arial", "Helvetica", "Times New Roman", "Verdana", "Impact"])
        form.addRow("Font:", self.font_combo)
        
        self.size_spin = QSpinBox()
        self.size_spin.setRange(8, 200)
        self.size_spin.setValue(48)
        form.addRow("Size:", self.size_spin)
        
        self.color = "#FFFFFF"
        self.color_btn = QPushButton("White")
        self.color_btn.setStyleSheet(f"background-color: {self.color};")
        self.color_btn.clicked.connect(self._choose_color)
        form.addRow("Color:", self.color_btn)
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 300)
        self.duration_spin.setValue(5)
        self.duration_spin.setSuffix(" seconds")
        form.addRow("Duration:", self.duration_spin)
        
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def _choose_color(self):
        color = QColorDialog.getColor(QColor(self.color), self)
        if color.isValid():
            self.color = color.name()
            self.color_btn.setText(self.color)
            self.color_btn.setStyleSheet(f"background-color: {self.color}; color: black;")
    
    def get_text_clip(self) -> TextClip:
        return TextClip(
            text=self.text_edit.text() or "Text",
            font_family=self.font_combo.currentText(),
            font_size=self.size_spin.value(),
            font_color=self.color,
            duration=float(self.duration_spin.value())
        )
