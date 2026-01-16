"""
Video Exporter
Handles final video rendering and export
"""
import os
import subprocess
from typing import Optional, Callable, List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

from config import TEMP_DIR, EXPORT_PRESETS
from .project import Project
from .clip import VideoClip, AudioClip, ImageClip, TextClip, ClipType
from .ffmpeg_engine import FFmpegEngine


@dataclass
class ExportSettings:
    """Export configuration"""
    output_path: str
    resolution: tuple = (1920, 1080)
    fps: float = 30.0
    bitrate: str = "10M"
    codec: str = "libx264"
    audio_codec: str = "aac"
    audio_bitrate: str = "192k"
    preset: str = "medium"  # ultrafast, fast, medium, slow, veryslow


class Exporter:
    """
    Handles video export/rendering
    Composes all clips and exports final video
    """
    
    def __init__(self, project: Project):
        self.project = project
        self.ffmpeg = FFmpegEngine()
        self.progress_callback: Optional[Callable[[float, str], None]] = None
        self._cancelled = False
    
    def set_progress_callback(self, callback: Callable[[float, str], None]):
        """Set callback for progress updates: callback(percentage, status_message)"""
        self.progress_callback = callback
    
    def cancel(self):
        """Cancel export"""
        self._cancelled = True
    
    def _report_progress(self, percentage: float, message: str):
        """Report progress to callback"""
        if self.progress_callback:
            self.progress_callback(percentage, message)
    
    def export(self, settings: ExportSettings) -> bool:
        """
        Export project to video file
        Returns True on success
        """
        self._cancelled = False
        
        try:
            self._report_progress(0, "Preparing export...")
            
            # Create temp directory for intermediate files
            export_temp = TEMP_DIR / "export"
            export_temp.mkdir(exist_ok=True)
            
            # Step 1: Process video tracks
            self._report_progress(5, "Processing video clips...")
            video_segments = self._process_video_tracks(export_temp, settings)
            
            if self._cancelled:
                return False
            
            # Step 2: Process audio tracks
            self._report_progress(40, "Processing audio clips...")
            audio_segments = self._process_audio_tracks(export_temp)
            
            if self._cancelled:
                return False
            
            # Step 3: Composite video layers
            self._report_progress(60, "Compositing video layers...")
            composited_video = self._composite_videos(video_segments, export_temp, settings)
            
            if self._cancelled:
                return False
            
            # Step 4: Mix audio
            self._report_progress(75, "Mixing audio...")
            final_audio = self._mix_audio(audio_segments, export_temp)
            
            if self._cancelled:
                return False
            
            # Step 5: Final render
            self._report_progress(85, "Rendering final video...")
            success = self._final_render(composited_video, final_audio, settings)
            
            if self._cancelled:
                return False
            
            # Cleanup
            self._report_progress(95, "Cleaning up...")
            self._cleanup(export_temp)
            
            self._report_progress(100, "Export complete!")
            return success
            
        except Exception as e:
            print(f"Export error: {e}")
            self._report_progress(0, f"Export failed: {e}")
            return False
    
    def _process_video_tracks(self, temp_dir: Path, settings: ExportSettings) -> List[str]:
        """Process all video track clips"""
        segments = []
        total_clips = sum(len(track) for track in self.project.video_tracks)
        processed = 0
        
        for track_idx, track in enumerate(self.project.video_tracks):
            for clip in track:
                if self._cancelled:
                    return segments
                
                output_path = str(temp_dir / f"video_t{track_idx}_{clip.id}.mp4")
                
                if isinstance(clip, VideoClip):
                    # Trim and process video clip
                    success = self._process_video_clip(clip, output_path, settings)
                elif isinstance(clip, ImageClip):
                    # Convert image to video
                    success = self.ffmpeg.image_to_video(
                        clip.source_path, 
                        output_path,
                        clip.duration,
                        settings.fps
                    )
                
                if success and os.path.exists(output_path):
                    segments.append({
                        'path': output_path,
                        'start_time': clip.start_time,
                        'duration': clip.duration,
                        'track': track_idx
                    })
                
                processed += 1
                progress = 5 + (35 * processed / max(total_clips, 1))
                self._report_progress(progress, f"Processing video {processed}/{total_clips}")
        
        return segments
    
    def _process_video_clip(self, clip: VideoClip, output_path: str, 
                           settings: ExportSettings) -> bool:
        """Process a single video clip"""
        # Build filter chain
        filters = []
        
        # Trim
        if clip.trim_start > 0 or clip.trim_end > 0:
            duration = clip.duration
            start = clip.trim_start
            # Trim will be done via -ss and -t
        
        # Scale to output resolution
        filters.append(f"scale={settings.resolution[0]}:{settings.resolution[1]}")
        
        # Apply color adjustments
        if clip.brightness != 0 or clip.contrast != 0 or clip.saturation != 0:
            eq_filter = f"eq=brightness={clip.brightness}:contrast={1 + clip.contrast}:saturation={1 + clip.saturation}"
            filters.append(eq_filter)
        
        # Build FFmpeg command
        args = [
            "-y",
            "-ss", str(clip.trim_start),
            "-i", clip.source_path,
            "-t", str(clip.duration),
        ]
        
        if filters:
            args.extend(["-vf", ",".join(filters)])
        
        args.extend([
            "-c:v", settings.codec,
            "-b:v", settings.bitrate,
            "-c:a", "aac",
            "-preset", "fast",
            output_path
        ])
        
        result = subprocess.run(
            [self.ffmpeg.ffmpeg_path] + args,
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
    
    def _process_audio_tracks(self, temp_dir: Path) -> List[Dict]:
        """Process all audio track clips"""
        segments = []
        
        for track_idx, track in enumerate(self.project.audio_tracks):
            for clip in track:
                if self._cancelled:
                    return segments
                
                if isinstance(clip, AudioClip):
                    output_path = str(temp_dir / f"audio_t{track_idx}_{clip.id}.mp3")
                    
                    # Trim audio
                    args = [
                        "-y",
                        "-ss", str(clip.trim_start),
                        "-i", clip.source_path,
                        "-t", str(clip.duration),
                        "-c:a", "libmp3lame",
                    ]
                    
                    # Apply volume
                    if clip.volume != 1.0:
                        args.extend(["-af", f"volume={clip.volume}"])
                    
                    args.append(output_path)
                    
                    result = subprocess.run(
                        [self.ffmpeg.ffmpeg_path] + args,
                        capture_output=True,
                        text=True
                    )
                    
                    if result.returncode == 0:
                        segments.append({
                            'path': output_path,
                            'start_time': clip.start_time,
                            'duration': clip.duration,
                            'track': track_idx
                        })
        
        return segments
    
    def _composite_videos(self, segments: List[Dict], temp_dir: Path,
                         settings: ExportSettings) -> str:
        """Composite all video segments onto timeline"""
        if not segments:
            # Create blank video
            blank_path = str(temp_dir / "blank.mp4")
            args = [
                "-y",
                "-f", "lavfi",
                "-i", f"color=c=black:s={settings.resolution[0]}x{settings.resolution[1]}:d={self.project.duration}:r={settings.fps}",
                "-c:v", settings.codec,
                blank_path
            ]
            subprocess.run([self.ffmpeg.ffmpeg_path] + args, capture_output=True)
            return blank_path
        
        # Sort segments by start time
        segments.sort(key=lambda s: s['start_time'])
        
        # For MVP, concatenate clips in order
        # Future: proper compositing with overlay
        output_path = str(temp_dir / "composited.mp4")
        
        # Create concat file
        concat_file = str(temp_dir / "concat.txt")
        with open(concat_file, 'w') as f:
            for seg in segments:
                f.write(f"file '{seg['path']}'\n")
        
        args = [
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c:v", settings.codec,
            "-b:v", settings.bitrate,
            "-c:a", "aac",
            output_path
        ]
        
        result = subprocess.run(
            [self.ffmpeg.ffmpeg_path] + args,
            capture_output=True,
            text=True
        )
        
        return output_path if result.returncode == 0 else segments[0]['path']
    
    def _mix_audio(self, segments: List[Dict], temp_dir: Path) -> Optional[str]:
        """Mix all audio segments"""
        if not segments:
            return None
        
        if len(segments) == 1:
            return segments[0]['path']
        
        # Mix multiple audio tracks
        output_path = str(temp_dir / "mixed_audio.mp3")
        
        inputs = []
        filter_parts = []
        
        for i, seg in enumerate(segments):
            inputs.extend(["-i", seg['path']])
            filter_parts.append(f"[{i}:a]")
        
        filter_str = "".join(filter_parts) + f"amix=inputs={len(segments)}:duration=longest[out]"
        
        args = ["-y"] + inputs + [
            "-filter_complex", filter_str,
            "-map", "[out]",
            "-c:a", "libmp3lame",
            output_path
        ]
        
        result = subprocess.run(
            [self.ffmpeg.ffmpeg_path] + args,
            capture_output=True,
            text=True
        )
        
        return output_path if result.returncode == 0 else segments[0]['path']
    
    def _final_render(self, video_path: str, audio_path: Optional[str],
                     settings: ExportSettings) -> bool:
        """Final render with video and audio"""
        args = ["-y", "-i", video_path]
        
        if audio_path:
            args.extend(["-i", audio_path])
        
        args.extend([
            "-c:v", settings.codec,
            "-b:v", settings.bitrate,
            "-preset", settings.preset,
            "-c:a", settings.audio_codec,
            "-b:a", settings.audio_bitrate,
        ])
        
        if audio_path:
            args.extend(["-map", "0:v", "-map", "1:a"])
        
        args.append(settings.output_path)
        
        result = subprocess.run(
            [self.ffmpeg.ffmpeg_path] + args,
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
    
    def _cleanup(self, temp_dir: Path):
        """Clean up temporary files"""
        import shutil
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception as e:
            print(f"Cleanup error: {e}")
    
    @staticmethod
    def get_presets() -> Dict[str, Dict]:
        """Get available export presets"""
        return EXPORT_PRESETS
    
    def quick_export(self, output_path: str, preset: str = "full_hd") -> bool:
        """Quick export with preset"""
        preset_settings = EXPORT_PRESETS.get(preset, EXPORT_PRESETS['full_hd'])
        
        settings = ExportSettings(
            output_path=output_path,
            resolution=preset_settings['resolution'],
            fps=preset_settings['fps'],
            bitrate=preset_settings['bitrate'],
            codec=preset_settings['codec']
        )
        
        return self.export(settings)
