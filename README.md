---
homepage: https://github.com/geraldnguyen/frontmatter-utils
package: https://pypi.org/project/frontmatter-utils/
stats: https://pypistats.org/packages/frontmatter-utils
---

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

## Documentation

For detailed information about using fmu, see:

- **[CLI Command Reference](CLI.md)**: Complete guide to all CLI commands, options, and examples
- **[Library API Reference](API.md)**: Comprehensive Python API documentation
- **[Specs File Specification](SPECS.md)**: Format and usage of specs files for command automation

## Changelog

### Version 0.17.0

- **Frontmatter Order Preservation**
  - The `update` command now preserves the original order of frontmatter fields when writing back to files
  - Previously, frontmatter fields were sorted alphabetically after updates
  - Now maintains the exact order in which fields appeared in the original file
  - Implementation: Added `sort_keys=False` parameter to all `yaml.dump()` calls in the update functionality
- **Library API Updates**
  - `update_frontmatter()` and related functions now preserve field order when modifying frontmatter
- **Testing**
  - Added comprehensive unit test `test_frontmatter_order_preservation()` to verify field order is maintained
  - All 202 tests passing (201 previous tests + 1 new test for order preservation)

### Version 0.16.0

- **YAML Syntax Error Detection (Bugfix)**
  - The `validate` command now properly detects and reports YAML syntax errors in frontmatter
  - Previously, files with malformed YAML frontmatter were silently skipped
  - Now reports detailed YAML parsing errors as validation failures with:
    - Field name: `frontmatter`
    - Error message includes the specific YAML syntax error and line/column location
    - Returns non-zero exit code (1) when YAML syntax errors are detected
  - Works with both console and CSV output modes
  - Example: Files with incorrect indentation (e.g., ` themes:` with leading space) are now properly detected
- **Library API Updates**
  - `validate_frontmatter()` now reports YAML parsing errors as validation failures instead of silently skipping files
  - File encoding errors (UnicodeDecodeError) are also reported as validation failures
- **Testing**
  - Added 6 comprehensive unit tests for various YAML syntax error detection scenarios
  - Tests cover: incorrect indentation, missing colons, invalid structures, CSV output, and more
  - All 201 tests passing (195 previous tests + 6 new tests for YAML error handling)

### Version 0.15.0

- **Execute Command Exit Code Handling**
  - The `execute` command now properly returns exit codes from executed commands
  - If any command returns a non-zero exit code, execution stops immediately and returns that exit code
  - If a command returns exit code 0, execution continues to the next command
  - Enables spec files to be used in CI/CD pipelines and scripts that check exit codes
  - Works with all command types: `read`, `search`, `validate`, and `update`
- **Library API Updates**
  - `execute_command()` function now returns an exit code (integer) instead of a boolean success tuple
  - `execute_specs_file()` function now returns a tuple of (exit_code, stats_dict)
  - `cmd_execute()` function now returns an exit code
- **Testing**
  - Added 4 new comprehensive unit tests for exit code behavior
  - All 195 tests passing (24 total specs tests)

### Version 0.14.0

- **Exit Code for Validation Failures**
  - The `validate` command now returns a non-zero exit code (1) when any validation fails
  - Returns exit code 0 when all validations pass
  - Enables validation to be used in CI/CD pipelines and scripts that check exit codes
  - Works with all validation types: `--exist`, `--not`, `--eq`, `--ne`, `--contain`, `--not-contain`, `--match`, `--not-match`, `--not-empty`, `--list-size`
  - Exit code behavior applies to both console and CSV output modes
- **Library API Updates**
  - `validate_and_output()` function now returns the count of validation failures (integer)
  - `cmd_validate()` function now returns an exit code (0 for success, 1 for failure)
- **Testing**
  - Added comprehensive unit tests for exit code behavior
  - All 191 tests passing (9 new tests for exit code functionality, including CSV output tests)

### Version 0.13.0

- **Slice Function for Compute Operations**
  - New `slice()` function for list slicing in `--compute` option
  - Support for Python-like slicing syntax: `slice(list, start)`, `slice(list, start, stop)`, `slice(list, start, stop, step)`
  - Negative indices support for reverse indexing (e.g., `-1` for last element)
  - Negative step support for reverse iteration
- **Enhanced Compute Behavior**
  - When computed value is a list (e.g., from `slice()`), it now replaces the entire list instead of appending
  - Maintains backward compatibility: scalar computed values still append to list fields
- **Use Cases**
  - Extract last element: `=slice($frontmatter.aliases, -1)`
  - Get first N elements: `=slice($frontmatter.tags, 0, 3)`
  - Filter with step: `=slice($frontmatter.items, 0, 10, 2)` (every other element)
  - Reverse lists: `=slice($frontmatter.list, -1, 0, -1)`
- **Documentation**
  - Updated CLI.md with slice function examples
  - Updated API.md with slice function specifications
  - Updated SPECS.md with slice function usage
  - All 182 tests passing (18 new tests for slice functionality)

### Version 0.12.0

- **Compute Operations**
  - New `--compute` option for the update command to calculate and set frontmatter values
  - Support for literal values, placeholder references, and function calls
  - Built-in functions: `now()`, `list()`, `hash(string, length)`, `concat(string, ...)`
  - Placeholder references: `$filename`, `$filepath`, `$content`, `$frontmatter.name`, `$frontmatter.name[index]`
  - Auto-create frontmatter fields if they don't exist
  - Automatically append to list fields when computing values
- **Formula Types**
  - **Literals**: Set static values like `1`, `2nd`, `any text`
  - **Placeholders**: Reference file metadata and frontmatter fields
  - **Functions**: Dynamic value generation with built-in functions
- **Use Cases**
  - Generate timestamps with `=now()`
  - Create content IDs with `=hash($frontmatter.url, 10)`
  - Build dynamic URLs with `=concat(/post/, $frontmatter.id)`
  - Initialize empty arrays with `=list()`
  - Store file metadata in frontmatter
- **Documentation**
  - Updated CLI.md with compute examples and function reference
  - Updated API.md with compute operation specifications
  - Updated SPECS.md with compute formula examples
  - All 164 tests passing (28 new tests for compute functionality)

### Version 0.11.0

- **Documentation Reorganization**
  - Extracted CLI Command Reference to separate [CLI.md](CLI.md) file
  - Extracted Library API Reference to separate [API.md](API.md) file
  - Streamlined README.md to focus on Features, Installation, Getting Started, Changelog, and Mics sections
  - Added Documentation section with links to CLI, API, and Specs documentation
  - Enhanced SPECS.md with up-to-date command and option information
  - All documentation now reflects current implementation and features through v0.10.0

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
