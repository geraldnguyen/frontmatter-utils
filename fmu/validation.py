"""
Validation functionality for frontmatter in files.
"""

import csv
import re
from typing import List, Dict, Any, Optional, Tuple, Union
from .core import parse_file, get_files_from_patterns


def validate_frontmatter(
    patterns: List[str],
    validations: List[Dict[str, Any]],
    ignore_case: bool = False,
    format_type: str = "yaml"
) -> List[Tuple[str, str, Any, str]]:
    """
    Validate frontmatter in files matching glob patterns.
    
    Args:
        patterns: List of glob patterns or file paths
        validations: List of validation rules
        ignore_case: Whether to perform case-insensitive matching
        format_type: The format of the frontmatter
        
    Returns:
        List of tuples (file_path, field_name, field_value, failure_reason) for failed validations
    """
    failures = []
    files = get_files_from_patterns(patterns)
    
    for file_path in files:
        try:
            frontmatter, _ = parse_file(file_path, format_type)
            if frontmatter is None:
                frontmatter = {}
                
            # Apply each validation rule
            for validation in validations:
                validation_type = validation['type']
                field_name = validation['field']
                
                if validation_type == 'exist':
                    failure = _validate_exist(frontmatter, field_name, ignore_case)
                elif validation_type == 'not':
                    failure = _validate_not_exist(frontmatter, field_name, ignore_case)
                elif validation_type == 'eq':
                    failure = _validate_equal(frontmatter, field_name, validation['value'], ignore_case)
                elif validation_type == 'ne':
                    failure = _validate_not_equal(frontmatter, field_name, validation['value'], ignore_case)
                elif validation_type == 'contain':
                    failure = _validate_contain(frontmatter, field_name, validation['value'], ignore_case)
                elif validation_type == 'not-contain':
                    failure = _validate_not_contain(frontmatter, field_name, validation['value'], ignore_case)
                elif validation_type == 'match':
                    failure = _validate_match(frontmatter, field_name, validation['regex'], ignore_case)
                elif validation_type == 'not-match':
                    failure = _validate_not_match(frontmatter, field_name, validation['regex'], ignore_case)
                elif validation_type == 'not-empty':
                    failure = _validate_not_empty(frontmatter, field_name, ignore_case)
                elif validation_type == 'list-size':
                    failure = _validate_list_size(frontmatter, field_name, validation['min'], validation['max'], ignore_case)
                else:
                    continue
                    
                if failure:
                    field_value = _get_field_value(frontmatter, field_name, ignore_case)
                    failures.append((file_path, field_name, field_value, failure))
                    
        except ValueError as e:
            # YAML parsing error or file encoding error - report as validation failure
            error_msg = str(e)
            # If the error message already starts with the prefix, use it as-is
            # Otherwise, add the prefix to make it clear this is a YAML/frontmatter issue
            if not error_msg.startswith("Invalid YAML frontmatter:"):
                failure_reason = f"Invalid YAML frontmatter: {error_msg}"
            else:
                failure_reason = error_msg
            failures.append((file_path, "frontmatter", None, failure_reason))
        except FileNotFoundError as e:
            # For file not found errors, report as validation failure
            failure_reason = f"File error: {str(e)}"
            failures.append((file_path, "file", None, failure_reason))
            
    return failures


def _get_field_value(frontmatter: Dict[str, Any], field_name: str, ignore_case: bool) -> Any:
    """Get the value of a field from frontmatter, handling case sensitivity."""
    if ignore_case:
        for fm_name, fm_value in frontmatter.items():
            if fm_name.lower() == field_name.lower():
                return fm_value
    else:
        return frontmatter.get(field_name)
    return None


def _validate_exist(frontmatter: Dict[str, Any], field_name: str, ignore_case: bool) -> Optional[str]:
    """Validate that a field exists."""
    if ignore_case:
        existing_fields = [name.lower() for name in frontmatter.keys()]
        if field_name.lower() not in existing_fields:
            return f"Field '{field_name}' does not exist"
    else:
        if field_name not in frontmatter:
            return f"Field '{field_name}' does not exist"
    return None


def _validate_not_exist(frontmatter: Dict[str, Any], field_name: str, ignore_case: bool) -> Optional[str]:
    """Validate that a field does not exist."""
    if ignore_case:
        existing_fields = [name.lower() for name in frontmatter.keys()]
        if field_name.lower() in existing_fields:
            return f"Field '{field_name}' should not exist"
    else:
        if field_name in frontmatter:
            return f"Field '{field_name}' should not exist"
    return None


def _validate_equal(frontmatter: Dict[str, Any], field_name: str, expected_value: str, ignore_case: bool) -> Optional[str]:
    """Validate that a field equals the expected value."""
    field_value = _get_field_value(frontmatter, field_name, ignore_case)
    
    if field_value is None:
        return f"Field '{field_name}' does not exist (required for equality check)"
    
    field_str = str(field_value)
    if ignore_case:
        if field_str.lower() != expected_value.lower():
            return f"Field '{field_name}' value '{field_str}' does not equal '{expected_value}'"
    else:
        if field_str != expected_value:
            return f"Field '{field_name}' value '{field_str}' does not equal '{expected_value}'"
    return None


def _validate_not_equal(frontmatter: Dict[str, Any], field_name: str, expected_value: str, ignore_case: bool) -> Optional[str]:
    """Validate that a field does not equal the expected value."""
    field_value = _get_field_value(frontmatter, field_name, ignore_case)
    
    if field_value is None:
        return f"Field '{field_name}' does not exist (required for non-equality check)"
    
    field_str = str(field_value)
    if ignore_case:
        if field_str.lower() == expected_value.lower():
            return f"Field '{field_name}' value '{field_str}' should not equal '{expected_value}'"
    else:
        if field_str == expected_value:
            return f"Field '{field_name}' value '{field_str}' should not equal '{expected_value}'"
    return None


def _validate_contain(frontmatter: Dict[str, Any], field_name: str, expected_value: str, ignore_case: bool) -> Optional[str]:
    """Validate that an array field contains the expected value."""
    field_value = _get_field_value(frontmatter, field_name, ignore_case)
    
    if field_value is None:
        return f"Field '{field_name}' does not exist (required for contain check)"
    
    if not isinstance(field_value, list):
        return f"Field '{field_name}' is not an array (required for contain check)"
    
    for item in field_value:
        item_str = str(item)
        if ignore_case:
            if item_str.lower() == expected_value.lower():
                return None
        else:
            if item_str == expected_value:
                return None
    
    return f"Field '{field_name}' array does not contain '{expected_value}'"


def _validate_not_contain(frontmatter: Dict[str, Any], field_name: str, expected_value: str, ignore_case: bool) -> Optional[str]:
    """Validate that an array field does not contain the expected value."""
    field_value = _get_field_value(frontmatter, field_name, ignore_case)
    
    if field_value is None:
        return f"Field '{field_name}' does not exist (required for not-contain check)"
    
    if not isinstance(field_value, list):
        return f"Field '{field_name}' is not an array (required for not-contain check)"
    
    for item in field_value:
        item_str = str(item)
        if ignore_case:
            if item_str.lower() == expected_value.lower():
                return f"Field '{field_name}' array should not contain '{expected_value}'"
        else:
            if item_str == expected_value:
                return f"Field '{field_name}' array should not contain '{expected_value}'"
    
    return None


def _validate_match(frontmatter: Dict[str, Any], field_name: str, regex_pattern: str, ignore_case: bool) -> Optional[str]:
    """Validate that a field matches the regex pattern."""
    field_value = _get_field_value(frontmatter, field_name, ignore_case)
    
    if field_value is None:
        return f"Field '{field_name}' does not exist (required for regex match)"
    
    field_str = str(field_value)
    flags = re.IGNORECASE if ignore_case else 0
    
    try:
        if not re.search(regex_pattern, field_str, flags):
            return f"Field '{field_name}' value '{field_str}' does not match pattern '{regex_pattern}'"
    except re.error as e:
        return f"Invalid regex pattern '{regex_pattern}': {e}"
    
    return None


def _validate_not_match(frontmatter: Dict[str, Any], field_name: str, regex_pattern: str, ignore_case: bool) -> Optional[str]:
    """Validate that a field does not match the regex pattern."""
    field_value = _get_field_value(frontmatter, field_name, ignore_case)
    
    if field_value is None:
        return f"Field '{field_name}' does not exist (required for regex non-match)"
    
    field_str = str(field_value)
    flags = re.IGNORECASE if ignore_case else 0
    
    try:
        if re.search(regex_pattern, field_str, flags):
            return f"Field '{field_name}' value '{field_str}' should not match pattern '{regex_pattern}'"
    except re.error as e:
        return f"Invalid regex pattern '{regex_pattern}': {e}"
    
    return None


def _validate_not_empty(frontmatter: Dict[str, Any], field_name: str, ignore_case: bool) -> Optional[str]:
    """Validate that a field is an array and has at least 1 value."""
    field_value = _get_field_value(frontmatter, field_name, ignore_case)
    
    if field_value is None:
        return f"Field '{field_name}' does not exist (required for not-empty check)"
    
    if not isinstance(field_value, list):
        return f"Field '{field_name}' is not an array (required for not-empty check)"
    
    if len(field_value) == 0:
        return f"Field '{field_name}' array is empty but should contain at least 1 value"
    
    return None


def _validate_list_size(frontmatter: Dict[str, Any], field_name: str, min_size: int, max_size: int, ignore_case: bool) -> Optional[str]:
    """Validate that a field is an array and has a count between min and max inclusively."""
    field_value = _get_field_value(frontmatter, field_name, ignore_case)
    
    if field_value is None:
        return f"Field '{field_name}' does not exist (required for list-size check)"
    
    if not isinstance(field_value, list):
        return f"Field '{field_name}' is not an array (required for list-size check)"
    
    actual_size = len(field_value)
    if actual_size < min_size or actual_size > max_size:
        return f"Field '{field_name}' array has {actual_size} items but should have between {min_size} and {max_size} items"
    
    return None


def output_validation_results(
    failures: List[Tuple[str, str, Any, str]],
    csv_file: Optional[str] = None
) -> None:
    """
    Output validation failure results either to console or CSV file.
    
    Args:
        failures: List of tuples (file_path, field_name, field_value, failure_reason)
        csv_file: Optional path to CSV file for output
    """
    if csv_file:
        # Output to CSV file
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(['File Path', 'Front Matter Name', 'Front Matter Value', 'Failure Reason'])
            # Write results
            for file_path, field_name, field_value, failure_reason in failures:
                writer.writerow([file_path, field_name, field_value, failure_reason])
    else:
        # Output to console
        for file_path, field_name, field_value, failure_reason in failures:
            print(f"{file_path}:")
            print(f"- \t{field_name}: {field_value} --> {failure_reason}")


def validate_and_output(
    patterns: List[str],
    validations: List[Dict[str, Any]],
    ignore_case: bool = False,
    csv_file: Optional[str] = None,
    format_type: str = "yaml"
) -> int:
    """
    Validate frontmatter and output results.
    
    Args:
        patterns: List of glob patterns or file paths
        validations: List of validation rules
        ignore_case: Whether to perform case-insensitive matching
        csv_file: Optional path to CSV file for output
        format_type: The format of the frontmatter
        
    Returns:
        Number of validation failures
    """
    failures = validate_frontmatter(patterns, validations, ignore_case, format_type)
    output_validation_results(failures, csv_file)
    return len(failures)