"""
Unit tests for fmu search functionality.
"""

import unittest
import tempfile
import os
import csv
from fmu.search import search_frontmatter, output_search_results, search_and_output


class TestSearchFunctionality(unittest.TestCase):
    
    def setUp(self):
        """Set up test files."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create test files with different frontmatter
        self.file1 = os.path.join(self.temp_dir, 'post1.md')
        with open(self.file1, 'w') as f:
            f.write("""---
title: First Post
author: John Doe
category: programming
tags: [python, testing]
---

Content of first post.""")
        
        self.file2 = os.path.join(self.temp_dir, 'post2.md')
        with open(self.file2, 'w') as f:
            f.write("""---
title: Second Post
author: Jane Smith
category: design
tags: [ui, ux]
---

Content of second post.""")
        
        self.file3 = os.path.join(self.temp_dir, 'post3.md')
        with open(self.file3, 'w') as f:
            f.write("""---
title: Third Post
author: john doe
category: Programming
---

Content of third post.""")
    
    def tearDown(self):
        """Clean up test files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_search_by_field_name(self):
        """Test searching by field name only."""
        results = search_frontmatter([self.temp_dir], 'title')
        
        self.assertEqual(len(results), 3)
        # Check that all files have title field
        file_paths = [result[0] for result in results]
        self.assertIn(self.file1, file_paths)
        self.assertIn(self.file2, file_paths)
        self.assertIn(self.file3, file_paths)
    
    def test_search_by_field_name_and_value(self):
        """Test searching by field name and value."""
        results = search_frontmatter([self.temp_dir], 'author', 'John Doe')
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], self.file1)
        self.assertEqual(results[0][1], 'author')
        self.assertEqual(results[0][2], 'John Doe')
    
    def test_search_case_insensitive(self):
        """Test case-insensitive search."""
        # Search for "john doe" with ignore_case=True
        results = search_frontmatter([self.temp_dir], 'author', 'john doe', ignore_case=True)
        
        self.assertEqual(len(results), 2)
        file_paths = [result[0] for result in results]
        self.assertIn(self.file1, file_paths)  # "John Doe"
        self.assertIn(self.file3, file_paths)  # "john doe"
    
    def test_search_case_sensitive(self):
        """Test case-sensitive search."""
        results = search_frontmatter([self.temp_dir], 'author', 'john doe', ignore_case=False)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], self.file3)
    
    def test_search_field_name_case_insensitive(self):
        """Test case-insensitive field name search."""
        results = search_frontmatter([self.temp_dir], 'CATEGORY', 'programming', ignore_case=True)
        
        self.assertEqual(len(results), 2)
        file_paths = [result[0] for result in results]
        self.assertIn(self.file1, file_paths)  # category: programming
        self.assertIn(self.file3, file_paths)  # category: Programming
    
    def test_search_no_matches(self):
        """Test search with no matches."""
        results = search_frontmatter([self.temp_dir], 'nonexistent')
        
        self.assertEqual(len(results), 0)
    
    def test_output_search_results_console(self):
        """Test console output of search results."""
        import io
        import sys
        
        results = [(self.file1, 'title', 'First Post')]
        
        # Capture stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        output_search_results(results)
        
        # Restore stdout
        sys.stdout = sys.__stdout__
        
        output = captured_output.getvalue()
        self.assertIn(self.file1, output)
        self.assertIn('title: First Post', output)
    
    def test_output_search_results_csv(self):
        """Test CSV output of search results."""
        results = [
            (self.file1, 'title', 'First Post'),
            (self.file2, 'author', 'Jane Smith')
        ]
        
        csv_file = os.path.join(self.temp_dir, 'results.csv')
        output_search_results(results, csv_file)
        
        # Verify CSV file was created and contains correct data
        self.assertTrue(os.path.exists(csv_file))
        
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            rows = list(reader)
            
            # Check header
            self.assertEqual(rows[0], ['File Path', 'Front Matter Name', 'Front Matter Value'])
            
            # Check data rows
            self.assertEqual(rows[1], [self.file1, 'title', 'First Post'])
            self.assertEqual(rows[2], [self.file2, 'author', 'Jane Smith'])


if __name__ == '__main__':
    unittest.main()