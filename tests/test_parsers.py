import unittest
import tempfile
import os
import shutil
from pathlib import Path
from PIL import Image
import json

from src.parsers.image_parser import ImageParser
from src.parsers.document_parser import DocumentParser
from src.parsers.audio_parser import AudioParser
from src.parsers.video_parser import VideoParser


class TestImageParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = ImageParser()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_parse_jpeg_image(self):
        file_path = Path(self.test_dir) / "test.jpg"
        
        img = Image.new('RGB', (800, 600), color='red')
        img.save(file_path, 'JPEG', quality=95)
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertEqual(metadata.width, 800)
        self.assertEqual(metadata.height, 600)
        self.assertEqual(metadata.color_mode, 'RGB')
    
    def test_parse_png_image(self):
        file_path = Path(self.test_dir) / "test.png"
        
        img = Image.new('RGBA', (1024, 768), color=(255, 0, 0, 255))
        img.save(file_path, 'PNG')
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertEqual(metadata.width, 1024)
        self.assertEqual(metadata.height, 768)
        self.assertEqual(metadata.color_mode, 'RGBA')
    
    def test_parse_gif_image(self):
        file_path = Path(self.test_dir) / "test.gif"
        
        img = Image.new('P', (200, 150), color=1)
        img.save(file_path, 'GIF')
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertEqual(metadata.width, 200)
        self.assertEqual(metadata.height, 150)
    
    def test_parse_non_existent_image(self):
        file_path = Path(self.test_dir) / "nonexistent.jpg"
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.width, None)
        self.assertEqual(metadata.height, None)


class TestDocumentParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = DocumentParser()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_parse_text_file(self):
        file_path = Path(self.test_dir) / "test.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("This is a test document with multiple words for testing word count.")
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.word_count, 14)
        self.assertGreater(metadata.character_count, 0)
        self.assertIsNotNone(metadata.page_count)
    
    def test_parse_empty_text_file(self):
        file_path = Path(self.test_dir) / "empty.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertEqual(metadata.word_count, 0)
        self.assertEqual(metadata.character_count, 0)
    
    def test_parse_text_file_with_special_characters(self):
        file_path = Path(self.test_dir) / "special.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Hello World! @#$%^&*() 12345")
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata.word_count)
        self.assertGreater(metadata.word_count, 0)
    
    def test_parse_unknown_document_type(self):
        file_path = Path(self.test_dir) / "test.xyz"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Unknown file type test")
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
    
    def test_parse_pdf_file_missing_library(self):
        file_path = Path(self.test_dir) / "test.pdf"
        
        with open(file_path, 'w') as f:
            f.write("%PDF-1.4\n%Test PDF")
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)


class TestAudioParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = AudioParser()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_parse_wav_file(self):
        file_path = Path(self.test_dir) / "test.wav"
        
        import wave
        import struct
        
        with wave.open(str(file_path), 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            
            data = b''
            for i in range(1000):
                sample = int(32767 * (i / 1000))
                data += struct.pack('<h', sample)
            
            wav_file.writeframes(data)
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
        self.assertIsNotNone(metadata.duration_seconds)
        self.assertIsNotNone(metadata.sample_rate)
        self.assertEqual(metadata.channels, 1)
    
    def test_parse_non_audio_file(self):
        file_path = Path(self.test_dir) / "test.txt"
        
        with open(file_path, 'w') as f:
            f.write("This is not an audio file")
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.duration_seconds, None)
        self.assertEqual(metadata.sample_rate, None)
    
    def test_parse_mp3_file_metadata(self):
        file_path = Path(self.test_dir) / "test.mp3"
        
        with open(file_path, 'wb') as f:
            f.write(b'\xff\xfb\x90\x64')
            f.write(b'\x00' * 100)
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
    
    def test_parse_corrupted_audio_file(self):
        file_path = Path(self.test_dir) / "corrupt.mp3"
        
        with open(file_path, 'wb') as f:
            f.write(b'\x00\x00\x00\x00')
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)


class TestVideoParser(unittest.TestCase):
    
    def setUp(self):
        self.parser = VideoParser()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_parse_video_file_without_ffprobe(self):
        file_path = Path(self.test_dir) / "test.mp4"
        
        with open(file_path, 'wb') as f:
            f.write(b'\x00\x00\x00\x18ftypisom')
            f.write(b'\x00' * 1000)
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
    
    def test_parse_non_video_file(self):
        file_path = Path(self.test_dir) / "test.txt"
        
        with open(file_path, 'w') as f:
            f.write("This is not a video file")
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
    
    def test_parse_video_file_basic_info(self):
        file_path = Path(self.test_dir) / "video.mkv"
        
        with open(file_path, 'wb') as f:
            f.write(b'\x1a\x45\xdf\xa3\x93\x42\x82\x88')
            f.write(b'\x00' * 100)
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
    
    def test_parse_corrupted_video_file(self):
        file_path = Path(self.test_dir) / "corrupt.avi"
        
        with open(file_path, 'wb') as f:
            f.write(b'\x00' * 100)
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)


class TestParserIntegration(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.image_parser = ImageParser()
        self.document_parser = DocumentParser()
        self.audio_parser = AudioParser()
        self.video_parser = VideoParser()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_multiple_parsers_same_file(self):
        file_path = Path(self.test_dir) / "test.jpg"
        
        img = Image.new('RGB', (640, 480), color='blue')
        img.save(file_path, 'JPEG')
        
        image_metadata, _ = self.image_parser.parse(file_path)
        doc_metadata, _ = self.document_parser.parse(file_path)
        
        self.assertEqual(image_metadata.width, 640)
        self.assertEqual(image_metadata.height, 480)
        self.assertIsNotNone(doc_metadata)
    
    def test_large_image_parsing(self):
        file_path = Path(self.test_dir) / "large.jpg"
        
        img = Image.new('RGB', (5000, 4000), color='green')
        img.save(file_path, 'JPEG', quality=85)
        
        metadata, raw = self.image_parser.parse(file_path)
        
        self.assertEqual(metadata.width, 5000)
        self.assertEqual(metadata.height, 4000)
    
    def test_file_with_extended_attributes(self):
        file_path = Path(self.test_dir) / "attributes.txt"
        
        with open(file_path, 'w') as f:
            f.write("Content with extended attributes test")
        
        os.chmod(file_path, 0o755)
        
        metadata, raw = self.document_parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
        self.assertGreater(metadata.word_count, 0)
    
    def test_unicode_filename_handling(self):
        file_path = Path(self.test_dir) / "测试文件.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Unicode content for testing")
        
        metadata, raw = self.document_parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
        self.assertGreater(metadata.word_count, 0)


class TestParserErrorHandling(unittest.TestCase):
    
    def setUp(self):
        self.parser = ImageParser()
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        shutil.rmtree(self.test_dir)
    
    def test_parse_empty_file(self):
        file_path = Path(self.test_dir) / "empty.jpg"
        
        with open(file_path, 'wb') as f:
            pass
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata.width, None)
    
    def test_parse_directory_as_file(self):
        dir_path = Path(self.test_dir) / "test_dir"
        os.makedirs(dir_path)
        
        metadata, raw = self.parser.parse(dir_path)
        
        self.assertIsNotNone(metadata)
    
    def test_parse_file_without_permission(self):
        file_path = Path(self.test_dir) / "no_permission.txt"
        
        with open(file_path, 'w') as f:
            f.write("No permission test")
        
        os.chmod(file_path, 0o000)
        
        metadata, raw = self.parser.parse(file_path)
        
        self.assertIsNotNone(metadata)
        
        os.chmod(file_path, 0o644)
    
    def test_parse_file_with_unicode_content(self):
        file_path = Path(self.test_dir) / "unicode.txt"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("Hello 世界 🌍 🚀")
        
        metadata, raw = self.document_parser = DocumentParser()
        result, _ = self.document_parser.parse(file_path)
        
        self.assertIsNotNone(result)
        self.assertGreater(result.word_count, 0)


if __name__ == '__main__':
    unittest.main()
