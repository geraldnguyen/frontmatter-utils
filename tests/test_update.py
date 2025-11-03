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
from fmu.core import parse_file
from fmu.update import (
    transform_case, apply_replace_operation, apply_remove_operation,
    apply_case_transformation, deduplicate_array, update_frontmatter,
    update_and_output, evaluate_formula, apply_compute_operation,
    _resolve_placeholder, _parse_function_call, _execute_function
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

    # Version 0.12.0 tests: --compute functionality
    
    def test_resolve_placeholder_filename(self):
        """Test resolving $filename placeholder."""
        result = _resolve_placeholder('$filename', '/path/to/test.md', {}, '')
        self.assertEqual(result, 'test.md')
    
    def test_resolve_placeholder_filepath(self):
        """Test resolving $filepath placeholder."""
        result = _resolve_placeholder('$filepath', '/path/to/test.md', {}, '')
        self.assertEqual(result, '/path/to/test.md')
    
    def test_resolve_placeholder_content(self):
        """Test resolving $content placeholder."""
        result = _resolve_placeholder('$content', '/path/to/test.md', {}, 'Test content')
        self.assertEqual(result, 'Test content')
    
    def test_resolve_placeholder_frontmatter_scalar(self):
        """Test resolving $frontmatter.name placeholder for scalar value."""
        frontmatter = {'title': 'Test Title'}
        result = _resolve_placeholder('$frontmatter.title', '/path/to/test.md', frontmatter, '')
        self.assertEqual(result, 'Test Title')
    
    def test_resolve_placeholder_frontmatter_array(self):
        """Test resolving $frontmatter.name placeholder for array value."""
        frontmatter = {'tags': ['tag1', 'tag2']}
        result = _resolve_placeholder('$frontmatter.tags', '/path/to/test.md', frontmatter, '')
        self.assertEqual(result, ['tag1', 'tag2'])
    
    def test_resolve_placeholder_frontmatter_array_index(self):
        """Test resolving $frontmatter.name[index] placeholder."""
        frontmatter = {'tags': ['tag1', 'tag2', 'tag3']}
        result = _resolve_placeholder('$frontmatter.tags[1]', '/path/to/test.md', frontmatter, '')
        self.assertEqual(result, 'tag2')
    
    def test_parse_function_call_now(self):
        """Test parsing now() function call."""
        func_name, params = _parse_function_call('=now()')
        self.assertEqual(func_name, 'now')
        self.assertEqual(params, [])
    
    def test_parse_function_call_list(self):
        """Test parsing list() function call."""
        func_name, params = _parse_function_call('=list()')
        self.assertEqual(func_name, 'list')
        self.assertEqual(params, [])
    
    def test_parse_function_call_hash(self):
        """Test parsing hash() function call."""
        func_name, params = _parse_function_call('=hash($frontmatter.url, 10)')
        self.assertEqual(func_name, 'hash')
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0], '$frontmatter.url')
        self.assertEqual(params[1], '10')
    
    def test_parse_function_call_concat(self):
        """Test parsing concat() function call."""
        func_name, params = _parse_function_call('=concat(/post/, $frontmatter.id)')
        self.assertEqual(func_name, 'concat')
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0], '/post/')
        self.assertEqual(params[1], '$frontmatter.id')
    
    def test_execute_function_now(self):
        """Test executing now() function."""
        result = _execute_function('now', [])
        # Check format: YYYY-MM-DDTHH:MM:SSZ
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        self.assertIsNotNone(re.match(pattern, result))
    
    def test_execute_function_list(self):
        """Test executing list() function."""
        result = _execute_function('list', [])
        self.assertEqual(result, [])
    
    def test_execute_function_hash(self):
        """Test executing hash() function."""
        result = _execute_function('hash', ['/post/original/a-book-title', 10])
        self.assertEqual(len(result), 10)
        # Hash should be deterministic
        result2 = _execute_function('hash', ['/post/original/a-book-title', 10])
        self.assertEqual(result, result2)
    
    def test_execute_function_concat(self):
        """Test executing concat() function."""
        result = _execute_function('concat', ['/post/', 'abc123'])
        self.assertEqual(result, '/post/abc123')
    
    def test_evaluate_formula_literal(self):
        """Test evaluating literal formula."""
        result = evaluate_formula('2', '/path/to/test.md', {}, '')
        self.assertEqual(result, '2')
        
        result = evaluate_formula('2nd', '/path/to/test.md', {}, '')
        self.assertEqual(result, '2nd')
    
    def test_evaluate_formula_placeholder(self):
        """Test evaluating placeholder formula."""
        frontmatter = {'url': '/original/path'}
        result = evaluate_formula('$frontmatter.url', '/path/to/test.md', frontmatter, '')
        self.assertEqual(result, '/original/path')
    
    def test_evaluate_formula_function(self):
        """Test evaluating function formula."""
        result = evaluate_formula('=list()', '/path/to/test.md', {}, '')
        self.assertEqual(result, [])
    
    def test_evaluate_formula_function_with_placeholder(self):
        """Test evaluating function formula with placeholder parameters."""
        frontmatter = {'content_id': 'abc123'}
        result = evaluate_formula('=concat(/post/, $frontmatter.content_id)', '/path/to/test.md', frontmatter, '')
        self.assertEqual(result, '/post/abc123')
    
    def test_apply_compute_operation_create_field(self):
        """Test compute operation creating a new field."""
        frontmatter = {'title': 'Test'}
        frontmatter, changed = apply_compute_operation(frontmatter, 'edition', '1', '/path/to/test.md', '')
        
        self.assertTrue(changed)
        self.assertEqual(frontmatter['edition'], '1')
    
    def test_apply_compute_operation_update_scalar(self):
        """Test compute operation updating a scalar field."""
        frontmatter = {'edition': '1'}
        frontmatter, changed = apply_compute_operation(frontmatter, 'edition', '2', '/path/to/test.md', '')
        
        self.assertTrue(changed)
        self.assertEqual(frontmatter['edition'], '2')
    
    def test_apply_compute_operation_append_to_list(self):
        """Test compute operation appending to a list field."""
        frontmatter = {'aliases': ['/old-alias', '/newer-alias']}
        frontmatter, changed = apply_compute_operation(frontmatter, 'aliases', '/newest-alias', '/path/to/test.md', '')
        
        self.assertTrue(changed)
        self.assertEqual(len(frontmatter['aliases']), 3)
        self.assertIn('/newest-alias', frontmatter['aliases'])
    
    def test_update_frontmatter_with_compute_literal(self):
        """Test update with compute operation using literal value."""
        # Create test file
        test_file = os.path.join(self.temp_dir, 'compute_test1.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test
---

Content.""")
        
        operations = [{'type': 'compute', 'formula': '1'}]
        results = update_frontmatter([test_file], 'edition', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertEqual(results[0]['new_value'], '1')
    
    def test_update_frontmatter_with_compute_function_now(self):
        """Test update with compute operation using now() function."""
        # Create test file
        test_file = os.path.join(self.temp_dir, 'compute_test2.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test
---

Content.""")
        
        operations = [{'type': 'compute', 'formula': '=now()'}]
        results = update_frontmatter([test_file], 'last_update', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        # Check that it's a valid timestamp
        import re
        pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        self.assertIsNotNone(re.match(pattern, results[0]['new_value']))
    
    def test_update_frontmatter_with_compute_function_list(self):
        """Test update with compute operation using list() function."""
        # Create test file
        test_file = os.path.join(self.temp_dir, 'compute_test3.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test
---

Content.""")
        
        operations = [{'type': 'compute', 'formula': '=list()'}]
        results = update_frontmatter([test_file], 'aliases', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertEqual(results[0]['new_value'], [])
    
    def test_update_frontmatter_with_compute_function_hash(self):
        """Test update with compute operation using hash() function."""
        # Create test file
        test_file = os.path.join(self.temp_dir, 'compute_test4.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test
url: /post/original/a-book-title
---

Content.""")
        
        operations = [{'type': 'compute', 'formula': '=hash($frontmatter.url, 10)'}]
        results = update_frontmatter([test_file], 'content_id', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertEqual(len(results[0]['new_value']), 10)
    
    def test_update_frontmatter_with_compute_function_concat(self):
        """Test update with compute operation using concat() function."""
        # Create test file
        test_file = os.path.join(self.temp_dir, 'compute_test5.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test
content_id: abc123
aliases: []
---

Content.""")
        
        operations = [{'type': 'compute', 'formula': '=concat(/post/, $frontmatter.content_id)'}]
        results = update_frontmatter([test_file], 'aliases', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertIn('/post/abc123', results[0]['new_value'])
    
    def test_update_frontmatter_with_multiple_compute(self):
        """Test update with multiple compute operations (Example 3 from spec)."""
        # Create test file
        test_file = os.path.join(self.temp_dir, 'compute_test6.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: a book title
url: /post/original/a-book-title
---

Content.""")
        
        # Step 1: Create empty aliases
        operations = [{'type': 'compute', 'formula': '=list()'}]
        results = update_frontmatter([test_file], 'aliases', operations, False)
        self.assertTrue(results[0]['changes_made'])
        
        # Step 2: Create content_id from hash
        operations = [{'type': 'compute', 'formula': '=hash($frontmatter.url, 10)'}]
        results = update_frontmatter([test_file], 'content_id', operations, False)
        self.assertTrue(results[0]['changes_made'])
        
        # Step 3: Add alias using concat
        operations = [{'type': 'compute', 'formula': '=concat(/post/, $frontmatter.content_id)'}]
        results = update_frontmatter([test_file], 'aliases', operations, False)
        self.assertTrue(results[0]['changes_made'])
        self.assertEqual(len(results[0]['new_value']), 1)
    
    @patch('sys.argv', ['fmu', 'update', '/tmp/compute_cli.md', '--name', 'edition', '--compute', '2'])
    def test_main_update_with_compute(self):
        """Test main function with compute operation via CLI."""
        # Create a temporary test file
        test_file = '/tmp/compute_cli.md'
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test Document
edition: 1
---

Content here.""")
        
        try:
            output = self.capture_output(main)
            self.assertIn("Updated 'edition'", output)
            
            # Verify the file was updated
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('edition: \'2\'', content)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
    
    # Version 0.13.0 tests: slice function
    
    def test_execute_function_slice_start_only(self):
        """Test executing slice() function with start parameter only."""
        test_list = ['a', 'b', 'c', 'd', 'e']
        result = _execute_function('slice', [test_list, '2'])
        self.assertEqual(result, ['c', 'd', 'e'])
    
    def test_execute_function_slice_start_negative(self):
        """Test executing slice() function with negative start."""
        test_list = ['a', 'b', 'c', 'd', 'e']
        result = _execute_function('slice', [test_list, '-2'])
        self.assertEqual(result, ['d', 'e'])
    
    def test_execute_function_slice_start_stop(self):
        """Test executing slice() function with start and stop parameters."""
        test_list = ['a', 'b', 'c', 'd', 'e']
        result = _execute_function('slice', [test_list, '1', '4'])
        self.assertEqual(result, ['b', 'c', 'd'])
    
    def test_execute_function_slice_start_stop_negative(self):
        """Test executing slice() function with negative stop."""
        test_list = ['a', 'b', 'c', 'd', 'e']
        result = _execute_function('slice', [test_list, '0', '-1'])
        self.assertEqual(result, ['a', 'b', 'c', 'd'])
    
    def test_execute_function_slice_start_stop_step(self):
        """Test executing slice() function with start, stop, and step."""
        test_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g']
        result = _execute_function('slice', [test_list, '0', '7', '2'])
        self.assertEqual(result, ['a', 'c', 'e', 'g'])
    
    def test_execute_function_slice_negative_step(self):
        """Test executing slice() function with negative step (reverse)."""
        test_list = ['a', 'b', 'c', 'd', 'e']
        result = _execute_function('slice', [test_list, '4', '0', '-1'])
        self.assertEqual(result, ['e', 'd', 'c', 'b'])
    
    def test_execute_function_slice_last_element(self):
        """Test executing slice() function to get last element (from spec example)."""
        test_list = ['/old-alias', '/newest-alias']
        result = _execute_function('slice', [test_list, '-1'])
        self.assertEqual(result, ['/newest-alias'])
    
    def test_execute_function_slice_all_negative_indices(self):
        """Test executing slice() function with all negative indices."""
        test_list = ['a', 'b', 'c', 'd', 'e']
        result = _execute_function('slice', [test_list, '-4', '-1'])
        self.assertEqual(result, ['b', 'c', 'd'])
    
    def test_execute_function_slice_empty_result(self):
        """Test executing slice() function that results in empty list."""
        test_list = ['a', 'b', 'c']
        result = _execute_function('slice', [test_list, '5'])
        self.assertEqual(result, [])
    
    def test_execute_function_slice_invalid_first_param(self):
        """Test executing slice() function with non-list first parameter."""
        with self.assertRaises(ValueError) as context:
            _execute_function('slice', ['not-a-list', '0'])
        self.assertIn('must be a list', str(context.exception))
    
    def test_execute_function_slice_invalid_start(self):
        """Test executing slice() function with invalid start parameter."""
        test_list = ['a', 'b', 'c']
        with self.assertRaises(ValueError) as context:
            _execute_function('slice', [test_list, 'invalid'])
        self.assertIn('start parameter must be an integer', str(context.exception))
    
    def test_execute_function_slice_insufficient_params(self):
        """Test executing slice() function with insufficient parameters."""
        with self.assertRaises(ValueError) as context:
            _execute_function('slice', [['a', 'b']])
        self.assertIn('at least 2 parameters', str(context.exception))
    
    def test_parse_function_call_slice(self):
        """Test parsing slice() function call."""
        func_name, params = _parse_function_call('=slice($frontmatter.aliases, -1)')
        self.assertEqual(func_name, 'slice')
        self.assertEqual(len(params), 2)
        self.assertEqual(params[0], '$frontmatter.aliases')
        self.assertEqual(params[1], '-1')
    
    def test_parse_function_call_slice_with_stop(self):
        """Test parsing slice() function call with stop parameter."""
        func_name, params = _parse_function_call('=slice($frontmatter.tags, 0, 3)')
        self.assertEqual(func_name, 'slice')
        self.assertEqual(len(params), 3)
        self.assertEqual(params[0], '$frontmatter.tags')
        self.assertEqual(params[1], '0')
        self.assertEqual(params[2], '3')
    
    def test_parse_function_call_slice_with_step(self):
        """Test parsing slice() function call with step parameter."""
        func_name, params = _parse_function_call('=slice($frontmatter.items, 0, 10, 2)')
        self.assertEqual(func_name, 'slice')
        self.assertEqual(len(params), 4)
        self.assertEqual(params[0], '$frontmatter.items')
        self.assertEqual(params[1], '0')
        self.assertEqual(params[2], '10')
        self.assertEqual(params[3], '2')
    
    def test_update_frontmatter_with_compute_function_slice(self):
        """Test update with compute operation using slice() function (from spec example)."""
        # Create test file with aliases
        test_file = os.path.join(self.temp_dir, 'compute_slice_test.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test
aliases:
  - /old-alias
  - /newest-alias
---

Content.""")
        
        # Test slice to get last element
        operations = [{'type': 'compute', 'formula': '=slice($frontmatter.aliases, -1)'}]
        results = update_frontmatter([test_file], 'aliases', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertEqual(results[0]['new_value'], ['/newest-alias'])
    
    def test_update_frontmatter_with_compute_function_slice_first_three(self):
        """Test update with compute operation using slice() to get first three elements."""
        # Create test file with tags
        test_file = os.path.join(self.temp_dir, 'compute_slice_test2.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test
tags:
  - python
  - javascript
  - java
  - go
  - rust
---

Content.""")
        
        # Test slice to get first three elements
        operations = [{'type': 'compute', 'formula': '=slice($frontmatter.tags, 0, 3)'}]
        results = update_frontmatter([test_file], 'tags', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertEqual(results[0]['new_value'], ['python', 'javascript', 'java'])
    
    def test_update_frontmatter_with_compute_function_slice_every_other(self):
        """Test update with compute operation using slice() with step."""
        # Create test file with items
        test_file = os.path.join(self.temp_dir, 'compute_slice_test3.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test
items:
  - item1
  - item2
  - item3
  - item4
  - item5
  - item6
---

Content.""")
        
        # Test slice to get every other element
        operations = [{'type': 'compute', 'formula': '=slice($frontmatter.items, 0, 6, 2)'}]
        results = update_frontmatter([test_file], 'items', operations, False)
        
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        self.assertEqual(results[0]['new_value'], ['item1', 'item3', 'item5'])

    def test_frontmatter_order_preservation(self):
        """Test that frontmatter field order is preserved after update."""
        # Create a test file with specific order of frontmatter fields
        test_file = os.path.join(self.temp_dir, 'order_test.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: Test Document
date: 2025-01-01
draft: false
author: Test Author
tags:
- tag1
- tag2
categories:
- cat1
description: A test description
---

Test content here.""")
        
        # Update the tags field
        operations = [{'type': 'compute', 'formula': 'tag3'}]
        results = update_frontmatter([test_file], 'tags', operations, False)
        
        # Verify update was successful
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]['changes_made'])
        
        # Read the file using the existing parse_file function
        frontmatter_dict, _ = parse_file(test_file)
        
        # Get the field order from the parsed dictionary (Python 3.7+ maintains insertion order)
        field_order = list(frontmatter_dict.keys())
        
        # The expected order should be preserved
        expected_order = ['title', 'date', 'draft', 'author', 'tags', 'categories', 'description']
        self.assertEqual(field_order, expected_order, 
                        f"Field order not preserved. Expected {expected_order}, got {field_order}")


if __name__ == '__main__':
    unittest.main()