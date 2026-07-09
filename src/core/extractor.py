import os
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Union

from src.core.metadata_types import (
    FileMetadata, BasicMetadata, FileCategory,
    ImageMetadata, DocumentMetadata, AudioMetadata, VideoMetadata
)
from src.parsers.image_parser import ImageParser
from src.parsers.document_parser import DocumentParser
from src.parsers.audio_parser import AudioParser
from src.parsers.video_parser import VideoParser
from src.utils.file_utils import get_mime_type, get_file_category


class FileMetadataExtractor:
    def __init__(self):
        self.image_parser = ImageParser()
        self.document_parser = DocumentParser()
        self.audio_parser = AudioParser()
        self.video_parser = VideoParser()
    
    def extract(self, file_path: Union[str, Path]) -> FileMetadata:
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        basic_metadata = self._extract_basic_metadata(file_path)
        category = basic_metadata.file_category
        
        image_metadata = None
        document_metadata = None
        audio_metadata = None
        video_metadata = None
        raw_metadata = {}
        
        if category == FileCategory.IMAGE:
            image_metadata, raw_metadata = self.image_parser.parse(file_path)
        elif category == FileCategory.DOCUMENT:
            document_metadata, raw_metadata = self.document_parser.parse(file_path)
        elif category == FileCategory.AUDIO:
            audio_metadata, raw_metadata = self.audio_parser.parse(file_path)
        elif category == FileCategory.VIDEO:
            video_metadata, raw_metadata = self.video_parser.parse(file_path)
        
        return FileMetadata(
            basic=basic_metadata,
            image=image_metadata,
            document=document_metadata,
            audio=audio_metadata,
            video=video_metadata,
            raw_metadata=raw_metadata
        )
    
    def _extract_basic_metadata(self, file_path: Path) -> BasicMetadata:
        stat_info = file_path.stat()
        
        file_name = file_path.name
        file_extension = file_path.suffix.lower()
        file_size = stat_info.st_size
        mime_type = get_mime_type(file_path)
        file_category = get_file_category(file_extension, mime_type)
        
        creation_time = None
        modification_time = None
        access_time = None
        
        try:
            if hasattr(stat_info, 'st_ctime'):
                creation_time = datetime.fromtimestamp(stat_info.st_ctime)
        except (OSError, ValueError):
            pass
        
        try:
            if hasattr(stat_info, 'st_mtime'):
                modification_time = datetime.fromtimestamp(stat_info.st_mtime)
        except (OSError, ValueError):
            pass
        
        try:
            if hasattr(stat_info, 'st_atime'):
                access_time = datetime.fromtimestamp(stat_info.st_atime)
        except (OSError, ValueError):
            pass
        
        return BasicMetadata(
            file_name=file_name,
            file_path=str(file_path),
            file_size=file_size,
            file_extension=file_extension,
            mime_type=mime_type,
            creation_time=creation_time,
            modification_time=modification_time,
            access_time=access_time,
            file_category=file_category
        )
