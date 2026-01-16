"""
AI Services - API integrations for AI features
"""
import os
import json
import base64
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum

from config import ASSETS_DIR, TEMP_DIR


class AIProvider(Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ELEVENLABS = "elevenlabs"


@dataclass
class AIConfig:
    """API configuration"""
    gemini_api_key: str = ""
    elevenlabs_api_key: str = ""
    openai_api_key: str = ""
    
    @classmethod
    def load(cls) -> 'AIConfig':
        """Load config from file"""
        config_path = ASSETS_DIR / "ai_config.json"
        if config_path.exists():
            with open(config_path) as f:
                data = json.load(f)
                return cls(**data)
        return cls()
    
    def save(self):
        """Save config to file"""
        config_path = ASSETS_DIR / "ai_config.json"
        with open(config_path, 'w') as f:
            json.dump({
                'gemini_api_key': self.gemini_api_key,
                'elevenlabs_api_key': self.elevenlabs_api_key,
                'openai_api_key': self.openai_api_key
            }, f)


class GeminiService:
    """Google Gemini API integration"""
    
    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def generate_text(self, prompt: str, context: str = "") -> Optional[str]:
        """Generate text response from Gemini"""
        if not self.api_key:
            return "⚠️ Gemini API key not configured. Go to Settings > AI Configuration."
        
        try:
            url = f"{self.BASE_URL}/models/gemini-pro:generateContent?key={self.api_key}"
            
            full_prompt = f"{context}\n\n{prompt}" if context else prompt
            
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }]
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
                
                if 'candidates' in result:
                    return result['candidates'][0]['content']['parts'][0]['text']
                return "No response generated."
                
        except urllib.error.HTTPError as e:
            return f"API Error: {e.code} - {e.reason}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_script(self, topic: str, duration: int = 30) -> str:
        """Generate video script"""
        prompt = f"""You are a professional video scriptwriter.

Create a {duration}-second video script for: {topic}

Format:
---
TITLE: [Catchy title]

HOOK (0-3 sec): [Opening hook]

SCENE 1 (3-10 sec):
- Visual: [What to show]
- Voiceover: [What to say]
- Text overlay: [On-screen text]

SCENE 2 (10-20 sec):
- Visual: [What to show]
- Voiceover: [What to say]
- Text overlay: [On-screen text]

SCENE 3 (20-{duration} sec):
- Visual: [What to show]
- Voiceover: [What to say]
- CTA: [Call to action]

MUSIC SUGGESTION: [Type of background music]
---

Be creative, engaging, and keep it punchy!"""
        
        return self.generate_text(prompt)
    
    def generate_image_prompt(self, description: str) -> str:
        """Generate optimized image generation prompt"""
        prompt = f"""Create an optimized image generation prompt for:
{description}

The prompt should be:
- Detailed and specific
- Include style (cinematic, realistic, artistic, etc.)
- Include lighting, mood, composition
- Be under 200 words

Just output the prompt, nothing else."""
        
        return self.generate_text(prompt)
    
    def suggest_music(self, video_description: str) -> str:
        """Suggest background music"""
        prompt = f"""Suggest royalty-free background music for this video:
{video_description}

Provide:
1. Music genre/style
2. Tempo (BPM range)
3. Mood keywords
4. 3 specific song suggestions (royalty-free)
5. Where to find them (YouTube Audio Library, Pixabay, etc.)"""
        
        return self.generate_text(prompt)
    
    def generate_captions(self, script: str) -> str:
        """Generate social media captions"""
        prompt = f"""Create social media captions for this video script:
{script}

Provide:
1. YouTube title (60 chars max)
2. YouTube description (with hashtags)
3. Instagram caption (with emojis)
4. TikTok caption (short & catchy)
5. 10 relevant hashtags"""
        
        return self.generate_text(prompt)


class ElevenLabsService:
    """ElevenLabs Text-to-Speech API"""
    
    BASE_URL = "https://api.elevenlabs.io/v1"
    
    # Popular voice IDs
    VOICES = {
        "Rachel": "21m00Tcm4TlvDq8ikWAM",
        "Adam": "pNInz6obpgDQGcFmaJgB",
        "Antoni": "ErXwobaYiN019PkySvjV",
        "Josh": "TxGEqnHWrfWFTfGW9XjX",
        "Sam": "yoZ06aMxZJJ28mfd3POQ",
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def text_to_speech(self, text: str, voice: str = "Rachel", 
                       output_path: Optional[str] = None) -> Optional[str]:
        """Convert text to speech audio"""
        if not self.api_key:
            return None
        
        voice_id = self.VOICES.get(voice, self.VOICES["Rachel"])
        
        try:
            url = f"{self.BASE_URL}/text-to-speech/{voice_id}"
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={
                    'Content-Type': 'application/json',
                    'xi-api-key': self.api_key
                },
                method='POST'
            )
            
            if not output_path:
                output_path = str(TEMP_DIR / f"voice_{hash(text)}.mp3")
            
            with urllib.request.urlopen(req, timeout=60) as response:
                audio_data = response.read()
                with open(output_path, 'wb') as f:
                    f.write(audio_data)
                return output_path
                
        except Exception as e:
            print(f"ElevenLabs Error: {e}")
            return None
    
    def get_voices(self) -> Dict[str, str]:
        """Get available voices"""
        return self.VOICES


class AIAssistant:
    """Main AI assistant coordinating all services"""
    
    def __init__(self):
        self.config = AIConfig.load()
        self.gemini = GeminiService(self.config.gemini_api_key)
        self.elevenlabs = ElevenLabsService(self.config.elevenlabs_api_key)
        
        # Generated assets directory
        self.generated_dir = ASSETS_DIR / "generated"
        self.generated_dir.mkdir(exist_ok=True)
    
    def update_config(self, config: AIConfig):
        """Update API configuration"""
        self.config = config
        self.config.save()
        self.gemini = GeminiService(config.gemini_api_key)
        self.elevenlabs = ElevenLabsService(config.elevenlabs_api_key)
    
    def chat(self, message: str) -> str:
        """General chat with AI"""
        context = """You are ClipForge AI, an intelligent video editing assistant.
You help users with:
- Writing video scripts
- Suggesting edits and effects
- Creating captions and titles
- Recommending music
- Generating voiceover text
- Creative ideas for videos

Be helpful, creative, and concise. Use emojis occasionally."""
        
        return self.gemini.generate_text(message, context)
    
    def generate_script(self, topic: str, duration: int = 30) -> str:
        """Generate video script"""
        return self.gemini.generate_script(topic, duration)
    
    def generate_voiceover(self, text: str, voice: str = "Rachel") -> Optional[str]:
        """Generate voiceover audio"""
        output_path = str(self.generated_dir / f"voiceover_{hash(text) % 10000}.mp3")
        return self.elevenlabs.text_to_speech(text, voice, output_path)
    
    def suggest_edits(self, video_description: str) -> str:
        """Suggest editing techniques"""
        prompt = f"""For this video: {video_description}

Suggest professional editing techniques:
1. Cutting style (jump cuts, smooth transitions, etc.)
2. Pacing recommendations
3. Color grading style
4. Text/overlay suggestions
5. Sound design tips
6. Thumbnail ideas"""
        
        return self.gemini.generate_text(prompt)
