"""
FFmpeg Engine
Wrapper for FFmpeg operations - video processing, encoding, effects
"""
import subprocess
import shutil
import os
import json
from typing import Optional, Tuple, List, Dict, Any
from pathlib import Path

from config import TEMP_DIR


class FFmpegEngine:
    """
    FFmpeg wrapper for video processing operations
    """
    
    def __init__(self):
        self.ffmpeg_path = self._find_ffmpeg()
        self.ffprobe_path = self._find_ffprobe()
        
        if not self.ffmpeg_path:
            raise RuntimeError("FFmpeg not found. Please install FFmpeg.")
    
    def _find_ffmpeg(self) -> Optional[str]:
        """Find FFmpeg executable"""
        # Check if in PATH
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            return ffmpeg
        
        # Common locations
        common_paths = [
            "/usr/local/bin/ffmpeg",
            "/usr/bin/ffmpeg",
            "/opt/homebrew/bin/ffmpeg",  # macOS ARM
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        return None
    
    def _find_ffprobe(self) -> Optional[str]:
        """Find FFprobe executable"""
        ffprobe = shutil.which("ffprobe")
        if ffprobe:
            return ffprobe
        
        # Try same directory as ffmpeg
        if self.ffmpeg_path:
            ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")
            if os.path.exists(ffprobe_path):
                return ffprobe_path
        
        return None
    
    def _run(self, args: List[str], capture_output: bool = True) -> subprocess.CompletedProcess:
        """Run FFmpeg command"""
        cmd = [self.ffmpeg_path] + args
        print(f"Running: {' '.join(cmd)}")
        
        return subprocess.run(
            cmd,
            capture_output=capture_output,
            text=True
        )
    
    def _run_ffprobe(self, args: List[str]) -> subprocess.CompletedProcess:
        """Run FFprobe command"""
        if not self.ffprobe_path:
            raise RuntimeError("FFprobe not found")
        
        cmd = [self.ffprobe_path] + args
        return subprocess.run(cmd, capture_output=True, text=True)
    
    def get_media_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Get media file information"""
        if not self.ffprobe_path:
            return None
        
        try:
            result = self._run_ffprobe([
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                path
            ])
            
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"Error getting media info: {e}")
        
        return None
    
    def get_duration(self, path: str) -> float:
        """Get media duration in seconds"""
        info = self.get_media_info(path)
        if info and 'format' in info:
            return float(info['format'].get('duration', 0))
        return 0.0
    
    def get_resolution(self, path: str) -> Tuple[int, int]:
        """Get video resolution"""
        info = self.get_media_info(path)
        if info and 'streams' in info:
            for stream in info['streams']:
                if stream.get('codec_type') == 'video':
                    return (stream.get('width', 0), stream.get('height', 0))
        return (0, 0)
    
    def get_fps(self, path: str) -> float:
        """Get video frame rate"""
        info = self.get_media_info(path)
        if info and 'streams' in info:
            for stream in info['streams']:
                if stream.get('codec_type') == 'video':
                    fps_str = stream.get('r_frame_rate', '30/1')
                    if '/' in fps_str:
                        num, den = fps_str.split('/')
                        return float(num) / float(den)
                    return float(fps_str)
        return 30.0
    
    def extract_frame(self, video_path: str, time: float, output_path: str, 
                      size: Optional[Tuple[int, int]] = None) -> bool:
        """Extract a single frame from video"""
        args = [
            "-y",  # Overwrite
            "-ss", str(time),
            "-i", video_path,
            "-vframes", "1",
        ]
        
        if size:
            args.extend(["-vf", f"scale={size[0]}:{size[1]}"])
        
        args.append(output_path)
        
        result = self._run(args)
        return result.returncode == 0
    
    def generate_thumbnail(self, video_path: str, output_path: str,
                          size: Tuple[int, int] = (160, 90)) -> bool:
        """Generate video thumbnail"""
        duration = self.get_duration(video_path)
        # Get frame at 10% into the video
        time = duration * 0.1 if duration > 0 else 0
        return self.extract_frame(video_path, time, output_path, size)
    
    def trim_video(self, input_path: str, output_path: str,
                   start: float, end: float) -> bool:
        """Trim video to specified range"""
        duration = end - start
        
        args = [
            "-y",
            "-ss", str(start),
            "-i", input_path,
            "-t", str(duration),
            "-c", "copy",  # Copy without re-encoding
            output_path
        ]
        
        result = self._run(args)
        return result.returncode == 0
    
    def cut_video(self, input_path: str, output_path: str,
                  cut_start: float, cut_end: float) -> bool:
        """Cut a section out of video (remove middle portion)"""
        temp1 = str(TEMP_DIR / "temp_part1.mp4")
        temp2 = str(TEMP_DIR / "temp_part2.mp4")
        concat_file = str(TEMP_DIR / "concat.txt")
        
        duration = self.get_duration(input_path)
        
        # Get first part
        self.trim_video(input_path, temp1, 0, cut_start)
        
        # Get second part
        self.trim_video(input_path, temp2, cut_end, duration)
        
        # Create concat file
        with open(concat_file, 'w') as f:
            f.write(f"file '{temp1}'\n")
            f.write(f"file '{temp2}'\n")
        
        # Concatenate
        args = [
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            output_path
        ]
        
        result = self._run(args)
        
        # Cleanup
        for f in [temp1, temp2, concat_file]:
            if os.path.exists(f):
                os.remove(f)
        
        return result.returncode == 0
    
    def merge_videos(self, input_paths: List[str], output_path: str) -> bool:
        """Merge multiple videos into one"""
        concat_file = str(TEMP_DIR / "concat.txt")
        
        # Create concat file
        with open(concat_file, 'w') as f:
            for path in input_paths:
                f.write(f"file '{path}'\n")
        
        args = [
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_file,
            "-c", "copy",
            output_path
        ]
        
        result = self._run(args)
        
        # Cleanup
        if os.path.exists(concat_file):
            os.remove(concat_file)
        
        return result.returncode == 0
    
    def add_audio(self, video_path: str, audio_path: str, output_path: str,
                  volume: float = 1.0) -> bool:
        """Add/replace audio in video"""
        args = [
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
        ]
        
        if volume != 1.0:
            args.extend(["-af", f"volume={volume}"])
        
        args.append(output_path)
        
        result = self._run(args)
        return result.returncode == 0
    
    def mix_audio(self, video_path: str, audio_path: str, output_path: str,
                  video_volume: float = 1.0, audio_volume: float = 0.5) -> bool:
        """Mix video's audio with external audio"""
        args = [
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-filter_complex",
            f"[0:a]volume={video_volume}[a1];[1:a]volume={audio_volume}[a2];[a1][a2]amix=inputs=2:duration=first",
            "-c:v", "copy",
            output_path
        ]
        
        result = self._run(args)
        return result.returncode == 0
    
    def add_text_overlay(self, input_path: str, output_path: str,
                        text: str, position: Tuple[int, int] = (100, 100),
                        font_size: int = 48, font_color: str = "white",
                        start_time: float = 0, end_time: Optional[float] = None) -> bool:
        """Add text overlay to video"""
        # Build drawtext filter
        filter_str = (
            f"drawtext=text='{text}':"
            f"x={position[0]}:y={position[1]}:"
            f"fontsize={font_size}:fontcolor={font_color}"
        )
        
        if end_time:
            filter_str += f":enable='between(t,{start_time},{end_time})'"
        
        args = [
            "-y",
            "-i", input_path,
            "-vf", filter_str,
            "-c:a", "copy",
            output_path
        ]
        
        result = self._run(args)
        return result.returncode == 0
    
    def apply_transition(self, clip1_path: str, clip2_path: str, output_path: str,
                        transition: str = "fade", duration: float = 1.0) -> bool:
        """Apply transition between two clips"""
        clip1_duration = self.get_duration(clip1_path)
        
        if transition == "fade":
            # Crossfade transition
            args = [
                "-y",
                "-i", clip1_path,
                "-i", clip2_path,
                "-filter_complex",
                f"[0:v]fade=t=out:st={clip1_duration - duration}:d={duration}[v0];"
                f"[1:v]fade=t=in:st=0:d={duration}[v1];"
                f"[v0][v1]concat=n=2:v=1:a=0[outv];"
                f"[0:a][1:a]acrossfade=d={duration}[outa]",
                "-map", "[outv]",
                "-map", "[outa]",
                output_path
            ]
        else:
            # Default: simple concatenation
            return self.merge_videos([clip1_path, clip2_path], output_path)
        
        result = self._run(args)
        return result.returncode == 0
    
    def image_to_video(self, image_path: str, output_path: str,
                      duration: float = 5.0, fps: float = 30) -> bool:
        """Convert image to video clip"""
        args = [
            "-y",
            "-loop", "1",
            "-i", image_path,
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            "-r", str(fps),
            output_path
        ]
        
        result = self._run(args)
        return result.returncode == 0
    
    def scale_video(self, input_path: str, output_path: str,
                   width: int, height: int) -> bool:
        """Scale video to specified resolution"""
        args = [
            "-y",
            "-i", input_path,
            "-vf", f"scale={width}:{height}",
            "-c:a", "copy",
            output_path
        ]
        
        result = self._run(args)
        return result.returncode == 0
    
    def speed_change(self, input_path: str, output_path: str,
                    speed: float = 1.0) -> bool:
        """Change video speed (0.5 = half speed, 2.0 = double speed)"""
        video_pts = 1.0 / speed
        audio_tempo = speed
        
        # Audio tempo filter has limits
        if audio_tempo < 0.5:
            audio_tempo = 0.5
        elif audio_tempo > 2.0:
            audio_tempo = 2.0
        
        args = [
            "-y",
            "-i", input_path,
            "-filter_complex",
            f"[0:v]setpts={video_pts}*PTS[v];[0:a]atempo={audio_tempo}[a]",
            "-map", "[v]",
            "-map", "[a]",
            output_path
        ]
        
        result = self._run(args)
        return result.returncode == 0
