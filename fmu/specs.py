"""
Specs file handling functionality.
"""

import os
import yaml
import time
from typing import Dict, Any, List, Tuple


def save_specs_file(
    specs_file: str,
    command: str,
    description: str,
    patterns: List[str],
    options: Dict[str, Any]
):
    """
    Save command specs to a YAML specs file.
    
    Args:
        specs_file: Path to the specs file
        command: Command name (read, search, validate, update)
        description: Short description of the command
        patterns: List of glob patterns or file paths
        options: Dictionary of command options
    """
    # Create the command entry
    command_entry = {
        'command': command,
        'description': description,
        'patterns': patterns
    }
    
    # Add options to the command entry
    command_entry.update(options)
    
    # Load existing specs file or create new structure
    specs_data = {'commands': []}
    if os.path.exists(specs_file):
        try:
            with open(specs_file, 'r', encoding='utf-8') as f:
                specs_data = yaml.safe_load(f) or {'commands': []}
            if 'commands' not in specs_data:
                specs_data['commands'] = []
        except (yaml.YAMLError, IOError):
            # If file exists but can't be read, start fresh
            specs_data = {'commands': []}
    
    # Append the new command
    specs_data['commands'].append(command_entry)
    
    # Save the updated specs file
    with open(specs_file, 'w', encoding='utf-8') as f:
        yaml.dump(specs_data, f, default_flow_style=False, indent=2)


def convert_read_args_to_options(args) -> Dict[str, Any]:
    """Convert read command arguments to options dictionary."""
    options = {}
    
    if hasattr(args, 'output') and args.output != 'both':
        options['output'] = args.output
    
    if hasattr(args, 'skip_heading') and args.skip_heading:
        options['skip_heading'] = True
    
    if hasattr(args, 'escape') and args.escape:
        options['escape'] = True
    
    if hasattr(args, 'template') and args.template:
        options['template'] = args.template
    
    if hasattr(args, 'file') and args.file:
        options['file'] = args.file
        
    return options


def convert_search_args_to_options(args) -> Dict[str, Any]:
    """Convert search command arguments to options dictionary."""
    options = {}
    
    if hasattr(args, 'name'):
        options['name'] = args.name
    
    if hasattr(args, 'value') and args.value:
        options['value'] = args.value
    
    if hasattr(args, 'ignore_case') and args.ignore_case:
        options['ignore_case'] = True
    
    if hasattr(args, 'regex') and args.regex:
        options['regex'] = True
        
    if hasattr(args, 'csv_file') and args.csv_file:
        options['csv'] = args.csv_file
        
    return options


def convert_validate_args_to_options(args) -> Dict[str, Any]:
    """Convert validate command arguments to options dictionary."""
    options = {}
    
    # Handle validation rules - store as arrays with separate items
    if hasattr(args, 'exist') and args.exist:
        options['exist'] = args.exist
        
    if hasattr(args, 'not_exist') and args.not_exist:
        options['not'] = args.not_exist
        
    if hasattr(args, 'eq') and args.eq:
        options['eq'] = []
        for field, value in args.eq:
            options['eq'].extend([field, value])
        
    if hasattr(args, 'ne') and args.ne:
        options['ne'] = []
        for field, value in args.ne:
            options['ne'].extend([field, value])
        
    if hasattr(args, 'contain') and args.contain:
        options['contain'] = []
        for field, value in args.contain:
            options['contain'].extend([field, value])
        
    if hasattr(args, 'not_contain') and args.not_contain:
        options['not_contain'] = []
        for field, value in args.not_contain:
            options['not_contain'].extend([field, value])
        
    if hasattr(args, 'match') and args.match:
        options['match'] = []
        for field, regex in args.match:
            options['match'].extend([field, regex])
        
    if hasattr(args, 'not_match') and args.not_match:
        options['not_match'] = []
        for field, regex in args.not_match:
            options['not_match'].extend([field, regex])
    
    # Handle new validation rules added in Version 0.8.0
    if hasattr(args, 'not_empty') and args.not_empty:
        options['not_empty'] = args.not_empty
        
    if hasattr(args, 'list_size') and args.list_size:
        options['list_size'] = []
        for field, min_str, max_str in args.list_size:
            options['list_size'].extend([field, min_str, max_str])
    
    if hasattr(args, 'ignore_case') and args.ignore_case:
        options['ignore_case'] = True
        
    if hasattr(args, 'csv_file') and args.csv_file:
        options['csv'] = args.csv_file
        
    return options


def convert_update_args_to_options(args) -> Dict[str, Any]:
    """Convert update command arguments to options dictionary."""
    options = {}
    
    if hasattr(args, 'name'):
        options['name'] = args.name
    
    if hasattr(args, 'deduplication') and args.deduplication != 'true':
        options['deduplication'] = args.deduplication
    
    if hasattr(args, 'case') and args.case:
        options['case'] = args.case
        
    if hasattr(args, 'replace') and args.replace:
        # Fix: Keep --replace arguments as separate items instead of combining them
        options['replace'] = []
        for from_val, to_val in args.replace:
            options['replace'].extend([from_val, to_val])
        
    if hasattr(args, 'remove') and args.remove:
        options['remove'] = args.remove
    
    if hasattr(args, 'ignore_case') and args.ignore_case:
        options['ignore_case'] = True
    
    if hasattr(args, 'regex') and args.regex:
        options['regex'] = True
        
    return options


def load_specs_file(specs_file: str) -> Dict[str, Any]:
    """
    Load specs from a YAML specs file.
    
    Args:
        specs_file: Path to the specs file
        
    Returns:
        Dict containing the specs data
        
    Raises:
        FileNotFoundError: If specs file doesn't exist
        yaml.YAMLError: If specs file has invalid YAML
    """
    if not os.path.exists(specs_file):
        raise FileNotFoundError(f"Specs file not found: {specs_file}")
    
    try:
        with open(specs_file, 'r', encoding='utf-8') as f:
            specs_data = yaml.safe_load(f)
        
        if not specs_data or 'commands' not in specs_data:
            raise ValueError(f"Invalid specs file format. Expected 'commands' key.")
            
        return specs_data
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Invalid YAML in specs file: {e}")


def format_command_text(command_entry: Dict[str, Any]) -> str:
    """
    Format a command entry for display.
    
    Args:
        command_entry: Dictionary containing command information
        
    Returns:
        Formatted command string
    """
    cmd = command_entry.get('command', '')
    description = command_entry.get('description', '')
    patterns = command_entry.get('patterns', [])
    
    # Build command text
    parts = [f"fmu {cmd}"]
    
    # Add patterns
    if patterns:
        for pattern in patterns:
            # Quote patterns that contain spaces
            if ' ' in pattern:
                parts.append(f'"{pattern}"')
            else:
                parts.append(pattern)
    
    # Helper function to format values with quotes if they contain spaces
    def format_value(value):
        if isinstance(value, str) and ' ' in value:
            return f'"{value}"'
        return str(value)
    
    # Add options
    for key, value in command_entry.items():
        if key in ['command', 'description', 'patterns']:
            continue
            
        if key == 'output' and value != 'both':
            parts.append(f"--output {format_value(value)}")
        elif key == 'skip_heading' and value:
            parts.append("--skip-heading")
        elif key == 'escape' and value:
            parts.append("--escape")
        elif key == 'template':
            parts.append(f"--template {format_value(value)}")
        elif key == 'file':
            parts.append(f"--file {format_value(value)}")
        elif key == 'name':
            parts.append(f"--name {format_value(value)}")
        elif key == 'value':
            parts.append(f"--value {format_value(value)}")
        elif key == 'ignore_case' and value:
            parts.append("--ignore-case")
        elif key == 'regex' and value:
            parts.append("--regex")
        elif key == 'csv':
            parts.append(f"--csv {format_value(value)}")
        elif key == 'exist' and isinstance(value, list):
            for exist_field in value:
                parts.append(f"--exist {format_value(exist_field)}")
        elif key == 'not' and isinstance(value, list):
            for not_field in value:
                parts.append(f"--not {format_value(not_field)}")
        elif key == 'eq' and isinstance(value, list):
            # Handle arrays: pairs of [field, value, field, value, ...]
            for i in range(0, len(value), 2):
                if i + 1 < len(value):
                    field, val = value[i], value[i + 1]
                    parts.append(f"--eq {format_value(field)} {format_value(val)}")
        elif key == 'ne' and isinstance(value, list):
            for i in range(0, len(value), 2):
                if i + 1 < len(value):
                    field, val = value[i], value[i + 1]
                    parts.append(f"--ne {format_value(field)} {format_value(val)}")
        elif key == 'contain' and isinstance(value, list):
            for i in range(0, len(value), 2):
                if i + 1 < len(value):
                    field, val = value[i], value[i + 1]
                    parts.append(f"--contain {format_value(field)} {format_value(val)}")
        elif key == 'not_contain' and isinstance(value, list):
            for i in range(0, len(value), 2):
                if i + 1 < len(value):
                    field, val = value[i], value[i + 1]
                    parts.append(f"--not-contain {format_value(field)} {format_value(val)}")
        elif key == 'match' and isinstance(value, list):
            for i in range(0, len(value), 2):
                if i + 1 < len(value):
                    field, regex = value[i], value[i + 1]
                    parts.append(f"--match {format_value(field)} {format_value(regex)}")
        elif key == 'not_match' and isinstance(value, list):
            for i in range(0, len(value), 2):
                if i + 1 < len(value):
                    field, regex = value[i], value[i + 1]
                    parts.append(f"--not-match {format_value(field)} {format_value(regex)}")
        elif key == 'not_empty' and isinstance(value, list):
            for field in value:
                parts.append(f"--not-empty {format_value(field)}")
        elif key == 'list_size' and isinstance(value, list):
            # Handle triplets: [field, min, max, field, min, max, ...]
            for i in range(0, len(value), 3):
                if i + 2 < len(value):
                    field, min_val, max_val = value[i], value[i + 1], value[i + 2]
                    parts.append(f"--list-size {format_value(field)} {min_val} {max_val}")
        elif key == 'case':
            parts.append(f"--case {format_value(value)}")
        elif key == 'replace' and isinstance(value, list):
            # Handle pairs: [from, to, from, to, ...]
            for i in range(0, len(value), 2):
                if i + 1 < len(value):
                    from_val, to_val = value[i], value[i + 1]
                    parts.append(f"--replace {format_value(from_val)} {format_value(to_val)}")
        elif key == 'remove' and isinstance(value, list):
            for remove_val in value:
                parts.append(f"--remove {format_value(remove_val)}")
        elif key == 'deduplication' and value != 'true':
            parts.append(f"--deduplication {value}")
    
    return ' '.join(parts)


def convert_specs_to_args(command_entry: Dict[str, Any]):
    """
    Convert a specs command entry to arguments object for command execution.
    
    Args:
        command_entry: Dictionary containing command information
        
    Returns:
        Arguments object that can be passed to command functions
    """
    # Create a basic args object
    args_dict = {
        'patterns': command_entry.get('patterns', []),
        'format': 'yaml'  # Default format
    }
    
    command = command_entry.get('command')
    
    if command == 'read':
        args_dict.update({
            'output': command_entry.get('output', 'both'),
            'skip_heading': command_entry.get('skip_heading', False),
            'escape': command_entry.get('escape', False),
            'template': command_entry.get('template'),
            'file': command_entry.get('file')
        })
    elif command == 'search':
        args_dict.update({
            'name': command_entry.get('name', ''),
            'value': command_entry.get('value'),
            'ignore_case': command_entry.get('ignore_case', False),
            'regex': command_entry.get('regex', False),
            'csv_file': command_entry.get('csv')
        })
    elif command == 'validate':
        args_dict.update({
            'exist': command_entry.get('exist'),
            'not_exist': command_entry.get('not'),
            'eq': _parse_validation_pairs_from_array(command_entry.get('eq', [])),
            'ne': _parse_validation_pairs_from_array(command_entry.get('ne', [])),
            'contain': _parse_validation_pairs_from_array(command_entry.get('contain', [])),
            'not_contain': _parse_validation_pairs_from_array(command_entry.get('not_contain', [])),
            'match': _parse_validation_pairs_from_array(command_entry.get('match', [])),
            'not_match': _parse_validation_pairs_from_array(command_entry.get('not_match', [])),
            'not_empty': command_entry.get('not_empty'),
            'list_size': _parse_list_size_triplets_from_array(command_entry.get('list_size', [])),
            'ignore_case': command_entry.get('ignore_case', False),
            'csv_file': command_entry.get('csv')
        })
    elif command == 'update':
        args_dict.update({
            'name': command_entry.get('name', ''),
            'case': command_entry.get('case'),
            'replace': _parse_update_pairs_from_array(command_entry.get('replace', [])),
            'remove': command_entry.get('remove'),
            'deduplication': command_entry.get('deduplication', 'true'),
            'ignore_case': command_entry.get('ignore_case', False),
            'regex': command_entry.get('regex', False)
        })
    
    # Convert to object
    return type('Args', (), args_dict)()


def _parse_validation_pairs(pairs: List[str]) -> List[Tuple[str, str]]:
    """Parse validation field-value pairs from specs format (legacy string format)."""
    if not pairs:
        return None
    
    result = []
    for pair in pairs:
        parts = pair.split(' ', 1)
        if len(parts) == 2:
            result.append((parts[0], parts[1]))
    return result if result else None


def _parse_validation_pairs_from_array(array: List[str]) -> List[Tuple[str, str]]:
    """Parse validation field-value pairs from array format."""
    if not array:
        return None
    
    result = []
    # Process pairs: [field, value, field, value, ...]
    for i in range(0, len(array), 2):
        if i + 1 < len(array):
            result.append((array[i], array[i + 1]))
    return result if result else None


def _parse_list_size_triplets_from_array(array: List[str]) -> List[Tuple[str, str, str]]:
    """Parse list-size field-min-max triplets from array format."""
    if not array:
        return None
    
    result = []
    # Process triplets: [field, min, max, field, min, max, ...]
    for i in range(0, len(array), 3):
        if i + 2 < len(array):
            result.append((array[i], array[i + 1], array[i + 2]))
    return result if result else None


def _parse_update_pairs(pairs: List[str]) -> List[Tuple[str, str]]:
    """Parse update from-to pairs from specs format (legacy string format)."""
    if not pairs:
        return None
    
    result = []
    for pair in pairs:
        parts = pair.split(' ', 1)
        if len(parts) == 2:
            result.append((parts[0], parts[1]))
    return result if result else None


def _parse_update_pairs_from_array(array: List[str]) -> List[Tuple[str, str]]:
    """Parse update from-to pairs from array format."""
    if not array:
        return None
    
    result = []
    # Process pairs: [from, to, from, to, ...]
    for i in range(0, len(array), 2):
        if i + 1 < len(array):
            result.append((array[i], array[i + 1]))
    return result if result else None


def execute_command(command_entry: Dict[str, Any]) -> int:
    """
    Execute a single command from specs.
    
    Args:
        command_entry: Dictionary containing command information
        
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        from .cli import cmd_read, cmd_search, cmd_validate, cmd_update, _parse_validation_args, _parse_update_args
        
        command = command_entry.get('command')
        args = convert_specs_to_args(command_entry)
        
        if command == 'read':
            cmd_read(
                patterns=args.patterns,
                output=args.output,
                skip_heading=args.skip_heading,
                format_type=args.format,
                escape=args.escape,
                template=args.template,
                file_output=args.file
            )
            return 0
        elif command == 'search':
            cmd_search(
                patterns=args.patterns,
                name=args.name,
                value=args.value,
                ignore_case=args.ignore_case,
                regex=args.regex,
                csv_file=args.csv_file,
                format_type=args.format
            )
            return 0
        elif command == 'validate':
            validations = _parse_validation_args(args)
            exit_code = cmd_validate(
                patterns=args.patterns,
                validations=validations,
                ignore_case=args.ignore_case,
                csv_file=args.csv_file,
                format_type=args.format
            )
            return exit_code
        elif command == 'update':
            operations = _parse_update_args(args)
            cmd_update(
                patterns=args.patterns,
                frontmatter_name=args.name,
                operations=operations,
                deduplication=(args.deduplication == 'true'),
                format_type=args.format
            )
            return 0
        else:
            print(f"Unknown command: {command}")
            return 1
            
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1


def execute_specs_file(
    specs_file: str, 
    skip_confirmation: bool = False
) -> Tuple[int, Dict[str, Any]]:
    """
    Execute all commands from a specs file.
    
    Args:
        specs_file: Path to the specs file
        skip_confirmation: Whether to skip user confirmation for each command
        
    Returns:
        Tuple of (exit_code, statistics_dict)
        - exit_code: 0 if all commands succeeded, non-zero if any command failed
        - statistics_dict: Dictionary containing execution statistics
    """
    # Load specs file
    specs_data = load_specs_file(specs_file)
    commands = specs_data.get('commands', [])
    
    # Initialize statistics
    stats = {
        'total_commands': len(commands),
        'executed_commands': 0,
        'failed_commands': 0,
        'command_counts': {'read': 0, 'search': 0, 'validate': 0, 'update': 0},
        'total_elapsed_time': 0,
        'total_execution_time': 0,
        'average_execution_time': 0,
        'exit_code': 0
    }
    
    if not commands:
        print("No commands found in specs file.")
        return 0, stats
    
    overall_start_time = time.time()
    total_execution_time = 0
    
    for i, command_entry in enumerate(commands, 1):
        command_name = command_entry.get('command', 'unknown')
        description = command_entry.get('description', 'No description')
        
        # Display command
        print("------------")
        print(format_command_text(command_entry))
        print("------------")
        print(f"Description: {description}")
        
        # Confirmation
        if not skip_confirmation:
            response = input("Proceed with the above command? Answer yes or no: ").strip().lower()
            if response not in ['yes', 'y']:
                print(f"Skipping command {i} of {len(commands)}")
                continue
        
        # Execute command
        print(f"Executing command {i} of {len(commands)}...")
        execution_start_time = time.time()
        
        exit_code = execute_command(command_entry)
        
        execution_end_time = time.time()
        execution_time = execution_end_time - execution_start_time
        total_execution_time += execution_time
        
        if exit_code == 0:
            stats['executed_commands'] += 1
            if command_name in stats['command_counts']:
                stats['command_counts'][command_name] += 1
            print(f"Command completed successfully in {execution_time:.2f} seconds.")
        else:
            stats['failed_commands'] += 1
            stats['exit_code'] = exit_code
            print(f"Command failed with exit code {exit_code}.")
            # Stop execution on non-zero exit code
            print(f"Stopping execution due to command failure.")
            overall_end_time = time.time()
            stats['total_elapsed_time'] = overall_end_time - overall_start_time
            stats['total_execution_time'] = total_execution_time
            if stats['executed_commands'] > 0:
                stats['average_execution_time'] = total_execution_time / stats['executed_commands']
            return exit_code, stats
        
        print()  # Add spacing between commands
    
    overall_end_time = time.time()
    stats['total_elapsed_time'] = overall_end_time - overall_start_time
    stats['total_execution_time'] = total_execution_time
    
    if stats['executed_commands'] > 0:
        stats['average_execution_time'] = total_execution_time / stats['executed_commands']
    
    return 0, stats


def print_execution_stats(stats: Dict[str, Any]):
    """
    Print execution statistics.
    
    Args:
        stats: Dictionary containing execution statistics
    """
    print("=" * 50)
    print("EXECUTION STATISTICS")
    print("=" * 50)
    print(f"Number of commands executed: {stats['executed_commands']}")
    print(f"Total elapsed time: {stats['total_elapsed_time']:.2f} seconds")
    print(f"Total execution time: {stats['total_execution_time']:.2f} seconds")
    
    if stats['executed_commands'] > 0:
        print(f"Average execution time per command: {stats['average_execution_time']:.2f} seconds")
    
    # Print command type counts
    print()
    print("Commands executed by type:")
    for cmd_type, count in stats['command_counts'].items():
        print(f"  {cmd_type}: {count}")
    
    if stats['failed_commands'] > 0:
        print(f"\nFailed commands: {stats['failed_commands']}")