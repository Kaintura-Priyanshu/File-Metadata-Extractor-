import json
from datetime import datetime
from typing import Dict, Any

from src.core.metadata_types import FileMetadata


class JSONFormatter:
    @staticmethod
    def format(metadata: FileMetadata, pretty: bool = True) -> str:
        data = JSONFormatter._to_dict(metadata)
        
        if pretty:
            return json.dumps(data, indent=2, default=str, ensure_ascii=False)
        else:
            return json.dumps(data, default=str, ensure_ascii=False)
    
    @staticmethod
    def _to_dict(metadata: FileMetadata) -> Dict[str, Any]:
        result = {}
        
        if metadata.basic:
            result['basic'] = {
                'file_name': metadata.basic.file_name,
                'file_path': metadata.basic.file_path,
                'file_size': metadata.basic.file_size,
                'file_size_formatted': metadata.basic.file_size,
                'file_extension': metadata.basic.file_extension,
                'mime_type': metadata.basic.mime_type,
                'file_category': metadata.basic.file_category.value if metadata.basic.file_category else None,
                'creation_time': metadata.basic.creation_time,
                'modification_time': metadata.basic.modification_time,
                'access_time': metadata.basic.access_time
            }
        
        if metadata.image:
            result['image'] = {
                'width': metadata.image.width,
                'height': metadata.image.height,
                'bits_per_pixel': metadata.image.bits_per_pixel,
                'color_mode': metadata.image.color_mode,
                'compression': metadata.image.compression,
                'dpi': metadata.image.dpi,
                'camera_make': metadata.image.camera_make,
                'camera_model': metadata.image.camera_model,
                'exposure_time': metadata.image.exposure_time,
                'aperture': metadata.image.aperture,
                'iso_speed': metadata.image.iso_speed,
                'focal_length': metadata.image.focal_length,
                'gps_latitude': metadata.image.gps_latitude,
                'gps_longitude': metadata.image.gps_longitude,
                'gps_altitude': metadata.image.gps_altitude
            }
        
        if metadata.document:
            result['document'] = {
                'author': metadata.document.author,
                'title': metadata.document.title,
                'subject': metadata.document.subject,
                'keywords': metadata.document.keywords,
                'page_count': metadata.document.page_count,
                'word_count': metadata.document.word_count,
                'character_count': metadata.document.character_count,
                'creation_date': metadata.document.creation_date,
                'last_modified_date': metadata.document.last_modified_date,
                'application_name': metadata.document.application_name,
                'application_version': metadata.document.application_version
            }
        
        if metadata.audio:
            result['audio'] = {
                'duration_seconds': metadata.audio.duration_seconds,
                'bit_rate': metadata.audio.bit_rate,
                'sample_rate': metadata.audio.sample_rate,
                'channels': metadata.audio.channels,
                'bit_depth': metadata.audio.bit_depth,
                'codec': metadata.audio.codec,
                'artist': metadata.audio.artist,
                'album': metadata.audio.album,
                'genre': metadata.audio.genre,
                'track_number': metadata.audio.track_number,
                'year': metadata.audio.year,
                'lyrics': metadata.audio.lyrics
            }
        
        if metadata.video:
            result['video'] = {
                'duration_seconds': metadata.video.duration_seconds,
                'width': metadata.video.width,
                'height': metadata.video.height,
                'frame_rate': metadata.video.frame_rate,
                'bit_rate': metadata.video.bit_rate,
                'codec': metadata.video.codec,
                'aspect_ratio': metadata.video.aspect_ratio,
                'color_space': metadata.video.color_space,
                'audio_codec': metadata.video.audio_codec,
                'audio_channels': metadata.video.audio_channels,
                'audio_sample_rate': metadata.video.audio_sample_rate
            }
        
        if metadata.raw_metadata:
            result['raw_metadata'] = metadata.raw_metadata
        
        return result
