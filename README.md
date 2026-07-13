# File-Metadata-Extractor-

A professional Python tool that extracts comprehensive metadata from images, documents, audio, and video files with multiple output formats.

## Features

- **Images** (JPEG, PNG, GIF, BMP, TIFF, WebP): dimensions, color mode, DPI, and EXIF data — camera make/model, exposure, aperture, ISO, focal length, and GPS coordinates.
- **Documents** (PDF, DOCX, XLSX, PPTX, TXT): author, title, subject, keywords, page/word/character counts, creation and modification dates, and authoring application.
- **Audio** (MP3, FLAC, WAV, AAC, OGG, M4A, and more via mutagen): duration, bitrate, sample rate, channels, codec, and tags (artist, album, genre, track, year).
- **Video** (MP4, AVI, MKV, MOV, WebM, and more via ffprobe): duration, resolution, frame rate, bitrate, codec, aspect ratio, and audio stream info.
- Console or JSON output, optionally written to a file.

## Installation (Kali / Debian)

```bash
sudo apt update
sudo apt install libmagic1 ffmpeg   # system dependencies
git clone https://github.com/Kaintura-Priyanshu/File-Metadata-Extractor-.git
cd File-Metadata-Extractor-
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

`libmagic1` is used for accurate MIME-type detection, and `ffmpeg` provides `ffprobe`, used for video metadata. Both are optional — the tool degrades gracefully without them (falling back to extension-based MIME guessing, and to basic file info for video), but installing them gives more accurate results.

To install as a command-line tool (`metadata-extractor`):

```bash
pip install -e .
```

## Usage

```bash
python3 main.py <file_path> [-f console|json] [-o output_file] [-v]
```

Examples:

```bash
# Console output (default)
python3 main.py photo.jpg

# JSON output
python3 main.py document.pdf -f json

# Save output to a file
python3 main.py video.mp4 -f json -o video_metadata.json

# Verbose mode (prints a traceback on error)
python3 main.py song.mp3 -v
```

If installed via `pip install -e .`:

```bash
metadata-extractor photo.jpg -f json
```

## Project structure

```
File-Metadata-Extractor-/
├── main.py                     # CLI entry point
├── setup.py
├── requirements.txt
├── src/
│   ├── core/
│   │   ├── extractor.py        # Orchestrates parsing + basic file stats
│   │   └── metadata_types.py   # Dataclasses for each metadata category
│   ├── parsers/
│   │   ├── base_parser.py
│   │   ├── image_parser.py
│   │   ├── document_parser.py
│   │   ├── audio_parser.py
│   │   └── video_parser.py
│   ├── output/
│   │   ├── console_formatter.py
│   │   └── json_formatter.py
│   └── utils/
│       └── file_utils.py
└── tests/
    ├── test_extractor.py
    └── test_parsers.py
```

## Running tests

```bash
python3 -m unittest discover tests
```


