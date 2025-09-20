"""
Specs file handling functionality.
"""

import os
import yaml
from typing import Dict, Any, List


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
    
    # Handle validation rules
    if hasattr(args, 'exist') and args.exist:
        options['exist'] = args.exist
        
    if hasattr(args, 'not_exist') and args.not_exist:
        options['not'] = args.not_exist
        
    if hasattr(args, 'eq') and args.eq:
        options['eq'] = [f"{field} {value}" for field, value in args.eq]
        
    if hasattr(args, 'ne') and args.ne:
        options['ne'] = [f"{field} {value}" for field, value in args.ne]
        
    if hasattr(args, 'contain') and args.contain:
        options['contain'] = [f"{field} {value}" for field, value in args.contain]
        
    if hasattr(args, 'not_contain') and args.not_contain:
        options['not_contain'] = [f"{field} {value}" for field, value in args.not_contain]
        
    if hasattr(args, 'match') and args.match:
        options['match'] = [f"{field} {regex}" for field, regex in args.match]
        
    if hasattr(args, 'not_match') and args.not_match:
        options['not_match'] = [f"{field} {regex}" for field, regex in args.not_match]
    
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
        options['replace'] = [f"{from_val} {to_val}" for from_val, to_val in args.replace]
        
    if hasattr(args, 'remove') and args.remove:
        options['remove'] = args.remove
    
    if hasattr(args, 'ignore_case') and args.ignore_case:
        options['ignore_case'] = True
    
    if hasattr(args, 'regex') and args.regex:
        options['regex'] = True
        
    return options