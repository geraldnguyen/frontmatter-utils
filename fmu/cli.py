"""
Command Line Interface for fmu.
"""

import argparse
import os
import sys
from typing import List, Dict, Any
from . import __version__
from .core import parse_file, get_files_from_patterns
from .search import search_and_output
from .validation import validate_and_output
from .update import update_and_output
from .specs import (
    save_specs_file, 
    convert_read_args_to_options,
    convert_search_args_to_options,
    convert_validate_args_to_options,
    convert_update_args_to_options
)


def _escape_string(text: str) -> str:
    """
    Escape special characters in a string.
    
    Args:
        text: String to escape
        
    Returns:
        Escaped string
    """
    if not text:
        return text
    # Escape special characters
    text = text.replace('\\', '\\\\')  # Backslash first
    text = text.replace('\n', '\\n')   # Newline
    text = text.replace('\r', '\\r')   # Carriage return
    text = text.replace('\t', '\\t')   # Tab
    text = text.replace("'", "\\'")    # Single quote
    text = text.replace('"', '\\"')    # Double quote
    return text


def _escape_frontmatter(frontmatter: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively escape special characters in frontmatter values.
    
    Args:
        frontmatter: Frontmatter dictionary
        
    Returns:
        Dictionary with escaped values
    """
    if not frontmatter:
        return frontmatter
    
    escaped = {}
    for key, value in frontmatter.items():
        if isinstance(value, str):
            escaped[key] = _escape_string(value)
        elif isinstance(value, list):
            escaped[key] = [_escape_string(v) if isinstance(v, str) else v for v in value]
        elif isinstance(value, dict):
            escaped[key] = _escape_frontmatter(value)
        else:
            escaped[key] = value
    return escaped


def _render_template(template: str, file_path: str, frontmatter: Dict[str, Any], content: str) -> str:
    """
    Render a template string with placeholders.
    
    Args:
        template: Template string with placeholders
        file_path: Full path to the file
        frontmatter: Frontmatter dictionary
        content: Content string
        
    Returns:
        Rendered template string
    """
    import os
    import re
    
    result = template
    
    # Replace $filename
    filename = os.path.basename(file_path)
    result = result.replace('$filename', filename)
    
    # Replace $filepath
    result = result.replace('$filepath', file_path)
    
    # Replace $folderpath
    folderpath = os.path.dirname(file_path)
    result = result.replace('$folderpath', folderpath)
    
    # Replace $foldername
    foldername = os.path.basename(os.path.dirname(file_path))
    result = result.replace('$foldername', foldername)
    
    # Replace $content
    result = result.replace('$content', content)
    
    # Replace $frontmatter.name and $frontmatter.name[index] placeholders
    if frontmatter:
        # Find all frontmatter placeholders
        # Pattern: $frontmatter.name or $frontmatter.name[number]
        pattern = r'\$frontmatter\.([a-zA-Z_][a-zA-Z0-9_]*)(?:\[(\d+)\])?'
        
        def replace_frontmatter(match):
            field_name = match.group(1)
            index_str = match.group(2)
            
            if field_name not in frontmatter:
                return match.group(0)  # Keep placeholder if field not found
            
            value = frontmatter[field_name]
            
            if index_str is not None:
                # Array indexing
                index = int(index_str)
                if isinstance(value, list) and 0 <= index < len(value):
                    return str(value[index])
                else:
                    return match.group(0)  # Keep placeholder if invalid
            else:
                # Regular field access
                if isinstance(value, list):
                    # Convert list to string representation
                    import json
                    return json.dumps(value)
                else:
                    return str(value)
        
        result = re.sub(pattern, replace_frontmatter, result)
    
    return result


def _build_map_from_items(map_items: List[tuple], file_path: str, frontmatter: Dict[str, Any], content: str) -> Dict[str, Any]:
    """
    Build a map/dictionary from map items by evaluating each value.
    
    Args:
        map_items: List of (key, value) tuples
        file_path: Full path to the file
        frontmatter: Frontmatter dictionary
        content: Content string
        
    Returns:
        Dictionary with evaluated values
    """
    from .update import evaluate_formula
    import datetime
    
    def _convert_to_json_serializable(obj):
        """Convert non-JSON-serializable types to JSON-serializable equivalents."""
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        elif isinstance(obj, list):
            return [_convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: _convert_to_json_serializable(val) for key, val in obj.items()}
        else:
            return obj
    
    result_map = {}
    for key, value in map_items:
        # Evaluate the value using the same logic as compute operations
        evaluated_value = evaluate_formula(value, file_path, frontmatter, content)
        # Convert to JSON-serializable format
        result_map[key] = _convert_to_json_serializable(evaluated_value)
    
    return result_map


def cmd_version():
    """Handle version command."""
    print(__version__)


def cmd_help():
    """Handle help command."""
    print("fmu - Front Matter Utils")
    print(f"Version: {__version__}")
    print()
    print("Usage: fmu [--format FORMAT] COMMAND [OPTIONS]")
    print()
    print("Global Options:")
    print("  --format FORMAT    Format of frontmatter (default: yaml)")
    print("                     May support TOML, JSON, INI in future versions")
    print()
    print("Commands:")
    print("  version           Show version number")
    print("  help              Show this help message")
    print("  read PATTERNS     Parse files and extract frontmatter/content")
    print("  search PATTERNS   Search for specific frontmatter fields")
    print("  validate PATTERNS Validate frontmatter fields against rules")
    print("  update PATTERNS   Update frontmatter fields")
    print("  execute SPECS     Execute commands from specs file")
    print()
    print("All commands support --save-specs option to save command configuration:")
    print("  --save-specs DESCRIPTION SPECS_FILE")
    print("                    Save command and options to YAML specs file")
    print()
    print("For command-specific help, use: fmu COMMAND --help")


def cmd_read(patterns: List[str], output: str = "both", skip_heading: bool = False, format_type: str = "yaml", 
             escape: bool = False, template: str = None, file_output: str = None, individual: bool = False, 
             map_items: List[tuple] = None, pretty: bool = False, compact: bool = False, save_specs=None):
    """
    Handle read command.
    
    Args:
        patterns: List of glob patterns or file paths
        output: What to output ('frontmatter', 'content', 'both', 'template', 'json', 'yaml')
        skip_heading: Whether to skip section headings
        format_type: Format of frontmatter
        escape: Whether to escape special characters
        template: Template string for output (required when output='template')
        file_output: File path to save output (if None, output to console)
        individual: Whether to create individual output files relative to each input file's folder
        map_items: List of (key, value) tuples for building JSON/YAML output
        pretty: Whether to prettify JSON/YAML output
        compact: Whether to minify JSON/YAML output
        save_specs: Tuple of (description, specs_file) for saving specs
    """
    # Validate template requirement
    if output == 'template' and not template:
        print("Error: --template is required when --output is 'template'", file=sys.stderr)
        sys.exit(1)
    
    # Validate map requirement for JSON/YAML output
    if output in ['json', 'yaml'] and not map_items:
        print("Error: --map is required when --output is 'json' or 'yaml'", file=sys.stderr)
        sys.exit(1)
    
    # Pretty and compact are mutually exclusive
    if pretty and compact:
        print("Error: --pretty and --compact cannot be used together", file=sys.stderr)
        sys.exit(1)
    
    # Save specs if requested
    if save_specs:
        description, specs_file = save_specs
        options = convert_read_args_to_options(type('Args', (), {
            'output': output,
            'skip_heading': skip_heading,
            'escape': escape,
            'template': template,
            'file': file_output,
            'individual': individual,
            'map': map_items,
            'pretty': pretty,
            'compact': compact
        })())
        save_specs_file(specs_file, 'read', description, patterns, options)
        print(f"Specs saved to {specs_file}")
        return
    
    # Determine output destination
    output_file = None
    
    # If individual mode is enabled, we'll create separate output files for each input file
    if individual and file_output:
        # In individual mode, we process each file with its own output file
        pass  # Will be handled in the loop
    elif file_output:
        try:
            output_file = open(file_output, 'w', encoding='utf-8')
            output_stream = output_file
        except IOError as e:
            print(f"Error: Cannot open file {file_output}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        output_stream = sys.stdout
    
    try:
        files = get_files_from_patterns(patterns)
        
        for file_path in files:
            try:
                # Handle individual file output mode
                if individual and file_output:
                    # Get the directory of the current file
                    file_dir = os.path.dirname(os.path.abspath(file_path))
                    # Create the output path relative to the file's directory
                    individual_output_path = os.path.join(file_dir, file_output)
                    
                    # Create directory if needed
                    os.makedirs(os.path.dirname(individual_output_path) if os.path.dirname(individual_output_path) else '.', exist_ok=True)
                    
                    try:
                        output_file = open(individual_output_path, 'w', encoding='utf-8')
                        output_stream = output_file
                    except IOError as e:
                        print(f"Error: Cannot open file {individual_output_path}: {e}", file=sys.stderr)
                        continue
                
                frontmatter, content = parse_file(file_path, format_type)
                
                # Apply escaping if needed
                if escape:
                    content = _escape_string(content)
                    if frontmatter:
                        frontmatter = _escape_frontmatter(frontmatter)
                
                if output == 'template':
                    # Render template
                    result = _render_template(template, file_path, frontmatter, content)
                    print(result, file=output_stream)
                elif output in ['json', 'yaml']:
                    # Build map and serialize to JSON/YAML
                    result_map = _build_map_from_items(map_items, file_path, frontmatter, content)
                    
                    if output == 'json':
                        import json
                        if pretty:
                            json_output = json.dumps(result_map, indent=2, ensure_ascii=False)
                        elif compact:
                            json_output = json.dumps(result_map, separators=(',', ':'), ensure_ascii=False)
                        else:
                            json_output = json.dumps(result_map, ensure_ascii=False)
                        print(json_output, file=output_stream)
                    else:  # yaml
                        import yaml
                        if pretty:
                            yaml_output = yaml.dump(result_map, default_flow_style=False, allow_unicode=True, sort_keys=False)
                        elif compact:
                            yaml_output = yaml.dump(result_map, default_flow_style=True, allow_unicode=True)
                        else:
                            yaml_output = yaml.dump(result_map, allow_unicode=True, sort_keys=False)
                        print(yaml_output.rstrip(), file=output_stream)
                else:
                    if len(files) > 1 and not individual:
                        print(f"\n=== {file_path} ===", file=output_stream)
                    
                    if output in ['frontmatter', 'both']:
                        if not skip_heading:
                            print("Front matter:", file=output_stream)
                        if frontmatter:
                            import yaml
                            print(yaml.dump(frontmatter, default_flow_style=False).rstrip(), file=output_stream)
                        else:
                            print("None", file=output_stream)
                        
                    if output in ['content', 'both']:
                        if output == 'both' and not skip_heading:
                            print("\nContent:", file=output_stream)
                        print(content.rstrip(), file=output_stream)
                
                # Close individual output file after each file
                if individual and file_output and output_file:
                    output_file.close()
                    output_file = None
                    
            except (FileNotFoundError, ValueError, UnicodeDecodeError) as e:
                print(f"Error processing {file_path}: {e}", file=sys.stderr)
    finally:
        if output_file:
            output_file.close()


def cmd_search(
    patterns: List[str],
    name: str,
    value: str = None,
    ignore_case: bool = False,
    regex: bool = False,
    csv_file: str = None,
    format_type: str = "yaml",
    save_specs=None
):
    """
    Handle search command.
    
    Args:
        patterns: List of glob patterns or file paths
        name: Name of frontmatter field to search for
        value: Optional value to match
        ignore_case: Whether to perform case-insensitive matching
        regex: Whether to use regex pattern matching for values
        csv_file: Optional CSV file for output
        format_type: Format of frontmatter
        save_specs: Tuple of (description, specs_file) for saving specs
    """
    # Save specs if requested
    if save_specs:
        description, specs_file = save_specs
        options = convert_search_args_to_options(type('Args', (), {
            'name': name,
            'value': value,
            'ignore_case': ignore_case,
            'regex': regex,
            'csv_file': csv_file
        })())
        save_specs_file(specs_file, 'search', description, patterns, options)
        print(f"Specs saved to {specs_file}")
        return
    
    search_and_output(patterns, name, value, ignore_case, regex, csv_file, format_type)


def cmd_validate(
    patterns: List[str],
    validations: List[Dict[str, Any]],
    ignore_case: bool = False,
    csv_file: str = None,
    format_type: str = "yaml",
    save_specs=None,
    args=None
) -> int:
    """
    Handle validate command.
    
    Args:
        patterns: List of glob patterns or file paths
        validations: List of validation rules
        ignore_case: Whether to perform case-insensitive matching
        csv_file: Optional CSV file for output
        format_type: Format of frontmatter
        save_specs: Tuple of (description, specs_file) for saving specs
        args: Original arguments object for specs conversion
        
    Returns:
        Exit code: 0 if all validations pass, non-zero if any fail
    """
    # Save specs if requested
    if save_specs and args:
        description, specs_file = save_specs
        options = convert_validate_args_to_options(args)
        save_specs_file(specs_file, 'validate', description, patterns, options)
        print(f"Specs saved to {specs_file}")
        return 0
    
    failure_count = validate_and_output(patterns, validations, ignore_case, csv_file, format_type)
    return 1 if failure_count > 0 else 0


def cmd_update(
    patterns: List[str],
    frontmatter_name: str,
    operations: List[Dict[str, Any]],
    deduplication: bool = True,
    format_type: str = "yaml",
    save_specs=None,
    args=None
):
    """
    Handle update command.
    
    Args:
        patterns: List of glob patterns or file paths
        frontmatter_name: Name of frontmatter field to update
        operations: List of update operations to apply
        deduplication: Whether to deduplicate array values
        format_type: Format of frontmatter
        save_specs: Tuple of (description, specs_file) for saving specs
        args: Original arguments object for specs conversion
    """
    # Save specs if requested
    if save_specs and args:
        description, specs_file = save_specs
        options = convert_update_args_to_options(args)
        save_specs_file(specs_file, 'update', description, patterns, options)
        print(f"Specs saved to {specs_file}")
        return
    
    update_and_output(patterns, frontmatter_name, operations, deduplication, format_type)


def cmd_execute(
    specs_file: str,
    skip_confirmation: bool = False,
    command_regex: str = None,
    patterns: List[str] = None
) -> int:
    """
    Handle execute command.
    
    Args:
        specs_file: Path to the specs file
        skip_confirmation: Whether to skip user confirmation
        command_regex: Optional regex to filter commands by description
        patterns: Optional list of patterns to override in commands
        
    Returns:
        Exit code from execution (0 for success, non-zero for failure)
    """
    from .specs import execute_specs_file, print_execution_stats
    
    try:
        exit_code, stats = execute_specs_file(
            specs_file, skip_confirmation, command_regex, patterns
        )
        print_execution_stats(stats)
        return exit_code
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error executing specs file: {e}", file=sys.stderr)
        return 1


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog='fmu',
        description='Front Matter Utils - Parse and search frontmatter in files'
    )
    
    parser.add_argument(
        '--format',
        default='yaml',
        help='Format of frontmatter (default: yaml). May support TOML, JSON, INI in future versions'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Version command
    subparsers.add_parser('version', help='Show version number')
    
    # Help command  
    subparsers.add_parser('help', help='Show help information')
    
    # Read command
    read_parser = subparsers.add_parser('read', help='Parse files and extract frontmatter/content')
    read_parser.add_argument('patterns', nargs='+', help='Glob patterns or file paths')
    read_parser.add_argument(
        '--output',
        choices=['frontmatter', 'content', 'both', 'template', 'json', 'yaml'],
        default='both',
        help='What to output (default: both)'
    )
    read_parser.add_argument(
        '--skip-heading',
        action='store_true',
        help='Skip section headings (default: false)'
    )
    read_parser.add_argument(
        '--escape',
        action='store_true',
        help='Escape special characters (newline, carriage return, tab, quotes) in output (default: false)'
    )
    read_parser.add_argument(
        '--template',
        help='Template string for output (required when --output is template). Supports: $filename, $filepath, $folderpath, $foldername, $content, $frontmatter.name, $frontmatter.name[index]'
    )
    read_parser.add_argument(
        '--file',
        help='Save output to file instead of console'
    )
    read_parser.add_argument(
        '--individual',
        action='store_true',
        help='Create individual output files relative to each input file\'s folder (requires --file)'
    )
    read_parser.add_argument(
        '--map',
        action='append',
        nargs=2,
        metavar=('KEY', 'VALUE'),
        help='Build a key-value map for JSON/YAML output. VALUE can be literals, placeholders ($filepath, $folderpath, $foldername, $frontmatter.name), or functions (=now(), =list(), =basename(), =trim(), =truncate(), =wtruncate(), =path(), =flat_list()). Can be used multiple times.'
    )
    read_parser.add_argument(
        '--pretty',
        action='store_true',
        help='Prettify JSON/YAML output (only applies with --output json or yaml)'
    )
    read_parser.add_argument(
        '--compact',
        action='store_true',
        help='Minify JSON/YAML output (only applies with --output json or yaml)'
    )
    read_parser.add_argument(
        '--save-specs',
        nargs=2,
        metavar=('DESCRIPTION', 'SPECS_FILE'),
        help='Save command specs to YAML file'
    )
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for specific frontmatter fields')
    search_parser.add_argument('patterns', nargs='+', help='Glob patterns or file paths')
    search_parser.add_argument('--name', required=True, help='Name of frontmatter field to search for')
    search_parser.add_argument('--value', help='Value to match (optional)')
    search_parser.add_argument(
        '--ignore-case',
        action='store_true',
        help='Case-insensitive matching (default: false)'
    )
    search_parser.add_argument(
        '--regex',
        action='store_true',
        help='Use regex pattern matching for values (default: false)'
    )
    search_parser.add_argument('--csv', dest='csv_file', help='Output to CSV file')
    search_parser.add_argument(
        '--save-specs',
        nargs=2,
        metavar=('DESCRIPTION', 'SPECS_FILE'),
        help='Save command specs to YAML file'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate frontmatter fields against rules')
    validate_parser.add_argument('patterns', nargs='+', help='Glob patterns or file paths')
    
    # Validation rule options (can appear multiple times)
    validate_parser.add_argument('--exist', action='append', help='Require field to exist')
    validate_parser.add_argument('--not', action='append', dest='not_exist', help='Require field to not exist')
    validate_parser.add_argument('--eq', action='append', nargs=2, metavar=('FIELD', 'VALUE'), help='Require field equals value')
    validate_parser.add_argument('--ne', action='append', nargs=2, metavar=('FIELD', 'VALUE'), help='Require field not equals value')
    validate_parser.add_argument('--contain', action='append', nargs=2, metavar=('FIELD', 'VALUE'), help='Require array field contains value')
    validate_parser.add_argument('--not-contain', action='append', nargs=2, metavar=('FIELD', 'VALUE'), dest='not_contain', help='Require array field does not contain value')
    validate_parser.add_argument('--match', action='append', nargs=2, metavar=('FIELD', 'REGEX'), help='Require field matches regex')
    validate_parser.add_argument('--not-match', action='append', nargs=2, metavar=('FIELD', 'REGEX'), dest='not_match', help='Require field does not match regex')
    validate_parser.add_argument('--not-empty', action='append', help='Require field to be an array with at least 1 value')
    validate_parser.add_argument('--list-size', action='append', nargs=3, metavar=('FIELD', 'MIN', 'MAX'), help='Require field to be an array with count between min and max inclusively')
    
    validate_parser.add_argument(
        '--ignore-case',
        action='store_true',
        help='Case-insensitive matching (default: false)'
    )
    validate_parser.add_argument('--csv', dest='csv_file', help='Output to CSV file')
    validate_parser.add_argument(
        '--save-specs',
        nargs=2,
        metavar=('DESCRIPTION', 'SPECS_FILE'),
        help='Save command specs to YAML file'
    )
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update frontmatter fields')
    update_parser.add_argument('patterns', nargs='+', help='Glob patterns or file paths')
    update_parser.add_argument('--name', required=True, help='Name of frontmatter field to update')
    
    # Update operation options
    update_parser.add_argument(
        '--deduplication',
        choices=['true', 'false'],
        default='true',
        help='Eliminate exact duplicates in array values (default: true)'
    )
    update_parser.add_argument(
        '--case',
        choices=['upper', 'lower', 'Sentence case', 'Title Case', 'snake_case', 'kebab-case'],
        help='Transform the case of the frontmatter value(s)'
    )
    
    # Compute operation
    update_parser.add_argument(
        '--compute',
        action='append',
        help='Compute and set frontmatter value using formula (literal, placeholder, or function call). Can be used multiple times.'
    )
    
    # Replace operations (can appear multiple times)
    update_parser.add_argument(
        '--replace',
        action='append',
        nargs=2,
        metavar=('FROM', 'TO'),
        help='Replace values matching FROM with TO (can be used multiple times)'
    )
    
    # Remove operations (can appear multiple times)
    update_parser.add_argument(
        '--remove',
        action='append',
        nargs='?',
        const=None,
        help='Remove values matching the specified pattern. If no value provided, removes the entire frontmatter field (can be used multiple times)'
    )
    
    # Shared options for replace and remove operations
    update_parser.add_argument(
        '--ignore-case',
        action='store_true',
        help='Ignore case when performing replacements and removals (default: false)'
    )
    update_parser.add_argument(
        '--regex',
        action='store_true',
        help='Treat patterns as regex for replacements and removals (default: false)'
    )
    update_parser.add_argument(
        '--save-specs',
        nargs=2,
        metavar=('DESCRIPTION', 'SPECS_FILE'),
        help='Save command specs to YAML file'
    )
    
    # Execute command
    execute_parser = subparsers.add_parser('execute', help='Execute commands from specs file')
    execute_parser.add_argument('specs_file', help='Path to YAML specs file')
    execute_parser.add_argument(
        '--yes',
        action='store_true',
        help='Skip all confirmations and execute all commands'
    )
    execute_parser.add_argument(
        '--command',
        type=str,
        dest='command_regex',
        help='Regex pattern to filter commands by description'
    )
    execute_parser.add_argument(
        '--pattern',
        action='append',
        help='Override patterns for commands (can be specified multiple times)'
    )
    
    return parser


def _parse_update_args(args) -> List[Dict[str, Any]]:
    """Parse update arguments into update operations."""
    operations = []
    
    # Handle --compute operations
    if hasattr(args, 'compute') and args.compute:
        for formula in args.compute:
            operations.append({
                'type': 'compute',
                'formula': formula
            })
    
    # Handle --case
    if args.case:
        operations.append({
            'type': 'case',
            'case_type': args.case
        })
    
    # Handle --replace operations
    if args.replace:
        for from_val, to_val in args.replace:
            operations.append({
                'type': 'replace',
                'from': from_val,
                'to': to_val,
                'ignore_case': args.ignore_case,
                'regex': args.regex
            })
    
    # Handle --remove operations
    if args.remove:
        for remove_val in args.remove:
            operations.append({
                'type': 'remove',
                'value': remove_val,
                'ignore_case': args.ignore_case,
                'regex': args.regex
            })
    
    # Handle --deduplication (deduplication should be considered a valid operation)
    if hasattr(args, 'deduplication') and args.deduplication == 'true':
        operations.append({
            'type': 'deduplication'
        })
    
    return operations


def _parse_validation_args(args) -> List[Dict[str, Any]]:
    """Parse validation arguments into validation rules."""
    validations = []
    
    # Handle --exist
    if args.exist:
        for field in args.exist:
            validations.append({'type': 'exist', 'field': field})
    
    # Handle --not
    if args.not_exist:
        for field in args.not_exist:
            validations.append({'type': 'not', 'field': field})
    
    # Handle --eq
    if args.eq:
        for field, value in args.eq:
            validations.append({'type': 'eq', 'field': field, 'value': value})
    
    # Handle --ne
    if args.ne:
        for field, value in args.ne:
            validations.append({'type': 'ne', 'field': field, 'value': value})
    
    # Handle --contain
    if args.contain:
        for field, value in args.contain:
            validations.append({'type': 'contain', 'field': field, 'value': value})
    
    # Handle --not-contain
    if args.not_contain:
        for field, value in args.not_contain:
            validations.append({'type': 'not-contain', 'field': field, 'value': value})
    
    # Handle --match
    if args.match:
        for field, regex in args.match:
            validations.append({'type': 'match', 'field': field, 'regex': regex})
    
    # Handle --not-match
    if args.not_match:
        for field, regex in args.not_match:
            validations.append({'type': 'not-match', 'field': field, 'regex': regex})
    
    # Handle --not-empty
    if args.not_empty:
        for field in args.not_empty:
            validations.append({'type': 'not-empty', 'field': field})
    
    # Handle --list-size
    if args.list_size:
        for field, min_str, max_str in args.list_size:
            try:
                min_size = int(min_str)
                max_size = int(max_str)
                validations.append({'type': 'list-size', 'field': field, 'min': min_size, 'max': max_size})
            except ValueError:
                print(f"Error: Invalid list-size parameters. Min and max must be integers: {min_str}, {max_str}", file=sys.stderr)
                sys.exit(1)
    
    return validations


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == 'version':
        cmd_version()
    elif args.command == 'help':
        cmd_help()
    elif args.command == 'read':
        cmd_read(
            patterns=args.patterns,
            output=args.output,
            skip_heading=args.skip_heading,
            format_type=args.format,
            escape=args.escape if hasattr(args, 'escape') else False,
            template=args.template if hasattr(args, 'template') else None,
            file_output=args.file if hasattr(args, 'file') else None,
            individual=args.individual if hasattr(args, 'individual') else False,
            map_items=args.map if hasattr(args, 'map') and args.map else None,
            pretty=args.pretty if hasattr(args, 'pretty') else False,
            compact=args.compact if hasattr(args, 'compact') else False,
            save_specs=args.save_specs if hasattr(args, 'save_specs') else None
        )
    elif args.command == 'search':
        cmd_search(
            patterns=args.patterns,
            name=args.name,
            value=args.value,
            ignore_case=args.ignore_case,
            regex=args.regex,
            csv_file=args.csv_file,
            format_type=args.format,
            save_specs=args.save_specs if hasattr(args, 'save_specs') else None
        )
    elif args.command == 'validate':
        validations = _parse_validation_args(args)
        if not validations and not (hasattr(args, 'save_specs') and args.save_specs):
            print("Error: No validation rules specified", file=sys.stderr)
            sys.exit(1)
        exit_code = cmd_validate(
            patterns=args.patterns,
            validations=validations,
            ignore_case=args.ignore_case,
            csv_file=args.csv_file,
            format_type=args.format,
            save_specs=args.save_specs if hasattr(args, 'save_specs') else None,
            args=args
        )
        sys.exit(exit_code)
    elif args.command == 'update':
        operations = _parse_update_args(args)
        if not operations and not (hasattr(args, 'save_specs') and args.save_specs):
            print("Error: No update operations specified", file=sys.stderr)
            sys.exit(1)
        cmd_update(
            patterns=args.patterns,
            frontmatter_name=args.name,
            operations=operations,
            deduplication=(args.deduplication == 'true'),
            format_type=args.format,
            save_specs=args.save_specs if hasattr(args, 'save_specs') else None,
            args=args
        )
    elif args.command == 'execute':
        exit_code = cmd_execute(
            specs_file=args.specs_file,
            skip_confirmation=args.yes,
            command_regex=args.command_regex,
            patterns=args.pattern
        )
        sys.exit(exit_code)
    elif args.command is None:
        # No command provided, show help
        cmd_help()
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()