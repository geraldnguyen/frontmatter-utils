# Specs File Specification

The specs file format allows you to save and reuse command configurations for the frontmatter-utils CLI. This is useful for storing commonly used commands and their options.

## File Format

The specs file is a YAML file with the following structure:

```yaml
commands:
  - command: [command_name]
    description: [short_description]
    patterns: [array_of_patterns]
    [option1]: [option_value]
    [option2]: [option_value]
```

## Commands

### Read Command

Saves configuration for parsing files and extracting frontmatter/content.

```yaml
commands:
  - command: read
    description: read blog posts
    patterns:
      - "blog/*.md"
      - "posts/*.md"
    output: frontmatter
    skip_heading: true
  
  - command: read
    description: export to JSON with template
    patterns:
      - "*.md"
    output: template
    template: '{ "title": "$frontmatter.title", "content": "$content" }'
    escape: true
    file: output.json
```

**Options:**
- `output`: What to output (`frontmatter`, `content`, `both`, or `template`) *(template added in v0.9.0)*
- `skip_heading`: Whether to skip section headings (`true` or `false`)
- `template`: Template string for custom output formatting *(New in v0.9.0)*
- `escape`: Escape special characters in output (`true` or `false`) *(New in v0.9.0)*
- `file`: Save output to file instead of console *(New in v0.10.0)*

### Search Command

Saves configuration for searching specific frontmatter fields.

```yaml
commands:
  - command: search
    description: search folk tales
    patterns:
      - "stories/*.md"
    name: tags
    value: folk-tale
    regex: false
    
  - command: search
    description: search myths with regex
    patterns:
      - "stories/*.md"
    name: tags
    value: myth.*
    regex: true
    ignore_case: true
    csv: search_results.csv
```

**Options:**
- `name`: Name of frontmatter field to search for (required)
- `value`: Value to match (optional)
- `ignore_case`: Case-insensitive matching (`true` or `false`)
- `regex`: Use regex pattern matching (`true` or `false`)
- `csv`: Output to CSV file (file path)

### Validate Command

Saves configuration for validating frontmatter fields against rules.

```yaml
commands:
  - command: validate
    description: title required and less than 50 chars
    patterns:
      - "*.md"
    match:
      - "title ^.{0,50}$"
    eq:
      - "status Published"
    exist:
      - "author"
    csv: validation_report.csv
  
  - command: validate
    description: tags must be non-empty and have 1-5 items
    patterns:
      - "*.md"
    not_empty:
      - "tags"
    list_size:
      - "tags 1 5"
```

**Options:**
- `exist`: Array of fields that must exist
- `not`: Array of fields that must not exist
- `eq`: Array of "field value" pairs for equality checks
- `ne`: Array of "field value" pairs for inequality checks
- `contain`: Array of "field value" pairs for array containment checks
- `not_contain`: Array of "field value" pairs for array non-containment checks
- `match`: Array of "field regex" pairs for regex matching
- `not_match`: Array of "field regex" pairs for regex non-matching
- `not_empty`: Array of fields that must be non-empty arrays *(New in v0.8.0)*
- `list_size`: Array of "field min max" triples for array size validation *(New in v0.8.0)*
- `ignore_case`: Case-insensitive matching (`true` or `false`)
- `csv`: Output to CSV file (file path)

**Exit Code:** *(New in v0.14.0)*
- The validate command returns exit code `0` if all validations pass, or `1` if any validation fails
- This enables validation to be used in CI/CD pipelines and scripts

**YAML Syntax Error Detection:** *(New in v0.16.0)*
- Files with malformed YAML frontmatter are now detected and reported as validation failures
- Previously, files with YAML syntax errors were silently skipped
- Validation failures due to YAML syntax errors are reported with field name `frontmatter`

### Update Command

Saves configuration for updating frontmatter fields.

```yaml
commands:
  - command: update
    description: Title case transformation
    patterns:
      - "*.md"
    name: title
    case: Title Case
    
  - command: update
    description: remove test tags
    patterns:
      - "*.md"
    name: tags
    remove:
      - "^test.*"
    regex: true
    deduplication: true
  
  - command: update
    description: set edition number
    patterns:
      - "index.md"
    name: edition
    compute:
      - "2"
  
  - command: update
    description: update last modified timestamp
    patterns:
      - "*.md"
    name: last_update
    compute:
      - "=now()"
  
  - command: update
    description: create content ID from URL
    patterns:
      - "*.md"
    name: content_id
    compute:
      - "=hash($frontmatter.url, 10)"
  
  - command: update
    description: build short alias
    patterns:
      - "*.md"
    name: aliases
    compute:
      - "=concat(/post/, $frontmatter.content_id)"
  
  - command: update
    description: keep only last alias (v0.13.0)
    patterns:
      - "*.md"
    name: aliases
    compute:
      - "=slice($frontmatter.aliases, -1)"
```

**Options:**
- `name`: Name of frontmatter field to update (required)
- `deduplication`: Eliminate exact duplicates in array values (`true` or `false`)
- `case`: Transform case (`upper`, `lower`, `Sentence case`, `Title Case`, `snake_case`, `kebab-case`)
- `compute`: Array of formulas to compute and set field values *(New in v0.12.0)*
- `replace`: Array of "from to" pairs for value replacement
- `remove`: Array of values to remove
- `ignore_case`: Ignore case for replacements and removals (`true` or `false`)
- `regex`: Treat patterns as regex for replacements and removals (`true` or `false`)

**Compute Formulas (v0.12.0):**
- Literal values: `"1"`, `"2nd"`, `"any text"`
- Placeholder references: `"$filename"`, `"$filepath"`, `"$content"`, `"$frontmatter.name"`, `"$frontmatter.name[index]"`
- Function calls: `"=now()"`, `"=list()"`, `"=hash($frontmatter.url, 10)"`, `"=concat(/post/, $frontmatter.id)"`

**Built-in Functions:**
- `now()`: Current datetime in ISO 8601 format
- `list()`: Empty list
- `hash(string, length)`: Fixed-length hash of string
- `concat(str1, str2, ...)`: Concatenate strings
- `slice(list, start)`: Slice list from start to end *(New in v0.13.0)*
- `slice(list, start, stop)`: Slice list from start to stop (exclusive) *(New in v0.13.0)*
- `slice(list, start, stop, step)`: Slice list with step interval *(New in v0.13.0)*

## Usage

### Saving Specs

Use the `--save-specs` option with any command to save the command configuration:

```bash
# Save a read command configuration
fmu read "*.md" --output frontmatter --save-specs "read blog posts" specs.yaml

# Save a search command configuration  
fmu search "*.md" --name tags --value folk-tale --save-specs "search folk tales" specs.yaml

# Save a validate command configuration
fmu validate "*.md" --exist title --match "title ^.{0,50}$" --save-specs "validate titles" specs.yaml

# Save an update command configuration
fmu update "*.md" --name title --case "Title Case" --save-specs "title case" specs.yaml
```

### File Behavior

- If the specs file doesn't exist, it will be created
- If the specs file exists, new commands will be appended to the existing commands array
- Commands are always appended (no overwriting or merging of existing commands)

### Example Specs File

```yaml
commands:
  - command: read
    description: read all markdown files
    patterns:
      - "*.md"
      - "docs/*.md"
    output: both
    
  - command: search
    description: find published posts
    patterns:
      - "posts/*.md"
    name: status
    value: published
    ignore_case: true
    
  - command: validate
    description: check required fields
    patterns:
      - "posts/*.md"
    exist:
      - "title"
      - "author"
      - "date"
    match:
      - "date \\d{4}-\\d{2}-\\d{2}"
    csv: validation_results.csv
    
  - command: update
    description: standardize tags
    patterns:
      - "posts/*.md"
    name: tags
    case: lower
    deduplication: true
```
## Executing Specs Files

Once you have created a specs file with saved commands, you can execute all commands in the file using the `execute` command.

### Basic Usage

```bash
# Execute with confirmation prompts
fmu execute specs.yaml

# Execute without confirmation prompts
fmu execute specs.yaml --yes
```

### Execution Behavior

**Command Execution:**
- Commands are executed sequentially in the order they appear in the specs file
- Before each command, displays the formatted command text
- Without `--yes`, prompts for confirmation: `Proceed with the above command? Answer yes or no`
- Each command's output is displayed as it executes

**Exit Code Handling (v0.15.0):**
- If any command returns a non-zero exit code, execution stops immediately
- The `execute` command returns the same non-zero exit code from the failed command
- If all commands succeed (return 0), execution continues through all commands
- This enables use in CI/CD pipelines and automation scripts

**Execution Statistics:**
After execution completes (or stops on failure), displays:
- Number of commands executed
- Total elapsed time
- Total execution time (excluding user confirmation waits)
- Average execution time per command
- Breakdown by command type (e.g., `read: 1, validate: 2, update: 0`)

### Example

```bash
# Create a specs file with multiple commands
fmu validate "posts/*.md" --exist title --exist author --save-specs "validate posts" checks.yaml
fmu validate "posts/*.md" --not-empty tags --save-specs "validate tags" checks.yaml
fmu search "posts/*.md" --name status --value draft --csv draft_posts.csv --save-specs "find drafts" checks.yaml

# Execute all commands
fmu execute checks.yaml --yes
```

**Output:**
```
------------
fmu validate posts/*.md --exist title --exist author
------------
Description: validate posts
Executing command 1 of 3...
Command completed successfully in 0.01 seconds.

------------
fmu validate posts/*.md --not-empty tags
------------
Description: validate tags
Executing command 2 of 3...
posts/draft-post.md:
- tags: [] --> Field 'tags' must be an array with at least 1 value
Command failed with exit code 1.
Stopping execution due to command failure.
==================================================
EXECUTION STATISTICS
==================================================
Number of commands executed: 1
Total elapsed time: 0.02 seconds
Total execution time: 0.02 seconds
Average execution time per command: 0.02 seconds

Commands executed by type:
  read: 0
  search: 0
  validate: 1
  update: 0

Failed commands: 1
```

The execution stops at the second command because it failed, and the third command is not executed. The exit code is 1, indicating failure.
