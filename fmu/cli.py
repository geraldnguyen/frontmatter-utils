"""
Command Line Interface for fmu.
"""

import argparse
import sys
from typing import List
from . import __version__
from .core import parse_file, get_files_from_patterns
from .search import search_and_output


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
    print()
    print("For command-specific help, use: fmu COMMAND --help")


def cmd_read(patterns: List[str], output: str = "both", skip_heading: bool = False, format_type: str = "yaml"):
    """
    Handle read command.
    
    Args:
        patterns: List of glob patterns or file paths
        output: What to output ('frontmatter', 'content', 'both')
        skip_heading: Whether to skip section headings
        format_type: Format of frontmatter
    """
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
    csv_file: str = None,
    format_type: str = "yaml"
):
    """
    Handle search command.
    
    Args:
        patterns: List of glob patterns or file paths
        name: Name of frontmatter field to search for
        value: Optional value to match
        ignore_case: Whether to perform case-insensitive matching
        csv_file: Optional CSV file for output
        format_type: Format of frontmatter
    """
    search_and_output(patterns, name, value, ignore_case, csv_file, format_type)


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
    search_parser.add_argument('--csv', dest='csv_file', help='Output to CSV file')
    
    return parser


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
            format_type=args.format
        )
    elif args.command == 'search':
        cmd_search(
            patterns=args.patterns,
            name=args.name,
            value=args.value,
            ignore_case=args.ignore_case,
            csv_file=args.csv_file,
            format_type=args.format
        )
    elif args.command is None:
        # No command provided, show help
        cmd_help()
    else:
        print(f"Unknown command: {args.command}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()