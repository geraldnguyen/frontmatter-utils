"""
Update functionality for frontmatter fields.
"""

import re
import csv
import sys
from typing import List, Dict, Any, Union, Optional
from .core import parse_file, get_files_from_patterns
import yaml


def transform_case(value: str, case_type: str) -> str:
    """Transform a string to the specified case."""
    if case_type == 'upper':
        return value.upper()
    elif case_type == 'lower':
        return value.lower()
    elif case_type == 'Sentence case':
        return value.capitalize()
    elif case_type == 'Title Case':
        # Handle contractions properly by using a custom title case logic
        return _title_case_with_contractions(value)
    elif case_type == 'snake_case':
        # Convert to snake_case
        # First, handle camelCase by inserting underscores before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', value)
        # Then handle sequences of uppercase letters
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
        # Replace spaces and hyphens with underscores, collapse multiple
        s3 = re.sub(r'[-\s]+', '_', s2)
        # Remove any double underscores
        s4 = re.sub(r'_+', '_', s3)
        return s4.lower()
    elif case_type == 'kebab-case':
        # Convert to kebab-case
        # First, handle camelCase by inserting hyphens before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', value)
        # Then handle sequences of uppercase letters
        s2 = re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1)
        # Replace spaces and underscores with hyphens, collapse multiple
        s3 = re.sub(r'[_\s]+', '-', s2)
        # Remove any double hyphens
        s4 = re.sub(r'-+', '-', s3)
        return s4.lower()
    else:
        return value


def _title_case_with_contractions(value: str) -> str:
    """
    Convert to title case while properly handling contractions.
    
    This fixes the bug where contractions like "can't" become "Can'T" instead of "Can't".
    """
    # Split into words
    words = value.split()
    result_words = []
    
    for word in words:
        # Check if this word contains an apostrophe (potential contraction)
        if "'" in word:
            # Handle contractions specially
            parts = word.split("'")
            if len(parts) == 2:
                # Standard contraction like "can't", "aren't", etc.
                first_part = parts[0].capitalize()
                second_part = parts[1].lower()  # Keep the part after apostrophe lowercase
                result_words.append(f"{first_part}'{second_part}")
            else:
                # Multiple apostrophes or other cases, just capitalize normally
                result_words.append(word.capitalize())
        else:
            # Regular word, capitalize normally
            result_words.append(word.capitalize())
    
    return ' '.join(result_words)


def apply_replace_operation(value: Any, from_val: str, to_val: str, ignore_case: bool = False, use_regex: bool = False) -> Any:
    """Apply replace operation to a value or list of values."""
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str):
                result.append(apply_replace_operation(item, from_val, to_val, ignore_case, use_regex))
            else:
                result.append(item)
        return result
    elif isinstance(value, str):
        if use_regex:
            flags = re.IGNORECASE if ignore_case else 0
            try:
                return re.sub(from_val, to_val, value, flags=flags)
            except re.error:
                # Invalid regex, treat as literal string
                return value
        else:
            # For non-regex, do substring replacement
            if ignore_case:
                # Case insensitive substring replacement
                # Use a regex with re.IGNORECASE for case-insensitive replacement
                pattern = re.escape(from_val)
                return re.sub(pattern, to_val, value, flags=re.IGNORECASE)
            else:
                # Case sensitive substring replacement
                return value.replace(from_val, to_val)
    else:
        return value


def apply_remove_operation(value: Any, remove_val: str, ignore_case: bool = False, use_regex: bool = False) -> Any:
    """Apply remove operation to a value or list of values."""
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str):
                should_remove = False
                if use_regex:
                    flags = re.IGNORECASE if ignore_case else 0
                    try:
                        should_remove = bool(re.search(remove_val, item, flags=flags))
                    except re.error:
                        # Invalid regex, treat as literal string
                        should_remove = False
                else:
                    if ignore_case:
                        should_remove = item.lower() == remove_val.lower()
                    else:
                        should_remove = item == remove_val
                
                if not should_remove:
                    result.append(item)
            else:
                result.append(item)
        return result
    elif isinstance(value, str):
        should_remove = False
        if use_regex:
            flags = re.IGNORECASE if ignore_case else 0
            try:
                should_remove = bool(re.search(remove_val, value, flags=flags))
            except re.error:
                # Invalid regex, treat as literal string
                should_remove = False
        else:
            if ignore_case:
                should_remove = value.lower() == remove_val.lower()
            else:
                should_remove = value == remove_val
        
        # For scalar values, return None to indicate removal
        return None if should_remove else value
    else:
        return value


def apply_case_transformation(value: Any, case_type: str) -> Any:
    """Apply case transformation to a value or list of values."""
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str):
                result.append(transform_case(item, case_type))
            else:
                result.append(item)
        return result
    elif isinstance(value, str):
        return transform_case(value, case_type)
    else:
        return value


def deduplicate_array(value: Any) -> Any:
    """Remove exact duplicates from array values."""
    if isinstance(value, list):
        seen = set()
        result = []
        for item in value:
            # Use a tuple representation for hashability
            key = tuple(item) if isinstance(item, list) else item
            if key not in seen:
                seen.add(key)
                result.append(item)
        return result
    else:
        return value


def update_frontmatter(
    patterns: List[str],
    frontmatter_name: str,
    operations: List[Dict[str, Any]],
    deduplication: bool = True,
    format_type: str = "yaml"
) -> List[Dict[str, Any]]:
    """
    Update frontmatter in files.
    
    Args:
        patterns: List of glob patterns or file paths
        frontmatter_name: Name of frontmatter field to update
        operations: List of update operations to apply
        deduplication: Whether to deduplicate array values (applied last)
        format_type: Format type (default: 'yaml')
    
    Returns:
        List of update results with file paths and changes made
    """
    files = get_files_from_patterns(patterns)
    results = []
    
    for file_path in files:
        try:
            # Parse the file
            frontmatter_data, content = parse_file(file_path, format_type)
            
            if frontmatter_data is None:
                frontmatter_data = {}
            
            # Track if any changes were made
            changes_made = False
            original_value = frontmatter_data.get(frontmatter_name)
            
            # Skip if frontmatter field doesn't exist
            if frontmatter_name not in frontmatter_data:
                results.append({
                    'file_path': file_path,
                    'field': frontmatter_name,
                    'original_value': None,
                    'new_value': None,
                    'changes_made': False,
                    'reason': f"Field '{frontmatter_name}' does not exist"
                })
                continue
            
            current_value = frontmatter_data[frontmatter_name]
            
            # Apply operations in order
            for operation in operations:
                op_type = operation['type']
                
                if op_type == 'case':
                    current_value = apply_case_transformation(current_value, operation['case_type'])
                    changes_made = True
                    
                elif op_type == 'replace':
                    new_value = apply_replace_operation(
                        current_value,
                        operation['from'],
                        operation['to'],
                        operation.get('ignore_case', False),
                        operation.get('regex', False)
                    )
                    if new_value != current_value:
                        current_value = new_value
                        changes_made = True
                        
                elif op_type == 'remove':
                    new_value = apply_remove_operation(
                        current_value,
                        operation['value'],
                        operation.get('ignore_case', False),
                        operation.get('regex', False)
                    )
                    if new_value != current_value:
                        current_value = new_value
                        changes_made = True
                        
                elif op_type == 'deduplication':
                    # Handle deduplication as a standalone operation
                    if isinstance(current_value, list):
                        deduplicated_value = deduplicate_array(current_value)
                        if deduplicated_value != current_value:
                            current_value = deduplicated_value
                            changes_made = True
            
            # Apply deduplication last if requested
            if deduplication and isinstance(current_value, list):
                deduplicated_value = deduplicate_array(current_value)
                if deduplicated_value != current_value:
                    current_value = deduplicated_value
                    changes_made = True
            
            # Handle removal of scalar fields
            if current_value is None and not isinstance(original_value, list):
                # Remove the field entirely
                del frontmatter_data[frontmatter_name]
                changes_made = True
            else:
                # Update the field
                frontmatter_data[frontmatter_name] = current_value
            
            # Save changes back to file if any were made
            if changes_made:
                try:
                    # Read the original file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    # Reconstruct the file with updated frontmatter
                    if format_type == 'yaml':
                        # Extract the frontmatter delimiter
                        if original_content.startswith('---\n'):
                            # Find the closing delimiter
                            end_pos = original_content.find('\n---\n', 4)
                            if end_pos != -1:
                                # Reconstruct with updated frontmatter
                                new_frontmatter = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
                                new_content = f"---\n{new_frontmatter}---\n{content}"
                            else:
                                # No closing delimiter found, append to end
                                new_frontmatter = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
                                new_content = f"---\n{new_frontmatter}---\n{content}"
                        else:
                            # No frontmatter originally, add it
                            new_frontmatter = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True)
                            new_content = f"---\n{new_frontmatter}---\n{original_content}"
                    else:
                        # For other formats, this would need additional implementation
                        new_content = original_content
                    
                    # Write back to file
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                except Exception as e:
                    results.append({
                        'file_path': file_path,
                        'field': frontmatter_name,
                        'original_value': original_value,
                        'new_value': current_value,
                        'changes_made': False,
                        'reason': f"Error saving file: {e}"
                    })
                    continue
            
            if changes_made:
                results.append({
                    'file_path': file_path,
                    'field': frontmatter_name,
                    'original_value': original_value,
                    'new_value': current_value if frontmatter_name in frontmatter_data else None,
                    'changes_made': changes_made,
                    'reason': 'Updated successfully'
                })
            
        except Exception as e:
            results.append({
                'file_path': file_path,
                'field': frontmatter_name,
                'original_value': None,
                'new_value': None,
                'changes_made': False,
                'reason': f"Error processing file: {e}"
            })
    
    return results


def update_and_output(
    patterns: List[str],
    frontmatter_name: str,
    operations: List[Dict[str, Any]],
    deduplication: bool = True,
    format_type: str = "yaml"
):
    """
    Update frontmatter and output results.
    
    Args:
        patterns: List of glob patterns or file paths
        frontmatter_name: Name of frontmatter field to update
        operations: List of update operations to apply
        deduplication: Whether to deduplicate array values
        format_type: Format type (default: 'yaml')
    """
    results = update_frontmatter(patterns, frontmatter_name, operations, deduplication, format_type)
    
    # Output results to console
    for result in results:
        file_path = result['file_path']
        changes_made = result['changes_made']
        reason = result['reason']
        
        if changes_made:
            print(f"{file_path}: Updated '{frontmatter_name}' - {reason}")
        else:
            print(f"{file_path}: No changes to '{frontmatter_name}' - {reason}")