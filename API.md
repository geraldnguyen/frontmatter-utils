# Library API Reference

This document provides a comprehensive reference for the Python library API of `fmu` (frontmatter-utils).

## Core Functions

### `parse_frontmatter(content, format_type='yaml')`
Parse frontmatter from a content string.

**Parameters:**
- `content` (str): The file content as a string
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `Tuple[Optional[Dict[str, Any]], str]`: Frontmatter dictionary and remaining content

**Example:**
```python
from fmu import parse_frontmatter

content = """---
title: My Post
author: John Doe
---
Content here."""

frontmatter, remaining_content = parse_frontmatter(content)
print(frontmatter)  # {'title': 'My Post', 'author': 'John Doe'}
print(remaining_content)  # 'Content here.'
```

### `parse_file(file_path, format_type='yaml')`
Parse frontmatter from a file.

**Parameters:**
- `file_path` (str): Path to the file
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `Tuple[Optional[Dict[str, Any]], str]`: Frontmatter dictionary and content

**Example:**
```python
from fmu import parse_file

frontmatter, content = parse_file('example.md')
print(f"Title: {frontmatter.get('title')}")
print(f"Content: {content}")
```

### `extract_content(content, format_type='yaml')`
Extract only the content (without frontmatter) from a string.

**Parameters:**
- `content` (str): The file content as a string
- `format_type` (str): Format type (default: 'yaml')

**Returns:**
- `str`: Content without frontmatter

**Example:**
```python
from fmu import extract_content

content = """---
title: My Post
---
Content here."""

extracted = extract_content(content)
print(extracted)  # 'Content here.'
```

### `get_files_from_patterns(patterns)`
Get list of files matching the given glob patterns.

**Parameters:**
- `patterns` (List[str]): List of glob patterns, file paths, or directory paths

**Returns:**
- `List[str]`: List of file paths

**Example:**
```python
from fmu.core import get_files_from_patterns

# Get all markdown files
files = get_files_from_patterns(['*.md', 'docs/*.md'])
print(files)  # ['/path/to/file1.md', '/path/to/file2.md', ...]
```

## Search Functions

### `search_frontmatter(patterns, name, value=None, ignore_case=False, regex=False, format_type='yaml')`
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

**Example:**
```python
from fmu import search_frontmatter

# Search for all files with 'author' field
results = search_frontmatter(['*.md'], 'author')
for file_path, field_name, field_value in results:
    print(f"{file_path}: {field_name} = {field_value}")

# Search for specific author
results = search_frontmatter(['*.md'], 'author', 'John Doe')

# Search within array values
results = search_frontmatter(['*.md'], 'tags', 'python')

# Regex search
results = search_frontmatter(['*.md'], 'title', '^Guide.*', regex=True)

# Case-insensitive search
results = search_frontmatter(['*.md'], 'category', 'programming', ignore_case=True)
```

**Enhanced Features (v0.2.0):**
- **Array Matching**: When searching array/list frontmatter fields, each element is checked against the search value
- **Regex Support**: Use regular expressions for flexible pattern matching (Python's `re` module)

### `search_and_output(patterns, name, value=None, ignore_case=False, regex=False, csv_file=None, format_type='yaml')`
Search for frontmatter and output results directly.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `name` (str): Frontmatter field name to search for
- `value` (Optional[str]): Value to match (optional)
- `ignore_case` (bool): Case-insensitive matching (default: False)
- `regex` (bool): Use regex pattern matching for values (default: False)
- `csv_file` (Optional[str]): Path to CSV file for output (default: console output)
- `format_type` (str): Format type (default: 'yaml')

**Example:**
```python
from fmu import search_and_output

# Search and print to console
search_and_output(['*.md'], 'tags', 'python')

# Search and export to CSV
search_and_output(['*.md'], 'author', 'John Doe', csv_file='authors.csv')
```

## Validation Functions

### `validate_frontmatter(patterns, validations, ignore_case=False, format_type='yaml')`
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

# Array not empty validation (v0.8.0)
{'type': 'not-empty', 'field': 'tags'}

# Array size validation (v0.8.0)
{'type': 'list-size', 'field': 'tags', 'min': 1, 'max': 5}
```

**Example:**
```python
from fmu import validate_frontmatter

# Define validation rules
validations = [
    {'type': 'exist', 'field': 'title'},
    {'type': 'exist', 'field': 'author'},
    {'type': 'eq', 'field': 'status', 'value': 'published'},
    {'type': 'contain', 'field': 'tags', 'value': 'tech'},
    {'type': 'match', 'field': 'date', 'regex': r'^\d{4}-\d{2}-\d{2}$'},
    {'type': 'not-empty', 'field': 'tags'},  # v0.8.0
    {'type': 'list-size', 'field': 'tags', 'min': 1, 'max': 5}  # v0.8.0
]

# Validate files
failures = validate_frontmatter(['*.md'], validations)

# Process validation failures
for file_path, field_name, field_value, reason in failures:
    print(f"Validation failed in {file_path}: {reason}")
```

### `validate_and_output(patterns, validations, ignore_case=False, csv_file=None, format_type='yaml')`
Validate frontmatter and output results directly.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `validations` (List[Dict[str, Any]]): List of validation rule dictionaries
- `ignore_case` (bool): Case-insensitive matching (default: False)
- `csv_file` (Optional[str]): Path to CSV file for output (default: console output)
- `format_type` (str): Format type (default: 'yaml')

**Returns:** *(New in v0.14.0)*
- `int`: Number of validation failures (0 if all validations pass)

**Example:**
```python
from fmu import validate_and_output

validations = [
    {'type': 'exist', 'field': 'title'},
    {'type': 'eq', 'field': 'status', 'value': 'published'}
]

# Validate and print to console
failure_count = validate_and_output(['*.md'], validations)
if failure_count > 0:
    print(f"Validation failed with {failure_count} failures")
else:
    print("All validations passed!")

# Validate and export to CSV
validate_and_output(['*.md'], validations, csv_file='validation_report.csv')
```

**New Features (v0.3.0):**
- **Comprehensive Validation**: Eight different validation types for thorough frontmatter checking
- **Flexible Rules**: Multiple validation rules can be applied to the same file
- **Error Reporting**: Clear, descriptive error messages for each validation failure
- **CSV Export**: Export validation failures to CSV for analysis and reporting

## Update Functions *(New in v0.4.0)*

### `update_frontmatter(patterns, frontmatter_name, operations, deduplication=True, format_type='yaml')`
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
# Compute operation (v0.12.0)
{'type': 'compute', 'formula': 'literal_value'}  # Literal value
{'type': 'compute', 'formula': '$filename'}  # Placeholder reference
{'type': 'compute', 'formula': '=now()'}  # Function call

# Case transformation
{'type': 'case', 'case_type': 'upper'}  
# Options: 'upper', 'lower', 'Sentence case', 'Title Case', 'snake_case', 'kebab-case'

# Value replacement
{'type': 'replace', 'from': 'old_value', 'to': 'new_value', 'ignore_case': False, 'regex': False}

# Value removal
{'type': 'remove', 'value': 'value_to_remove', 'ignore_case': False, 'regex': False}
```

**Example:**
```python
from fmu import update_frontmatter

# Compute operations (v0.12.0)

# Set literal value (creates field if doesn't exist)
operations = [{'type': 'compute', 'formula': '1'}]
results = update_frontmatter(['index.md'], 'edition', operations, deduplication=False)

# Set value using now() function
operations = [{'type': 'compute', 'formula': '=now()'}]
results = update_frontmatter(['*.md'], 'last_update', operations, deduplication=False)

# Create empty list
operations = [{'type': 'compute', 'formula': '=list()'}]
results = update_frontmatter(['index.md'], 'aliases', operations, deduplication=False)

# Append to existing list
operations = [{'type': 'compute', 'formula': '/newest-alias'}]
results = update_frontmatter(['index.md'], 'aliases', operations, deduplication=False)

# Create hash from frontmatter field
operations = [{'type': 'compute', 'formula': '=hash($frontmatter.url, 10)'}]
results = update_frontmatter(['*.md'], 'content_id', operations, deduplication=False)

# Concatenate strings
operations = [{'type': 'compute', 'formula': '=concat(/post/, $frontmatter.content_id)'}]
results = update_frontmatter(['*.md'], 'aliases', operations, deduplication=False)

# Use placeholder references
operations = [{'type': 'compute', 'formula': '$filename'}]
results = update_frontmatter(['*.md'], 'source_file', operations, deduplication=False)

# Multiple compute operations example (builds an alias)
# Step 1: Create empty aliases list
operations = [{'type': 'compute', 'formula': '=list()'}]
results = update_frontmatter(['index.md'], 'aliases', operations, deduplication=False)

# Step 2: Create content_id from hash
operations = [{'type': 'compute', 'formula': '=hash($frontmatter.url, 10)'}]
results = update_frontmatter(['index.md'], 'content_id', operations, deduplication=False)

# Step 3: Add alias using concat
operations = [{'type': 'compute', 'formula': '=concat(/post/, $frontmatter.content_id)'}]
results = update_frontmatter(['index.md'], 'aliases', operations, deduplication=False)

# Define update operations (traditional operations)
operations = [
    {'type': 'case', 'case_type': 'lower'},
    {'type': 'replace', 'from': 'python', 'to': 'programming', 'ignore_case': False, 'regex': False},
    {'type': 'remove', 'value': 'deprecated', 'ignore_case': False, 'regex': False}
]

# Update files
results = update_frontmatter(['*.md'], 'tags', operations, deduplication=True)

# Process results
for result in results:
    if result['changes_made']:
        print(f"Updated {result['file_path']}")
        print(f"  Original: {result['original_value']}")
        print(f"  New: {result['new_value']}")
        print(f"  Reason: {result['reason']}")
```

**Additional Examples:**
```python
# Case transformation only
operations = [{'type': 'case', 'case_type': 'Title Case'}]
results = update_frontmatter(['*.md'], 'title', operations)

# Regex-based replacement
operations = [{
    'type': 'replace',
    'from': r'^test.*',
    'to': 'production',
    'regex': True,
    'ignore_case': False
}]
results = update_frontmatter(['*.md'], 'status', operations)

# Remove with regex
operations = [{
    'type': 'remove',
    'value': r'^draft.*',
    'regex': True,
    'ignore_case': True
}]
results = update_frontmatter(['*.md'], 'tags', operations)

# Deduplication only (v0.8.0)
results = update_frontmatter(['*.md'], 'categories', [], deduplication=True)
```

### `update_and_output(patterns, frontmatter_name, operations, deduplication=True, format_type='yaml')`
Update frontmatter and output results directly to console.

**Parameters:**
- `patterns` (List[str]): Glob patterns or file paths
- `frontmatter_name` (str): Name of frontmatter field to update
- `operations` (List[Dict[str, Any]]): List of update operation dictionaries
- `deduplication` (bool): Whether to deduplicate array values (default: True)
- `format_type` (str): Format type (default: 'yaml')

**Example:**
```python
from fmu import update_and_output

operations = [
    {'type': 'case', 'case_type': 'lower'},
    {'type': 'replace', 'from': 'old', 'to': 'new', 'ignore_case': False, 'regex': False}
]

# Update and print results to console
update_and_output(['*.md'], 'tags', operations, deduplication=True)
```

**New Features (v0.4.0):**
- **Case Transformations**: Six different case transformation types (upper, lower, sentence, title, snake_case, kebab-case)
- **Flexible Replacements**: Substring and regex-based replacements with case sensitivity options
- **Value Removal**: Remove specific values or regex patterns from frontmatter fields
- **Array Deduplication**: Automatic removal of exact duplicates in array values
- **Multiple Operations**: Apply multiple transformations in sequence
- **In-place Updates**: Modify files directly while preserving original structure

**New Features (v0.12.0):**
- **Compute Operations**: Calculate and set frontmatter values using formulas
- **Placeholder References**: Access file metadata and other frontmatter fields
- **Built-in Functions**: now(), list(), hash(), concat() for dynamic value generation
- **Auto-create Fields**: Compute operations can create frontmatter fields that don't exist
- **List Append**: Automatically append computed values to existing list fields

## Compute Functions *(New in v0.12.0)*

The update operations support compute formulas that can be:
- **Literal values**: `1`, `2nd`, `just any text`
- **Placeholder references**: `$filename`, `$filepath`, `$content`, `$frontmatter.name`, `$frontmatter.name[index]`
- **Function calls**: `=function_name(param1, param2, ...)`

### Built-in Compute Functions

#### `now()`
Return current datetime in ISO 8601 format.

**Returns:** String in format `YYYY-MM-DDTHH:MM:SSZ` (e.g., `2025-10-20T00:30:00Z`)

**Example:**
```python
operations = [{'type': 'compute', 'formula': '=now()'}]
results = update_frontmatter(['*.md'], 'last_update', operations, deduplication=False)
```

#### `list()`
Return an empty list.

**Returns:** Empty list `[]`

**Example:**
```python
operations = [{'type': 'compute', 'formula': '=list()'}]
results = update_frontmatter(['index.md'], 'aliases', operations, deduplication=False)
```

#### `hash(string, hash_length)`
Create a fixed-length hash of a string.

**Parameters:**
- `string`: String to hash (can be a placeholder reference)
- `hash_length`: Integer length of the resulting hash

**Returns:** Hexadecimal hash string of specified length

**Example:**
```python
operations = [{'type': 'compute', 'formula': '=hash($frontmatter.url, 10)'}]
results = update_frontmatter(['*.md'], 'content_id', operations, deduplication=False)
```

#### `concat(string1, string2, ...)`
Concatenate 2 or more strings.

**Parameters:**
- `string1, string2, ...`: Strings to concatenate (can be placeholder references or literals)

**Returns:** Concatenated string

**Example:**
```python
operations = [{'type': 'compute', 'formula': '=concat(/post/, $frontmatter.content_id)'}]
results = update_frontmatter(['*.md'], 'short_url', operations, deduplication=False)
```

#### `slice(list, start)` *(New in v0.13.0)*
#### `slice(list, start, stop)` *(New in v0.13.0)*
#### `slice(list, start, stop, step)` *(New in v0.13.0)*
Slice a list using Python-like slicing semantics.

**Parameters:**
- `list`: List to slice (typically a placeholder reference like `$frontmatter.aliases`)
- `start`: Starting index (can be negative for reverse indexing)
- `stop`: Stopping index (exclusive, optional)
- `step`: Step interval (optional, can be negative for reverse iteration)

**Returns:** Sliced list

**Examples:**
```python
# Get last element
operations = [{'type': 'compute', 'formula': '=slice($frontmatter.aliases, -1)'}]
results = update_frontmatter(['*.md'], 'aliases', operations, deduplication=False)

# Get first three elements
operations = [{'type': 'compute', 'formula': '=slice($frontmatter.tags, 0, 3)'}]
results = update_frontmatter(['*.md'], 'top_tags', operations, deduplication=False)

# Get every other element
operations = [{'type': 'compute', 'formula': '=slice($frontmatter.items, 0, 10, 2)'}]
results = update_frontmatter(['*.md'], 'filtered_items', operations, deduplication=False)
```

### Placeholder References

- `$filename`: Base filename (e.g., "post.md")
- `$filepath`: Full file path
- `$content`: Content after frontmatter
- `$frontmatter.fieldname`: Access frontmatter field (single value or array)
- `$frontmatter.fieldname[N]`: Access array element by index (0-based)

### Compute Operation Behavior

The compute operation has special behavior compared to other update operations:

1. **Field Creation**: If the frontmatter field doesn't exist, it will be created
2. **Scalar Replacement**: If the field exists and is a scalar value, it will be replaced
3. **List Behavior**: If the field exists and is a list:
   - If the computed value is **not a list**, it will be **appended** to the list
   - If the computed value **is a list** (e.g., from `slice()`), it will **replace** the entire list *(Updated in v0.13.0)*

**Example:**
```python
# File initially has: title: "Test"

# Creates new field
operations = [{'type': 'compute', 'formula': '1'}]
results = update_frontmatter(['file.md'], 'edition', operations, deduplication=False)
# Result: title: "Test", edition: 1

# Replaces scalar field
operations = [{'type': 'compute', 'formula': '2'}]
results = update_frontmatter(['file.md'], 'edition', operations, deduplication=False)
# Result: title: "Test", edition: 2

# Appends to list field
# File has: aliases: ['/old']
operations = [{'type': 'compute', 'formula': '/new'}]
results = update_frontmatter(['file.md'], 'aliases', operations, deduplication=False)
# Result: aliases: ['/old', '/new']
```

## Template Functions *(New in v0.9.0)*

### `render_template(template_str, filename, filepath, content, frontmatter, escape=False)`
Render a template string with file data and frontmatter values.

**Parameters:**
- `template_str` (str): Template string with placeholders
- `filename` (str): Filename to substitute for `$filename`
- `filepath` (str): File path to substitute for `$filepath`
- `content` (str): Content to substitute for `$content`
- `frontmatter` (Dict[str, Any]): Frontmatter dictionary
- `escape` (bool): Whether to escape special characters (default: False)

**Returns:**
- `str`: Rendered template string

**Template Placeholders:**
- `$filename`: Base filename
- `$filepath`: Full file path
- `$content`: Content after frontmatter
- `$frontmatter.fieldname`: Access frontmatter field
- `$frontmatter.fieldname[N]`: Access array element by index

**Example:**
```python
from fmu.core import render_template

frontmatter = {
    'title': 'My Post',
    'tags': ['python', 'tutorial'],
    'author': 'John Doe'
}

template = '{ "title": "$frontmatter.title", "first_tag": "$frontmatter.tags[0]", "file": "$filename" }'
result = render_template(template, 'post.md', '/path/to/post.md', 'Content here', frontmatter)
print(result)
# Output: { "title": "My Post", "first_tag": "python", "file": "post.md" }
```

### `escape_string(text)`
Escape special characters in a string.

**Parameters:**
- `text` (str): Text to escape

**Returns:**
- `str`: Escaped text

**Escaped Characters:**
- Newline: `\n`
- Carriage return: `\r`
- Tab: `\t`
- Single quote: `'` → `\'`
- Double quote: `"` → `\"`

**Example:**
```python
from fmu.core import escape_string

text = "Line 1\nLine 2\t'quoted'"
escaped = escape_string(text)
print(escaped)
# Output: Line 1\\nLine 2\\t\\'quoted\\'
```

## Specs Functions *(New in v0.5.0)*

### `save_command_to_specs(command, description, patterns, options, specs_file)`
Save a command configuration to a YAML specs file.

**Parameters:**
- `command` (str): Command name ('read', 'search', 'validate', 'update')
- `description` (str): Short description of the command
- `patterns` (List[str]): List of file patterns
- `options` (Dict[str, Any]): Command options
- `specs_file` (str): Path to specs file

**Example:**
```python
from fmu.specs import save_command_to_specs

options = {
    'name': 'tags',
    'value': 'python',
    'regex': False,
    'ignore_case': True
}

save_command_to_specs('search', 'Find Python tags', ['*.md'], options, 'commands.yaml')
```

### `load_specs_file(specs_file)`
Load commands from a YAML specs file.

**Parameters:**
- `specs_file` (str): Path to specs file

**Returns:**
- `List[Dict[str, Any]]`: List of command dictionaries

**Example:**
```python
from fmu.specs import load_specs_file

commands = load_specs_file('commands.yaml')
for cmd in commands:
    print(f"Command: {cmd['command']}, Description: {cmd['description']}")
```

### `execute_specs_file(specs_file, skip_confirmation=False)` *(New in v0.6.0, Enhanced in v0.15.0)*
Execute all commands from a specs file.

**Parameters:**
- `specs_file` (str): Path to specs file
- `skip_confirmation` (bool): Whether to skip user confirmation prompts (default: False)

**Returns:**
- `Tuple[int, Dict[str, Any]]`: Exit code and execution statistics
  - `exit_code` (int): 0 if all commands succeeded, non-zero if any command failed
  - `stats` (dict): Dictionary containing execution statistics

**Example:**
```python
from fmu.specs import execute_specs_file, print_execution_stats

# Execute with confirmation prompts
exit_code, stats = execute_specs_file('commands.yaml')
print_execution_stats(stats)

# Execute without confirmation prompts
exit_code, stats = execute_specs_file('commands.yaml', skip_confirmation=True)
if exit_code != 0:
    print(f"Execution failed with exit code {exit_code}")
```

**Behavior (v0.15.0):**
- Commands are executed sequentially
- If any command returns a non-zero exit code, execution stops immediately and returns that exit code
- If a command returns 0, execution continues to the next command
- Enables use in CI/CD pipelines and automation scripts

### `execute_command(command_entry)` *(New in v0.6.0, Enhanced in v0.15.0)*
Execute a single command from a command dictionary.

**Parameters:**
- `command_entry` (Dict[str, Any]): Command dictionary with command type, patterns, and options

**Returns:**
- `int`: Exit code (0 for success, non-zero for failure)

**Example:**
```python
from fmu.specs import execute_command

command = {
    'command': 'validate',
    'description': 'Check required fields',
    'patterns': ['*.md'],
    'exist': ['title', 'author']
}

exit_code = execute_command(command)
if exit_code == 0:
    print("Validation passed")
else:
    print(f"Validation failed with exit code {exit_code}")
```

## Error Handling

The library handles various error conditions gracefully:

- **File not found**: Raises `FileNotFoundError`
- **Invalid YAML**: Raises `ValueError` with details
- **Encoding issues**: Raises `ValueError` for non-UTF-8 files
- **Invalid format**: Raises `ValueError` for unsupported formats
- **Invalid regex**: Raises `ValueError` for regex compilation errors

**Example:**
```python
from fmu import parse_file

try:
    frontmatter, content = parse_file('nonexistent.md')
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Parsing error: {e}")
```

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
- **Case-insensitive**: Use `ignore_case=True` parameter

### Regex Examples

```python
from fmu import search_frontmatter

# Find titles starting with "Guide" or "Tutorial"
results = search_frontmatter(['*.md'], 'title', '^(Guide|Tutorial)', regex=True)

# Find tags containing digits
results = search_frontmatter(['*.md'], 'tags', r'\d', regex=True)

# Find authors with names ending in "son"
results = search_frontmatter(['*.md'], 'author', 'son$', regex=True, ignore_case=True)

# Find categories with 2-4 characters
results = search_frontmatter(['*.md'], 'category', '^.{2,4}$', regex=True)
```

### Array + Regex Combination

When using regex with array fields, the pattern is matched against each array element:

```python
# File content:
# ---
# tags: [python3, javascript, html5, css3]
# ---

# Matches both "python3" and "html5" (numbers at end)
results = search_frontmatter(['file.md'], 'tags', r'\d+$', regex=True)
```

## Testing

Run the test suite:

```bash
python -m pytest tests/
```

Or run individual test modules:

```bash
python -m pytest tests/test_core.py
python -m pytest tests/test_search.py
python -m pytest tests/test_validation.py
python -m pytest tests/test_update.py
```

## Usage Examples

### Basic Usage

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

### Advanced Usage

```python
from fmu import search_frontmatter, validate_frontmatter, update_frontmatter

# Complex search with regex
results = search_frontmatter(
    patterns=['blog/**/*.md'],
    name='tags',
    value='^(python|javascript)',
    regex=True,
    ignore_case=True
)

# Comprehensive validation
validations = [
    {'type': 'exist', 'field': 'title'},
    {'type': 'exist', 'field': 'author'},
    {'type': 'eq', 'field': 'status', 'value': 'published'},
    {'type': 'contain', 'field': 'tags', 'value': 'tech'},
    {'type': 'not-empty', 'field': 'tags'},
    {'type': 'list-size', 'field': 'tags', 'min': 1, 'max': 5}
]
failures = validate_frontmatter(['*.md'], validations)

# Complex update with multiple operations
operations = [
    {'type': 'case', 'case_type': 'lower'},
    {'type': 'replace', 'from': 'javascript', 'to': 'js', 'ignore_case': False, 'regex': False},
    {'type': 'replace', 'from': 'python', 'to': 'py', 'ignore_case': False, 'regex': False},
    {'type': 'remove', 'value': '^test.*', 'ignore_case': False, 'regex': True}
]
results = update_frontmatter(['*.md'], 'tags', operations, deduplication=True)
```
