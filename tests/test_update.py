"""
Test update functionality.
"""

import unittest
import tempfile
import os
import shutil
from io import StringIO
from unittest.mock import patch
import sys
from fmu.update import (
    transform_case, apply_replace_operation, apply_remove_operation,
    apply_case_transformation, deduplicate_array, update_frontmatter,
    update_and_output
)
from fmu.cli import cmd_update, main


class TestUpdateFunctionality(unittest.TestCase):
    """Test update functionality."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_file1 = os.path.join(self.temp_dir, 'test1.md')
        with open(self.test_file1, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test Document
tags: 
  - python
  - testing
  - python
  - automation
author: John Doe
status: draft
category: programming
---

This is a test document.""")
        
        self.test_file2 = os.path.join(self.temp_dir, 'test2.md')
        with open(self.test_file2, 'w', encoding='utf-8') as f:
            f.write("""---
title: Another Test
tags: 
  - javascript
  - web
category: tutorial
author: jane smith
---

Another test document.""")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def capture_output(self, func, *args, **kwargs):
        """Capture stdout from function call."""
        old_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            func(*args, **kwargs)
            return sys.stdout.getvalue()
        finally:
            sys.stdout = old_stdout

    def test_transform_case_upper(self):
        """Test uppercase transformation."""
        self.assertEqual(transform_case("hello world", "upper"), "HELLO WORLD")

    def test_transform_case_lower(self):
        """Test lowercase transformation."""
        self.assertEqual(transform_case("HELLO WORLD", "lower"), "hello world")

    def test_transform_case_sentence(self):
        """Test sentence case transformation."""
        self.assertEqual(transform_case("hello world", "Sentence case"), "Hello world")

    def test_transform_case_title(self):
        """Test title case transformation."""
        self.assertEqual(transform_case("hello world", "Title Case"), "Hello World")

    def test_transform_case_title_contractions(self):
        """Test title case transformation with contractions (Version 0.8.0 fix)."""
        # Test the specific bug cases mentioned in the requirements
        self.assertEqual(transform_case("can't", "Title Case"), "Can't")
        self.assertEqual(transform_case("aren't", "Title Case"), "Aren't")
        self.assertEqual(transform_case("don't", "Title Case"), "Don't")
        self.assertEqual(transform_case("won't", "Title Case"), "Won't")
        # Test multiple words with contractions
        self.assertEqual(transform_case("i can't do this", "Title Case"), "I Can't Do This")

    def test_transform_case_snake_case(self):
        """Test snake_case transformation."""
        self.assertEqual(transform_case("Hello World", "snake_case"), "hello_world")
        self.assertEqual(transform_case("HelloWorld", "snake_case"), "hello_world")
        self.assertEqual(transform_case("hello-world", "snake_case"), "hello_world")

    def test_transform_case_kebab_case(self):
        """Test kebab-case transformation."""
        self.assertEqual(transform_case("Hello World", "kebab-case"), "hello-world")
        self.assertEqual(transform_case("HelloWorld", "kebab-case"), "hello-world")
        self.assertEqual(transform_case("hello_world", "kebab-case"), "hello-world")

    def test_apply_replace_operation_string(self):
        """Test replace operation on string."""
        result = apply_replace_operation("hello world", "world", "universe")
        self.assertEqual(result, "hello universe")

    def test_apply_replace_operation_string_case_insensitive(self):
        """Test case insensitive replace operation on string."""
        result = apply_replace_operation("Hello World", "WORLD", "universe", ignore_case=True)
        self.assertEqual(result, "Hello universe")

    def test_apply_replace_operation_string_regex(self):
        """Test regex replace operation on string."""
        result = apply_replace_operation("hello123world", r"\d+", "-", use_regex=True)
        self.assertEqual(result, "hello-world")

    def test_apply_replace_operation_array(self):
        """Test replace operation on array."""
        result = apply_replace_operation(["hello", "world", "test"], "world", "universe")
        self.assertEqual(result, ["hello", "universe", "test"])

    def test_apply_remove_operation_string(self):
        """Test remove operation on string."""
        result = apply_remove_operation("hello", "hello")
        self.assertIsNone(result)
        
        result = apply_remove_operation("hello", "world")
        self.assertEqual(result, "hello")

    def test_apply_remove_operation_array(self):
        """Test remove operation on array."""
        result = apply_remove_operation(["hello", "world", "test"], "world")
        self.assertEqual(result, ["hello", "test"])

    def test_apply_remove_operation_regex(self):
        """Test regex remove operation."""
        result = apply_remove_operation(["hello123", "world456", "test"], r"\d+", use_regex=True)
        self.assertEqual(result, ["test"])

    def test_deduplicate_array(self):
        """Test array deduplication."""
        result = deduplicate_array(["hello", "world", "hello", "test"])
        self.assertEqual(result, ["hello", "world", "test"])

    def test_deduplicate_array_non_array(self):
        """Test deduplication on non-array."""
        result = deduplicate_array("hello")
        self.assertEqual(result, "hello")

    def test_update_frontmatter_case_transformation(self):
        """Test frontmatter case transformation."""
        operations = [{'type': 'case', 'case_type': 'upper'}]
        results = update_frontmatter([self.test_file1], 'title', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertEqual(results[0]['new_value'], 'TEST DOCUMENT')

    def test_update_frontmatter_deduplication(self):
        """Test frontmatter deduplication."""
        operations = []
        results = update_frontmatter([self.test_file1], 'tags', operations, True)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        # Should have removed duplicate 'python'
        self.assertIn('python', results[0]['new_value'])
        self.assertEqual(results[0]['new_value'].count('python'), 1)

    def test_update_frontmatter_replace_operation(self):
        """Test frontmatter replace operation."""
        operations = [{
            'type': 'replace',
            'from': 'python',
            'to': 'programming',
            'ignore_case': False,
            'regex': False
        }]
        results = update_frontmatter([self.test_file1], 'tags', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertIn('programming', results[0]['new_value'])
        self.assertNotIn('python', results[0]['new_value'])

    def test_update_frontmatter_remove_operation(self):
        """Test frontmatter remove operation."""
        operations = [{
            'type': 'remove',
            'value': 'python',
            'ignore_case': False,
            'regex': False
        }]
        results = update_frontmatter([self.test_file1], 'tags', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertNotIn('python', results[0]['new_value'])

    def test_update_frontmatter_remove_scalar_field(self):
        """Test removal of scalar field."""
        operations = [{
            'type': 'remove',
            'value': 'draft',
            'ignore_case': False,
            'regex': False
        }]
        results = update_frontmatter([self.test_file1], 'status', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertIsNone(results[0]['new_value'])

    def test_update_frontmatter_multiple_operations(self):
        """Test multiple operations in sequence."""
        operations = [
            {'type': 'case', 'case_type': 'lower'},
            {
                'type': 'replace',
                'from': 'python',
                'to': 'programming',
                'ignore_case': False,
                'regex': False
            }
        ]
        results = update_frontmatter([self.test_file1], 'tags', operations, True)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        # Should have lowercase values and python replaced with programming
        self.assertIn('programming', results[0]['new_value'])
        self.assertIn('testing', results[0]['new_value'])
        self.assertNotIn('python', results[0]['new_value'])

    def test_update_frontmatter_nonexistent_field(self):
        """Test update on nonexistent field."""
        operations = [{'type': 'case', 'case_type': 'upper'}]
        results = update_frontmatter([self.test_file1], 'nonexistent', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0]['changes_made'])
        self.assertIn("does not exist", results[0]['reason'])

    def test_update_and_output(self):
        """Test update and output function."""
        operations = [{'type': 'case', 'case_type': 'upper'}]
        output = self.capture_output(update_and_output, [self.test_file1], 'title', operations, False)
        
        self.assertIn("Updated 'title'", output)

    def test_cmd_update_case_transformation(self):
        """Test cmd_update with case transformation."""
        operations = [{'type': 'case', 'case_type': 'upper'}]
        output = self.capture_output(cmd_update, [self.test_file1], 'title', operations, False)
        
        self.assertIn("Updated 'title'", output)

    def test_cmd_update_no_changes(self):
        """Test cmd_update when no changes are made."""
        operations = [{'type': 'case', 'case_type': 'upper'}]
        output = self.capture_output(cmd_update, [self.test_file1], 'nonexistent', operations, False)
        
        self.assertIn("No changes to 'nonexistent'", output)

    @patch('sys.argv', ['fmu', 'update', '/tmp/test.md', '--name', 'title', '--case', 'upper'])
    def test_main_update_basic(self):
        """Test main function with basic update command."""
        # Create a temporary test file
        test_file = '/tmp/test.md'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: test document
---

Content here.""")
        
        try:
            output = self.capture_output(main)
            self.assertIn("Updated 'title'", output)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    @patch('sys.argv', ['fmu', 'update', '/tmp/test.md', '--name', 'title', '--deduplication', 'false'])
    def test_main_update_no_operations(self):
        """Test main function with update command but no operations."""
        # Create a temporary test file
        test_file = '/tmp/test.md'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: test document
---

Content here.""")
        
        try:
            with self.assertRaises(SystemExit):
                main()
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    @patch('sys.argv', ['fmu', 'update', '/tmp/test_dedup.md', '--name', 'tags', '--deduplication', 'true'])
    def test_main_update_deduplication_only(self):
        """Test main function with deduplication as the only operation (Version 0.8.0 fix)."""
        # Create a temporary test file with duplicates
        test_file = '/tmp/test_dedup.md'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
tags: ["tag1", "tag2", "tag1", "tag3", "tag2"]
---

Content here.""")
        
        try:
            # This should succeed (not raise SystemExit) in Version 0.8.0
            output = self.capture_output(main)
            self.assertIn("Updated 'tags'", output)
        except SystemExit:
            self.fail("main() raised SystemExit when deduplication should be a valid operation")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)


if __name__ == '__main__':
    unittest.main()