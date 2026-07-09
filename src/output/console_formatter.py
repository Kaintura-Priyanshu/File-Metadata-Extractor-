from typing import Dict, Any

from src.core.metadata_types import FileMetadata
from src.utils.file_utils import format_file_size


class ConsoleFormatter:
    @staticmethod
    def format(metadata: FileMetadata) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f"FILE METADATA: {metadata.basic.file_name}")
        lines.append("=" * 60)
        lines.append("")
        
        lines.append("BASIC INFORMATION")
        lines.append("-" * 60)
        lines.append(f"  File Path: {metadata.basic.file_path}")
        lines.append(f"  File Size: {format_file_size(metadata.basic.file_size)}")
        lines.append(f"  File Type: {metadata.basic.file_extension}")
        lines.append(f"  MIME Type: {metadata.basic.mime_type}")
        lines.append(f"  Category: {metadata.basic.file_category.value}")
        
        if metadata.basic.creation_time:
            lines.append(f"  Created: {metadata.basic.creation_time}")
        if metadata.basic.modification_time:
            lines.append(f"  Modified: {metadata.basic.modification_time}")
        if metadata.basic.access_time:
            lines.append(f"  Accessed: {metadata.basic.access_time}")
        
        if metadata.image:
            lines.append("")
            lines.append("IMAGE DETAILS")
            lines.append("-" * 60)
            if metadata.image.width and metadata.image.height:
                lines.append(f"  Dimensions: {metadata.image.width} x {metadata.image.height} pixels")
            if metadata.image.color_mode:
                lines.append(f"  Color Mode: {metadata.image.color_mode}")
            if metadata.image.bits_per_pixel:
                lines.append(f"  Bits Per Pixel: {metadata.image.bits_per_pixel}")
            if metadata.image.compression:
                lines.append(f"  Compression: {metadata.image.compression}")
            if metadata.image.dpi:
                lines.append(f"  DPI: {metadata.image.dpi[0]} x {metadata.image.dpi[1]}")
            if metadata.image.camera_make:
                lines.append(f"  Camera Make: {metadata.image.camera_make}")
            if metadata.image.camera_model:
                lines.append(f"  Camera Model: {metadata.image.camera_model}")
            if metadata.image.exposure_time:
                lines.append(f"  Exposure Time: {metadata.image.exposure_time}")
            if metadata.image.aperture:
                lines.append(f"  Aperture: f/{metadata.image.aperture}")
            if metadata.image.iso_speed:
                lines.append(f"  ISO Speed: {metadata.image.iso_speed}")
            if metadata.image.focal_length:
                lines.append(f"  Focal Length: {metadata.image.focal_length}mm")
            if metadata.image.gps_latitude is not None and metadata.image.gps_longitude is not None:
                lines.append(f"  GPS Location: {metadata.image.gps_latitude}, {metadata.image.gps_longitude}")
                if metadata.image.gps_altitude is not None:
                    lines.append(f"  GPS Altitude: {metadata.image.gps_altitude}m")
        
        if metadata.document:
            lines.append("")
            lines.append("DOCUMENT DETAILS")
            lines.append("-" * 60)
            if metadata.document.title:
                lines.append(f"  Title: {metadata.document.title}")
            if metadata.document.author:
                lines.append(f"  Author: {metadata.document.author}")
            if metadata.document.subject:
                lines.append(f"  Subject: {metadata.document.subject}")
            if metadata.document.keywords:
                lines.append(f"  Keywords: {', '.join(metadata.document.keywords)}")
            if metadata.document.page_count:
                lines.append(f"  Page Count: {metadata.document.page_count}")
            if metadata.document.word_count:
                lines.append(f"  Word Count: {metadata.document.word_count}")
            if metadata.document.character_count:
                lines.append(f"  Character Count: {metadata.document.character_count}")
            if metadata.document.application_name:
                lines.append(f"  Application: {metadata.document.application_name}")
                if metadata.document.application_version:
                    lines.append(f"  Version: {metadata.document.application_version}")
            if metadata.document.creation_date:
                lines.append(f"  Created: {metadata.document.creation_date}")
            if metadata.document.last_modified_date:
                lines.append(f"  Modified: {metadata.document.last_modified_date}")
        
        if metadata.audio:
            lines.append("")
            lines.append("AUDIO DETAILS")
            lines.append("-" * 60)
            if metadata.audio.duration_seconds:
                minutes = int(metadata.audio.duration_seconds // 60)
                seconds = int(metadata.audio.duration_seconds % 60)
                lines.append(f"  Duration: {minutes}:{seconds:02d}")
            if metadata.audio.bit_rate:
                lines.append(f"  Bit Rate: {metadata.audio.bit_rate} bps")
            if metadata.audio.sample_rate:
                lines.append(f"  Sample Rate: {metadata.audio.sample_rate} Hz")
            if metadata.audio.channels:
                lines.append(f"  Channels: {metadata.audio.channels}")
            if metadata.audio.bit_depth:
                lines.append(f"  Bit Depth: {metadata.audio.bit_depth}")
            if metadata.audio.codec:
                lines.append(f"  Codec: {metadata.audio.codec}")
            if metadata.audio.artist:
                lines.append(f"  Artist: {metadata.audio.artist}")
            if metadata.audio.album:
                lines.append(f"  Album: {metadata.audio.album}")
            if metadata.audio.genre:
                lines.append(f"  Genre: {metadata.audio.genre}")
            if metadata.audio.track_number:
                lines.append(f"  Track Number: {metadata.audio.track_number}")
            if metadata.audio.year:
                lines.append(f"  Year: {metadata.audio.year}")
            if metadata.audio.lyrics:
                lines.append(f"  Lyrics: {metadata.audio.lyrics}")
        
        if metadata.video:
            lines.append("")
            lines.append("VIDEO DETAILS")
            lines.append("-" * 60)
            if metadata.video.duration_seconds:
                minutes = int(metadata.video.duration_seconds // 60)
                seconds = int(metadata.video.duration_seconds % 60)
                hours = minutes // 60
                minutes = minutes % 60
                if hours > 0:
                    lines.append(f"  Duration: {hours}:{minutes:02d}:{seconds:02d}")
                else:
                    lines.append(f"  Duration: {minutes}:{seconds:02d}")
            if metadata.video.width and metadata.video.height:
                lines.append(f"  Resolution: {metadata.video.width} x {metadata.video.height}")
            if metadata.video.frame_rate:
                lines.append(f"  Frame Rate: {metadata.video.frame_rate:.2f} fps")
            if metadata.video.bit_rate:
                lines.append(f"  Bit Rate: {metadata.video.bit_rate} bps")
            if metadata.video.codec:
                lines.append(f"  Codec: {metadata.video.codec}")
            if metadata.video.aspect_ratio:
                lines.append(f"  Aspect Ratio: {metadata.video.aspect_ratio}")
            if metadata.video.color_space:
                lines.append(f"  Color Space: {metadata.video.color_space}")
            if metadata.video.audio_codec:
                lines.append(f"  Audio Codec: {metadata.video.audio_codec}")
            if metadata.video.audio_channels:
                lines.append(f"  Audio Channels: {metadata.video.audio_channels}")
            if metadata.video.audio_sample_rate:
                lines.append(f"  Audio Sample Rate: {metadata.video.audio_sample_rate} Hz")
        
        if metadata.raw_metadata:
            lines.append("")
            lines.append("ADDITIONAL METADATA")
            lines.append("-" * 60)
            for key, value in metadata.raw_metadata.items():
                if isinstance(value, (dict, list)):
                    lines.append(f"  {key}: {str(value)[:100]}...")
                else:
                    lines.append(f"  {key}: {value}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
