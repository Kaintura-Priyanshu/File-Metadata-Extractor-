from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from src.parsers.base_parser import BaseParser
from src.core.metadata_types import ImageMetadata


class ImageParser(BaseParser):
    def parse(self, file_path: Path) -> Tuple[Optional[ImageMetadata], Dict[str, Any]]:
        metadata = ImageMetadata()
        raw_metadata = {}
        
        try:
            with Image.open(file_path) as img:
                metadata.width = img.width
                metadata.height = img.height
                metadata.color_mode = img.mode
                
                if hasattr(img, 'info'):
                    info = img.info
                    if 'dpi' in info:
                        dpi = info['dpi']
                        if isinstance(dpi, tuple) and len(dpi) == 2:
                            metadata.dpi = dpi
                    
                    if 'compression' in info:
                        metadata.compression = info['compression']
                
                exif_data = img._getexif()
                if exif_data:
                    raw_metadata = self._parse_exif(exif_data)
                    self._apply_exif_to_metadata(metadata, raw_metadata)
        
        except Exception as e:
            print(f"Error parsing image metadata: {e}")
        
        return metadata, raw_metadata
    
    def _parse_exif(self, exif_data: Dict) -> Dict[str, Any]:
        parsed_exif = {}
        
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            
            if tag_name == 'GPSInfo':
                gps_data = {}
                for gps_tag_id, gps_value in value.items():
                    gps_tag_name = GPSTAGS.get(gps_tag_id, gps_tag_id)
                    gps_data[gps_tag_name] = gps_value
                parsed_exif[tag_name] = gps_data
            else:
                parsed_exif[tag_name] = value
        
        return parsed_exif
    
    def _apply_exif_to_metadata(self, metadata: ImageMetadata, exif_data: Dict[str, Any]) -> None:
        if 'Make' in exif_data:
            metadata.camera_make = str(exif_data['Make'])
        
        if 'Model' in exif_data:
            metadata.camera_model = str(exif_data['Model'])
        
        if 'ExposureTime' in exif_data:
            exposure = exif_data['ExposureTime']
            if isinstance(exposure, tuple) and len(exposure) == 2:
                if exposure[1] != 0:
                    metadata.exposure_time = f"{exposure[0]}/{exposure[1]}"
            else:
                metadata.exposure_time = str(exposure)
        
        if 'FNumber' in exif_data:
            f_number = exif_data['FNumber']
            if isinstance(f_number, tuple) and len(f_number) == 2:
                if f_number[1] != 0:
                    metadata.aperture = round(f_number[0] / f_number[1], 1)
            else:
                metadata.aperture = self._convert_to_float(f_number)
        
        if 'ISOSpeedRatings' in exif_data:
            metadata.iso_speed = self._convert_to_int(exif_data['ISOSpeedRatings'])
        
        if 'FocalLength' in exif_data:
            focal = exif_data['FocalLength']
            if isinstance(focal, tuple) and len(focal) == 2:
                if focal[1] != 0:
                    metadata.focal_length = round(focal[0] / focal[1], 1)
            else:
                metadata.focal_length = self._convert_to_float(focal)
        
        if 'BitsPerSample' in exif_data:
            bits = exif_data['BitsPerSample']
            if isinstance(bits, tuple):
                metadata.bits_per_pixel = bits[0]
            else:
                metadata.bits_per_pixel = self._convert_to_int(bits)
        
        if 'GPSInfo' in exif_data:
            gps_info = exif_data['GPSInfo']
            if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
                lat = gps_info['GPSLatitude']
                lat_ref = gps_info['GPSLatitudeRef']
                metadata.gps_latitude = self._convert_gps_to_decimal(lat, lat_ref)
            
            if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                lon = gps_info['GPSLongitude']
                lon_ref = gps_info['GPSLongitudeRef']
                metadata.gps_longitude = self._convert_gps_to_decimal(lon, lon_ref)
            
            if 'GPSAltitude' in gps_info:
                alt = gps_info['GPSAltitude']
                if isinstance(alt, tuple) and len(alt) == 2:
                    if alt[1] != 0:
                        metadata.gps_altitude = alt[0] / alt[1]
                else:
                    metadata.gps_altitude = self._convert_to_float(alt)
    
    def _convert_gps_to_decimal(self, gps_coords: tuple, ref: str) -> float:
        if not isinstance(gps_coords, tuple) or len(gps_coords) != 3:
            return None
        
        degrees, minutes, seconds = gps_coords
        
        deg = self._convert_to_float(degrees, 0)
        min_ = self._convert_to_float(minutes, 0)
        sec = self._convert_to_float(seconds, 0)
        
        decimal = deg + (min_ / 60.0) + (sec / 3600.0)
        
        if ref in ['S', 'W']:
            decimal = -decimal
        
        return decimal
