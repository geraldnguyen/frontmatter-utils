"""
Core frontmatter parsing functionality for fmu.
"""

import re
import yaml
from typing import Dict, Any, Tuple, Optional
import glob
import os


def parse_frontmatter(content: str, format_type: str = "yaml") -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Parse frontmatter from content string.
    
    Args:
        content: The file content as a string
        format_type: The format of the frontmatter (currently only 'yaml' supported)
        
    Returns:
        Tuple of (frontmatter_dict, remaining_content)
    """
    if format_type.lower() != "yaml":
        raise ValueError(f"Format '{format_type}' not supported. Currently only 'yaml' is supported.")
    
    # Look for YAML frontmatter delimited by ---
    pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)$'
    match = re.match(pattern, content, re.DOTALL)
    
    if not match:
        # No frontmatter found
        return None, content
        
    frontmatter_content = match.group(1)
    remaining_content = match.group(2)
    
    try:
        frontmatter = yaml.safe_load(frontmatter_content)
        return frontmatter, remaining_content
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML frontmatter: {e}")


def extract_content(content: str, format_type: str = "yaml") -> str:
    """
    Extract only the content (without frontmatter) from a string.
    
    Args:
        content: The file content as a string
        format_type: The format of the frontmatter
        
    Returns:
        The content without frontmatter
    """
    _, content_only = parse_frontmatter(content, format_type)
    return content_only


def parse_file(file_path: str, format_type: str = "yaml") -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Parse frontmatter from a file.
    
    Args:
        file_path: Path to the file to parse
        format_type: The format of the frontmatter
        
    Returns:
        Tuple of (frontmatter_dict, content)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return parse_frontmatter(content, format_type)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {file_path}")
    except UnicodeDecodeError:
        raise ValueError(f"Unable to decode file as UTF-8: {file_path}")


def get_files_from_patterns(patterns: list) -> list:
    """
    Get list of files from glob patterns.
    
    Args:
        patterns: List of glob patterns or file paths
        
    Returns:
        List of file paths
    """
    files = []
    for pattern in patterns:
        if os.path.isfile(pattern):
            files.append(pattern)
        elif os.path.isdir(pattern):
            # If it's a directory, add all files in it
            for root, _, filenames in os.walk(pattern):
                for filename in filenames:
                    files.append(os.path.join(root, filename))
        else:
            # Treat as glob pattern
            matched_files = glob.glob(pattern, recursive=True)
            files.extend(matched_files)
    
    # Remove duplicates and sort
    return sorted(list(set(files)))