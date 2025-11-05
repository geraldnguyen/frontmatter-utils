# CLI Command Reference

This document provides a comprehensive reference for all CLI commands and options available in the `fmu` (frontmatter-utils) tool.

## Global Options

- `--format FORMAT`: Format of frontmatter (default: yaml). May support TOML, JSON, INI in future versions.

## Commands

### `version`
Show the version number.

```bash
fmu version
```

### `help`
Show help information.

```bash
fmu help
```

### `read PATTERNS`
Parse files and extract frontmatter and/or content.

**Arguments:**
- `PATTERNS`: One or more glob patterns, file paths, or directory paths

**Options:**
- `--output [frontmatter|content|both|template]`: What to output (default: both)
- `--skip-heading`: Skip section headings (default: false)
- `--escape`: Escape special characters in output (default: false) *(New in v0.9.0)*
- `--template TEMPLATE`: Template string for output (required when --output is template) *(New in v0.9.0)*
- `--file FILE`: Save output to file instead of console *(New in v0.10.0)*
- `--save-specs DESCRIPTION FILE`: Save command configuration to specs file *(New in v0.5.0)*

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

# Save command to specs file
fmu read "*.md" --output frontmatter --save-specs "read blog posts" specs.yaml
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

### `search PATTERNS`
Search for specific frontmatter fields.

**Arguments:**
- `PATTERNS`: One or more glob patterns, file paths, or directory paths

**Options:**
- `--name NAME`: **Required.** Name of the frontmatter field to search for
- `--value VALUE`: Optional. Value of the frontmatter to match
- `--ignore-case`: Case-insensitive matching (default: false)
- `--regex`: Use regex pattern matching for values (default: false)
- `--csv FILE`: Optional. Output results to specified CSV file
- `--save-specs DESCRIPTION FILE`: Save command configuration to specs file *(New in v0.5.0)*

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

# Save command to specs file
fmu search "*.md" --name tags --value "python" --save-specs "search python tags" specs.yaml
```

**Array Search (v0.2.0):**
When searching array/list frontmatter fields, each element is checked against the search value.

**Regex Support (v0.2.0):**
Use regular expressions for flexible pattern matching. Supports Python's `re` module syntax including:
- **Basic patterns**: `python`, `test`, etc.
- **Anchors**: `^start`, `end$`, `^exact$`
- **Character classes**: `[abc]`, `[a-z]`, `\d`, `\w`, `\s`
- **Quantifiers**: `*`, `+`, `?`, `{n}`, `{n,m}`
- **Groups**: `(pattern)`, `(?:pattern)`
- **Alternation**: `pattern1|pattern2`
- **Case-insensitive**: Use `--ignore-case` flag

### `validate PATTERNS`
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
- `--not-empty FIELD`: **Repeatable.** Require array field has at least one value *(New in v0.8.0)*
- `--list-size FIELD MIN MAX`: **Repeatable.** Require array field has between MIN and MAX values (inclusive) *(New in v0.8.0)*

**General Options:**
- `--ignore-case`: Case-insensitive matching (default: false)
- `--csv FILE`: Optional. Output validation failures to specified CSV file
- `--save-specs DESCRIPTION FILE`: Save command configuration to specs file *(New in v0.5.0)*

**Exit Code:** *(New in v0.14.0)*
- Returns `0` if all validations pass
- Returns `1` if any validation fails (including YAML syntax errors *(v0.16.0)*)
- Exit code behavior applies to both console and CSV output modes
- This enables the validate command to be used in CI/CD pipelines and shell scripts that check exit codes

**YAML Syntax Error Detection:** *(New in v0.16.0)*
- Files with malformed YAML frontmatter are now detected and reported as validation failures
- Previously, files with YAML syntax errors were silently skipped
- Error messages include the specific YAML syntax error and line/column location
- Common issues detected:
  - Incorrect indentation (e.g., ` themes:` with leading space)
  - Invalid YAML syntax
  - Malformed key-value pairs
- Reported with field name `frontmatter` and detailed error message

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

# Validate array is not empty (v0.8.0)
fmu validate "*.md" --not-empty tags

# Validate array size (v0.8.0)
fmu validate "*.md" --list-size tags 1 5

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

# Use in CI/CD pipelines (v0.14.0)
# The command will exit with 1 if validation fails, stopping the pipeline
fmu validate "content/**/*.md" --exist title --exist date
if [ $? -eq 0 ]; then
  echo "All validations passed!"
else
  echo "Validation failed!"
  exit 1
fi

# Export failures to CSV and check exit code (v0.14.0)
# Exit code is 1 even when using --csv if validations fail
fmu validate "*.md" --exist title --exist author --csv validation_report.csv
if [ $? -ne 0 ]; then
  echo "Validation failed! Check validation_report.csv for details"
  exit 1
fi

# Save command to specs file
fmu validate "*.md" --exist title --match "title ^.{0,50}$" --save-specs "validate titles" specs.yaml
```

### `update PATTERNS` *(New in v0.4.0)*
Update frontmatter fields in files with various transformations.

**Note:** As of v0.17.0, the update command preserves the original order of frontmatter fields when writing back to files.

**Arguments:**
- `PATTERNS`: One or more glob patterns, file paths, or directory paths

**Required Options:**
- `--name FIELD`: **Required.** Name of the frontmatter field to update

**Update Operations:**
- `--compute FORMULA`: **Repeatable.** Compute and set frontmatter value using formula (literal, placeholder, or function call) *(New in v0.12.0)*
- `--case CASE_TYPE`: Transform case of values. Options: `upper`, `lower`, `Sentence case`, `Title Case`, `snake_case`, `kebab-case`
- `--replace FROM TO`: **Repeatable.** Replace values matching FROM with TO
- `--remove VALUE`: **Repeatable.** Remove values matching VALUE

**Shared Operation Options:**
- `--ignore-case`: Ignore case when performing replacements and removals (default: false)
- `--regex`: Treat patterns as regex for replacements and removals (default: false)

**General Options:**
- `--deduplication {true,false}`: Eliminate exact duplicates in array values (default: true, applied last)
- `--save-specs DESCRIPTION FILE`: Save command configuration to specs file *(New in v0.5.0)*

**Examples:**
```bash
# Compute operations (v0.12.0)

## Update with literal value
fmu update "index.md" --name edition --compute 2
fmu update "index.md" --name edition --compute "2nd"

## Update with current timestamp
fmu update "*.md" --name last_update --compute "=now()"

## Create empty list
fmu update "index.md" --name aliases --compute "=list()"

## Append to existing list
fmu update "index.md" --name aliases --compute "/newest-alias"

## Create hash from frontmatter field
fmu update "*.md" --name content_id --compute "=hash($frontmatter.url, 10)"

## Concatenate strings
fmu update "*.md" --name aliases --compute "=concat(/post/, $frontmatter.content_id)"

## Use placeholder references
fmu update "*.md" --name source_file --compute "$filename"
fmu update "*.md" --name full_path --compute "$filepath"

## Multiple compute operations (executed in order)
fmu update "index.md" --name aliases --compute "=list()"
fmu update "index.md" --name content_id --compute "=hash($frontmatter.url, 10)"
fmu update "index.md" --name aliases --compute "=concat(/post/, $frontmatter.content_id)"

## Slice list to get last element (v0.13.0)
fmu update "*.md" --name aliases --compute "=slice($frontmatter.aliases, -1)"

## Slice list to get first three elements (v0.13.0)
fmu update "*.md" --name top_tags --compute "=slice($frontmatter.tags, 0, 3)"

## Slice list with step (every other element) (v0.13.0)
fmu update "*.md" --name filtered_items --compute "=slice($frontmatter.items, 0, 10, 2)"

## Use coalesce to provide fallback values (v0.18.0)
fmu update "*.md" --name final_description --compute "=coalesce($frontmatter.description, $frontmatter.summary, 'No description available')"

## Use coalesce with multiple frontmatter fields (v0.18.0)
fmu update "*.md" --name display_title --compute "=coalesce($frontmatter.short_title, $frontmatter.title, $frontmatter.name)"

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

# Deduplication only (v0.8.0 fix)
fmu update "*.md" --name categories --deduplication true

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

# Save command to specs file
fmu update "*.md" --name title --case "Title Case" --save-specs "title case" specs.yaml
```

**Compute Formulas (v0.12.0):**
Formulas can be:
- **Literal values**: `1`, `2nd`, `just any text`
- **Placeholder references**:
  - `$filename`: Base filename (e.g., "post.md")
  - `$filepath`: Full file path
  - `$content`: Content after frontmatter
  - `$frontmatter.fieldname`: Access frontmatter field (single value or array)
  - `$frontmatter.fieldname[N]`: Access array element by index (0-based)
- **Function calls**: `=function_name(param1, param2, ...)`

**Built-in Functions (v0.12.0):**
- `now()`: Return current datetime in ISO 8601 format (e.g., `2025-10-20T00:30:00Z`)
- `list()`: Return an empty list
- `hash(string, hash_length)`: Create a fixed-length hash of the string parameter
- `concat(string, ...)`: Concatenate 2 or more string parameters
- `slice(list, start)`: Slice a list from start index to end *(New in v0.13.0)*
- `slice(list, start, stop)`: Slice a list from start to stop (exclusive) *(New in v0.13.0)*
- `slice(list, start, stop, step)`: Slice a list with step interval *(New in v0.13.0)*
  - Supports negative indices (Python-like behavior)
  - Example: `slice($frontmatter.aliases, -1)` gets the last element
- `coalesce(value1, value2, ...)`: Return the first non-empty, non-blank value *(New in v0.18.0)*
  - Skips: None/null values, empty strings, whitespace-only strings, empty lists, empty dicts, unresolved placeholders
  - Keeps: Numbers (including 0), booleans (including False), non-empty strings/lists/dicts
  - Returns: The first valid value, or None if all values are empty
  - Example: `coalesce($frontmatter.description, $frontmatter.summary, "default")` uses description if not empty, falls back to summary, then to "default"

**Compute Behavior:**
- If the frontmatter field **does not exist**, it will be **created** with the computed value
- If the frontmatter field **exists and is a scalar**, it will be **replaced** with the computed value
- If the frontmatter field **exists and is a list**:
  - If the computed value is **not a list**, it will be **appended** to the list
  - If the computed value **is a list** (e.g., from `slice()`), it will **replace** the entire list *(Updated in v0.13.0)*

**Case Transformations:**
- `upper`: UPPERCASE
- `lower`: lowercase
- `Sentence case`: Sentence case (first letter capitalized)
- `Title Case`: Title Case (capitalize each word)
- `snake_case`: snake_case (lowercase with underscores)
- `kebab-case`: kebab-case (lowercase with hyphens)

**Note:** Case transformations properly handle contractions (e.g., "can't" → "Can't", not "Can'T") as of v0.8.0.

### `execute SPECS_FILE` *(New in v0.6.0, Enhanced in v0.15.0)*
Execute all commands stored in a specs file.

**Arguments:**
- `SPECS_FILE`: Path to the YAML specs file containing commands

**Options:**
- `--yes`: Skip all confirmation prompts and execute all commands automatically

**Examples:**
```bash
# Execute commands with confirmation prompts
fmu execute commands.yaml

# Execute commands without confirmation prompts
fmu execute commands.yaml --yes
```

**Behavior:**
- Commands are executed sequentially in the order they appear in the specs file
- Before each command, displays: `------------\n[command text]\n------------\n`
- Without `--yes`, prompts: `Proceed with the above command? Answer yes or no`
- **Exit Code Handling (v0.15.0):**
  - If any command returns a non-zero exit code, execution stops immediately
  - The `execute` command returns that same non-zero exit code
  - If all commands succeed (return 0), execution continues through all commands
- After all commands complete (or stop on failure), displays execution statistics:
  - Number of commands executed
  - Total elapsed time
  - Total execution time (excluding user confirmation waits)
  - Average execution time per command
  - Breakdown by command type (e.g., `read: 0, validate: 1, update: 3`)

**Note:** 
- Each command in the specs file can specify its own output destination (console or file via `--file` option), allowing for flexible output workflows.
- Exit codes enable use in CI/CD pipelines and scripts that check for command success/failure.

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
/path/to/file1.md:
- 	author: None --> Field 'author' does not exist

/path/to/file2.md:
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

## Error Handling

The CLI handles various error conditions gracefully:

- **File not found**: Reports error for each missing file
- **Invalid YAML**: Reports parsing errors with details
- **Encoding issues**: Reports non-UTF-8 file encoding errors
- **Invalid format**: Reports unsupported format errors
- **Missing required options**: Displays usage information
- **Invalid regex**: Reports regex compilation errors

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


## Troubleshooting

### CI: UnicodeEncodeError on Windows runners

If an `fmu update` or `fmu execute` command fails on CI with an error like:

```
Error executing command: 'charmap' codec can't encode character '\u0101' in position 47: character maps to <undefined>
```

This typically means the runner's Python standard streams are using a non-UTF-8 encoding (for example Windows cp1252) and a script tried to print or write characters outside that encoding.

Fix: set Python's IO encoding to UTF-8 in the GitHub Actions job or step by adding:

```yaml
# add to job or step
env:
  PYTHONIOENCODING: utf-8
```

This ensures stdout/stderr use UTF-8 and prevents UnicodeEncodeError when output contains extended Unicode characters.