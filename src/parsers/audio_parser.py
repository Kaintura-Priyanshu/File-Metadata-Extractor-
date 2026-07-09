from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from mutagen.aac import AAC
from mutagen.mp4 import MP4

from src.parsers.base_parser import BaseParser
from src.core.metadata_types import AudioMetadata


class AudioParser(BaseParser):
    def parse(self, file_path: Path) -> Tuple[Optional[AudioMetadata], Dict[str, Any]]:
        metadata = AudioMetadata()
        raw_metadata = {}
        
        try:
            audio = MutagenFile(file_path)
            
            if audio:
                raw_metadata = self._extract_raw_metadata(audio)
                self._apply_metadata(metadata, audio, raw_metadata)
        
        except Exception as e:
            print(f"Error parsing audio metadata: {e}")
        
        return metadata, raw_metadata
    
    def _extract_raw_metadata(self, audio) -> Dict[str, Any]:
        raw_metadata = {}
        
        try:
            if hasattr(audio, 'info'):
                info = audio.info
                for attr in dir(info):
                    if not attr.startswith('_'):
                        try:
                            value = getattr(info, attr)
                            if not callable(value):
                                raw_metadata[attr] = value
                        except (AttributeError, TypeError):
                            pass
            
            if hasattr(audio, 'tags'):
                tags = audio.tags
                if tags:
                    for key in tags.keys():
                        try:
                            raw_metadata[key] = tags.get(key, [None])[0]
                        except (KeyError, IndexError):
                            pass
        
        except Exception as e:
            print(f"Error extracting raw audio data: {e}")
        
        return raw_metadata
    
    def _apply_metadata(self, metadata: AudioMetadata, audio, raw_metadata: Dict) -> None:
        if hasattr(audio, 'info'):
            info = audio.info
            
            if hasattr(info, 'length'):
                metadata.duration_seconds = info.length
            
            if hasattr(info, 'bitrate'):
                metadata.bit_rate = info.bitrate
            
            if hasattr(info, 'sample_rate'):
                metadata.sample_rate = info.sample_rate
            
            if hasattr(info, 'channels'):
                metadata.channels = info.channels
            
            if hasattr(info, 'bits_per_sample'):
                metadata.bit_depth = info.bits_per_sample
            
            if hasattr(info, 'codec'):
                metadata.codec = info.codec
        
        tags = {}
        if hasattr(audio, 'tags') and audio.tags:
            tags = audio.tags
        
        tag_fields = {
            'TPE1': 'artist',
            'TPE2': 'artist',
            'ARTIST': 'artist',
            '©ART': 'artist',
            
            'TALB': 'album',
            'ALBUM': 'album',
            '©alb': 'album',
            
            'TCON': 'genre',
            'GENRE': 'genre',
            '©gen': 'genre',
            
            'TRCK': 'track_number',
            'TRACKNUMBER': 'track_number',
            '©trk': 'track_number',
            
            'TDRC': 'year',
            'YEAR': 'year',
            '©day': 'year',
            
            'USLT': 'lyrics',
            'LYRICS': 'lyrics',
        }
        
        for tag_key, meta_key in tag_fields.items():
            if tag_key in tags:
                value = tags[tag_key]
                if isinstance(value, list) and value:
                    value = value[0]
                
                if meta_key == 'track_number':
                    track_value = self._parse_track_number(str(value))
                    if track_value is not None:
                        setattr(metadata, meta_key, track_value)
                elif meta_key == 'year':
                    year_value = self._parse_year(str(value))
                    if year_value is not None:
                        setattr(metadata, meta_key, year_value)
                else:
                    setattr(metadata, meta_key, str(value))
        
        if hasattr(audio, 'filename'):
            filename = str(audio.filename)
            if 'lyrics' in filename.lower():
                try:
                    with open(filename, 'r', encoding='utf-8') as f:
                        metadata.lyrics = f.read()
                except Exception:
                    pass
    
    def _parse_track_number(self, value: str) -> Optional[int]:
        try:
            if '/' in value:
                return int(value.split('/')[0])
            return int(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_year(self, value: str) -> Optional[int]:
        try:
            if len(value) >= 4:
                return int(value[:4])
            return int(value)
        except (ValueError, TypeError):
            return None
