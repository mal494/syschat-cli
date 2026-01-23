import unittest
import tempfile
import os
import sys
from pathlib import Path

# Adjust path to import src
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from log_parser import parse_log_file

class TestLogParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.dir_path = Path(self.test_dir.name)

    def tearDown(self):
        self.test_dir.cleanup()

    def test_parse_log_file_keywords(self):
        log_file = self.dir_path / "test.log"
        content = """INFO: Application started
WARN: Low memory
DEBUG: Variable x=10
ERROR: Database connection failed
CRITICAL: System crash imminent
INFO: Shutting down
"""
        log_file.write_text(content, encoding='utf-8')
        
        results = parse_log_file(str(log_file))
        
        self.assertEqual(len(results), 3)
        self.assertIn("WARN: Low memory", results)
        self.assertIn("ERROR: Database connection failed", results)
        self.assertIn("CRITICAL: System crash imminent", results)

    def test_parse_log_file_max_lines(self):
        log_file = self.dir_path / "large.log"
        content = "\n".join([f"ERROR: Error {i}" for i in range(100)])
        log_file.write_text(content, encoding='utf-8')
        
        results = parse_log_file(str(log_file), max_lines=10)
        
        self.assertEqual(len(results), 10)
        self.assertEqual(results[0], "ERROR: Error 0")
        self.assertEqual(results[9], "ERROR: Error 9")

    def test_parse_log_file_not_found(self):
        results = parse_log_file(str(self.dir_path / "missing.log"))
        self.assertEqual(results, [])

if __name__ == '__main__':
    unittest.main()
