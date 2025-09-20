"""
Test specs functionality.
"""

import unittest
import tempfile
import os
import yaml
from io import StringIO
from unittest.mock import patch
import sys
from fmu.specs import (
    save_specs_file,
    convert_read_args_to_options,
    convert_search_args_to_options,
    convert_validate_args_to_options,
    convert_update_args_to_options
)
from fmu.cli import main


class TestSpecsFunctionality(unittest.TestCase):
    """Test specs functionality."""

    def setUp(self):
        """Set up test files."""
        self.test_dir = tempfile.mkdtemp()
        self.specs_file = os.path.join(self.test_dir, 'test_specs.yaml')
        
    def tearDown(self):
        """Clean up test files."""
        if os.path.exists(self.specs_file):
            os.remove(self.specs_file)
        os.rmdir(self.test_dir)

    def test_save_specs_file_new_file(self):
        """Test saving specs to a new file."""
        patterns = ['*.md', 'docs/*.md']
        options = {'output': 'frontmatter', 'skip_heading': True}
        
        save_specs_file(self.specs_file, 'read', 'test read', patterns, options)
        
        # Verify file was created and has correct content
        self.assertTrue(os.path.exists(self.specs_file))
        
        with open(self.specs_file, 'r') as f:
            data = yaml.safe_load(f)
            
        expected = {
            'commands': [{
                'command': 'read',
                'description': 'test read',
                'patterns': patterns,
                'output': 'frontmatter',
                'skip_heading': True
            }]
        }
        
        self.assertEqual(data, expected)

    def test_save_specs_file_append_to_existing(self):
        """Test appending specs to an existing file."""
        # Create initial specs file
        initial_data = {
            'commands': [{
                'command': 'read',
                'description': 'existing read',
                'patterns': ['old/*.md']
            }]
        }
        
        with open(self.specs_file, 'w') as f:
            yaml.dump(initial_data, f)
        
        # Append new command
        patterns = ['new/*.md']
        options = {'name': 'tags', 'value': 'test'}
        
        save_specs_file(self.specs_file, 'search', 'test search', patterns, options)
        
        # Verify both commands exist
        with open(self.specs_file, 'r') as f:
            data = yaml.safe_load(f)
            
        self.assertEqual(len(data['commands']), 2)
        self.assertEqual(data['commands'][0]['command'], 'read')
        self.assertEqual(data['commands'][1]['command'], 'search')
        self.assertEqual(data['commands'][1]['description'], 'test search')

    def test_convert_read_args_to_options(self):
        """Test converting read arguments to options."""
        args = type('Args', (), {
            'output': 'frontmatter',
            'skip_heading': True
        })()
        
        options = convert_read_args_to_options(args)
        
        expected = {
            'output': 'frontmatter',
            'skip_heading': True
        }
        
        self.assertEqual(options, expected)

    def test_convert_read_args_to_options_defaults(self):
        """Test converting read arguments with default values."""
        args = type('Args', (), {
            'output': 'both',
            'skip_heading': False
        })()
        
        options = convert_read_args_to_options(args)
        
        # Default values should not be included
        self.assertEqual(options, {})

    def test_convert_search_args_to_options(self):
        """Test converting search arguments to options."""
        args = type('Args', (), {
            'name': 'tags',
            'value': 'test',
            'ignore_case': True,
            'regex': False,
            'csv_file': 'results.csv'
        })()
        
        options = convert_search_args_to_options(args)
        
        expected = {
            'name': 'tags',
            'value': 'test',
            'ignore_case': True,
            'csv': 'results.csv'
        }
        
        self.assertEqual(options, expected)

    def test_convert_validate_args_to_options(self):
        """Test converting validate arguments to options."""
        args = type('Args', (), {
            'exist': ['title', 'author'],
            'not_exist': ['draft'],
            'eq': [('status', 'published')],
            'match': [('date', r'\d{4}-\d{2}-\d{2}')],
            'ignore_case': True,
            'csv_file': 'validation.csv'
        })()
        
        options = convert_validate_args_to_options(args)
        
        expected = {
            'exist': ['title', 'author'],
            'not': ['draft'],
            'eq': ['status published'],
            'match': ['date \\d{4}-\\d{2}-\\d{2}'],
            'ignore_case': True,
            'csv': 'validation.csv'
        }
        
        self.assertEqual(options, expected)

    def test_convert_update_args_to_options(self):
        """Test converting update arguments to options."""
        args = type('Args', (), {
            'name': 'title',
            'case': 'Title Case',
            'replace': [('old', 'new')],
            'remove': ['test'],
            'deduplication': 'true',
            'ignore_case': False,
            'regex': True
        })()
        
        options = convert_update_args_to_options(args)
        
        expected = {
            'name': 'title',
            'case': 'Title Case',
            'replace': ['old new'],
            'remove': ['test'],
            'regex': True
        }
        
        self.assertEqual(options, expected)

    def capture_output(self, func):
        """Capture output from a function."""
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()
        try:
            func()
        finally:
            sys.stdout = old_stdout
        return captured_output.getvalue()

    @patch('sys.argv', ['fmu', 'read', '/tmp/test.md', '--save-specs', 'test read', '/tmp/test_specs.yaml'])
    def test_main_read_save_specs(self):
        """Test main function with read command and save-specs."""
        output = self.capture_output(main)
        self.assertIn('Specs saved to /tmp/test_specs.yaml', output)
        
        # Verify the specs file was created
        self.assertTrue(os.path.exists('/tmp/test_specs.yaml'))
        
        with open('/tmp/test_specs.yaml', 'r') as f:
            data = yaml.safe_load(f)
            
        self.assertEqual(len(data['commands']), 1)
        self.assertEqual(data['commands'][0]['command'], 'read')
        self.assertEqual(data['commands'][0]['description'], 'test read')
        
        # Clean up
        os.remove('/tmp/test_specs.yaml')

    @patch('sys.argv', ['fmu', 'search', '/tmp/test.md', '--name', 'tags', '--value', 'test', '--save-specs', 'test search', '/tmp/test_specs.yaml'])
    def test_main_search_save_specs(self):
        """Test main function with search command and save-specs."""
        output = self.capture_output(main)
        self.assertIn('Specs saved to /tmp/test_specs.yaml', output)
        
        # Verify the specs file was created
        self.assertTrue(os.path.exists('/tmp/test_specs.yaml'))
        
        with open('/tmp/test_specs.yaml', 'r') as f:
            data = yaml.safe_load(f)
            
        self.assertEqual(len(data['commands']), 1)
        self.assertEqual(data['commands'][0]['command'], 'search')
        self.assertEqual(data['commands'][0]['name'], 'tags')
        self.assertEqual(data['commands'][0]['value'], 'test')
        
        # Clean up
        os.remove('/tmp/test_specs.yaml')


if __name__ == '__main__':
    unittest.main()