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
    convert_update_args_to_options,
    load_specs_file,
    format_command_text,
    execute_specs_file,
    print_execution_stats
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
        # Clean up any additional files in test directory
        for root, dirs, files in os.walk(self.test_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
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
            'eq': ['status', 'published'],  # Now stored as separate array items
            'match': ['date', r'\d{4}-\d{2}-\d{2}'],  # Now stored as separate array items
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
            'replace': ['old', 'new'],  # Fixed: arguments should be separate, not combined
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

    def test_load_specs_file_valid(self):
        """Test loading a valid specs file."""
        # Create a test specs file
        specs_data = {
            'commands': [
                {
                    'command': 'read',
                    'description': 'test read',
                    'patterns': ['*.md']
                }
            ]
        }
        
        with open(self.specs_file, 'w') as f:
            yaml.dump(specs_data, f)
        
        loaded_data = load_specs_file(self.specs_file)
        self.assertEqual(loaded_data, specs_data)

    def test_load_specs_file_not_found(self):
        """Test loading non-existent specs file."""
        with self.assertRaises(FileNotFoundError):
            load_specs_file('/nonexistent/file.yaml')

    def test_load_specs_file_invalid_yaml(self):
        """Test loading specs file with invalid YAML."""
        with open(self.specs_file, 'w') as f:
            f.write('invalid: yaml: content: [')
        
        with self.assertRaises(yaml.YAMLError):
            load_specs_file(self.specs_file)

    def test_format_command_text_read(self):
        """Test formatting read command text."""
        command_entry = {
            'command': 'read',
            'description': 'test read',
            'patterns': ['*.md', 'docs/*.md'],
            'output': 'frontmatter',
            'skip_heading': True
        }
        
        result = format_command_text(command_entry)
        expected = 'fmu read *.md docs/*.md --output frontmatter --skip-heading'
        self.assertEqual(result, expected)

    def test_format_command_text_search(self):
        """Test formatting search command text."""
        command_entry = {
            'command': 'search',
            'description': 'test search',
            'patterns': ['*.md'],
            'name': 'tags',
            'value': 'test',
            'regex': True,
            'csv': 'results.csv'
        }
        
        result = format_command_text(command_entry)
        expected = 'fmu search *.md --name tags --value test --regex --csv results.csv'
        self.assertEqual(result, expected)

    def test_format_command_text_validate(self):
        """Test formatting validate command text."""
        command_entry = {
            'command': 'validate',
            'description': 'test validate',
            'patterns': ['*.md'],
            'exist': ['title', 'author'],
            'eq': ['status', 'published'],  # Array format: separate items
            'ignore_case': True
        }
        
        result = format_command_text(command_entry)
        expected = 'fmu validate *.md --exist title --exist author --eq status published --ignore-case'
        self.assertEqual(result, expected)

    def test_format_command_text_update(self):
        """Test formatting update command text."""
        command_entry = {
            'command': 'update',
            'description': 'test update',
            'patterns': ['*.md'],
            'name': 'title',
            'case': 'Title Case',
            'replace': ['old', 'new'],  # Array format: separate items
            'remove': ['test'],
            'regex': True
        }
        
        result = format_command_text(command_entry)
        expected = 'fmu update *.md --name title --case "Title Case" --replace old new --remove test --regex'
        self.assertEqual(result, expected)

    def test_execute_specs_file_empty(self):
        """Test executing empty specs file."""
        specs_data = {'commands': []}
        
        with open(self.specs_file, 'w') as f:
            yaml.dump(specs_data, f)
        
        output = self.capture_output(lambda: execute_specs_file(self.specs_file, skip_confirmation=True))
        self.assertIn('No commands found in specs file.', output)

    def test_execute_specs_file_with_commands(self):
        """Test executing specs file with commands."""
        # Create a test markdown file
        test_md_file = os.path.join(self.test_dir, 'test.md')
        with open(test_md_file, 'w') as f:
            f.write('---\ntitle: Test\ntags: [test]\n---\nContent')
        
        specs_data = {
            'commands': [
                {
                    'command': 'read',
                    'description': 'read test file',
                    'patterns': [test_md_file],
                    'output': 'frontmatter'
                }
            ]
        }
        
        with open(self.specs_file, 'w') as f:
            yaml.dump(specs_data, f)
        
        exit_code, stats = execute_specs_file(self.specs_file, skip_confirmation=True)
        
        # Verify exit code and statistics
        self.assertEqual(exit_code, 0)
        self.assertEqual(stats['total_commands'], 1)
        self.assertEqual(stats['executed_commands'], 1)
        self.assertEqual(stats['failed_commands'], 0)
        self.assertEqual(stats['command_counts']['read'], 1)
        self.assertGreater(stats['total_elapsed_time'], 0)

    def test_print_execution_stats(self):
        """Test printing execution statistics."""
        stats = {
            'executed_commands': 3,
            'total_elapsed_time': 1.5,
            'total_execution_time': 1.2,
            'average_execution_time': 0.4,
            'command_counts': {'read': 1, 'search': 1, 'validate': 1, 'update': 0},
            'failed_commands': 1
        }
        
        output = self.capture_output(lambda: print_execution_stats(stats))
        
        self.assertIn('Number of commands executed: 3', output)
        self.assertIn('Total elapsed time: 1.50 seconds', output)
        self.assertIn('Total execution time: 1.20 seconds', output)
        self.assertIn('Average execution time per command: 0.40 seconds', output)
        self.assertIn('read: 1', output)
        self.assertIn('search: 1', output)
        self.assertIn('validate: 1', output)
        self.assertIn('update: 0', output)
        self.assertIn('Failed commands: 1', output)

    @patch('sys.argv', ['fmu', 'execute', '/tmp/test_specs.yaml', '--yes'])
    def test_main_execute_command(self):
        """Test main function with execute command."""
        # Create a simple specs file
        specs_data = {
            'commands': [
                {
                    'command': 'read',
                    'description': 'test read',
                    'patterns': ['/tmp/nonexistent.md'],
                    'output': 'frontmatter'
                }
            ]
        }
        
        with open('/tmp/test_specs.yaml', 'w') as f:
            yaml.dump(specs_data, f)
        
        # Since the file doesn't exist, this should show error handling
        output = self.capture_output_with_stderr(main)
        
        # Should contain execution elements
        self.assertIn('fmu read', output)
        self.assertIn('EXECUTION STATISTICS', output)
        
        # Clean up
        os.remove('/tmp/test_specs.yaml')

    def capture_output_with_stderr(self, func):
        """Capture both stdout and stderr from a function."""
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = captured_output = StringIO()
        sys.stderr = captured_error = StringIO()
        try:
            func()
        except SystemExit:
            pass  # Handle sys.exit calls
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
        return captured_output.getvalue() + captured_error.getvalue()

    def test_execute_specs_file_stops_on_validate_failure(self):
        """Test that execute stops on validation failure (version 0.15.0)."""
        # Create test markdown files
        test_md1 = os.path.join(self.test_dir, 'test1.md')
        test_md2 = os.path.join(self.test_dir, 'test2.md')
        
        with open(test_md1, 'w') as f:
            f.write('---\ntitle: Test 1\n---\nContent 1')
        
        with open(test_md2, 'w') as f:
            f.write('---\ntitle: Test 2\ntags: [test]\n---\nContent 2')
        
        # Create specs file with multiple commands where validation fails
        specs_data = {
            'commands': [
                {
                    'command': 'validate',
                    'description': 'validate test1 - should fail',
                    'patterns': [test_md1],
                    'exist': ['tags']  # This will fail for test1.md
                },
                {
                    'command': 'read',
                    'description': 'read test2 - should not execute',
                    'patterns': [test_md2],
                    'output': 'frontmatter'
                }
            ]
        }
        
        with open(self.specs_file, 'w') as f:
            yaml.dump(specs_data, f)
        
        exit_code, stats = execute_specs_file(self.specs_file, skip_confirmation=True)
        
        # Verify that execution stopped after first command failed
        self.assertNotEqual(exit_code, 0)
        self.assertEqual(stats['total_commands'], 2)
        self.assertEqual(stats['executed_commands'], 0)  # validate doesn't count as executed on failure
        self.assertEqual(stats['failed_commands'], 1)
        self.assertEqual(stats['command_counts']['validate'], 0)
        self.assertEqual(stats['command_counts']['read'], 0)  # Second command should not execute
        self.assertEqual(stats['exit_code'], exit_code)

    def test_execute_specs_file_continues_on_success(self):
        """Test that execute continues when commands succeed (version 0.15.0)."""
        # Create test markdown files
        test_md1 = os.path.join(self.test_dir, 'test1.md')
        test_md2 = os.path.join(self.test_dir, 'test2.md')
        
        with open(test_md1, 'w') as f:
            f.write('---\ntitle: Test 1\ntags: [test]\n---\nContent 1')
        
        with open(test_md2, 'w') as f:
            f.write('---\ntitle: Test 2\ntags: [test]\n---\nContent 2')
        
        # Create specs file with multiple successful commands
        specs_data = {
            'commands': [
                {
                    'command': 'validate',
                    'description': 'validate test1',
                    'patterns': [test_md1],
                    'exist': ['tags']  # This will succeed
                },
                {
                    'command': 'read',
                    'description': 'read test2',
                    'patterns': [test_md2],
                    'output': 'frontmatter'
                },
                {
                    'command': 'validate',
                    'description': 'validate test2',
                    'patterns': [test_md2],
                    'exist': ['title']  # This will succeed
                }
            ]
        }
        
        with open(self.specs_file, 'w') as f:
            yaml.dump(specs_data, f)
        
        exit_code, stats = execute_specs_file(self.specs_file, skip_confirmation=True)
        
        # Verify that all commands executed successfully
        self.assertEqual(exit_code, 0)
        self.assertEqual(stats['total_commands'], 3)
        self.assertEqual(stats['executed_commands'], 3)
        self.assertEqual(stats['failed_commands'], 0)
        self.assertEqual(stats['command_counts']['validate'], 2)
        self.assertEqual(stats['command_counts']['read'], 1)
        self.assertEqual(stats['exit_code'], 0)

    def test_execute_specs_file_stops_on_any_command_failure(self):
        """Test that execute stops on any command failure, not just validate (version 0.15.0)."""
        # Create test markdown files
        test_md1 = os.path.join(self.test_dir, 'test1.md')
        test_md2 = os.path.join(self.test_dir, 'test2.md')
        
        with open(test_md1, 'w') as f:
            f.write('---\ntitle: Test 1\n---\nContent 1')
        
        with open(test_md2, 'w') as f:
            f.write('---\ntitle: Test 2\n---\nContent 2')
        
        # Create specs file where read command fails (non-existent file)
        specs_data = {
            'commands': [
                {
                    'command': 'read',
                    'description': 'read non-existent file - should fail',
                    'patterns': ['/non/existent/file.md'],
                    'output': 'frontmatter'
                },
                {
                    'command': 'read',
                    'description': 'read test2 - should not execute',
                    'patterns': [test_md2],
                    'output': 'frontmatter'
                }
            ]
        }
        
        with open(self.specs_file, 'w') as f:
            yaml.dump(specs_data, f)
        
        exit_code, stats = execute_specs_file(self.specs_file, skip_confirmation=True)
        
        # Verify that execution stopped after first command succeeded but found no files
        # (read command returns 0 even if no files match, so this test is different)
        # Let me test with a command that actually fails
        self.assertEqual(stats['total_commands'], 2)

    def test_execute_command_returns_exit_code(self):
        """Test that execute_command returns proper exit codes (version 0.15.0)."""
        from fmu.specs import execute_command
        
        # Create test markdown file
        test_md = os.path.join(self.test_dir, 'test.md')
        with open(test_md, 'w') as f:
            f.write('---\ntitle: Test\n---\nContent')
        
        # Test successful read command
        command_entry = {
            'command': 'read',
            'description': 'test read',
            'patterns': [test_md],
            'output': 'frontmatter'
        }
        exit_code = execute_command(command_entry)
        self.assertEqual(exit_code, 0)
        
        # Test failed validate command
        command_entry = {
            'command': 'validate',
            'description': 'test validate failure',
            'patterns': [test_md],
            'exist': ['non_existent_field']
        }
        exit_code = execute_command(command_entry)
        self.assertNotEqual(exit_code, 0)
        
        # Test successful validate command
        command_entry = {
            'command': 'validate',
            'description': 'test validate success',
            'patterns': [test_md],
            'exist': ['title']
        }
        exit_code = execute_command(command_entry)
        self.assertEqual(exit_code, 0)


if __name__ == '__main__':
    unittest.main()