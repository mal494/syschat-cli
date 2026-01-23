import unittest
import tempfile
import os
import sys
from pathlib import Path

# Adjust path to import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from analyzer import get_file_metadata, read_file_safe

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_get_file_metadata_exists(self):
        f = self.dir_path / "test.txt"
        f.write_text("Hello", encoding='utf-8')
        meta = get_file_metadata(str(f))
        self.assertEqual(meta["filename"], "test.txt")
        self.assertEqual(meta["size_bytes"], 5)
        self.assertNotIn("error", meta)
        self.assertFalse(meta.get("is_log_file", True)) # Should be False for .txt

    def test_get_file_metadata_log_file(self):
        f = self.dir_path / "test.log"
        f.write_text("Log content", encoding='utf-8')
        meta = get_file_metadata(str(f))
        self.assertTrue(meta.get("is_log_file", False))

    def test_get_file_metadata_not_found(self):
        meta = get_file_metadata(str(self.dir_path / "missing.txt"))
        self.assertIn("error", meta)
        self.assertIn("not found", meta["error"])

    def test_read_file_safe_valid(self):
        f = self.dir_path / "valid.txt"
        content = "Safe content"
        f.write_text(content, encoding='utf-8')
        success, read_content = read_file_safe(str(f), len(content))
        self.assertTrue(success)
        self.assertEqual(read_content, content)

    def test_read_file_safe_too_large(self):
        f = self.dir_path / "large.txt"
        # We simulate passing a large size, even if file on disk is small, 
        # because the function relies on the passed size argument.
        success, msg = read_file_safe(str(f), 10001)
        self.assertFalse(success)
        self.assertIn("too large", msg)

    def test_read_file_safe_bad_extension(self):
        f = self.dir_path / "bad.exe"
        f.write_text("binary", encoding='utf-8')
        success, msg = read_file_safe(str(f), 6)
        self.assertFalse(success)
        self.assertIn("File type likely binary", msg)

    def test_read_file_safe_log_parsing(self):
        f = self.dir_path / "system.log"
        content = """INFO: Start
ERROR: Bad thing happened
INFO: Running
WARN: Be careful
"""
        f.write_text(content, encoding='utf-8')
        success, read_content = read_file_safe(str(f), len(content))
        
        self.assertTrue(success)
        self.assertIn("Relevant log entries found:", read_content)
        self.assertIn("ERROR: Bad thing happened", read_content)
        self.assertIn("WARN: Be careful", read_content)
        self.assertNotIn("INFO: Start", read_content)

if __name__ == '__main__':
    unittest.main()
