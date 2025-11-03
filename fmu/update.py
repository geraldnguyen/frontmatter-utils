"""
Update functionality for frontmatter fields.
"""

import re
import csv
import sys
import hashlib
import random
import string
from datetime import datetime
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


def _resolve_placeholder(placeholder: str, file_path: str, frontmatter: Dict[str, Any], content: str) -> Any:
    """
    Resolve a placeholder reference.
    
    Args:
        placeholder: Placeholder string (e.g., "$filename", "$frontmatter.title")
        file_path: Full path to the file
        frontmatter: Frontmatter dictionary
        content: Content string
        
    Returns:
        Resolved value
    """
    import os
    
    if placeholder == '$filename':
        return os.path.basename(file_path)
    elif placeholder == '$filepath':
        return file_path
    elif placeholder == '$content':
        return content
    elif placeholder.startswith('$frontmatter.'):
        # Extract field name and optional index
        pattern = r'\$frontmatter\.([a-zA-Z_][a-zA-Z0-9_]*)(?:\[(\d+)\])?'
        match = re.match(pattern, placeholder)
        if match:
            field_name = match.group(1)
            index_str = match.group(2)
            
            if field_name not in frontmatter:
                return placeholder  # Return placeholder if field not found
            
            value = frontmatter[field_name]
            
            if index_str is not None:
                # Array indexing
                index = int(index_str)
                if isinstance(value, list) and 0 <= index < len(value):
                    return value[index]
                else:
                    return placeholder
            else:
                return value
    
    return placeholder


def _parse_function_call(formula: str) -> tuple:
    """
    Parse a function call from a formula.
    
    Args:
        formula: Formula string starting with '='
        
    Returns:
        Tuple of (function_name, parameters)
    """
    # Remove the leading '='
    formula = formula[1:].strip()
    
    # Parse function name and parameters
    # Pattern: function_name(param1, param2, ...)
    match = re.match(r'([a-zA-Z_][a-zA-Z0-9_]*)\((.*)\)$', formula)
    if not match:
        return None, []
    
    function_name = match.group(1)
    params_str = match.group(2)
    
    # Parse parameters - handle quoted strings and nested commas
    parameters = []
    if params_str.strip():
        # Simple parameter parsing - split by comma but respect quotes
        current_param = []
        in_quotes = False
        quote_char = None
        
        for char in params_str:
            if char in ('"', "'") and not in_quotes:
                in_quotes = True
                quote_char = char
            elif char == quote_char and in_quotes:
                in_quotes = False
                quote_char = None
            elif char == ',' and not in_quotes:
                param = ''.join(current_param).strip()
                if param:
                    # Remove quotes if present
                    if (param.startswith('"') and param.endswith('"')) or \
                       (param.startswith("'") and param.endswith("'")):
                        param = param[1:-1]
                    parameters.append(param)
                current_param = []
                continue
            
            current_param.append(char)
        
        # Don't forget the last parameter
        param = ''.join(current_param).strip()
        if param:
            # Remove quotes if present
            if (param.startswith('"') and param.endswith('"')) or \
               (param.startswith("'") and param.endswith("'")):
                param = param[1:-1]
            parameters.append(param)
    
    return function_name, parameters


def _execute_function(function_name: str, parameters: List[Any]) -> Any:
    """
    Execute a built-in function.
    
    Args:
        function_name: Name of the function to execute
        parameters: List of parameters (already resolved)
        
    Returns:
        Result of function execution
    """
    if function_name == 'now':
        # Return current datetime in ISO 8601 format
        from datetime import timezone
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    
    elif function_name == 'list':
        # Return an empty list
        return []
    
    elif function_name == 'hash':
        # Create a hash of the given string with specified length
        if len(parameters) < 2:
            raise ValueError("hash() requires 2 parameters: string and hash_length")
        
        string_to_hash = str(parameters[0])
        try:
            hash_length = int(parameters[1])
        except (ValueError, TypeError):
            raise ValueError("hash_length must be an integer")
        
        # Create a deterministic hash using SHA256
        hash_obj = hashlib.sha256(string_to_hash.encode('utf-8'))
        hash_hex = hash_obj.hexdigest()
        
        # Use only alphanumeric characters and trim to requested length
        # Use the hex representation and convert to alphanumeric
        result = hash_hex[:hash_length]
        
        return result
    
    elif function_name == 'concat':
        # Concatenate all parameters
        return ''.join(str(param) for param in parameters)
    
    elif function_name == 'slice':
        # Slice a list with Python-like slicing semantics
        if len(parameters) < 2:
            raise ValueError("slice() requires at least 2 parameters: list and start")
        
        # First parameter should be a list
        input_list = parameters[0]
        if not isinstance(input_list, list):
            raise ValueError("First parameter of slice() must be a list")
        
        # Parse slice parameters
        try:
            start = int(parameters[1])
        except (ValueError, TypeError):
            raise ValueError("start parameter must be an integer")
        
        stop = None
        step = None
        
        if len(parameters) >= 3:
            try:
                stop = int(parameters[2])
            except (ValueError, TypeError):
                raise ValueError("stop parameter must be an integer")
        
        if len(parameters) >= 4:
            try:
                step = int(parameters[3])
            except (ValueError, TypeError):
                raise ValueError("step parameter must be an integer")
        
        # Perform the slice operation using Python's slice notation
        if stop is None and step is None:
            # slice(list, start)
            return input_list[start:]
        elif step is None:
            # slice(list, start, stop)
            return input_list[start:stop]
        else:
            # slice(list, start, stop, step)
            return input_list[start:stop:step]
    
    else:
        raise ValueError(f"Unknown function: {function_name}")


def evaluate_formula(
    formula: str,
    file_path: str,
    frontmatter: Dict[str, Any],
    content: str
) -> Any:
    """
    Evaluate a compute formula.
    
    Args:
        formula: Formula to evaluate (literal, placeholder, or function)
        file_path: Full path to the file
        frontmatter: Frontmatter dictionary
        content: Content string
        
    Returns:
        Evaluated result
    """
    # Check if it's a function call
    if formula.startswith('='):
        function_name, parameters = _parse_function_call(formula)
        if function_name:
            # Resolve parameters (they may contain placeholders)
            resolved_params = []
            for param in parameters:
                if param.startswith('$'):
                    resolved_params.append(_resolve_placeholder(param, file_path, frontmatter, content))
                else:
                    resolved_params.append(param)
            
            return _execute_function(function_name, resolved_params)
        else:
            # Invalid function syntax, treat as literal
            return formula
    
    # Check if it's a placeholder
    elif formula.startswith('$'):
        return _resolve_placeholder(formula, file_path, frontmatter, content)
    
    # Otherwise, it's a literal value
    else:
        return formula


def apply_compute_operation(
    frontmatter: Dict[str, Any],
    frontmatter_name: str,
    formula: str,
    file_path: str,
    content: str
) -> tuple:
    """
    Apply compute operation to frontmatter.
    
    Args:
        frontmatter: Frontmatter dictionary
        frontmatter_name: Name of frontmatter field
        formula: Formula to compute
        file_path: Full path to the file
        content: Content string
        
    Returns:
        Tuple of (updated_frontmatter, changes_made)
    """
    # Evaluate the formula
    computed_value = evaluate_formula(formula, file_path, frontmatter, content)
    
    changes_made = False
    
    # Check if frontmatter field exists
    if frontmatter_name in frontmatter:
        current_value = frontmatter[frontmatter_name]
        
        # If current value is a list and computed value is NOT a list, append the computed value
        # But if computed value IS a list, replace the entire list
        if isinstance(current_value, list) and not isinstance(computed_value, list):
            current_value.append(computed_value)
            frontmatter[frontmatter_name] = current_value
            changes_made = True
        else:
            # Replace the current value
            if frontmatter[frontmatter_name] != computed_value:
                frontmatter[frontmatter_name] = computed_value
                changes_made = True
    else:
        # Create the frontmatter field
        frontmatter[frontmatter_name] = computed_value
        changes_made = True
    
    return frontmatter, changes_made


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
            
            # Handle compute operations differently - they can create fields
            has_compute_operation = any(op['type'] == 'compute' for op in operations)
            
            # Skip if frontmatter field doesn't exist AND no compute operation
            if frontmatter_name not in frontmatter_data and not has_compute_operation:
                results.append({
                    'file_path': file_path,
                    'field': frontmatter_name,
                    'original_value': None,
                    'new_value': None,
                    'changes_made': False,
                    'reason': f"Field '{frontmatter_name}' does not exist"
                })
                continue
            
            current_value = frontmatter_data.get(frontmatter_name)
            
            # Apply operations in order
            for operation in operations:
                op_type = operation['type']
                
                if op_type == 'compute':
                    # Compute operations can create fields, so handle specially
                    frontmatter_data, op_changes = apply_compute_operation(
                        frontmatter_data,
                        frontmatter_name,
                        operation['formula'],
                        file_path,
                        content
                    )
                    if op_changes:
                        changes_made = True
                    current_value = frontmatter_data.get(frontmatter_name)
                    
                elif op_type == 'case':
                    if current_value is not None:
                        current_value = apply_case_transformation(current_value, operation['case_type'])
                        changes_made = True
                    
                elif op_type == 'replace':
                    if current_value is not None:
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
                    if current_value is not None:
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
            
            # Update frontmatter_data with current_value (except for compute which already updated it)
            if not has_compute_operation or any(op['type'] != 'compute' for op in operations):
                # Handle removal of scalar fields
                if current_value is None and not isinstance(original_value, list):
                    # Remove the field entirely
                    if frontmatter_name in frontmatter_data:
                        del frontmatter_data[frontmatter_name]
                        changes_made = True
                else:
                    # Update the field
                    if frontmatter_name in frontmatter_data or current_value is not None:
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
                                new_frontmatter = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
                                new_content = f"---\n{new_frontmatter}---\n{content}"
                            else:
                                # No closing delimiter found, append to end
                                new_frontmatter = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
                                new_content = f"---\n{new_frontmatter}---\n{content}"
                        else:
                            # No frontmatter originally, add it
                            new_frontmatter = yaml.dump(frontmatter_data, default_flow_style=False, allow_unicode=True, sort_keys=False)
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
                    'new_value': frontmatter_data.get(frontmatter_name),
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