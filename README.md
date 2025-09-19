# fmu - Front Matter Utils

A Python library and CLI tool for parsing and searching front matter in files.

## Features

- **Library Mode**: Reusable API for parsing and searching frontmatter
- **CLI Mode**: Command-line interface for batch operations
- **YAML Support**: Parse YAML frontmatter (default format)
- **Flexible Search**: Search by field name and optionally by value
- **Case Sensitivity**: Support for case-sensitive or case-insensitive matching
- **Multiple Output Formats**: Console output or CSV export
- **Glob Pattern Support**: Process multiple files using glob patterns

## Installation

### From Source

```bash
git clone https://github.com/geraldnguyen/frontmatter-utils.git
cd frontmatter-utils
pip install -e .
```

### Dependencies

- Python 3.7+
- PyYAML>=6.0

## Getting Started

### Library Usage

```python
from fmu import parse_file, search_frontmatter

# Parse a single file
frontmatter, content = parse_file('example.md')
print(f"Title: {frontmatter.get('title')}")
print(f"Content: {content}")

# Search for frontmatter across multiple files
results = search_frontmatter(['*.md'], 'author', 'John Doe')
for file_path, field_name, field_value in results:
    print(f"{file_path}: {field_name} = {field_value}")
```

### CLI Usage

#### Basic Commands

```bash
# Show version
fmu version

# Show help
fmu help

# Parse files and show both frontmatter and content
fmu read "*.md"

# Parse files and show only frontmatter
fmu read "*.md" --output frontmatter

# Parse files and show only content
fmu read "*.md" --output content

# Skip section headings
fmu read "*.md" --skip-heading
```

#### Search Commands

```bash
# Search for posts with 'author' field
fmu search "*.md" --name author

# Search for posts by specific author
fmu search "*.md" --name author --value "John Doe"

# Case-insensitive search
fmu search "*.md" --name author --value "john doe" --ignore-case

# Output results to CSV file
fmu search "*.md" --name category --csv results.csv
```

#### Global Options

```bash
# Specify frontmatter format (currently only YAML supported)
fmu --format yaml read "*.md"
```

## Command Reference

### Global Options

- `--format FORMAT`: Format of frontmatter (default: yaml). May support TOML, JSON, INI in future versions.

### Commands

#### `version`
Show the version number.

```bash
fmu version
```

#### `help`
Show help information.

```bash
fmu help
```

#### `read PATTERNS`
Parse files and extract frontmatter and/or content.

**Arguments:**
- `PATTERNS`: One or more glob patterns, file paths, or directory paths

**Options:**
- `--output [frontmatter|content|both]`: What to output (default: both)
- `--skip-heading [true|false]`: Skip section headings (default: false)

**Examples:**
```bash
# Read all markdown files in current directory
fmu read "*.md"

# Read specific files
fmu read file1.md file2.md

# Read all files in a directory
fmu read docs/

# Show only frontmatter
fmu read "*.md" --output frontmatter

# Show only content without headings
fmu read "*.md" --output content --skip-heading
```

#### `search PATTERNS`
Search for specific frontmatter fields.

**Arguments:**
- `PATTERNS`: One or more glob patterns, file paths, or directory paths

**Options:**
- `--name NAME`: **Required.** Name of the frontmatter field to search for
- `--value VALUE`: Optional. Value of the frontmatter to match
- `--ignore-case [true|false]`: Case-insensitive matching (default: false)
- `--csv FILE`: Optional. Output results to specified CSV file

**Examples:**
```bash
# Find all files with 'title' field
fmu search "*.md" --name title

# Find files where author is "John Doe"
fmu search "*.md" --name author --value "John Doe"

# Case-insensitive search
fmu search "*.md" --name category --value "programming" --ignore-case

# Export to CSV
fmu search "*.md" --name tags --csv tags_report.csv
```

## Output Formats

### Console Output

#### Read Command
```
Front matter:
title: Example Post
author: John Doe
tags: [python, tutorial]

Content:
This is the main content of the post.
```

#### Search Command
```
/path/to/file1.md:
- title: Example Post

/path/to/file2.md:
- author: John Doe
```

### CSV Output

When using the `--csv` option with search, output includes:

| File Path | Front Matter Name | Front Matter Value |
|-----------|-------------------|-------------------|
| /path/to/file1.md | title | Example Post |
| /path/to/file2.md | author | John Doe |

## Library API

### Core Functions

#### `parse_frontmatter(content, format_type='yaml')`
Parse frontmatter from a content string.

**Parameters:**
- `content` (str): The file content as a string
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `Tuple[Optional[Dict[str, Any]], str]`: Frontmatter dictionary and remaining content

#### `parse_file(file_path, format_type='yaml')`
Parse frontmatter from a file.

**Parameters:**
- `file_path` (str): Path to the file
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `Tuple[Optional[Dict[str, Any]], str]`: Frontmatter dictionary and content

#### `extract_content(content, format_type='yaml')`
Extract only the content (without frontmatter) from a string.

**Parameters:**
- `content` (str): The file content as a string
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `str`: Content without frontmatter

### Search Functions

#### `search_frontmatter(patterns, name, value=None, ignore_case=False, format_type='yaml')`
Search for frontmatter in files.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `name` (str): Frontmatter field name to search for
- `value` (Optional[str]): Value to match (optional)
- `ignore_case` (bool): Case-insensitive matching (default: False)
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `List[Tuple[str, str, Any]]`: List of (file_path, field_name, field_value)

## File Format Support

### YAML Frontmatter

Currently supported format. Frontmatter must be delimited by `---`:

```markdown
---
title: My Post
author: John Doe
tags: [python, web]
published: true
---

Content goes here.
```

### Future Format Support

Future versions may support:
- TOML frontmatter
- JSON frontmatter  
- INI frontmatter

## Error Handling

The library handles various error conditions gracefully:

- **File not found**: Raises `FileNotFoundError`
- **Invalid YAML**: Raises `ValueError` with details
- **Encoding issues**: Raises `ValueError` for non-UTF-8 files
- **Invalid format**: Raises `ValueError` for unsupported formats

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run individual test modules:

```bash
python -m pytest tests/test_core.py
python -m pytest tests/test_search.py
python -m pytest tests/test_cli.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Changelog

### Version 0.1.0

- Initial release
- YAML frontmatter parsing
- CLI with read and search commands
- Library API for programmatic usage
- Glob pattern support
- CSV export functionality
- Case-sensitive and case-insensitive search
- Comprehensive test suite