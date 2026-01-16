"""
Clip Data Models
Represents different types of media clips on the timeline
"""
from dataclasses import dataclass, field
from typing import Optional, Tuple, Dict, Any
from enum import Enum
import uuid
import os


class ClipType(Enum):
    """Types of clips"""
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    TEXT = "text"


@dataclass
class Clip:
    """Base clip class"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    clip_type: ClipType = ClipType.VIDEO
    
    # Position on timeline (in seconds)
    start_time: float = 0.0
    duration: float = 5.0
    
    # Track number (0 = bottom)
    track: int = 0
    
    # Source trimming (in seconds from original media)
    trim_start: float = 0.0
    trim_end: float = 0.0
    
    # Properties
    opacity: float = 1.0
    volume: float = 1.0
    
    # Transitions
    transition_in: Optional[str] = None
    transition_out: Optional[str] = None
    transition_duration: float = 0.5
    
    @property
    def end_time(self) -> float:
        """Get clip end time on timeline"""
        return self.start_time + self.duration
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'clip_type': self.clip_type.value,
            'start_time': self.start_time,
            'duration': self.duration,
            'track': self.track,
            'trim_start': self.trim_start,
            'trim_end': self.trim_end,
            'opacity': self.opacity,
            'volume': self.volume,
            'transition_in': self.transition_in,
            'transition_out': self.transition_out,
            'transition_duration': self.transition_duration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Clip':
        """Create clip from dictionary"""
        data['clip_type'] = ClipType(data['clip_type'])
        return cls(**data)


@dataclass
class VideoClip(Clip):
    """Video clip with source file"""
    source_path: str = ""
    original_duration: float = 0.0
    resolution: Tuple[int, int] = (1920, 1080)
    fps: float = 30.0
    has_audio: bool = True
    
    # Visual effects
    scale: float = 1.0
    position: Tuple[int, int] = (0, 0)
    rotation: float = 0.0
    
    # Color adjustments
    brightness: float = 0.0
    contrast: float = 0.0
    saturation: float = 0.0
    
    def __post_init__(self):
        self.clip_type = ClipType.VIDEO
        if not self.name and self.source_path:
            self.name = os.path.basename(self.source_path)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'source_path': self.source_path,
            'original_duration': self.original_duration,
            'resolution': self.resolution,
            'fps': self.fps,
            'has_audio': self.has_audio,
            'scale': self.scale,
            'position': self.position,
            'rotation': self.rotation,
            'brightness': self.brightness,
            'contrast': self.contrast,
            'saturation': self.saturation
        })
        return data


@dataclass
class AudioClip(Clip):
    """Audio clip"""
    source_path: str = ""
    original_duration: float = 0.0
    sample_rate: int = 44100
    channels: int = 2
    
    # Audio effects
    fade_in: float = 0.0
    fade_out: float = 0.0
    
    def __post_init__(self):
        self.clip_type = ClipType.AUDIO
        if not self.name and self.source_path:
            self.name = os.path.basename(self.source_path)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'source_path': self.source_path,
            'original_duration': self.original_duration,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'fade_in': self.fade_in,
            'fade_out': self.fade_out
        })
        return data


@dataclass
class ImageClip(Clip):
    """Image/Photo clip"""
    source_path: str = ""
    resolution: Tuple[int, int] = (1920, 1080)
    
    # Ken Burns effect
    ken_burns_enabled: bool = False
    ken_burns_start_scale: float = 1.0
    ken_burns_end_scale: float = 1.2
    ken_burns_start_pos: Tuple[int, int] = (0, 0)
    ken_burns_end_pos: Tuple[int, int] = (0, 0)
    
    # Visual
    scale: float = 1.0
    position: Tuple[int, int] = (0, 0)
    rotation: float = 0.0
    
    def __post_init__(self):
        self.clip_type = ClipType.IMAGE
        self.duration = 5.0  # Default 5 seconds for images
        if not self.name and self.source_path:
            self.name = os.path.basename(self.source_path)
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'source_path': self.source_path,
            'resolution': self.resolution,
            'ken_burns_enabled': self.ken_burns_enabled,
            'ken_burns_start_scale': self.ken_burns_start_scale,
            'ken_burns_end_scale': self.ken_burns_end_scale,
            'ken_burns_start_pos': self.ken_burns_start_pos,
            'ken_burns_end_pos': self.ken_burns_end_pos,
            'scale': self.scale,
            'position': self.position,
            'rotation': self.rotation
        })
        return data


@dataclass
class TextClip(Clip):
    """Text overlay clip"""
    text: str = "Text"
    font_family: str = "Arial"
    font_size: int = 48
    font_color: str = "#FFFFFF"
    background_color: Optional[str] = None
    
    # Position
    position: Tuple[int, int] = (960, 540)  # Center of 1080p
    alignment: str = "center"  # left, center, right
    
    # Effects
    shadow: bool = False
    shadow_color: str = "#000000"
    shadow_offset: Tuple[int, int] = (2, 2)
    
    outline: bool = False
    outline_color: str = "#000000"
    outline_width: int = 2
    
    # Animation
    animation_in: Optional[str] = None  # fade, slide, typewriter
    animation_out: Optional[str] = None
    animation_duration: float = 0.5
    
    def __post_init__(self):
        self.clip_type = ClipType.TEXT
        if not self.name:
            self.name = self.text[:20] + "..." if len(self.text) > 20 else self.text
    
    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'text': self.text,
            'font_family': self.font_family,
            'font_size': self.font_size,
            'font_color': self.font_color,
            'background_color': self.background_color,
            'position': self.position,
            'alignment': self.alignment,
            'shadow': self.shadow,
            'shadow_color': self.shadow_color,
            'shadow_offset': self.shadow_offset,
            'outline': self.outline,
            'outline_color': self.outline_color,
            'outline_width': self.outline_width,
            'animation_in': self.animation_in,
            'animation_out': self.animation_out,
            'animation_duration': self.animation_duration
        })
        return data
