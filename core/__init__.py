"""
Core package - Video editing engine
"""
from .clip import Clip, VideoClip, AudioClip, ImageClip, TextClip
from .project import Project
from .ffmpeg_engine import FFmpegEngine
from .exporter import Exporter

__all__ = [
    'Clip', 'VideoClip', 'AudioClip', 'ImageClip', 'TextClip',
    'Project', 'FFmpegEngine', 'Exporter'
]
