"""
Command Line Interface for fmu.
"""

import argparse
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


def cmd_read(patterns: List[str], output: str = "both", skip_heading: bool = False, format_type: str = "yaml", save_specs=None):
    """
    Handle read command.
    
    Args:
        patterns: List of glob patterns or file paths
        output: What to output ('frontmatter', 'content', 'both')
        skip_heading: Whether to skip section headings
        format_type: Format of frontmatter
        save_specs: Tuple of (description, specs_file) for saving specs
    """
    # Save specs if requested
    if save_specs:
        description, specs_file = save_specs
        options = convert_read_args_to_options(type('Args', (), {
            'output': output,
            'skip_heading': skip_heading
        })())
        save_specs_file(specs_file, 'read', description, patterns, options)
        print(f"Specs saved to {specs_file}")
        return
    
    files = get_files_from_patterns(patterns)
    
    for file_path in files:
        try:
            frontmatter, content = parse_file(file_path, format_type)
            
            if len(files) > 1:
                print(f"\n=== {file_path} ===")
            
            if output in ['frontmatter', 'both']:
                if not skip_heading:
                    print("Front matter:")
                if frontmatter:
                    import yaml
                    print(yaml.dump(frontmatter, default_flow_style=False).rstrip())
                else:
                    print("None")
                
            if output in ['content', 'both']:
                if output == 'both' and not skip_heading:
                    print("\nContent:")
                print(content.rstrip())
                
        except (FileNotFoundError, ValueError, UnicodeDecodeError) as e:
            print(f"Error processing {file_path}: {e}", file=sys.stderr)


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
):
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
    """
    # Save specs if requested
    if save_specs and args:
        description, specs_file = save_specs
        options = convert_validate_args_to_options(args)
        save_specs_file(specs_file, 'validate', description, patterns, options)
        print(f"Specs saved to {specs_file}")
        return
    
    validate_and_output(patterns, validations, ignore_case, csv_file, format_type)


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


def cmd_execute(specs_file: str, skip_confirmation: bool = False):
    """
    Handle execute command.
    
    Args:
        specs_file: Path to the specs file
        skip_confirmation: Whether to skip user confirmation
    """
    from .specs import execute_specs_file, print_execution_stats
    
    try:
        stats = execute_specs_file(specs_file, skip_confirmation)
        print_execution_stats(stats)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error executing specs file: {e}", file=sys.stderr)
        sys.exit(1)


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
        choices=['frontmatter', 'content', 'both'],
        default='both',
        help='What to output (default: both)'
    )
    read_parser.add_argument(
        '--skip-heading',
        action='store_true',
        help='Skip section headings (default: false)'
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
        help='Remove values matching the specified pattern (can be used multiple times)'
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
    
    return parser


def _parse_update_args(args) -> List[Dict[str, Any]]:
    """Parse update arguments into update operations."""
    operations = []
    
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
        cmd_validate(
            patterns=args.patterns,
            validations=validations,
            ignore_case=args.ignore_case,
            csv_file=args.csv_file,
            format_type=args.format,
            save_specs=args.save_specs if hasattr(args, 'save_specs') else None,
            args=args
        )
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
        cmd_execute(
            specs_file=args.specs_file,
            skip_confirmation=args.yes
        )
    elif args.command is None:
        # No command provided, show help
        cmd_help()
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()