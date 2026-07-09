import unittest
import tempfile
import os
from pathlib import Path

from src.core.extractor import FileMetadataExtractor
from src.core.metadata_types import FileCategory


class TestFileMetadataExtractor(unittest.TestCase):
    
    def setUp(self):
        self.extractor = FileMetadataExtractor()
    
    def test_extract_text_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test file with some content.")
            file_path = f.name
        
        try:
            metadata = self.extractor.extract(file_path)
            self.assertEqual(metadata.basic.file_category, FileCategory.DOCUMENT)
            self.assertIsNotNone(metadata.document)
            self.assertEqual(metadata.document.word_count, 8)
        finally:
            os.unlink(file_path)
    
    def test_extract_nonexistent_file(self):
        with self.assertRaises(FileNotFoundError):
            self.extractor.extract("nonexistent_file.txt")
    
    def test_extract_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                self.extractor.extract(temp_dir)


if __name__ == '__main__':
    unittest.main()
