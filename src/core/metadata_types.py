from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum


class FileCategory(Enum):
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    EXECUTABLE = "executable"
    ARCHIVE = "archive"
    OTHER = "other"


@dataclass
class BasicMetadata:
    file_name: str
    file_path: str
    file_size: int
    file_extension: str
    mime_type: str
    creation_time: Optional[datetime] = None
    modification_time: Optional[datetime] = None
    access_time: Optional[datetime] = None
    file_category: FileCategory = FileCategory.OTHER


@dataclass
class ImageMetadata:
    width: Optional[int] = None
    height: Optional[int] = None
    bits_per_pixel: Optional[int] = None
    color_mode: Optional[str] = None
    compression: Optional[str] = None
    dpi: Optional[tuple] = None
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    exposure_time: Optional[str] = None
    aperture: Optional[float] = None
    iso_speed: Optional[int] = None
    focal_length: Optional[float] = None
    gps_latitude: Optional[float] = None
    gps_longitude: Optional[float] = None
    gps_altitude: Optional[float] = None


@dataclass
class DocumentMetadata:
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    character_count: Optional[int] = None
    creation_date: Optional[datetime] = None
    last_modified_date: Optional[datetime] = None
    application_name: Optional[str] = None
    application_version: Optional[str] = None


@dataclass
class AudioMetadata:
    duration_seconds: Optional[float] = None
    bit_rate: Optional[int] = None
    sample_rate: Optional[int] = None
    channels: Optional[int] = None
    bit_depth: Optional[int] = None
    codec: Optional[str] = None
    artist: Optional[str] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    track_number: Optional[int] = None
    year: Optional[int] = None
    lyrics: Optional[str] = None


@dataclass
class VideoMetadata:
    duration_seconds: Optional[float] = None
    width: Optional[int] = None
    height: Optional[int] = None
    frame_rate: Optional[float] = None
    bit_rate: Optional[int] = None
    codec: Optional[str] = None
    aspect_ratio: Optional[str] = None
    color_space: Optional[str] = None
    audio_codec: Optional[str] = None
    audio_channels: Optional[int] = None
    audio_sample_rate: Optional[int] = None


@dataclass
class FileMetadata:
    basic: BasicMetadata
    image: Optional[ImageMetadata] = None
    document: Optional[DocumentMetadata] = None
    audio: Optional[AudioMetadata] = None
    video: Optional[VideoMetadata] = None
    raw_metadata: Dict[str, Any] = field(default_factory=dict)
