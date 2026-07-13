from pathlib import Path
import mimetypes

from src.core.metadata_types import FileCategory

try:
    import magic
    _HAS_MAGIC = True
except ImportError:
    # python-magic requires the system libmagic library. On Debian/Kali:
    #   sudo apt install libmagic1
    # If it's unavailable we fall back to Python's built-in mimetypes
    # module, which is less accurate (extension-based) but keeps the
    # tool working instead of crashing at import time.
    _HAS_MAGIC = False


def get_mime_type(file_path: Path) -> str:
    if _HAS_MAGIC:
        try:
            mime = magic.from_file(str(file_path), mime=True)
            if mime:
                return mime
        except Exception:
            pass

    guessed_type, _ = mimetypes.guess_type(str(file_path))
    return guessed_type or "application/octet-stream"


def get_file_category(file_extension: str, mime_type: str) -> FileCategory:
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif',
                         '.webp', '.svg', '.ico', '.psd', '.raw'}
    document_extensions = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt',
                            '.pptx', '.txt', '.rtf', '.odt', '.ods', '.odp', '.csv'}
    audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a',
                         '.aiff', '.alac'}
    video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', '.webm',
                         '.m4v', '.mpeg', '.mpg', '.3gp'}
    executable_extensions = {'.exe', '.msi', '.bat', '.cmd', '.sh', '.py', '.jar', '.elf'}
    archive_extensions = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz'}

    if file_extension in image_extensions:
        return FileCategory.IMAGE
    elif file_extension in document_extensions:
        return FileCategory.DOCUMENT
    elif file_extension in audio_extensions:
        return FileCategory.AUDIO
    elif file_extension in video_extensions:
        return FileCategory.VIDEO
    elif file_extension in executable_extensions:
        return FileCategory.EXECUTABLE
    elif file_extension in archive_extensions:
        return FileCategory.ARCHIVE

    if mime_type:
        if mime_type.startswith('image/'):
            return FileCategory.IMAGE
        elif mime_type.startswith('audio/'):
            return FileCategory.AUDIO
        elif mime_type.startswith('video/'):
            return FileCategory.VIDEO
        elif 'pdf' in mime_type:
            return FileCategory.DOCUMENT
        elif mime_type.startswith('text/'):
            return FileCategory.DOCUMENT
        elif 'msword' in mime_type or 'officedocument' in mime_type or 'opendocument' in mime_type:
            return FileCategory.DOCUMENT
        elif 'zip' in mime_type or 'compressed' in mime_type or 'archive' in mime_type:
            return FileCategory.ARCHIVE
        elif 'executable' in mime_type:
            return FileCategory.EXECUTABLE

    return FileCategory.OTHER


def format_file_size(size_bytes: int) -> str:
    if size_bytes is None:
        return "unknown"
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def is_valid_file_path(file_path: str) -> bool:
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False
