from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from mutagen import File as MutagenFile

from src.parsers.base_parser import BaseParser
from src.core.metadata_types import AudioMetadata


class AudioParser(BaseParser):
    """Extract technical and tag metadata from audio files via mutagen."""

    # Maps tag keys from various container formats (ID3, Vorbis comments,
    # MP4 atoms) onto our normalized AudioMetadata fields.
    TAG_FIELD_MAP = {
        'TPE1': 'artist', 'TPE2': 'artist', 'ARTIST': 'artist', '\xa9ART': 'artist',
        'TALB': 'album', 'ALBUM': 'album', '\xa9alb': 'album',
        'TCON': 'genre', 'GENRE': 'genre', '\xa9gen': 'genre',
        'TRCK': 'track_number', 'TRACKNUMBER': 'track_number', 'trkn': 'track_number',
        'TDRC': 'year', 'YEAR': 'year', 'DATE': 'year', '\xa9day': 'year',
        'USLT::eng': 'lyrics', 'LYRICS': 'lyrics', '\xa9lyr': 'lyrics',
    }

    def parse(self, file_path: Path) -> Tuple[Optional[AudioMetadata], Dict[str, Any]]:
        metadata = AudioMetadata()
        raw_metadata: Dict[str, Any] = {}

        try:
            audio = MutagenFile(file_path)

            if audio is not None:
                raw_metadata = self._extract_raw_metadata(audio)
                self._apply_metadata(metadata, audio, raw_metadata)

        except Exception as e:
            print(f"Error parsing audio metadata: {e}")

        return metadata, raw_metadata

    def _extract_raw_metadata(self, audio) -> Dict[str, Any]:
        raw_metadata: Dict[str, Any] = {}

        try:
            info = getattr(audio, 'info', None)
            if info is not None:
                for attr in dir(info):
                    if attr.startswith('_'):
                        continue
                    try:
                        value = getattr(info, attr)
                        if not callable(value):
                            raw_metadata[attr] = value
                    except (AttributeError, TypeError):
                        pass

            tags = getattr(audio, 'tags', None)
            if tags:
                for key in tags.keys():
                    try:
                        value = tags[key]
                        if isinstance(value, list) and value:
                            value = value[0]
                        raw_metadata[str(key)] = value
                    except (KeyError, IndexError):
                        pass

        except Exception as e:
            print(f"Error extracting raw audio data: {e}")

        return raw_metadata

    def _apply_metadata(self, metadata: AudioMetadata, audio, raw_metadata: Dict) -> None:
        info = getattr(audio, 'info', None)
        if info is not None:
            if hasattr(info, 'length'):
                metadata.duration_seconds = self._convert_to_float(info.length)
            if hasattr(info, 'bitrate'):
                metadata.bit_rate = self._convert_to_int(info.bitrate)
            if hasattr(info, 'sample_rate'):
                metadata.sample_rate = self._convert_to_int(info.sample_rate)
            if hasattr(info, 'channels'):
                metadata.channels = self._convert_to_int(info.channels)
            if hasattr(info, 'bits_per_sample'):
                metadata.bit_depth = self._convert_to_int(info.bits_per_sample)
            if hasattr(info, 'codec'):
                metadata.codec = str(info.codec)

        tags = getattr(audio, 'tags', None) or {}

        for tag_key, meta_key in self.TAG_FIELD_MAP.items():
            if tag_key not in tags:
                continue

            value = tags[tag_key]
            if isinstance(value, list) and value:
                value = value[0]

            if meta_key == 'track_number':
                track_value = self._parse_track_number(str(value))
                if track_value is not None:
                    metadata.track_number = track_value
            elif meta_key == 'year':
                year_value = self._parse_year(str(value))
                if year_value is not None:
                    metadata.year = year_value
            else:
                setattr(metadata, meta_key, str(value))

    def _parse_track_number(self, value: str) -> Optional[int]:
        try:
            if '/' in value:
                return int(value.split('/')[0])
            return int(value)
        except (ValueError, TypeError):
            return None

    def _parse_year(self, value: str) -> Optional[int]:
        try:
            digits = value[:4]
            if len(digits) >= 4 and digits.isdigit():
                return int(digits)
            return int(value)
        except (ValueError, TypeError):
            return None
