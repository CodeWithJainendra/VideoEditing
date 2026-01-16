"""
Project Management
Handles project saving, loading, and state management
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

from .clip import Clip, VideoClip, AudioClip, ImageClip, TextClip, ClipType


@dataclass
class ProjectSettings:
    """Project export/render settings"""
    resolution: tuple = (1920, 1080)
    fps: float = 30.0
    sample_rate: int = 44100
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'resolution': self.resolution,
            'fps': self.fps,
            'sample_rate': self.sample_rate
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectSettings':
        return cls(**data)


@dataclass
class Project:
    """
    Represents a video editing project
    Contains all clips, tracks, and settings
    """
    name: str = "Untitled Project"
    path: Optional[str] = None
    
    # Settings
    settings: ProjectSettings = field(default_factory=ProjectSettings)
    
    # Clips organized by track
    video_tracks: List[List[Clip]] = field(default_factory=lambda: [[] for _ in range(3)])
    audio_tracks: List[List[Clip]] = field(default_factory=lambda: [[] for _ in range(2)])
    
    # Text/overlay clips
    overlay_clips: List[Clip] = field(default_factory=list)
    
    # Project metadata
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    modified_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    # Imported media files
    media_files: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> float:
        """Calculate total project duration"""
        max_end = 0.0
        
        for track in self.video_tracks:
            for clip in track:
                max_end = max(max_end, clip.end_time)
        
        for track in self.audio_tracks:
            for clip in track:
                max_end = max(max_end, clip.end_time)
        
        for clip in self.overlay_clips:
            max_end = max(max_end, clip.end_time)
        
        return max_end
    
    def add_clip(self, clip: Clip, track_type: str = "video", track_index: int = 0) -> bool:
        """Add a clip to the specified track"""
        try:
            if track_type == "video":
                if track_index >= len(self.video_tracks):
                    self.video_tracks.append([])
                self.video_tracks[track_index].append(clip)
            elif track_type == "audio":
                if track_index >= len(self.audio_tracks):
                    self.audio_tracks.append([])
                self.audio_tracks[track_index].append(clip)
            elif track_type == "overlay":
                self.overlay_clips.append(clip)
            
            self._sort_clips()
            self.modified_at = datetime.now().isoformat()
            return True
        except Exception as e:
            print(f"Error adding clip: {e}")
            return False
    
    def remove_clip(self, clip_id: str) -> bool:
        """Remove a clip by ID"""
        for track in self.video_tracks:
            for clip in track:
                if clip.id == clip_id:
                    track.remove(clip)
                    self.modified_at = datetime.now().isoformat()
                    return True
        
        for track in self.audio_tracks:
            for clip in track:
                if clip.id == clip_id:
                    track.remove(clip)
                    self.modified_at = datetime.now().isoformat()
                    return True
        
        for clip in self.overlay_clips:
            if clip.id == clip_id:
                self.overlay_clips.remove(clip)
                self.modified_at = datetime.now().isoformat()
                return True
        
        return False
    
    def get_clip(self, clip_id: str) -> Optional[Clip]:
        """Get a clip by ID"""
        for track in self.video_tracks:
            for clip in track:
                if clip.id == clip_id:
                    return clip
        
        for track in self.audio_tracks:
            for clip in track:
                if clip.id == clip_id:
                    return clip
        
        for clip in self.overlay_clips:
            if clip.id == clip_id:
                return clip
        
        return None
    
    def get_all_clips(self) -> List[Clip]:
        """Get all clips in the project"""
        clips = []
        for track in self.video_tracks:
            clips.extend(track)
        for track in self.audio_tracks:
            clips.extend(track)
        clips.extend(self.overlay_clips)
        return clips
    
    def _sort_clips(self):
        """Sort clips by start time in each track"""
        for track in self.video_tracks:
            track.sort(key=lambda c: c.start_time)
        for track in self.audio_tracks:
            track.sort(key=lambda c: c.start_time)
        self.overlay_clips.sort(key=lambda c: c.start_time)
    
    def add_media_file(self, path: str) -> bool:
        """Add a media file to the project"""
        if path not in self.media_files and os.path.exists(path):
            self.media_files.append(path)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize project to dictionary"""
        return {
            'name': self.name,
            'path': self.path,
            'settings': self.settings.to_dict(),
            'video_tracks': [[clip.to_dict() for clip in track] for track in self.video_tracks],
            'audio_tracks': [[clip.to_dict() for clip in track] for track in self.audio_tracks],
            'overlay_clips': [clip.to_dict() for clip in self.overlay_clips],
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'media_files': self.media_files
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Project':
        """Deserialize project from dictionary"""
        project = cls()
        project.name = data.get('name', 'Untitled Project')
        project.path = data.get('path')
        project.settings = ProjectSettings.from_dict(data.get('settings', {}))
        project.created_at = data.get('created_at', datetime.now().isoformat())
        project.modified_at = data.get('modified_at', datetime.now().isoformat())
        project.media_files = data.get('media_files', [])
        
        # Deserialize clips
        def deserialize_clip(clip_data: Dict) -> Clip:
            clip_type = ClipType(clip_data['clip_type'])
            if clip_type == ClipType.VIDEO:
                return VideoClip(**{k: v for k, v in clip_data.items() if k != 'clip_type'})
            elif clip_type == ClipType.AUDIO:
                return AudioClip(**{k: v for k, v in clip_data.items() if k != 'clip_type'})
            elif clip_type == ClipType.IMAGE:
                return ImageClip(**{k: v for k, v in clip_data.items() if k != 'clip_type'})
            elif clip_type == ClipType.TEXT:
                return TextClip(**{k: v for k, v in clip_data.items() if k != 'clip_type'})
            return Clip(**clip_data)
        
        project.video_tracks = [
            [deserialize_clip(c) for c in track]
            for track in data.get('video_tracks', [[], [], []])
        ]
        project.audio_tracks = [
            [deserialize_clip(c) for c in track]
            for track in data.get('audio_tracks', [[], []])
        ]
        project.overlay_clips = [
            deserialize_clip(c) for c in data.get('overlay_clips', [])
        ]
        
        return project
    
    def save(self, path: Optional[str] = None) -> bool:
        """Save project to file"""
        save_path = path or self.path
        if not save_path:
            return False
        
        try:
            # Ensure .cfproj extension
            if not save_path.endswith('.cfproj'):
                save_path += '.cfproj'
            
            self.path = save_path
            self.modified_at = datetime.now().isoformat()
            
            with open(save_path, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving project: {e}")
            return False
    
    @classmethod
    def load(cls, path: str) -> Optional['Project']:
        """Load project from file"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
            return cls.from_dict(data)
        except Exception as e:
            print(f"Error loading project: {e}")
            return None
    
    @classmethod
    def new(cls, name: str = "Untitled Project") -> 'Project':
        """Create a new empty project"""
        return cls(name=name)
