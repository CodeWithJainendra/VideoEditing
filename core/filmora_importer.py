"""
Filmora Project Importer
Parses Wondershare Filmora .wfp project files
"""
import os
import sqlite3
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from config import TEMP_DIR
from core.project import Project, ProjectSettings
from core.clip import VideoClip, AudioClip, ImageClip, TextClip


@dataclass
class FilmoraClipInfo:
    """Parsed clip info from Filmora project"""
    media_path: str
    start_time: float
    duration: float
    track_index: int
    clip_type: str  # video, audio, image, text
    trim_start: float = 0
    trim_end: float = 0
    volume: float = 1.0
    text_content: str = ""


class FilmoraImporter:
    """
    Import Wondershare Filmora project files (.wfp)
    
    Note: .wfp files are SQLite databases containing project data.
    This importer extracts timeline, clips, and media references.
    """
    
    SUPPORTED_EXTENSIONS = ['.wfp', '.wve']  # Filmora, VN Editor
    
    def __init__(self):
        self.temp_db_path = str(TEMP_DIR / "filmora_temp.db")
    
    def can_import(self, file_path: str) -> bool:
        """Check if file can be imported"""
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.SUPPORTED_EXTENSIONS
    
    def import_project(self, file_path: str) -> Optional[Project]:
        """
        Import a Filmora .wfp file and convert to ClipForge project
        
        Args:
            file_path: Path to .wfp file
            
        Returns:
            Project object or None if import failed
        """
        if not os.path.exists(file_path):
            print(f"File not found: {file_path}")
            return None
        
        ext = os.path.splitext(file_path)[1].lower()
        
        try:
            if ext == '.wfp':
                return self._import_filmora(file_path)
            elif ext == '.wve':
                return self._import_vn(file_path)
            else:
                print(f"Unsupported format: {ext}")
                return None
        except Exception as e:
            print(f"Import error: {e}")
            return None
    
    def _import_filmora(self, file_path: str) -> Optional[Project]:
        """Import Filmora .wfp file"""
        # Copy to temp location (since it's a database)
        shutil.copy(file_path, self.temp_db_path)
        
        try:
            conn = sqlite3.connect(self.temp_db_path)
            cursor = conn.cursor()
            
            # Create new project
            project_name = os.path.splitext(os.path.basename(file_path))[0]
            project = Project.new(project_name)
            
            # Try to get project settings
            try:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                print(f"Found tables: {tables}")
                
                # Filmora uses different table names in different versions
                # Common tables: timeline, media, track, clip, etc.
                
                # Try to extract timeline clips
                if 'timeline_clip' in tables:
                    self._parse_timeline_clips(cursor, project)
                elif 'clip' in tables:
                    self._parse_clips(cursor, project)
                elif 'media' in tables:
                    self._parse_media(cursor, project)
                
                # Extract media files
                if 'media_resource' in tables:
                    self._parse_media_resources(cursor, project)
                elif 'resource' in tables:
                    self._parse_resources(cursor, project)
                    
            except sqlite3.Error as e:
                print(f"Database query error: {e}")
                # Fallback: just create empty project with name
            
            conn.close()
            
            # Setup source file reference
            project.path = file_path.replace('.wfp', '.cfproj')
            
            return project
            
        except Exception as e:
            print(f"Filmora import error: {e}")
            return None
        finally:
            # Cleanup temp file
            if os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
    
    def _parse_timeline_clips(self, cursor, project: Project):
        """Parse timeline_clip table"""
        try:
            cursor.execute("SELECT * FROM timeline_clip")
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                
                # Extract clip info
                start_time = data.get('start_time', 0) / 1000000  # Convert to seconds
                duration = data.get('duration', 5000000) / 1000000
                track = data.get('track_index', 0)
                media_path = data.get('media_path', '')
                
                if media_path and os.path.exists(media_path):
                    # Determine clip type from extension
                    ext = os.path.splitext(media_path)[1].lower()
                    
                    if ext in ['.mp4', '.mov', '.avi', '.mkv']:
                        clip = VideoClip(
                            source_path=media_path,
                            start_time=start_time,
                            duration=duration
                        )
                        project.add_clip(clip, "video", track)
                    elif ext in ['.mp3', '.wav', '.aac']:
                        clip = AudioClip(
                            source_path=media_path,
                            start_time=start_time,
                            duration=duration
                        )
                        project.add_clip(clip, "audio", track)
                    elif ext in ['.jpg', '.png', '.gif']:
                        clip = ImageClip(
                            source_path=media_path,
                            start_time=start_time,
                            duration=duration
                        )
                        project.add_clip(clip, "video", track)
                        
        except sqlite3.Error as e:
            print(f"Error parsing timeline_clip: {e}")
    
    def _parse_clips(self, cursor, project: Project):
        """Parse generic clip table"""
        try:
            cursor.execute("PRAGMA table_info(clip)")
            columns_info = cursor.fetchall()
            print(f"Clip table columns: {[c[1] for c in columns_info]}")
            
            cursor.execute("SELECT * FROM clip LIMIT 100")
            for row in cursor.fetchall():
                # Process row based on available columns
                pass
        except sqlite3.Error as e:
            print(f"Error parsing clip table: {e}")
    
    def _parse_media(self, cursor, project: Project):
        """Parse media table"""
        try:
            cursor.execute("SELECT * FROM media")
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                path = data.get('path', '') or data.get('file_path', '')
                if path and os.path.exists(path):
                    project.add_media_file(path)
        except sqlite3.Error as e:
            print(f"Error parsing media: {e}")
    
    def _parse_media_resources(self, cursor, project: Project):
        """Parse media_resource table"""
        try:
            cursor.execute("SELECT * FROM media_resource")
            columns = [desc[0] for desc in cursor.description]
            
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                path = data.get('local_path', '') or data.get('path', '')
                if path and os.path.exists(path):
                    project.add_media_file(path)
        except sqlite3.Error as e:
            print(f"Error parsing media_resource: {e}")
    
    def _parse_resources(self, cursor, project: Project):
        """Parse resource table"""
        try:
            cursor.execute("SELECT * FROM resource")
            for row in cursor.fetchall():
                # Try common column indices for path
                for item in row:
                    if isinstance(item, str) and os.path.exists(item):
                        project.add_media_file(item)
                        break
        except sqlite3.Error as e:
            print(f"Error parsing resource: {e}")
    
    def _import_vn(self, file_path: str) -> Optional[Project]:
        """Import VN Video Editor .wve file"""
        # VN files are also SQLite based
        # Similar structure to Filmora
        return self._import_filmora(file_path)  # Use same logic for now
    
    @staticmethod
    def get_supported_formats() -> List[str]:
        """Get list of supported import formats"""
        return [
            ("Filmora Project", "*.wfp"),
            ("VN Editor Project", "*.wve"),
            ("All Supported", "*.wfp *.wve"),
        ]


def analyze_wfp_structure(file_path: str) -> Dict[str, Any]:
    """
    Analyze a .wfp file structure for debugging
    Returns table names and sample data
    """
    result = {
        'tables': [],
        'sample_data': {}
    }
    
    temp_path = str(TEMP_DIR / "analyze_temp.db")
    shutil.copy(file_path, temp_path)
    
    try:
        conn = sqlite3.connect(temp_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        result['tables'] = tables
        
        # Get sample data from each table
        for table in tables[:10]:  # Limit to first 10 tables
            try:
                cursor.execute(f"PRAGMA table_info({table})")
                columns = [row[1] for row in cursor.fetchall()]
                
                cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                rows = cursor.fetchall()
                
                result['sample_data'][table] = {
                    'columns': columns,
                    'rows': rows
                }
            except:
                pass
        
        conn.close()
    except Exception as e:
        result['error'] = str(e)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    return result
