from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

from src.parsers.base_parser import BaseParser
from src.core.metadata_types import ImageMetadata

# Exif/GPS sub-IFD pointer tags (public API replacement for the old
# private ``_getexif`` method, which only worked for JPEG/TIFF).
_EXIF_IFD_TAG = 0x8769
_GPS_IFD_TAG = 0x8825


class ImageParser(BaseParser):
    """Extract dimension, color, and EXIF/GPS metadata from image files."""

    def parse(self, file_path: Path) -> Tuple[Optional[ImageMetadata], Dict[str, Any]]:
        metadata = ImageMetadata()
        raw_metadata: Dict[str, Any] = {}

        try:
            with Image.open(file_path) as img:
                metadata.width = img.width
                metadata.height = img.height
                metadata.color_mode = img.mode

                info = getattr(img, "info", {}) or {}
                dpi = info.get("dpi")
                if isinstance(dpi, tuple) and len(dpi) == 2:
                    metadata.dpi = dpi

                compression = info.get("compression")
                if compression:
                    metadata.compression = str(compression)

                raw_metadata = self._extract_exif(img)
                if raw_metadata:
                    self._apply_exif_to_metadata(metadata, raw_metadata)

        except Exception as e:
            print(f"Error parsing image metadata: {e}")

        return metadata, raw_metadata

    def _extract_exif(self, img: "Image.Image") -> Dict[str, Any]:
        """Read EXIF data using Pillow's public getexif()/get_ifd() API.

        Works across JPEG, TIFF, PNG, and WebP, unlike the old private
        ``_getexif()`` method which only supported JPEG/TIFF.
        """
        parsed: Dict[str, Any] = {}

        try:
            exif = img.getexif()
        except Exception:
            return parsed

        if not exif:
            return parsed

        for tag_id, value in exif.items():
            parsed[TAGS.get(tag_id, tag_id)] = value

        # The "real" EXIF fields (camera make/model, exposure, etc.) live
        # in a sub-IFD pointed to by tag 0x8769, not the top-level dict.
        try:
            exif_ifd = exif.get_ifd(_EXIF_IFD_TAG) or {}
        except Exception:
            exif_ifd = {}

        for tag_id, value in exif_ifd.items():
            parsed[TAGS.get(tag_id, tag_id)] = value

        # GPS data lives in its own sub-IFD (tag 0x8825).
        try:
            gps_ifd = exif.get_ifd(_GPS_IFD_TAG) or {}
        except Exception:
            gps_ifd = {}

        if gps_ifd:
            parsed["GPSInfo"] = {
                GPSTAGS.get(tag_id, tag_id): value for tag_id, value in gps_ifd.items()
            }

        return parsed

    def _apply_exif_to_metadata(self, metadata: ImageMetadata, exif_data: Dict[str, Any]) -> None:
        if 'Make' in exif_data:
            metadata.camera_make = str(exif_data['Make']).strip('\x00').strip()

        if 'Model' in exif_data:
            metadata.camera_model = str(exif_data['Model']).strip('\x00').strip()

        if 'ExposureTime' in exif_data:
            frac = self._as_fraction(exif_data['ExposureTime'])
            if frac is not None:
                num, den = frac
                metadata.exposure_time = f"{num}/{den}" if den else str(num)
            else:
                metadata.exposure_time = str(exif_data['ExposureTime'])

        if 'FNumber' in exif_data:
            frac = self._as_fraction(exif_data['FNumber'])
            if frac is not None and frac[1]:
                metadata.aperture = round(frac[0] / frac[1], 1)
            else:
                metadata.aperture = self._convert_to_float(exif_data['FNumber'])

        if 'ISOSpeedRatings' in exif_data:
            metadata.iso_speed = self._convert_to_int(exif_data['ISOSpeedRatings'])
        elif 'PhotographicSensitivity' in exif_data:
            metadata.iso_speed = self._convert_to_int(exif_data['PhotographicSensitivity'])

        if 'FocalLength' in exif_data:
            frac = self._as_fraction(exif_data['FocalLength'])
            if frac is not None and frac[1]:
                metadata.focal_length = round(frac[0] / frac[1], 1)
            else:
                metadata.focal_length = self._convert_to_float(exif_data['FocalLength'])

        if 'BitsPerSample' in exif_data:
            bits = exif_data['BitsPerSample']
            if isinstance(bits, (tuple, list)) and bits:
                metadata.bits_per_pixel = self._convert_to_int(bits[0])
            else:
                metadata.bits_per_pixel = self._convert_to_int(bits)

        gps_info = exif_data.get('GPSInfo')
        if gps_info:
            if 'GPSLatitude' in gps_info and 'GPSLatitudeRef' in gps_info:
                metadata.gps_latitude = self._convert_gps_to_decimal(
                    gps_info['GPSLatitude'], gps_info['GPSLatitudeRef']
                )

            if 'GPSLongitude' in gps_info and 'GPSLongitudeRef' in gps_info:
                metadata.gps_longitude = self._convert_gps_to_decimal(
                    gps_info['GPSLongitude'], gps_info['GPSLongitudeRef']
                )

            if 'GPSAltitude' in gps_info:
                frac = self._as_fraction(gps_info['GPSAltitude'])
                if frac is not None and frac[1]:
                    metadata.gps_altitude = frac[0] / frac[1]
                else:
                    metadata.gps_altitude = self._convert_to_float(gps_info['GPSAltitude'])

    @staticmethod
    def _as_fraction(value: Any) -> Optional[Tuple[float, float]]:
        """Normalize an EXIF rational value (tuple or Pillow IFDRational) to (num, den)."""
        if isinstance(value, tuple) and len(value) == 2:
            return value[0], value[1]
        if hasattr(value, "numerator") and hasattr(value, "denominator"):
            return value.numerator, value.denominator
        return None

    def _convert_gps_to_decimal(self, gps_coords, ref: str) -> Optional[float]:
        if not isinstance(gps_coords, (tuple, list)) or len(gps_coords) != 3:
            return None

        degrees, minutes, seconds = gps_coords

        deg = self._convert_to_float(degrees, 0)
        min_ = self._convert_to_float(minutes, 0)
        sec = self._convert_to_float(seconds, 0)

        decimal = deg + (min_ / 60.0) + (sec / 3600.0)

        if ref in ('S', 'W'):
            decimal = -decimal

        return decimal
