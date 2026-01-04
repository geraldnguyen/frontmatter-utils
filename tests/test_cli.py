"""
Unit tests for fmu CLI functionality.
"""

import unittest
import tempfile
import os
import sys
import io
from unittest.mock import patch
from fmu.cli import main, cmd_version, cmd_help, cmd_read, cmd_search, cmd_validate


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
        self.assertIn('0.24.0', output)
    
    def test_cmd_help(self):
        """Test help command."""
        output = self.capture_output(cmd_help)
        self.assertIn('fmu - Front Matter Utils', output)
        self.assertIn('version', output)
        self.assertIn('help', output)
        self.assertIn('read', output)
        self.assertIn('search', output)
        self.assertIn('validate', output)
    
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
    
    def test_cmd_read_with_escape(self):
        """Test read command with escape option."""
        # Create a test file with special characters
        test_file_escape = os.path.join(self.temp_dir, 'escape_test.md')
        with open(test_file_escape, 'w') as f:
            f.write("""---
title: Escape Test
description: Line one and line two
---

Content with "quotes" and 'apostrophes'
And newlines
and tabs.""")
        
        output = self.capture_output(cmd_read, [test_file_escape], 'both', False, 'yaml', True)
        # Check that newlines in the content are escaped
        self.assertIn('\\n', output)
        # Check that quotes in the content are escaped
        self.assertIn('\\"', output)
        self.assertIn("\\'", output)
    
    def test_cmd_read_template_basic(self):
        """Test read command with template output."""
        template = '{ "title": "$frontmatter.title", "author": "$frontmatter.author" }'
        output = self.capture_output(cmd_read, [self.test_file], 'template', False, 'yaml', False, template)
        self.assertIn('"title": "Test Post"', output)
        self.assertIn('"author": "Test Author"', output)
    
    def test_cmd_read_template_with_filepath(self):
        """Test read command with template using $filepath."""
        template = '{ "path": "$filepath" }'
        output = self.capture_output(cmd_read, [self.test_file], 'template', False, 'yaml', False, template)
        self.assertIn(f'"path": "{self.test_file}"', output)
    
    def test_cmd_read_template_with_filename(self):
        """Test read command with template using $filename."""
        template = '{ "file": "$filename" }'
        output = self.capture_output(cmd_read, [self.test_file], 'template', False, 'yaml', False, template)
        self.assertIn('"file": "test.md"', output)
    
    def test_cmd_read_template_with_content(self):
        """Test read command with template using $content."""
        template = '{ "content": "$content" }'
        output = self.capture_output(cmd_read, [self.test_file], 'template', False, 'yaml', False, template)
        self.assertIn('"content": "This is test content."', output)
    
    def test_cmd_read_template_with_array(self):
        """Test read command with template using array frontmatter."""
        # Create a test file with array frontmatter
        test_file_array = os.path.join(self.temp_dir, 'template_array.md')
        with open(test_file_array, 'w') as f:
            f.write("""---
title: Array Test
tags:
  - python
  - testing
---

Test content.""")
        
        template = '{ "tags": $frontmatter.tags }'
        output = self.capture_output(cmd_read, [test_file_array], 'template', False, 'yaml', False, template)
        self.assertIn('"tags": ["python", "testing"]', output)
    
    def test_cmd_read_template_with_array_index(self):
        """Test read command with template using array indexing."""
        # Create a test file with array frontmatter
        test_file_array = os.path.join(self.temp_dir, 'template_array_idx.md')
        with open(test_file_array, 'w') as f:
            f.write("""---
title: Array Index Test
tags:
  - python
  - testing
  - markdown
---

Test content.""")
        
        template = '{ "first": "$frontmatter.tags[0]", "second": "$frontmatter.tags[1]" }'
        output = self.capture_output(cmd_read, [test_file_array], 'template', False, 'yaml', False, template)
        self.assertIn('"first": "python"', output)
        self.assertIn('"second": "testing"', output)
    
    def test_cmd_read_template_with_escape(self):
        """Test read command with template and escape."""
        test_file_escape = os.path.join(self.temp_dir, 'template_escape.md')
        with open(test_file_escape, 'w') as f:
            f.write("""---
title: Test
---

Line one
Line two""")
        
        template = '{ "content": "$content" }'
        output = self.capture_output(cmd_read, [test_file_escape], 'template', False, 'yaml', True, template)
        self.assertIn('\\n', output)
    
    def test_cmd_read_template_missing_field(self):
        """Test read command with template referencing non-existent field."""
        template = '{ "missing": "$frontmatter.nonexistent" }'
        output = self.capture_output(cmd_read, [self.test_file], 'template', False, 'yaml', False, template)
        # Should keep placeholder if field doesn't exist
        self.assertIn('$frontmatter.nonexistent', output)
    
    def test_cmd_read_with_file_output(self):
        """Test read command with file output."""
        output_file = os.path.join(self.temp_dir, 'output.txt')
        cmd_read([self.test_file], 'both', False, 'yaml', False, None, output_file)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Check file content
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn('Front matter:', content)
            self.assertIn('title: Test Post', content)
            self.assertIn('Content:', content)
            self.assertIn('This is test content', content)
    
    def test_cmd_read_template_with_file_output(self):
        """Test read command with template and file output."""
        output_file = os.path.join(self.temp_dir, 'output.json')
        template = '{"title": "$frontmatter.title", "author": "$frontmatter.author"}'
        cmd_read([self.test_file], 'template', False, 'yaml', False, template, output_file)
        
        # Check that file was created
        self.assertTrue(os.path.exists(output_file))
        
        # Check file content
        with open(output_file, 'r') as f:
            content = f.read()
            self.assertIn('"title": "Test Post"', content)
            self.assertIn('"author": "Test Author"', content)
    
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
        self.assertIn('0.24.0', output)
    
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

    def test_cmd_search_array_values(self):
        """Test search command with array values."""
        # Create a test file with array frontmatter
        test_file_array = os.path.join(self.temp_dir, 'array_test.md')
        with open(test_file_array, 'w') as f:
            f.write("""---
title: Array Test
tags: [python, testing, arrays]
categories: [tech, programming]
---

Test content for arrays.""")
        
        # Test searching for a value in an array
        output = self.capture_output(cmd_search, [test_file_array], 'tags', 'python')
        self.assertIn(test_file_array, output)
        self.assertIn('tags: [\'python\', \'testing\', \'arrays\']', output)

    def test_cmd_search_with_regex(self):
        """Test search command with regex option."""
        output = self.capture_output(cmd_search, [self.test_file], 'title', r'^Test', False, True)
        self.assertIn(self.test_file, output)
        self.assertIn('title: Test Post', output)

    def test_cmd_search_array_with_regex(self):
        """Test search command with regex on array values."""
        # Create a test file with array frontmatter
        test_file_array = os.path.join(self.temp_dir, 'regex_array_test.md')
        with open(test_file_array, 'w') as f:
            f.write("""---
title: Regex Array Test
tags: [python, testing, programming, scripting]
---

Test content for regex arrays.""")
        
        # Test regex search for tags ending with 'ing'
        output = self.capture_output(cmd_search, [test_file_array], 'tags', r'ing$', False, True)
        self.assertIn(test_file_array, output)
        # Should match both "testing", "programming", and "scripting"

    @patch('sys.argv', ['fmu', 'search', 'test.md', '--name', 'title', '--regex'])
    def test_main_search_with_regex_flag(self):
        """Test main function with search command and regex flag."""
        # This tests that the argument parser correctly handles the --regex flag
        try:
            main()
        except SystemExit:
            pass  # Expected due to file not found, but parser should work
    
    def test_cmd_validate_console_output(self):
        """Test validate command with console output."""
        validations = [
            {'type': 'exist', 'field': 'nonexistent'}
        ]
        
        output = self.capture_output(cmd_validate, [self.test_file], validations)
        self.assertIn(self.test_file, output)
        self.assertIn('nonexistent', output)
        self.assertIn('does not exist', output)
    
    def test_cmd_validate_csv_output(self):
        """Test validate command with CSV output."""
        validations = [
            {'type': 'exist', 'field': 'nonexistent'}
        ]
        
        csv_file = os.path.join(self.temp_dir, 'validation_output.csv')
        cmd_validate([self.test_file], validations, csv_file=csv_file)
        
        self.assertTrue(os.path.exists(csv_file))
        with open(csv_file, 'r') as f:
            content = f.read()
            self.assertIn('File Path,Front Matter Name,Front Matter Value,Failure Reason', content)
            self.assertIn(self.test_file, content)
            self.assertIn('nonexistent', content)
    
    def test_cmd_validate_multiple_rules(self):
        """Test validate command with multiple validation rules."""
        validations = [
            {'type': 'exist', 'field': 'title'},
            {'type': 'eq', 'field': 'author', 'value': 'Wrong Author'},
            {'type': 'contain', 'field': 'tags', 'value': 'missing_tag'}
        ]
        
        output = self.capture_output(cmd_validate, [self.test_file], validations)
        
        # Should pass the exist check for title
        # Should fail the eq check for author
        # Should fail the contain check for tags (not an array)
        self.assertIn('author', output)
        self.assertIn('does not equal', output)
        self.assertIn('tags', output)
    
    def test_cmd_validate_case_insensitive(self):
        """Test validate command with case-insensitive matching."""
        validations = [
            {'type': 'eq', 'field': 'TITLE', 'value': 'test post'}
        ]
        
        output = self.capture_output(cmd_validate, [self.test_file], validations, ignore_case=True)
        
        # Should pass with case-insensitive matching
        self.assertEqual(output.strip(), '')  # No failures expected
    
    @patch('sys.argv', ['fmu', 'validate', 'nonexistent.md', '--exist', 'title'])
    def test_main_validate_basic(self):
        """Test main function with validate command."""
        # Test that the argument parser correctly handles validation arguments
        try:
            main()
        except SystemExit:
            pass  # Expected due to file not found, but parser should work
    
    @patch('sys.argv', ['fmu', 'validate', 'test.md'])
    def test_main_validate_no_rules(self):
        """Test main function with validate command but no validation rules."""
        # Should exit with error about no validation rules
        with self.assertRaises(SystemExit) as cm:
            main()
        self.assertEqual(cm.exception.code, 1)

    def test_cmd_validate_returns_zero_on_success(self):
        """Test cmd_validate returns 0 when all validations pass."""
        validations = [
            {'type': 'exist', 'field': 'title'},
            {'type': 'exist', 'field': 'author'}
        ]
        
        exit_code = cmd_validate([self.test_file], validations)
        self.assertEqual(exit_code, 0)
    
    def test_cmd_validate_returns_nonzero_on_failure(self):
        """Test cmd_validate returns non-zero when validations fail."""
        validations = [
            {'type': 'exist', 'field': 'nonexistent_field'}
        ]
        
        exit_code = cmd_validate([self.test_file], validations)
        self.assertEqual(exit_code, 1)
    
    def test_main_validate_success_exits_zero(self):
        """Test main function exits with 0 when all validations pass."""
        # Add pattern argument
        with patch('sys.argv', ['fmu', 'validate', self.test_file, '--exist', 'title', '--exist', 'author']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 0)
    
    def test_main_validate_failure_exits_nonzero(self):
        """Test main function exits with non-zero when validations fail."""
        # Add pattern and failing validation
        with patch('sys.argv', ['fmu', 'validate', self.test_file, '--exist', 'nonexistent_field']):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)
    
    def test_cmd_validate_returns_nonzero_with_csv_on_failure(self):
        """Test cmd_validate returns non-zero when validations fail even with CSV output."""
        validations = [
            {'type': 'exist', 'field': 'nonexistent_field'}
        ]
        
        csv_file = os.path.join(self.temp_dir, 'validation_failures.csv')
        exit_code = cmd_validate([self.test_file], validations, csv_file=csv_file)
        
        # Exit code should be 1 even when using CSV output
        self.assertEqual(exit_code, 1)
        # CSV file should be created with the failure
        self.assertTrue(os.path.exists(csv_file))
    
    def test_cmd_validate_returns_zero_with_csv_on_success(self):
        """Test cmd_validate returns zero when validations pass with CSV output."""
        validations = [
            {'type': 'exist', 'field': 'title'},
            {'type': 'exist', 'field': 'author'}
        ]
        
        csv_file = os.path.join(self.temp_dir, 'validation_success.csv')
        exit_code = cmd_validate([self.test_file], validations, csv_file=csv_file)
        
        # Exit code should be 0 when all validations pass
        self.assertEqual(exit_code, 0)
        # CSV file should be created but with only headers
        self.assertTrue(os.path.exists(csv_file))
    
    def test_cmd_read_with_individual_option(self):
        """Test read command with individual file output option."""
        # Create a directory structure with multiple markdown files
        folder1 = os.path.join(self.temp_dir, 'folder1')
        folder2 = os.path.join(self.temp_dir, 'folder2', 'subfolder')
        os.makedirs(folder1)
        os.makedirs(folder2)
        
        # Create file1.md in folder1
        file1 = os.path.join(folder1, 'file1.md')
        with open(file1, 'w') as f:
            f.write("""---
title: File 1
author: Author 1
---

Content of file 1.""")
        
        # Create file2.md in folder2
        file2 = os.path.join(folder2, 'file2.md')
        with open(file2, 'w') as f:
            f.write("""---
title: File 2
author: Author 2
---

Content of file 2.""")
        
        # Run read command with individual option
        patterns = [file1, file2]
        cmd_read(patterns, 'both', False, 'yaml', False, None, 'output.txt', True)
        
        # Check that individual output files were created
        output1 = os.path.join(folder1, 'output.txt')
        output2 = os.path.join(folder2, 'output.txt')
        
        self.assertTrue(os.path.exists(output1), f"Output file not created at {output1}")
        self.assertTrue(os.path.exists(output2), f"Output file not created at {output2}")
        
        # Check content of output1
        with open(output1, 'r') as f:
            content1 = f.read()
            self.assertIn('title: File 1', content1)
            self.assertIn('Content of file 1', content1)
            self.assertNotIn('title: File 2', content1)
        
        # Check content of output2
        with open(output2, 'r') as f:
            content2 = f.read()
            self.assertIn('title: File 2', content2)
            self.assertIn('Content of file 2', content2)
            self.assertNotIn('title: File 1', content2)
    
    def test_cmd_read_with_individual_and_template(self):
        """Test read command with individual option and template output."""
        # Create a directory with a markdown file
        folder = os.path.join(self.temp_dir, 'test_folder')
        os.makedirs(folder)
        
        file1 = os.path.join(folder, 'test.md')
        with open(file1, 'w') as f:
            f.write("""---
title: Test Title
tags: [tag1, tag2]
---

Test content.""")
        
        # Run read command with individual option and template
        template = '{ "title": "$frontmatter.title", "tags": $frontmatter.tags }'
        cmd_read([file1], 'template', False, 'yaml', False, template, 'output.json', True)
        
        # Check that output file was created
        output = os.path.join(folder, 'output.json')
        self.assertTrue(os.path.exists(output))
        
        # Check content
        with open(output, 'r') as f:
            content = f.read()
            self.assertIn('"title": "Test Title"', content)
            self.assertIn('"tags": ["tag1", "tag2"]', content)
    
    def test_cmd_read_without_individual_creates_single_file(self):
        """Test read command without individual option creates a single output file."""
        # Create two files in different directories
        folder1 = os.path.join(self.temp_dir, 'dir1')
        folder2 = os.path.join(self.temp_dir, 'dir2')
        os.makedirs(folder1)
        os.makedirs(folder2)
        
        file1 = os.path.join(folder1, 'test1.md')
        with open(file1, 'w') as f:
            f.write("""---
title: Title 1
---

Content 1.""")
        
        file2 = os.path.join(folder2, 'test2.md')
        with open(file2, 'w') as f:
            f.write("""---
title: Title 2
---

Content 2.""")
        
        # Run read command without individual option
        output_path = os.path.join(self.temp_dir, 'combined.txt')
        cmd_read([file1, file2], 'both', False, 'yaml', False, None, output_path, False)
        
        # Check that single output file was created
        self.assertTrue(os.path.exists(output_path))
        
        # Check that individual files were NOT created
        self.assertFalse(os.path.exists(os.path.join(folder1, 'combined.txt')))
        self.assertFalse(os.path.exists(os.path.join(folder2, 'combined.txt')))
        
        # Check that combined file contains both contents
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn('title: Title 1', content)
            self.assertIn('title: Title 2', content)
            self.assertIn('Content 1', content)
            self.assertIn('Content 2', content)
    
    def test_cmd_read_json_output_basic(self):
        """Test read command with JSON output."""
        import json
        map_items = [('title', '$frontmatter.title'), ('author', '$frontmatter.author')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        # Parse JSON to verify it's valid
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['author'], 'Test Author')
    
    def test_cmd_read_json_output_with_pretty(self):
        """Test read command with JSON output and pretty formatting."""
        import json
        map_items = [('title', '$frontmatter.title'), ('author', '$frontmatter.author')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items, True, False)
        
        # Check for pretty formatting (newlines and indentation)
        self.assertIn('\n', output)
        self.assertIn('  ', output)
        
        # Verify JSON is still valid
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Test Post')
    
    def test_cmd_read_json_output_with_compact(self):
        """Test read command with JSON output and compact formatting."""
        import json
        map_items = [('title', '$frontmatter.title'), ('author', '$frontmatter.author')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items, False, True)
        
        # Check for compact formatting (no spaces after separators)
        self.assertNotIn(': ', output)  # No space after colon
        self.assertIn(':', output)  # But colon still exists
        
        # Verify JSON is still valid
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Test Post')
    
    def test_cmd_read_yaml_output_basic(self):
        """Test read command with YAML output."""
        import yaml
        map_items = [('title', '$frontmatter.title'), ('author', '$frontmatter.author')]
        output = self.capture_output(cmd_read, [self.test_file], 'yaml', False, 'yaml', False, None, None, False, map_items)
        
        # Parse YAML to verify it's valid
        data = yaml.safe_load(output)
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['author'], 'Test Author')
    
    def test_cmd_read_json_with_literal_values(self):
        """Test read command with JSON output using literal values."""
        import json
        map_items = [('title', '$frontmatter.title'), ('type', 'article'), ('count', '5')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['type'], 'article')
        self.assertEqual(data['count'], '5')
    
    def test_cmd_read_json_with_placeholder_filepath(self):
        """Test read command with JSON output using $filepath placeholder."""
        import json
        map_items = [('title', '$frontmatter.title'), ('path', '$filepath'), ('filename', '$filename')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['path'], self.test_file)
        self.assertEqual(data['filename'], 'test.md')
    
    def test_cmd_read_json_with_content_placeholder(self):
        """Test read command with JSON output using $content placeholder."""
        import json
        map_items = [('title', '$frontmatter.title'), ('content', '$content')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Test Post')
        self.assertIn('This is test content', data['content'])
    
    def test_cmd_read_json_with_array_frontmatter(self):
        """Test read command with JSON output using array frontmatter."""
        import json
        # Create a test file with array frontmatter
        test_file_array = os.path.join(self.temp_dir, 'json_array.md')
        with open(test_file_array, 'w') as f:
            f.write("""---
title: Array Test
tags:
  - python
  - testing
---

Test content.""")
        
        map_items = [('title', '$frontmatter.title'), ('tags', '$frontmatter.tags')]
        output = self.capture_output(cmd_read, [test_file_array], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Array Test')
        self.assertEqual(data['tags'], ['python', 'testing'])
    
    def test_cmd_read_json_with_function_now(self):
        """Test read command with JSON output using =now() function."""
        import json
        from datetime import datetime
        map_items = [('title', '$frontmatter.title'), ('timestamp', '=now()')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Test Post')
        # Verify timestamp is in ISO format
        self.assertIn('T', data['timestamp'])
        self.assertIn('Z', data['timestamp'])
        
        # Verify it's a valid datetime
        datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
    
    def test_cmd_read_yaml_with_pretty_formatting(self):
        """Test read command with YAML output and pretty formatting."""
        import yaml
        # Create a test file with array frontmatter
        test_file_array = os.path.join(self.temp_dir, 'yaml_pretty.md')
        with open(test_file_array, 'w') as f:
            f.write("""---
title: YAML Test
tags:
  - yaml
  - pretty
---

Test content.""")
        
        map_items = [('title', '$frontmatter.title'), ('tags', '$frontmatter.tags')]
        output = self.capture_output(cmd_read, [test_file_array], 'yaml', False, 'yaml', False, None, None, False, map_items, True, False)
        
        # Check for pretty formatting (expanded list format)
        self.assertIn('- yaml', output)
        self.assertIn('- pretty', output)
        
        # Verify YAML is still valid
        data = yaml.safe_load(output)
        self.assertEqual(data['tags'], ['yaml', 'pretty'])
    
    def test_cmd_read_yaml_with_compact_formatting(self):
        """Test read command with YAML output and compact formatting."""
        import yaml
        test_file_array = os.path.join(self.temp_dir, 'yaml_compact.md')
        with open(test_file_array, 'w') as f:
            f.write("""---
title: YAML Test
tags:
  - yaml
  - compact
---

Test content.""")
        
        map_items = [('title', '$frontmatter.title'), ('tags', '$frontmatter.tags')]
        output = self.capture_output(cmd_read, [test_file_array], 'yaml', False, 'yaml', False, None, None, False, map_items, False, True)
        
        # Check for compact formatting (flow style with brackets)
        self.assertIn('[', output)
        self.assertIn(']', output)
        
        # Verify YAML is still valid
        data = yaml.safe_load(output)
        self.assertEqual(data['tags'], ['yaml', 'compact'])
    
    def test_cmd_read_json_with_boolean_and_integer_literals(self):
        """Test read command with JSON output using boolean and integer literals."""
        import json
        # When coming from specs file, YAML loads booleans and integers as native Python types
        map_items = [('title', '$frontmatter.title'), ('published', True), ('draft', False), ('rating', 5)]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['title'], 'Test Post')
        self.assertEqual(data['published'], True)
        self.assertEqual(data['draft'], False)
        self.assertEqual(data['rating'], 5)
        # Verify they are actual booleans and int, not strings
        self.assertIsInstance(data['published'], bool)
        self.assertIsInstance(data['draft'], bool)
        self.assertIsInstance(data['rating'], int)
    
    def test_cmd_read_template_with_folderpath(self):
        """Test read command with template using $folderpath (v0.23.0)."""
        template = '{ "folder": "$folderpath" }'
        output = self.capture_output(cmd_read, [self.test_file], 'template', False, 'yaml', False, template)
        expected_folder = os.path.dirname(self.test_file)
        self.assertIn(f'"folder": "{expected_folder}"', output)
    
    def test_cmd_read_template_with_foldername(self):
        """Test read command with template using $foldername (v0.23.0)."""
        template = '{ "folder": "$foldername" }'
        output = self.capture_output(cmd_read, [self.test_file], 'template', False, 'yaml', False, template)
        expected_foldername = os.path.basename(os.path.dirname(self.test_file))
        self.assertIn(f'"folder": "{expected_foldername}"', output)
    
    def test_cmd_read_json_with_folderpath_placeholder(self):
        """Test read command with JSON output using $folderpath placeholder (v0.23.0)."""
        import json
        map_items = [('folder', '$folderpath')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        expected_folder = os.path.dirname(self.test_file)
        self.assertEqual(data['folder'], expected_folder)
    
    def test_cmd_read_json_with_basename_function(self):
        """Test read command with JSON output using =basename() function (v0.23.0)."""
        import json
        map_items = [('name', '=basename($filepath)')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['name'], 'test')
    
    def test_cmd_read_json_with_trim_function(self):
        """Test read command with JSON output using =trim() function (v0.23.0)."""
        import json
        map_items = [('trimmed', '=trim(  hello world  )')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['trimmed'], 'hello world')
    
    def test_cmd_read_json_with_truncate_function(self):
        """Test read command with JSON output using =truncate() function (v0.23.0)."""
        import json
        map_items = [('short', '=truncate($frontmatter.title, 4)')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['short'], 'Test')
    
    def test_cmd_read_json_with_wtruncate_function(self):
        """Test read command with JSON output using =wtruncate() function (v0.23.0)."""
        import json
        map_items = [('short', '=wtruncate($frontmatter.title, 8, ...)')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['short'], 'Test...')
    
    def test_cmd_read_json_with_path_function(self):
        """Test read command with JSON output using =path() function (v0.23.0)."""
        import json
        map_items = [('output_path', '=path($folderpath, output, data.json)')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        expected = os.path.join(os.path.dirname(self.test_file), 'output', 'data.json')
        self.assertEqual(data['output_path'], expected)
    
    def test_cmd_read_json_with_dollar_prefix_function(self):
        """Test read command with JSON output using $ prefix function (v0.23.0)."""
        import json
        # Test simple concat with $ prefix
        map_items = [('result', '$concat($frontmatter.title, $frontmatter.author)')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['result'], 'Test PostTest Author')
    
    def test_cmd_read_json_with_nested_dollar_functions(self):
        """Test read command with JSON output using nested $ prefix functions (v0.23.0)."""
        import json
        map_items = [('trimmed_concat', '$trim($concat(  , $frontmatter.title,  ))')]
        output = self.capture_output(cmd_read, [self.test_file], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['trimmed_concat'], 'Test Post')
    
    def test_cmd_read_json_with_flat_list_function(self):
        """Test read command with JSON output using =flat_list() function (v0.23.0)."""
        import json
        # Create a test file with tags
        test_file_tags = os.path.join(self.temp_dir, 'test_tags.md')
        with open(test_file_tags, 'w') as f:
            f.write("""---
title: Test Tags
tags:
  - python
  - javascript
---

Test content.""")
        
        map_items = [('all_tags', '=flat_list(golang, $frontmatter.tags, rust)')]
        output = self.capture_output(cmd_read, [test_file_tags], 'json', False, 'yaml', False, None, None, False, map_items)
        
        data = json.loads(output.strip())
        self.assertEqual(data['all_tags'], ['golang', 'python', 'javascript', 'rust'])


if __name__ == '__main__':
    unittest.main()
