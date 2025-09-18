"""
Unit tests for fmu core functionality.
"""

import unittest
import tempfile
import os
from fmu.core import parse_frontmatter, extract_content, parse_file, get_files_from_patterns


class TestCoreFunctionality(unittest.TestCase):
    
    def test_parse_frontmatter_with_yaml(self):
        """Test parsing YAML frontmatter."""
        content = """---
title: Test Post
author: John Doe
tags: [python, testing]
---

This is the content of the post."""
        
        frontmatter, remaining_content = parse_frontmatter(content)
        
        self.assertIsNotNone(frontmatter)
        self.assertEqual(frontmatter['title'], 'Test Post')
        self.assertEqual(frontmatter['author'], 'John Doe')
        self.assertEqual(frontmatter['tags'], ['python', 'testing'])
        self.assertEqual(remaining_content.strip(), 'This is the content of the post.')
    
    def test_parse_frontmatter_no_frontmatter(self):
        """Test parsing content without frontmatter."""
        content = "This is just regular content without frontmatter."
        
        frontmatter, remaining_content = parse_frontmatter(content)
        
        self.assertIsNone(frontmatter)
        self.assertEqual(remaining_content, content)
    
    def test_parse_frontmatter_invalid_yaml(self):
        """Test parsing invalid YAML frontmatter."""
        content = """---
title: Test Post
invalid: [unclosed array
---

Content here."""
        
        with self.assertRaises(ValueError):
            parse_frontmatter(content)
    
    def test_extract_content(self):
        """Test extracting content only."""
        content = """---
title: Test Post
---

This is the content."""
        
        content_only = extract_content(content)
        self.assertEqual(content_only.strip(), 'This is the content.')
    
    def test_parse_file(self):
        """Test parsing a file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("""---
title: Test File
category: test
---

File content here.""")
            temp_file = f.name
        
        try:
            frontmatter, content = parse_file(temp_file)
            
            self.assertIsNotNone(frontmatter)
            self.assertEqual(frontmatter['title'], 'Test File')
            self.assertEqual(frontmatter['category'], 'test')
            self.assertEqual(content.strip(), 'File content here.')
        finally:
            os.unlink(temp_file)
    
    def test_parse_file_not_found(self):
        """Test parsing non-existent file."""
        with self.assertRaises(FileNotFoundError):
            parse_file('non_existent_file.md')
    
    def test_get_files_from_patterns_single_file(self):
        """Test getting files from a single file pattern."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.md') as f:
            f.write("test content")
            temp_file = f.name
        
        try:
            files = get_files_from_patterns([temp_file])
            self.assertEqual(files, [temp_file])
        finally:
            os.unlink(temp_file)
    
    def test_get_files_from_patterns_directory(self):
        """Test getting files from a directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            file1 = os.path.join(temp_dir, 'test1.md')
            file2 = os.path.join(temp_dir, 'test2.md')
            
            with open(file1, 'w') as f:
                f.write("test content 1")
            with open(file2, 'w') as f:
                f.write("test content 2")
            
            files = get_files_from_patterns([temp_dir])
            self.assertEqual(len(files), 2)
            self.assertIn(file1, files)
            self.assertIn(file2, files)


if __name__ == '__main__':
    unittest.main()