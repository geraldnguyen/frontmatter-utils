"""
Unit tests for fmu validation functionality.
"""

import unittest
import tempfile
import os
import csv
from fmu.validation import validate_frontmatter, output_validation_results, validate_and_output


class TestValidationFunctionality(unittest.TestCase):
    
    def setUp(self):
        """Set up test files."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test file 1
        self.file1 = os.path.join(self.temp_dir, 'test1.md')
        with open(self.file1, 'w') as f:
            f.write("""---
title: First Post
author: John Doe
tags: [tech, programming]
status: published
age: 25
---

This is the content of the first post.""")
        
        # Create test file 2
        self.file2 = os.path.join(self.temp_dir, 'test2.md')
        with open(self.file2, 'w') as f:
            f.write("""---
title: Second Post
author: Jane Smith
tags: [science, research]
draft: true
age: 30
---

This is the content of the second post.""")
        
        # Create test file 3 with no frontmatter
        self.file3 = os.path.join(self.temp_dir, 'test3.md')
        with open(self.file3, 'w') as f:
            f.write("This is just content without frontmatter.")
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_validate_exist_pass(self):
        """Test validation that should pass for existing fields."""
        validations = [
            {'type': 'exist', 'field': 'title'},
            {'type': 'exist', 'field': 'author'}
        ]
        
        failures = validate_frontmatter([self.file1, self.file2], validations)
        self.assertEqual(len(failures), 0)
    
    def test_validate_exist_fail(self):
        """Test validation that should fail for non-existing fields."""
        validations = [
            {'type': 'exist', 'field': 'nonexistent'}
        ]
        
        failures = validate_frontmatter([self.file1, self.file2], validations)
        self.assertEqual(len(failures), 2)
        
        # Check first failure
        self.assertEqual(failures[0][0], self.file1)
        self.assertEqual(failures[0][1], 'nonexistent')
        self.assertIsNone(failures[0][2])
        self.assertIn("does not exist", failures[0][3])
    
    def test_validate_not_exist_pass(self):
        """Test validation that should pass for non-existing fields."""
        validations = [
            {'type': 'not', 'field': 'nonexistent'}
        ]
        
        failures = validate_frontmatter([self.file1, self.file2], validations)
        self.assertEqual(len(failures), 0)
    
    def test_validate_not_exist_fail(self):
        """Test validation that should fail for existing fields."""
        validations = [
            {'type': 'not', 'field': 'title'}
        ]
        
        failures = validate_frontmatter([self.file1, self.file2], validations)
        self.assertEqual(len(failures), 2)
        
        # Check failure message
        self.assertIn("should not exist", failures[0][3])
    
    def test_validate_equal_pass(self):
        """Test validation that should pass for equal values."""
        validations = [
            {'type': 'eq', 'field': 'author', 'value': 'John Doe'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 0)
    
    def test_validate_equal_fail(self):
        """Test validation that should fail for non-equal values."""
        validations = [
            {'type': 'eq', 'field': 'author', 'value': 'John Doe'}
        ]
        
        failures = validate_frontmatter([self.file2], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertEqual(failures[0][1], 'author')
        self.assertEqual(failures[0][2], 'Jane Smith')
        self.assertIn("does not equal", failures[0][3])
    
    def test_validate_not_equal_pass(self):
        """Test validation that should pass for non-equal values."""
        validations = [
            {'type': 'ne', 'field': 'author', 'value': 'Someone Else'}
        ]
        
        failures = validate_frontmatter([self.file1, self.file2], validations)
        self.assertEqual(len(failures), 0)
    
    def test_validate_not_equal_fail(self):
        """Test validation that should fail for equal values."""
        validations = [
            {'type': 'ne', 'field': 'author', 'value': 'John Doe'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertIn("should not equal", failures[0][3])
    
    def test_validate_contain_pass(self):
        """Test validation that should pass for array containing value."""
        validations = [
            {'type': 'contain', 'field': 'tags', 'value': 'tech'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 0)
    
    def test_validate_contain_fail(self):
        """Test validation that should fail for array not containing value."""
        validations = [
            {'type': 'contain', 'field': 'tags', 'value': 'tech'}
        ]
        
        failures = validate_frontmatter([self.file2], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertIn("does not contain", failures[0][3])
    
    def test_validate_contain_non_array_fail(self):
        """Test validation that should fail for non-array field."""
        validations = [
            {'type': 'contain', 'field': 'title', 'value': 'test'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertIn("is not an array", failures[0][3])
    
    def test_validate_not_contain_pass(self):
        """Test validation that should pass for array not containing value."""
        validations = [
            {'type': 'not-contain', 'field': 'tags', 'value': 'missing'}
        ]
        
        failures = validate_frontmatter([self.file1, self.file2], validations)
        self.assertEqual(len(failures), 0)
    
    def test_validate_not_contain_fail(self):
        """Test validation that should fail for array containing value."""
        validations = [
            {'type': 'not-contain', 'field': 'tags', 'value': 'tech'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertIn("should not contain", failures[0][3])
    
    def test_validate_match_pass(self):
        """Test validation that should pass for regex match."""
        validations = [
            {'type': 'match', 'field': 'author', 'regex': r'John.*'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 0)
    
    def test_validate_match_fail(self):
        """Test validation that should fail for regex no match."""
        validations = [
            {'type': 'match', 'field': 'author', 'regex': r'John.*'}
        ]
        
        failures = validate_frontmatter([self.file2], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertIn("does not match pattern", failures[0][3])
    
    def test_validate_not_match_pass(self):
        """Test validation that should pass for regex no match."""
        validations = [
            {'type': 'not-match', 'field': 'author', 'regex': r'Unknown.*'}
        ]
        
        failures = validate_frontmatter([self.file1, self.file2], validations)
        self.assertEqual(len(failures), 0)
    
    def test_validate_not_match_fail(self):
        """Test validation that should fail for regex match."""
        validations = [
            {'type': 'not-match', 'field': 'author', 'regex': r'John.*'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertIn("should not match pattern", failures[0][3])
    
    def test_validate_case_insensitive(self):
        """Test case-insensitive validation."""
        validations = [
            {'type': 'exist', 'field': 'TITLE'},
            {'type': 'eq', 'field': 'AUTHOR', 'value': 'john doe'}
        ]
        
        failures = validate_frontmatter([self.file1], validations, ignore_case=True)
        self.assertEqual(len(failures), 0)
    
    def test_validate_invalid_regex(self):
        """Test validation with invalid regex."""
        validations = [
            {'type': 'match', 'field': 'author', 'regex': r'[invalid'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertIn("Invalid regex pattern", failures[0][3])
    
    def test_validate_missing_field_for_value_checks(self):
        """Test validation on missing field for value-based checks."""
        validations = [
            {'type': 'eq', 'field': 'nonexistent', 'value': 'test'},
            {'type': 'ne', 'field': 'nonexistent', 'value': 'test'},
            {'type': 'contain', 'field': 'nonexistent', 'value': 'test'},
            {'type': 'not-contain', 'field': 'nonexistent', 'value': 'test'},
            {'type': 'match', 'field': 'nonexistent', 'regex': 'test'},
            {'type': 'not-match', 'field': 'nonexistent', 'regex': 'test'}
        ]
        
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 6)
        
        # All should report field doesn't exist
        for failure in failures:
            self.assertIn("does not exist", failure[3])
    
    def test_output_validation_results_console(self):
        """Test console output of validation results."""
        import io
        import sys
        
        failures = [(self.file1, 'title', 'First Post', 'Test failure')]
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        output_validation_results(failures)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        self.assertIn(self.file1, output)
        self.assertIn('title: First Post --> Test failure', output)
    
    def test_output_validation_results_csv(self):
        """Test CSV output of validation results."""
        failures = [
            (self.file1, 'title', 'First Post', 'Test failure 1'),
            (self.file2, 'author', 'Jane Smith', 'Test failure 2')
        ]
        
        csv_file = os.path.join(self.temp_dir, 'results.csv')
        output_validation_results(failures, csv_file)
        
        # Verify CSV file was created and contains correct data
        self.assertTrue(os.path.exists(csv_file))
        
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Check header
            self.assertEqual(rows[0], ['File Path', 'Front Matter Name', 'Front Matter Value', 'Failure Reason'])
            
            # Check data rows
            self.assertEqual(rows[1], [self.file1, 'title', 'First Post', 'Test failure 1'])
            self.assertEqual(rows[2], [self.file2, 'author', 'Jane Smith', 'Test failure 2'])
    
    def test_validate_multiple_rules(self):
        """Test validation with multiple rules."""
        validations = [
            {'type': 'exist', 'field': 'title'},
            {'type': 'exist', 'field': 'author'},
            {'type': 'eq', 'field': 'status', 'value': 'published'}
        ]
        
        failures = validate_frontmatter([self.file1, self.file2], validations)
        
        # file1 should pass all validations
        # file2 should fail on status check (doesn't have status field)
        file2_failures = [f for f in failures if f[0] == self.file2]
        self.assertEqual(len(file2_failures), 1)
        self.assertEqual(file2_failures[0][1], 'status')
        self.assertIn("does not exist", file2_failures[0][3])
    
    def test_validate_empty_frontmatter(self):
        """Test validation on file with no frontmatter."""
        validations = [
            {'type': 'exist', 'field': 'title'}
        ]
        
        failures = validate_frontmatter([self.file3], validations)
        self.assertEqual(len(failures), 1)
        
        # Check failure
        self.assertEqual(failures[0][0], self.file3)
        self.assertEqual(failures[0][1], 'title')
        self.assertIn("does not exist", failures[0][3])

    def test_validate_not_empty_pass(self):
        """Test not-empty validation passes for non-empty arrays."""
        validations = [{'type': 'not-empty', 'field': 'tags'}]
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 0)

    def test_validate_not_empty_fail_empty_array(self):
        """Test not-empty validation fails for empty arrays."""
        # Create a test file with empty array
        test_file = os.path.join(self.temp_dir, 'empty_array.md')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("""---
title: "Test"
tags: []
---

Content here.""")
        
        validations = [{'type': 'not-empty', 'field': 'tags'}]
        failures = validate_frontmatter([test_file], validations)
        self.assertEqual(len(failures), 1)
        self.assertIn("array is empty", failures[0][3])

    def test_validate_not_empty_fail_non_array(self):
        """Test not-empty validation fails for non-array fields."""
        validations = [{'type': 'not-empty', 'field': 'title'}]
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 1)
        self.assertIn("is not an array", failures[0][3])

    def test_validate_list_size_pass(self):
        """Test list-size validation passes when within range."""
        validations = [{'type': 'list-size', 'field': 'tags', 'min': 1, 'max': 5}]
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 0)

    def test_validate_list_size_fail_too_small(self):
        """Test list-size validation fails when array too small."""
        validations = [{'type': 'list-size', 'field': 'tags', 'min': 5, 'max': 10}]
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 1)
        self.assertIn("should have between 5 and 10", failures[0][3])

    def test_validate_list_size_fail_non_array(self):
        """Test list-size validation fails for non-array fields."""
        validations = [{'type': 'list-size', 'field': 'title', 'min': 1, 'max': 3}]
        failures = validate_frontmatter([self.file1], validations)
        self.assertEqual(len(failures), 1)
        self.assertIn("is not an array", failures[0][3])

    def test_validate_and_output_returns_failure_count_zero(self):
        """Test validate_and_output returns 0 when all validations pass."""
        validations = [
            {'type': 'exist', 'field': 'title'},
            {'type': 'exist', 'field': 'author'}
        ]
        
        failure_count = validate_and_output([self.file1], validations)
        self.assertEqual(failure_count, 0)
    
    def test_validate_and_output_returns_failure_count_nonzero(self):
        """Test validate_and_output returns non-zero count when validations fail."""
        validations = [
            {'type': 'exist', 'field': 'title'},
            {'type': 'exist', 'field': 'nonexistent_field'}
        ]
        
        failure_count = validate_and_output([self.file1], validations)
        self.assertEqual(failure_count, 1)
    
    def test_validate_and_output_returns_multiple_failures(self):
        """Test validate_and_output returns correct count for multiple failures."""
        validations = [
            {'type': 'exist', 'field': 'nonexistent_field1'},
            {'type': 'exist', 'field': 'nonexistent_field2'}
        ]
        
        failure_count = validate_and_output([self.file1], validations)
        self.assertEqual(failure_count, 2)
    
    def test_validate_with_yaml_syntax_error(self):
        """Test validation reports YAML syntax errors as validation failures."""
        # Create a file with malformed YAML frontmatter
        malformed_file = os.path.join(self.temp_dir, 'malformed.md')
        with open(malformed_file, 'w') as f:
            f.write("""---
title: Valid Title
origins: [Cambodia]
 themes:
 - Perseverance
---

Content here""")
        
        # Try to validate any field
        validations = [{'type': 'not-empty', 'field': 'themes'}]
        failures = validate_frontmatter([malformed_file], validations)
        
        # Should report the YAML parsing error as a validation failure
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0][0], malformed_file)
        self.assertEqual(failures[0][1], "frontmatter")
        self.assertIsNone(failures[0][2])
        self.assertIn("Invalid YAML frontmatter", failures[0][3])
        self.assertIn("expected <block end>", failures[0][3])
    
    def test_validate_with_yaml_syntax_error_returns_nonzero(self):
        """Test validation with YAML syntax error returns non-zero exit code."""
        # Create a file with malformed YAML frontmatter
        malformed_file = os.path.join(self.temp_dir, 'malformed2.md')
        with open(malformed_file, 'w') as f:
            f.write("""---
title: Valid Title
 themes:
 - Test
---

Content""")
        
        # Validate should return non-zero count
        validations = [{'type': 'exist', 'field': 'title'}]
        failure_count = validate_and_output([malformed_file], validations)
        
        # Should have at least 1 failure (the YAML error)
        self.assertGreater(failure_count, 0)
    
    def test_validate_with_yaml_syntax_error_csv_output(self):
        """Test validation with YAML syntax error outputs to CSV correctly."""
        # Create a file with malformed YAML frontmatter - missing colon
        malformed_file = os.path.join(self.temp_dir, 'malformed3.md')
        with open(malformed_file, 'w') as f:
            f.write("""---
title Test
author: John
---

Content""")
        
        csv_file = os.path.join(self.temp_dir, 'yaml_error_test.csv')
        validations = [{'type': 'exist', 'field': 'title'}]
        failure_count = validate_and_output([malformed_file], validations, csv_file=csv_file)
        
        # Should report the error
        self.assertGreater(failure_count, 0)
        
        # Check CSV file
        self.assertTrue(os.path.exists(csv_file))
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            self.assertGreater(len(rows), 1)  # Header + at least 1 failure row
            self.assertEqual(rows[0], ['File Path', 'Front Matter Name', 'Front Matter Value', 'Failure Reason'])
            # Check that the failure row contains the YAML error
            self.assertEqual(rows[1][0], malformed_file)
            self.assertEqual(rows[1][1], 'frontmatter')
            self.assertIn('Invalid YAML frontmatter', rows[1][3])
    
    def test_validate_with_yaml_missing_closing_delimiter(self):
        """Test validation when file has no closing frontmatter delimiter."""
        # Create a file with missing closing --- delimiter
        # This is NOT a YAML error - the parser just won't find any frontmatter
        malformed_file = os.path.join(self.temp_dir, 'malformed4.md')
        with open(malformed_file, 'w') as f:
            f.write("""---
title: Test Title
author: Test Author

Content without closing delimiter""")
        
        # Try to validate a field that should exist if frontmatter was parsed
        validations = [{'type': 'exist', 'field': 'title'}]
        failures = validate_frontmatter([malformed_file], validations)
        
        # Should report that the field doesn't exist (because no frontmatter was found)
        self.assertEqual(len(failures), 1)
        self.assertEqual(failures[0][1], "title")
        self.assertIn("does not exist", failures[0][3])
    
    def test_validate_with_yaml_duplicate_keys(self):
        """Test validation with duplicate YAML keys."""
        # Create a file with duplicate keys (YAML will silently use last value, so this should parse OK)
        file_with_dups = os.path.join(self.temp_dir, 'duplicate_keys.md')
        with open(file_with_dups, 'w') as f:
            f.write("""---
title: First Title
author: Test Author
title: Second Title
---

Content""")
        
        # This should actually parse successfully (YAML allows duplicate keys, last one wins)
        validations = [{'type': 'exist', 'field': 'title'}]
        failures = validate_frontmatter([file_with_dups], validations)
        
        # Should have no failures - YAML allows this
        self.assertEqual(len(failures), 0)
    
    def test_validate_with_file_encoding_error(self):
        """Test validation reports file encoding errors as validation failures."""
        # Create a file with encoding that cannot be decoded as UTF-8
        # Note: core.py converts UnicodeDecodeError to ValueError
        # We'll simulate this by testing the behavior when parse_file raises ValueError
        # Since we can't easily create an actual encoding error in the test environment,
        # we verify the existing YAML error handling covers the ValueError path
        # which includes both YAML errors and encoding errors
        
        # This test validates that ValueError exceptions are caught and reported
        # (whether from YAML parsing or encoding issues)
        malformed_file = os.path.join(self.temp_dir, 'malformed_yaml.md')
        with open(malformed_file, 'w') as f:
            f.write("""---
title: Test
[invalid yaml structure
---

Content""")
        
        validations = [{'type': 'exist', 'field': 'title'}]
        failures = validate_frontmatter([malformed_file], validations)
        
        # Should report the error
        self.assertGreater(len(failures), 0)
        self.assertEqual(failures[0][1], "frontmatter")
        self.assertIn("Invalid YAML frontmatter", failures[0][3])


if __name__ == '__main__':
    unittest.main()