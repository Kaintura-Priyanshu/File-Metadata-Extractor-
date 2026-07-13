from pathlib import Path
from typing import Tuple, Dict, Any, Optional
import shutil
import subprocess
import json

from src.parsers.base_parser import BaseParser
from src.core.metadata_types import VideoMetadata


class VideoParser(BaseParser):
    """Extract video/audio stream metadata using ffprobe, with a basic fallback."""

    def parse(self, file_path: Path) -> Tuple[Optional[VideoMetadata], Dict[str, Any]]:
        metadata = VideoMetadata()
        raw_metadata: Dict[str, Any] = {}

        try:
            raw_metadata = self._extract_with_ffprobe(file_path)
            self._apply_metadata(metadata, raw_metadata)

        except Exception as e:
            print(f"Error parsing video metadata: {e}")

        return metadata, raw_metadata

    def _extract_with_ffprobe(self, file_path: Path) -> Dict[str, Any]:
        if shutil.which('ffprobe') is None:
            return self._extract_basic_video_info(file_path)

        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                str(file_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)

            if result.returncode == 0 and result.stdout:
                return json.loads(result.stdout)

            return self._extract_basic_video_info(file_path)

        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            return self._extract_basic_video_info(file_path)

    def _extract_basic_video_info(self, file_path: Path) -> Dict[str, Any]:
        """Best-effort fallback when ffprobe is unavailable or fails.

        Note: this only reports the file size and a MIME-sniffed format
        name — it cannot determine duration, resolution, or codecs
        without ffprobe (or an equivalent parser) actually decoding the
        container. ffprobe is strongly recommended; on Kali/Debian:
        ``sudo apt install ffmpeg``.
        """
        info: Dict[str, Any] = {}

        try:
            stat_info = file_path.stat()
            info['format'] = {
                'size': str(stat_info.st_size),
                'filename': str(file_path),
            }

            try:
                import magic
                mime = magic.from_file(str(file_path), mime=True)
                if mime:
                    info['format']['format_name'] = mime
            except Exception:
                pass

        except Exception as e:
            print(f"Error getting basic video info: {e}")

        return info

    def _apply_metadata(self, metadata: VideoMetadata, raw_metadata: Dict) -> None:
        fmt = raw_metadata.get('format')
        if fmt:
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

        streams = raw_metadata.get('streams')
        if not streams:
            return

        video_streams = [s for s in streams if s.get('codec_type') == 'video']
        audio_streams = [s for s in streams if s.get('codec_type') == 'audio']

        if video_streams:
            video_stream = video_streams[0]

            if 'width' in video_stream:
                metadata.width = self._convert_to_int(video_stream['width'])
            if 'height' in video_stream:
                metadata.height = self._convert_to_int(video_stream['height'])

            frame_rate = video_stream.get('r_frame_rate')
            if frame_rate and '/' in frame_rate:
                try:
                    num, den = frame_rate.split('/')
                    if int(den) != 0:
                        metadata.frame_rate = round(int(num) / int(den), 2)
                except (ValueError, ZeroDivisionError):
                    pass

            if 'codec_name' in video_stream:
                metadata.codec = video_stream['codec_name']

            if 'pix_fmt' in video_stream:
                metadata.color_space = video_stream['pix_fmt']

            if video_stream.get('display_aspect_ratio'):
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

            sample_rate = audio_stream.get('sample_rate')
            if sample_rate:
                metadata.audio_sample_rate = self._convert_to_int(sample_rate)
