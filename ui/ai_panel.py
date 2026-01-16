"""
AI Panel - Chat interface and AI tools
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QLineEdit, QScrollArea,
    QFrame, QTabWidget, QComboBox, QSpinBox,
    QDialog, QFormLayout, QDialogButtonBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QColor

from core.ai_services import AIAssistant, AIConfig


class ChatMessage(QFrame):
    """Single chat message widget"""
    
    def __init__(self, text: str, is_user: bool = True, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            ChatMessage {{
                background-color: {'#6366f1' if is_user else '#252525'};
                border-radius: 12px;
                padding: 8px;
                margin: 4px {'4px 4px 40px' if is_user else '40px 4px 4px'};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        
        label = QLabel(text)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setStyleSheet("color: white; font-size: 13px;")
        layout.addWidget(label)


class ChatWidget(QWidget):
    """Chat interface with AI"""
    
    asset_generated = pyqtSignal(str)  # path to generated asset
    
    def __init__(self, ai_assistant: AIAssistant, parent=None):
        super().__init__(parent)
        self.ai = ai_assistant
        self.is_processing = False
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Chat messages area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        
        self.messages_widget = QWidget()
        self.messages_layout = QVBoxLayout(self.messages_widget)
        self.messages_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.messages_layout.setSpacing(8)
        
        # Welcome message
        welcome = ChatMessage("👋 Hi! I'm ClipForge AI.\n\nI can help you with:\n• Writing video scripts\n• Generating voiceovers\n• Suggesting edits\n• Creating captions\n\nTry: 'Write a 30s script for a car ad'", False)
        self.messages_layout.addWidget(welcome)
        self.messages_layout.addStretch()
        
        scroll.setWidget(self.messages_widget)
        layout.addWidget(scroll, stretch=1)
        
        # Input area
        input_layout = QHBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Ask AI anything...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 20px;
                background: #252525;
                border: 1px solid #3f3f46;
            }
        """)
        self.input_field.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.input_field)
        
        send_btn = QPushButton("➤")
        send_btn.setFixedSize(44, 44)
        send_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 22px;
                font-size: 18px;
            }
        """)
        send_btn.clicked.connect(self._send_message)
        input_layout.addWidget(send_btn)
        
        layout.addLayout(input_layout)
    
    def _send_message(self):
        if self.is_processing:
            return
        
        text = self.input_field.text().strip()
        if not text:
            return
        
        self.input_field.clear()
        
        # Add user message
        user_msg = ChatMessage(text, True)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, user_msg)
        
        # Show typing indicator
        self.is_processing = True
        typing = ChatMessage("🤔 Thinking...", False)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, typing)
        
        # Process in background (simplified - should use QThread)
        QTimer.singleShot(100, lambda: self._process_message(text, typing))
    
    def _process_message(self, text: str, typing_widget: ChatMessage):
        response = self.ai.chat(text)
        
        # Remove typing indicator
        typing_widget.deleteLater()
        
        # Add AI response
        ai_msg = ChatMessage(response, False)
        self.messages_layout.insertWidget(self.messages_layout.count() - 1, ai_msg)
        
        self.is_processing = False


class ScriptGeneratorWidget(QWidget):
    """Script generation tool"""
    
    def __init__(self, ai_assistant: AIAssistant, parent=None):
        super().__init__(parent)
        self.ai = ai_assistant
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Topic input
        layout.addWidget(QLabel("📝 Video Topic:"))
        self.topic_input = QLineEdit()
        self.topic_input.setPlaceholderText("e.g., Tata Sierra SUV cinematic ad")
        layout.addWidget(self.topic_input)
        
        # Duration
        dur_layout = QHBoxLayout()
        dur_layout.addWidget(QLabel("⏱ Duration:"))
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(15, 300)
        self.duration_spin.setValue(30)
        self.duration_spin.setSuffix(" seconds")
        dur_layout.addWidget(self.duration_spin)
        dur_layout.addStretch()
        layout.addLayout(dur_layout)
        
        # Generate button
        gen_btn = QPushButton("✨ Generate Script")
        gen_btn.setObjectName("primaryButton")
        gen_btn.clicked.connect(self._generate)
        layout.addWidget(gen_btn)
        
        # Output
        layout.addWidget(QLabel("📄 Generated Script:"))
        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setPlaceholderText("Your script will appear here...")
        layout.addWidget(self.output, stretch=1)
        
        # Copy button
        copy_btn = QPushButton("📋 Copy to Clipboard")
        copy_btn.clicked.connect(self._copy)
        layout.addWidget(copy_btn)
    
    def _generate(self):
        topic = self.topic_input.text().strip()
        if not topic:
            return
        
        self.output.setPlainText("⏳ Generating script...")
        
        QTimer.singleShot(100, lambda: self._do_generate(topic))
    
    def _do_generate(self, topic: str):
        result = self.ai.generate_script(topic, self.duration_spin.value())
        self.output.setPlainText(result)
    
    def _copy(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.clipboard().setText(self.output.toPlainText())


class VoiceGeneratorWidget(QWidget):
    """Text-to-speech voiceover generator"""
    
    audio_generated = pyqtSignal(str)  # path to audio file
    
    def __init__(self, ai_assistant: AIAssistant, parent=None):
        super().__init__(parent)
        self.ai = ai_assistant
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        
        # Text input
        layout.addWidget(QLabel("🎤 Voiceover Text:"))
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("Enter the text you want to convert to speech...")
        self.text_input.setMaximumHeight(150)
        layout.addWidget(self.text_input)
        
        # Voice selection
        voice_layout = QHBoxLayout()
        voice_layout.addWidget(QLabel("🗣 Voice:"))
        self.voice_combo = QComboBox()
        self.voice_combo.addItems(["Rachel", "Adam", "Antoni", "Josh", "Sam"])
        voice_layout.addWidget(self.voice_combo)
        voice_layout.addStretch()
        layout.addLayout(voice_layout)
        
        # Generate button
        gen_btn = QPushButton("🎙 Generate Voiceover")
        gen_btn.setObjectName("primaryButton")
        gen_btn.clicked.connect(self._generate)
        layout.addWidget(gen_btn)
        
        # Status
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #71717a;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Note
        note = QLabel("💡 Generated audio will be added to your Media Library")
        note.setStyleSheet("color: #71717a; font-size: 11px;")
        layout.addWidget(note)
    
    def _generate(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            return
        
        self.status_label.setText("⏳ Generating voiceover...")
        
        QTimer.singleShot(100, lambda: self._do_generate(text))
    
    def _do_generate(self, text: str):
        voice = self.voice_combo.currentText()
        result = self.ai.generate_voiceover(text, voice)
        
        if result:
            self.status_label.setText(f"✅ Voiceover saved!")
            self.audio_generated.emit(result)
        else:
            self.status_label.setText("❌ Failed. Check API key in Settings.")


class AIPanel(QWidget):
    """Main AI panel with tabs for different tools"""
    
    asset_generated = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ai = AIAssistant()
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Header
        header = QHBoxLayout()
        title = QLabel("🤖 AI Assistant")
        title.setStyleSheet("font-size: 14px; font-weight: 600; color: #a1a1aa;")
        header.addWidget(title)
        header.addStretch()
        
        settings_btn = QPushButton("⚙️")
        settings_btn.setFixedSize(32, 32)
        settings_btn.setToolTip("AI Settings")
        settings_btn.clicked.connect(self._show_settings)
        header.addWidget(settings_btn)
        layout.addLayout(header)
        
        # Tabs
        tabs = QTabWidget()
        
        # Chat tab
        self.chat_widget = ChatWidget(self.ai)
        tabs.addTab(self.chat_widget, "💬 Chat")
        
        # Script tab
        self.script_widget = ScriptGeneratorWidget(self.ai)
        tabs.addTab(self.script_widget, "📝 Script")
        
        # Voice tab
        self.voice_widget = VoiceGeneratorWidget(self.ai)
        self.voice_widget.audio_generated.connect(self.asset_generated.emit)
        tabs.addTab(self.voice_widget, "🎤 Voice")
        
        layout.addWidget(tabs)
    
    def _show_settings(self):
        dialog = AISettingsDialog(self.ai.config, self)
        if dialog.exec():
            new_config = dialog.get_config()
            self.ai.update_config(new_config)
            QMessageBox.information(self, "Settings Saved", "AI configuration updated!")


class AISettingsDialog(QDialog):
    """AI API configuration dialog"""
    
    def __init__(self, config: AIConfig, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("AI Configuration")
        self.setMinimumWidth(450)
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Info
        info = QLabel("🔑 Enter your API keys to enable AI features")
        info.setStyleSheet("color: #a1a1aa; margin-bottom: 12px;")
        layout.addWidget(info)
        
        form = QFormLayout()
        
        # Gemini
        self.gemini_key = QLineEdit(self.config.gemini_api_key)
        self.gemini_key.setPlaceholderText("AIza...")
        self.gemini_key.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("Gemini API Key:", self.gemini_key)
        
        gemini_link = QLabel('<a href="https://aistudio.google.com/apikey">Get Gemini Key</a>')
        gemini_link.setOpenExternalLinks(True)
        form.addRow("", gemini_link)
        
        # ElevenLabs
        self.eleven_key = QLineEdit(self.config.elevenlabs_api_key)
        self.eleven_key.setPlaceholderText("sk-...")
        self.eleven_key.setEchoMode(QLineEdit.EchoMode.Password)
        form.addRow("ElevenLabs Key:", self.eleven_key)
        
        eleven_link = QLabel('<a href="https://elevenlabs.io/api">Get ElevenLabs Key</a>')
        eleven_link.setOpenExternalLinks(True)
        form.addRow("", eleven_link)
        
        layout.addLayout(form)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_config(self) -> AIConfig:
        return AIConfig(
            gemini_api_key=self.gemini_key.text().strip(),
            elevenlabs_api_key=self.eleven_key.text().strip()
        )
