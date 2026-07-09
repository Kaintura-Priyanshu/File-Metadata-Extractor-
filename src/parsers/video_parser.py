from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import subprocess
import json
import re

from src.parsers.base_parser import BaseParser
from src.core.metadata_types import VideoMetadata


class VideoParser(BaseParser):
    def parse(self, file_path: Path) -> Tuple[Optional[VideoMetadata], Dict[str, Any]]:
        metadata = VideoMetadata()
        raw_metadata = {}
        
        try:
            raw_metadata = self._extract_with_ffprobe(file_path)
            self._apply_metadata(metadata, raw_metadata)
        
        except Exception as e:
            print(f"Error parsing video metadata: {e}")
        
        return metadata, raw_metadata
    
    def _extract_with_ffprobe(self, file_path: Path) -> Dict[str, Any]:
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                return self._extract_basic_video_info(file_path)
        
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            return self._extract_basic_video_info(file_path)
    
    def _extract_basic_video_info(self, file_path: Path) -> Dict[str, Any]:
        info = {}
        
        try:
            import os
            stat_info = file_path.stat()
            info['format'] = {
                'size': stat_info.st_size,
                'filename': str(file_path)
            }
            
            file_size_mb = stat_info.st_size / (1024 * 1024)
            if file_size_mb < 1:
                info['format']['duration'] = 'unknown'
            
            import magic
            mime = magic.from_file(str(file_path), mime=True)
            info['format']['format_name'] = mime
        
        except Exception as e:
            print(f"Error getting basic video info: {e}")
        
        return info
    
    def _apply_metadata(self, metadata: VideoMetadata, raw_metadata: Dict) -> None:
        if 'format' in raw_metadata:
            fmt = raw_metadata['format']
            if 'duration' in fmt:
                try:
                    metadata.duration_seconds = float(fmt['duration'])
                except (ValueError, TypeError):
                    pass
            
            if 'bit_rate' in fmt:
                try:
                    metadata.bit_rate = int(fmt['bit_rate'])
                except (ValueError, TypeError):
                    pass
        
        if 'streams' in raw_metadata:
            video_streams = [s for s in raw_metadata['streams'] if s.get('codec_type') == 'video']
            audio_streams = [s for s in raw_metadata['streams'] if s.get('codec_type') == 'audio']
            
            if video_streams:
                video_stream = video_streams[0]
                
                if 'width' in video_stream:
                    metadata.width = self._convert_to_int(video_stream['width'])
                if 'height' in video_stream:
                    metadata.height = self._convert_to_int(video_stream['height'])
                
                if 'r_frame_rate' in video_stream:
                    frame_rate = video_stream['r_frame_rate']
                    if '/' in frame_rate:
                        try:
                            num, den = frame_rate.split('/')
                            if int(den) != 0:
                                metadata.frame_rate = int(num) / int(den)
                        except (ValueError, ZeroDivisionError):
                            pass
                
                if 'codec_name' in video_stream:
                    metadata.codec = video_stream['codec_name']
                
                if 'pix_fmt' in video_stream:
                    metadata.color_space = video_stream['pix_fmt']
                
                if 'display_aspect_ratio' in video_stream and video_stream['display_aspect_ratio']:
                    metadata.aspect_ratio = video_stream['display_aspect_ratio']
                elif metadata.width and metadata.height:
                    ratio = metadata.width / metadata.height
                    metadata.aspect_ratio = f"{ratio:.2f}:1"
            
            if audio_streams:
                audio_stream = audio_streams[0]
                
                if 'codec_name' in audio_stream:
                    metadata.audio_codec = audio_stream['codec_name']
                
                if 'channels' in audio_stream:
                    metadata.audio_channels = self._convert_to_int(audio_stream['channels'])
                
                if 'sample_rate' in audio_stream:
                    sample_rate = audio_stream['sample_rate']
                    if sample_rate:
                        try:
                            metadata.audio_sample_rate = int(sample_rate)
                        except ValueError:
                            pass
