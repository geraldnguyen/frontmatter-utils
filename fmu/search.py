"""
Search functionality for frontmatter in files.
"""

import csv
import os
import re
from typing import List, Dict, Any, Optional, Tuple
from .core import parse_file, get_files_from_patterns


def search_frontmatter(
    patterns: List[str],
    name: str,
    value: Optional[str] = None,
    ignore_case: bool = False,
    regex: bool = False,
    format_type: str = "yaml"
) -> List[Tuple[str, str, Any]]:
    """
    Search for frontmatter in files matching glob patterns.
    
    Args:
        patterns: List of glob patterns or file paths
        name: Name of the frontmatter field to search for
        value: Optional value to match (if None, just check for field presence)
        ignore_case: Whether to perform case-insensitive matching
        regex: Whether to use regex pattern matching for values
        format_type: The format of the frontmatter
        
    Returns:
        List of tuples (file_path, field_name, field_value)
    """
    results = []
    files = get_files_from_patterns(patterns)
    
    # Prepare search terms for case-insensitive comparison if needed
    search_name = name.lower() if ignore_case else name
    
    # Compile regex pattern if regex mode is enabled
    regex_pattern = None
    if regex and value:
        flags = re.IGNORECASE if ignore_case else 0
        try:
            regex_pattern = re.compile(value, flags)
        except re.error:
            # If regex is invalid, fall back to literal matching
            regex_pattern = None
    
    for file_path in files:
        try:
            frontmatter, _ = parse_file(file_path, format_type)
            if frontmatter is None:
                continue
                
            # Search through frontmatter fields
            for fm_name, fm_value in frontmatter.items():
                # Check if field name matches
                check_name = fm_name.lower() if ignore_case else fm_name
                if check_name == search_name:
                    # If no value specified, just match the field name
                    if value is None:
                        results.append((file_path, fm_name, fm_value))
                    else:
                        # Check if value matches (supports arrays and regex)
                        if _value_matches(fm_value, value, ignore_case, regex_pattern):
                            results.append((file_path, fm_name, fm_value))
                            
        except (FileNotFoundError, ValueError, UnicodeDecodeError):
            # Skip files that can't be processed
            continue
            
    return results


def _value_matches(fm_value: Any, search_value: str, ignore_case: bool, regex_pattern: Optional[re.Pattern]) -> bool:
    """
    Check if a frontmatter value matches the search criteria.
    
    Args:
        fm_value: The frontmatter value (can be scalar, list, etc.)
        search_value: The value to search for
        ignore_case: Whether to perform case-insensitive matching
        regex_pattern: Compiled regex pattern (None if not using regex)
        
    Returns:
        True if the value matches, False otherwise
    """
    # Handle array/list values
    if isinstance(fm_value, list):
        for item in fm_value:
            if _scalar_value_matches(item, search_value, ignore_case, regex_pattern):
                return True
        return False
    else:
        # Handle scalar values
        return _scalar_value_matches(fm_value, search_value, ignore_case, regex_pattern)


def _scalar_value_matches(item: Any, search_value: str, ignore_case: bool, regex_pattern: Optional[re.Pattern]) -> bool:
    """
    Check if a scalar value matches the search criteria.
    
    Args:
        item: The scalar value to check
        search_value: The value to search for
        ignore_case: Whether to perform case-insensitive matching
        regex_pattern: Compiled regex pattern (None if not using regex)
        
    Returns:
        True if the value matches, False otherwise
    """
    item_str = str(item)
    
    if regex_pattern:
        # Use regex matching
        return bool(regex_pattern.search(item_str))
    else:
        # Use literal matching
        check_value = item_str.lower() if ignore_case else item_str
        search_check = search_value.lower() if ignore_case else search_value
        return check_value == search_check


def output_search_results(
    results: List[Tuple[str, str, Any]],
    csv_file: Optional[str] = None
) -> None:
    """
    Output search results either to console or CSV file.
    
    Args:
        results: List of tuples (file_path, field_name, field_value)
        csv_file: Optional path to CSV file for output
    """
    if csv_file:
        # Output to CSV file
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['File Path', 'Front Matter Name', 'Front Matter Value'])
            # Write results
            for file_path, field_name, field_value in results:
                writer.writerow([file_path, field_name, field_value])
    else:
        # Output to console
        for file_path, field_name, field_value in results:
            print(f"{file_path}:")
            print(f"- {field_name}: {field_value}")


def search_and_output(
    patterns: List[str],
    name: str,
    value: Optional[str] = None,
    ignore_case: bool = False,
    regex: bool = False,
    csv_file: Optional[str] = None,
    format_type: str = "yaml"
) -> None:
    """
    Search for frontmatter and output results.
    
    Args:
        patterns: List of glob patterns or file paths
        name: Name of the frontmatter field to search for
        value: Optional value to match
        ignore_case: Whether to perform case-insensitive matching
        regex: Whether to use regex pattern matching for values
        csv_file: Optional path to CSV file for output
        format_type: The format of the frontmatter
    """
    results = search_frontmatter(patterns, name, value, ignore_case, regex, format_type)
    output_search_results(results, csv_file)