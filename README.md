# fmu - Front Matter Utils

A Python library and CLI tool for parsing and searching front matter in files.

## Features

- **Library Mode**: Reusable API for parsing and searching frontmatter
- **CLI Mode**: Command-line interface for batch operations
- **YAML Support**: Parse YAML frontmatter (default format)
- **Flexible Search**: Search by field name and optionally by value
- **Array Search**: Search within array/list frontmatter values
- **Regex Support**: Use regular expressions for value matching
- **Validation Engine**: Validate frontmatter fields against custom rules
- **Update Engine**: Transform, replace, and remove frontmatter values *(New in v0.4.0)*
- **Case Transformations**: Six different case conversion types *(New in v0.4.0)*
- **Value Deduplication**: Automatic removal of duplicate array values *(New in v0.4.0)*
- **Template Output**: Export content and frontmatter using custom templates *(New in v0.9.0)*
- **Character Escaping**: Escape special characters in output *(New in v0.9.0)*
- **File Output**: Save command output directly to files *(New in v0.10.0)*
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
from fmu import parse_file, search_frontmatter, validate_frontmatter, update_frontmatter

# Parse a single file
frontmatter, content = parse_file('example.md')
print(f"Title: {frontmatter.get('title')}")
print(f"Content: {content}")

# Search for frontmatter across multiple files
results = search_frontmatter(['*.md'], 'author', 'John Doe')
for file_path, field_name, field_value in results:
    print(f"{file_path}: {field_name} = {field_value}")

# Search within array values
results = search_frontmatter(['*.md'], 'tags', 'python')

# Validate frontmatter fields
validations = [
    {'type': 'exist', 'field': 'title'},
    {'type': 'eq', 'field': 'status', 'value': 'published'},
    {'type': 'contain', 'field': 'tags', 'value': 'tech'}
]
failures = validate_frontmatter(['*.md'], validations)
for file_path, field_name, field_value, reason in failures:
    print(f"Validation failed in {file_path}: {reason}")

# Update frontmatter fields (New in v0.4.0)
operations = [
    {'type': 'case', 'case_type': 'lower'},
    {'type': 'replace', 'from': 'python', 'to': 'programming', 'ignore_case': False, 'regex': False},
    {'type': 'remove', 'value': 'deprecated', 'ignore_case': False, 'regex': False}
]
results = update_frontmatter(['*.md'], 'tags', operations, deduplication=True)
for result in results:
    if result['changes_made']:
        print(f"Updated {result['file_path']}: {result['reason']}")
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

# Escape special characters in output (New in v0.9.0)
fmu read "*.md" --escape

# Use template output for custom formatting (New in v0.9.0)
fmu read "*.md" --output template --template '{ "title": "$frontmatter.title", "file": "$filename" }'

# Save output to file (New in v0.10.0)
fmu read "*.md" --file output.txt

# Save template output to JSON file (New in v0.10.0)
fmu read "*.md" --output template --template '{ "title": "$frontmatter.title" }' --file output.json
```

#### File Output (New in v0.10.0)

The `--file` option allows you to save command output directly to a file instead of displaying it in the console:

```bash
# Save standard output to file
fmu read "*.md" --file output.txt

# Save template output to file
fmu read "*.md" --output template --template '{ "title": "$frontmatter.title" }' --file output.json

# Combine with escape for JSON-safe file output
fmu read "*.md" --output template --template '{ "content": "$content" }' --escape --file data.json

# Works with specs files - different commands can output to different files
fmu execute commands.yaml  # Each command can specify its own --file destination
```

**Use Cases:**
- Export metadata to JSON files for further processing
- Generate data files for static site generators
- Create batch processing pipelines with file-based workflows
- Archive frontmatter and content in structured formats

#### Template Output (New in v0.9.0)

The `--output template` option allows you to export content and frontmatter in custom formats:

```bash
# Export as JSON-like format
fmu read "*.md" --output template --template '{ "title": "$frontmatter.title", "content": "$content" }'

# Access array elements by index
fmu read "*.md" --output template --template '{ "first_tag": "$frontmatter.tags[0]", "second_tag": "$frontmatter.tags[1]" }'

# Include file metadata
fmu read "*.md" --output template --template '{ "path": "$filepath", "name": "$filename" }'

# Combine with escape option for JSON-safe output
fmu read "*.md" --output template --template '{ "content": "$content" }' --escape
```

**Template Placeholders:**
- `$filename`: Base filename (e.g., "post.md")
- `$filepath`: Full file path
- `$content`: Content after frontmatter
- `$frontmatter.fieldname`: Access frontmatter field (single value or full array as JSON)
- `$frontmatter.fieldname[N]`: Access array element by index (0-based)

**Escape Option:**
When `--escape` is used, the following characters are escaped:
- Newline: `\n`
- Carriage return: `\r`
- Tab: `\t`
- Single quote: `'` → `\'`
- Double quote: `"` → `\"`

#### Search Commands

```bash
# Search for posts with 'author' field
fmu search "*.md" --name author

# Search for posts by specific author
fmu search "*.md" --name author --value "John Doe"

# Case-insensitive search
fmu search "*.md" --name author --value "john doe" --ignore-case

# Search within array values
fmu search "*.md" --name tags --value python

# Use regex for pattern matching
fmu search "*.md" --name title --value "^Guide.*" --regex

# Output results to CSV file
fmu search "*.md" --name category --csv results.csv
```

#### Validation Commands

```bash
# Validate that required fields exist
fmu validate "*.md" --exist title --exist author

# Validate that certain fields don't exist
fmu validate "*.md" --not draft --not private

# Validate field values
fmu validate "*.md" --eq status published --ne category "deprecated"

# Validate array contents
fmu validate "*.md" --contain tags "tech" --not-contain tags "obsolete"

# Validate using regex patterns
fmu validate "*.md" --match title "^[A-Z].*" --not-match content "TODO"

# Case-insensitive validation
fmu validate "*.md" --eq STATUS "published" --ignore-case

# Output validation failures to CSV
fmu validate "*.md" --exist title --csv validation_report.csv

# Complex validation with multiple rules
fmu validate "blog/*.md" \
  --exist title \
  --exist author \
  --eq status "published" \
  --contain tags "tech" \
  --match date "^\d{4}-\d{2}-\d{2}$" \
  --csv blog_validation.csv
```

#### Update Commands (New in v0.4.0)

```bash
# Transform case of frontmatter values
fmu update "*.md" --name title --case "Title Case"
fmu update "*.md" --name author --case lower

# Replace values
fmu update "*.md" --name status --replace draft published
fmu update "*.md" --name category --replace "old-name" "new-name"

# Case-insensitive replacement
fmu update "*.md" --name tags --replace Python python --ignore-case

# Regex-based replacement
fmu update "*.md" --name content --replace "TODO:.*" "DONE" --regex

# Remove specific values
fmu update "*.md" --name tags --remove "deprecated"
fmu update "*.md" --name status --remove "draft"

# Remove with regex patterns
fmu update "*.md" --name tags --remove "^test.*" --regex

# Multiple operations (applied in sequence)
fmu update "*.md" --name tags \
  --replace python programming \
  --remove deprecated \
  --case lower

# Disable deduplication (enabled by default for arrays)
fmu update "*.md" --name tags --deduplication false --case lower

# Complex update with multiple operations
fmu update "blog/*.md" \
  --name tags \
  --case lower \
  --replace "javascript" "js" \
  --replace "python" "py" \
  --remove "deprecated" \
  --remove "old" \
  --deduplication true
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
- `--output [frontmatter|content|both|template]`: What to output (default: both)
- `--skip-heading`: Skip section headings (default: false)
- `--escape`: Escape special characters in output (default: false) *(New in v0.9.0)*
- `--template TEMPLATE`: Template string for output (required when --output is template) *(New in v0.9.0)*
- `--file FILE`: Save output to file instead of console *(New in v0.10.0)*

**Examples:**
```bash
# Read all markdown files in current directory
fmu read "*.md"

# Read specific files
fmu read file1.md file2.md

# Read all files in a directory
fmu read docs/

# Export with custom template (New in v0.9.0)
fmu read "*.md" --output template --template '{ "title": "$frontmatter.title", "path": "$filepath" }'

# Save output to file (New in v0.10.0)
fmu read "*.md" --file output.txt

# Save template output to JSON file (New in v0.10.0)
fmu read "*.md" --output template --template '{ "title": "$frontmatter.title" }' --file data.json

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
- `--ignore-case`: Case-insensitive matching (default: false)
- `--regex`: Use regex pattern matching for values (default: false)
- `--csv FILE`: Optional. Output results to specified CSV file

**Examples:**
```bash
# Find all files with 'title' field
fmu search "*.md" --name title

# Find files where author is "John Doe"
fmu search "*.md" --name author --value "John Doe"

# Case-insensitive search
fmu search "*.md" --name category --value "programming" --ignore-case

# Search for 'python' in tags array
fmu search "*.md" --name tags --value "python"

# Regex search for tags ending with 'ing'
fmu search "*.md" --name tags --value "ing$" --regex

# Regex search for titles starting with "Guide"
fmu search "*.md" --name title --value "^Guide" --regex

# Case-insensitive regex search
fmu search "*.md" --name author --value "john.*doe" --regex --ignore-case

# Export to CSV
fmu search "*.md" --name tags --csv tags_report.csv
```

#### `validate PATTERNS`
Validate frontmatter fields against custom rules.

**Arguments:**
- `PATTERNS`: One or more glob patterns, file paths, or directory paths

**Validation Options:**
- `--exist FIELD`: **Repeatable.** Require field to exist
- `--not FIELD`: **Repeatable.** Require field to not exist
- `--eq FIELD VALUE`: **Repeatable.** Require field equals value
- `--ne FIELD VALUE`: **Repeatable.** Require field not equals value
- `--contain FIELD VALUE`: **Repeatable.** Require array field contains value
- `--not-contain FIELD VALUE`: **Repeatable.** Require array field does not contain value
- `--match FIELD REGEX`: **Repeatable.** Require field matches regex pattern
- `--not-match FIELD REGEX`: **Repeatable.** Require field does not match regex pattern

**General Options:**
- `--ignore-case`: Case-insensitive matching (default: false)
- `--csv FILE`: Optional. Output validation failures to specified CSV file

**Examples:**
```bash
# Validate required fields exist
fmu validate "*.md" --exist title --exist author

# Validate fields don't exist
fmu validate "*.md" --not draft --not private

# Validate field values
fmu validate "*.md" --eq status "published" --ne category "deprecated"

# Validate array contents
fmu validate "*.md" --contain tags "tech" --not-contain tags "obsolete"

# Validate using regex patterns
fmu validate "*.md" --match title "^[A-Z].*" --not-match content "TODO"

# Case-insensitive validation
fmu validate "*.md" --eq STATUS "published" --ignore-case

# Multiple validation rules
fmu validate "blog/*.md" \
  --exist title \
  --exist author \
  --eq status "published" \
  --contain tags "tech" \
  --match date "^\d{4}-\d{2}-\d{2}$"

# Export failures to CSV
fmu validate "*.md" --exist title --csv validation_report.csv
```

#### `update PATTERNS` (New in v0.4.0)
Update frontmatter fields in files with various transformations.

**Arguments:**
- `PATTERNS`: One or more glob patterns, file paths, or directory paths

**Required Options:**
- `--name FIELD`: **Required.** Name of the frontmatter field to update

**Update Operations:**
- `--case CASE_TYPE`: Transform case of values. Options: `upper`, `lower`, `Sentence case`, `Title Case`, `snake_case`, `kebab-case`
- `--replace FROM TO`: **Repeatable.** Replace values matching FROM with TO
- `--remove VALUE`: **Repeatable.** Remove values matching VALUE

**Shared Operation Options:**
- `--ignore-case`: Ignore case when performing replacements and removals (default: false)
- `--regex`: Treat patterns as regex for replacements and removals (default: false)

**General Options:**
- `--deduplication {true,false}`: Eliminate exact duplicates in array values (default: true, applied last)

**Examples:**
```bash
# Transform case of values
fmu update "*.md" --name title --case "Title Case"
fmu update "*.md" --name author --case lower
fmu update "*.md" --name tags --case kebab-case

# Replace values (substring replacement)
fmu update "*.md" --name status --replace draft published
fmu update "*.md" --name category --replace "old-name" "new-name"

# Case-insensitive replacement
fmu update "*.md" --name tags --replace Python python --ignore-case

# Regex-based replacement
fmu update "*.md" --name content --replace "TODO:.*" "DONE" --regex

# Remove specific values
fmu update "*.md" --name tags --remove "deprecated"
fmu update "*.md" --name status --remove "draft"

# Remove with regex patterns
fmu update "*.md" --name tags --remove "^test.*" --regex

# Multiple operations (applied in sequence: case, replace, remove, then deduplication)
fmu update "*.md" --name tags \
  --case lower \
  --replace python programming \
  --remove deprecated

# Disable deduplication
fmu update "*.md" --name tags --deduplication false --case lower

# Complex update example
fmu update "blog/*.md" \
  --name tags \
  --case lower \
  --replace "javascript" "js" \
  --replace "python" "py" \
  --remove "deprecated" \
  --remove "old" \
  --deduplication true
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

#### Validate Command
```
./path/to/file1.md:
- 	author: None --> Field 'author' does not exist

./path/to/file2.md:
- 	status: draft --> Field 'status' value 'draft' does not equal 'published'
```

### CSV Output

#### Search Command
When using the `--csv` option with search, output includes:

| File Path | Front Matter Name | Front Matter Value |
|-----------|-------------------|-------------------|
| /path/to/file1.md | title | Example Post |
| /path/to/file2.md | author | John Doe |

#### Validate Command
When using the `--csv` option with validate, output includes:

| File Path | Front Matter Name | Front Matter Value | Failure Reason |
|-----------|-------------------|--------------------|-----------------|
| /path/to/file1.md | author | | Field 'author' does not exist |
| /path/to/file2.md | status | draft | Field 'status' value 'draft' does not equal 'published' |

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

#### `search_frontmatter(patterns, name, value=None, ignore_case=False, regex=False, format_type='yaml')`
Search for frontmatter in files.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `name` (str): Frontmatter field name to search for
- `value` (Optional[str]): Value to match (optional)
- `ignore_case` (bool): Case-insensitive matching (default: False)
- `regex` (bool): Use regex pattern matching for values (default: False)
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `List[Tuple[str, str, Any]]`: List of (file_path, field_name, field_value)

**Enhanced Features (v0.2.0):**
- **Array Matching**: When searching array/list frontmatter fields, each element is checked against the search value
- **Regex Support**: Use regular expressions for flexible pattern matching (Python's `re` module)

### Validation Functions

#### `validate_frontmatter(patterns, validations, ignore_case=False, format_type='yaml')`
Validate frontmatter fields against custom rules.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `validations` (List[Dict[str, Any]]): List of validation rule dictionaries
- `ignore_case` (bool): Case-insensitive matching (default: False)
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `List[Tuple[str, str, Any, str]]`: List of (file_path, field_name, field_value, failure_reason) for failed validations

**Validation Rule Format:**
Each validation rule is a dictionary with the following structure:
```python
# Field existence validation
{'type': 'exist', 'field': 'title'}
{'type': 'not', 'field': 'draft'}

# Value equality validation
{'type': 'eq', 'field': 'status', 'value': 'published'}
{'type': 'ne', 'field': 'category', 'value': 'deprecated'}

# Array content validation
{'type': 'contain', 'field': 'tags', 'value': 'tech'}
{'type': 'not-contain', 'field': 'tags', 'value': 'obsolete'}

# Regex pattern validation
{'type': 'match', 'field': 'title', 'regex': '^[A-Z].*'}
{'type': 'not-match', 'field': 'content', 'regex': 'TODO'}
```

#### `validate_and_output(patterns, validations, ignore_case=False, csv_file=None, format_type='yaml')`
Validate frontmatter and output results directly.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `validations` (List[Dict[str, Any]]): List of validation rule dictionaries
- `ignore_case` (bool): Case-insensitive matching (default: False)
- `csv_file` (Optional[str]): Path to CSV file for output (default: console output)
- `format_type` (str): Format type (default: 'yaml')

**New Features (v0.3.0):**
- **Comprehensive Validation**: Eight different validation types for thorough frontmatter checking
- **Flexible Rules**: Multiple validation rules can be applied to the same file
- **Error Reporting**: Clear, descriptive error messages for each validation failure
- **CSV Export**: Export validation failures to CSV for analysis and reporting

### Update Functions (New in v0.4.0)

#### `update_frontmatter(patterns, frontmatter_name, operations, deduplication=True, format_type='yaml')`
Update frontmatter fields in files with various transformations.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `frontmatter_name` (str): Name of frontmatter field to update
- `operations` (List[Dict[str, Any]]): List of update operation dictionaries
- `deduplication` (bool): Whether to deduplicate array values (default: True, applied last)
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `List[Dict[str, Any]]`: List of update results with file paths and changes made

**Operation Types:**
```python
# Case transformation
{'type': 'case', 'case_type': 'upper'}  # or 'lower', 'Sentence case', 'Title Case', 'snake_case', 'kebab-case'

# Value replacement
{'type': 'replace', 'from': 'old_value', 'to': 'new_value', 'ignore_case': False, 'regex': False}

# Value removal
{'type': 'remove', 'value': 'value_to_remove', 'ignore_case': False, 'regex': False}
```

**Example:**
```python
from fmu import update_frontmatter

# Transform case and replace values
operations = [
    {'type': 'case', 'case_type': 'lower'},
    {'type': 'replace', 'from': 'python', 'to': 'programming', 'ignore_case': False, 'regex': False},
    {'type': 'remove', 'value': 'deprecated', 'ignore_case': False, 'regex': False}
]

results = update_frontmatter(['*.md'], 'tags', operations, deduplication=True)
for result in results:
    if result['changes_made']:
        print(f"Updated {result['file_path']}: {result['original_value']} -> {result['new_value']}")
```

#### `update_and_output(patterns, frontmatter_name, operations, deduplication=True, format_type='yaml')`
Update frontmatter and output results directly to console.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `frontmatter_name` (str): Name of frontmatter field to update
- `operations` (List[Dict[str, Any]]): List of update operation dictionaries
- `deduplication` (bool): Whether to deduplicate array values (default: True)
- `format_type` (str): Format type (default: 'yaml')

**New Features (v0.4.0):**
- **Case Transformations**: Six different case transformation types (upper, lower, sentence, title, snake_case, kebab-case)
- **Flexible Replacements**: Substring and regex-based replacements with case sensitivity options
- **Value Removal**: Remove specific values or regex patterns from frontmatter fields
- **Array Deduplication**: Automatic removal of exact duplicates in array values
- **Multiple Operations**: Apply multiple transformations in sequence
- **In-place Updates**: Modify files directly while preserving original structure

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

## Regex Support

Version 0.2.0 introduces regex pattern matching for value searches using Python's `re` module.

### Supported Regex Features

- **Basic patterns**: `python`, `test`, etc.
- **Anchors**: `^start`, `end$`, `^exact$`
- **Character classes**: `[abc]`, `[a-z]`, `\d`, `\w`, `\s`
- **Quantifiers**: `*`, `+`, `?`, `{n}`, `{n,m}`
- **Groups**: `(pattern)`, `(?:pattern)`
- **Alternation**: `pattern1|pattern2`
- **Case-insensitive**: Use `--ignore-case` flag

### Regex Examples

```bash
# Find titles starting with "Guide" or "Tutorial"
fmu search "*.md" --name title --value "^(Guide|Tutorial)" --regex

# Find tags containing digits
fmu search "*.md" --name tags --value "\d" --regex

# Find authors with names ending in "son"
fmu search "*.md" --name author --value "son$" --regex --ignore-case

# Find categories with 2-4 characters
fmu search "*.md" --name category --value "^.{2,4}$" --regex
```

### Array + Regex Combination

When using regex with array fields, the pattern is matched against each array element:

```yaml
---
tags: [python3, javascript, html5, css3]
---
```

```bash
# Matches both "python3" and "html5" (numbers at end)
fmu search "file.md" --name tags --value "\d+$" --regex
```

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

### Version 0.10.0

- **File Output Feature**
  - New `--file` option to save command output directly to files
  - Works with all output modes (frontmatter, content, both, template)
  - Enable file-based workflows for batch processing
  - Multiple commands in specs files can output to different files
- **Enhanced Integration**
  - Seamless integration with specs file execution
  - Each command can specify independent output destination
  - Console and file output can be mixed in the same workflow
- **Use Cases**
  - Export metadata to JSON files for further processing
  - Generate data files for static site generators
  - Create automated pipelines with file-based workflows
- **Testing**
  - Added comprehensive tests for file output functionality
  - All 136 tests passing

### Version 0.9.0

- **Template Output Feature**
  - New `--output template` option for custom formatting
  - Template placeholders: `$filename`, `$filepath`, `$content`, `$frontmatter.field`
  - Array indexing support: `$frontmatter.field[N]`
  - Array values exported as JSON when accessed without index
- **Character Escaping**
  - New `--escape` option to escape special characters
  - Escapes: newline (`\n`), carriage return (`\r`), tab (`\t`), quotes (`'`, `"`)
  - Works with all output modes (frontmatter, content, both, template)
- **Enhanced Read Command**
  - Template mode validation (requires `--template` when `--output template`)
  - Support for complex output formats (JSON, custom text, etc.)
  - Graceful handling of missing frontmatter fields in templates
- **Library API Updates**
  - Template rendering functions available for library users
  - Character escaping functions for text processing

### Version 0.4.0

- **New update command**
  - `update` command for modifying frontmatter fields in place
  - Six case transformation types: upper, lower, Sentence case, Title Case, snake_case, kebab-case
  - Flexible value replacement with substring and regex support
  - Value removal with regex pattern support
  - Automatic array deduplication (configurable)
  - Multiple operations can be applied in sequence
- **Enhanced CLI options**
  - `--case` option for case transformations
  - `--replace` option for value replacement
  - `--remove` option for value removal
  - Shared `--ignore-case` and `--regex` options for both replace and remove operations
  - `--deduplication` option to control array deduplication
- **Library API enhancements**
  - `update_frontmatter()` function for programmatic updates
  - `update_and_output()` function for direct console output
  - Comprehensive operation support in library mode
- **Comprehensive testing**
  - 27 new update tests covering all update functionality
  - Enhanced error handling and edge case coverage
- **Documentation updates**
  - Complete update command documentation
  - Detailed update examples and use cases
  - Enhanced API documentation with update functions

### Version 0.3.0

- **New validation command**
  - `validate` command for comprehensive frontmatter validation
  - Eight validation types: exist, not, eq, ne, contain, not-contain, match, not-match
  - Support for field existence, value equality, array content, and regex pattern validation
- **Enhanced CLI capabilities**
  - Repeatable validation options (e.g., multiple `--exist` flags)
  - Case-insensitive validation with `--ignore-case`
  - CSV export for validation failures with detailed failure reasons
- **Library API enhancements**
  - New `validate_frontmatter()` function for programmatic validation
  - New `validate_and_output()` function for direct output
  - Comprehensive validation rule format
- **Comprehensive testing**
  - 30 new validation tests covering all validation types
  - 7 new CLI tests for validation functionality
  - Enhanced error handling and edge case coverage
- **Documentation updates**
  - Complete validation command documentation
  - Detailed validation examples and use cases
  - Enhanced API documentation with validation functions

### Version 0.2.0

- **Enhanced search capabilities**
  - Array/list value matching: Search within array frontmatter fields
  - Regex pattern matching: Use regular expressions for flexible value search
  - Support for both scalar and array field searches
- **New CLI options**
  - `--regex` flag for enabling regex pattern matching
  - Improved help documentation with regex examples
- **Library API enhancements**
  - Updated `search_frontmatter()` function with `regex` parameter
  - Backward compatible with existing code
- **Comprehensive testing**
  - Added tests for array value matching
  - Added tests for regex functionality
  - Added CLI tests for new features
- **Documentation updates**
  - Detailed regex support documentation
  - Enhanced examples and usage patterns

### Version 0.1.0

- Initial release
- YAML frontmatter parsing
- CLI with read and search commands
- Library API for programmatic usage
- Glob pattern support
- CSV export functionality
- Case-sensitive and case-insensitive search
- Comprehensive test suite

## Mics

- Download stats: https://pypistats.org/packages/frontmatter-utils
