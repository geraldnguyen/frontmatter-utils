"""
Unit tests for fmu CLI functionality.
"""

import unittest
import tempfile
import os
import sys
import io
from unittest.mock import patch
from fmu.cli import main, cmd_version, cmd_help, cmd_read, cmd_search


class TestCLIFunctionality(unittest.TestCase):
    
    def setUp(self):
        """Set up test files."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test file with frontmatter
        self.test_file = os.path.join(self.temp_dir, 'test.md')
        with open(self.test_file, 'w') as f:
            f.write("""---
title: Test Post
author: Test Author
category: testing
---

This is test content.""")
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def capture_output(self, func, *args, **kwargs):
        """Helper to capture stdout."""
        captured_output = io.StringIO()
        sys.stdout = captured_output
        try:
            func(*args, **kwargs)
        finally:
            sys.stdout = sys.__stdout__
        return captured_output.getvalue()
    
    def test_cmd_version(self):
        """Test version command."""
        output = self.capture_output(cmd_version)
        self.assertIn('0.1.0', output)
    
    def test_cmd_help(self):
        """Test help command."""
        output = self.capture_output(cmd_help)
        self.assertIn('fmu - Front Matter Utils', output)
        self.assertIn('version', output)
        self.assertIn('help', output)
        self.assertIn('read', output)
        self.assertIn('search', output)
    
    def test_cmd_read_both(self):
        """Test read command with both output."""
        output = self.capture_output(cmd_read, [self.test_file], 'both', False)
        self.assertIn('Front matter:', output)
        self.assertIn('title: Test Post', output)
        self.assertIn('Content:', output)
        self.assertIn('This is test content', output)
    
    def test_cmd_read_frontmatter_only(self):
        """Test read command with frontmatter output only."""
        output = self.capture_output(cmd_read, [self.test_file], 'frontmatter', False)
        self.assertIn('Front matter:', output)
        self.assertIn('title: Test Post', output)
        self.assertNotIn('Content:', output)
        self.assertNotIn('This is test content', output)
    
    def test_cmd_read_content_only(self):
        """Test read command with content output only."""
        output = self.capture_output(cmd_read, [self.test_file], 'content', False)
        self.assertNotIn('Front matter:', output)
        self.assertNotIn('title: Test Post', output)
        self.assertIn('This is test content', output)
    
    def test_cmd_read_skip_heading(self):
        """Test read command with skip heading."""
        output = self.capture_output(cmd_read, [self.test_file], 'both', True)
        self.assertNotIn('Front matter:', output)
        self.assertNotIn('Content:', output)
        self.assertIn('title: Test Post', output)
        self.assertIn('This is test content', output)
    
    def test_cmd_search_console_output(self):
        """Test search command with console output."""
        output = self.capture_output(cmd_search, [self.test_file], 'title')
        self.assertIn(self.test_file, output)
        self.assertIn('title: Test Post', output)
    
    def test_cmd_search_with_value(self):
        """Test search command with specific value."""
        output = self.capture_output(cmd_search, [self.test_file], 'author', 'Test Author')
        self.assertIn(self.test_file, output)
        self.assertIn('author: Test Author', output)
    
    def test_cmd_search_csv_output(self):
        """Test search command with CSV output."""
        csv_file = os.path.join(self.temp_dir, 'output.csv')
        cmd_search([self.test_file], 'title', csv_file=csv_file)
        
        self.assertTrue(os.path.exists(csv_file))
        with open(csv_file, 'r') as f:
            content = f.read()
            self.assertIn('File Path,Front Matter Name,Front Matter Value', content)
            self.assertIn(self.test_file, content)
            self.assertIn('title,Test Post', content)
    
    @patch('sys.argv', ['fmu', 'version'])
    def test_main_version(self):
        """Test main function with version command."""
        output = self.capture_output(main)
        self.assertIn('0.1.0', output)
    
    @patch('sys.argv', ['fmu', 'help'])
    def test_main_help(self):
        """Test main function with help command."""
        output = self.capture_output(main)
        self.assertIn('fmu - Front Matter Utils', output)
    
    @patch('sys.argv', ['fmu'])
    def test_main_no_command(self):
        """Test main function with no command (should show help)."""
        output = self.capture_output(main)
        self.assertIn('fmu - Front Matter Utils', output)


if __name__ == '__main__':
    unittest.main()