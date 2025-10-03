# Version 0.1.0

Create a publishable python module named "fmu" with the following features:


Support 2 modes:
- Library: create re-usable API and packages to support the CLI and for general usages
- CLI:

Under CLI mode, the module support the following command and options
- "--format": default to YAML if not provided. May support other format e.g. TOML, JSON, INI in the future. Note this in the help info.
- "version": return the version number
- "help": return help information
- "read [glob-pattern]*": Support one or multiple glob pattern or file paths. Parse the files obtained from the command argument to extract the front matter and content and output them separately. This command supports the following options
  + "--output [frontmatter|content|both]": default to "both"
  + "--skip-heading [true|false]": default to false - print "Front matter:\n [front matter content]", "Content: \n [content"]" for each parsed part
- "search [glob-pattern]*": Support one or multiple glob pattern or file or folder paths. This command supports the following options:
  + "--name": required. name of the front matter to search for
  + "--value [value]": optional. value of the front matter to match
  + "--ignore-case [true|false]": default to false. Determine if the name and value matching should be case-sensitive or case-insensitive
  + "--csv [file path]": optional. If provided, output the search results to the specified CSV file. The CSV file should contain columns for file path, front matter name, and front matter value. The CSV contains column headings. If not provided, output each match in the following format: [file path]:\n- [front matter name]: [front matter value]

Save all dependencies in a requirements.txt file

Create extensive unit tests for both the library mode and CLI modes. 

Create comprehensive README file with instruction on getting started and how to use the library and CLI

# Version 0.2.0

Enhance the search capability with the following:
- Support searching values within an array front matter: if the front matter is an array and a "--value" is provided, match each element of the front matters values with search value. If the front matter is a scalar value and a "--value" is provided, continue matching the front matter's whole value with the search value. 
- Add "--regex [true|false]" option: default to false. Determine how the value-matching is performed. Document the flavour of regex supported in the README and help text.

Update or expose correcting library function to support the above changes in CLI.

Save all dependencies in a requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README file with comprehensive instruction on getting started and how to use the library and CLI

# Version 0.3.0

Add a new capability/command: Validation:

Support a new command "validate [patterns]". This command supports the following options:
- "--exist [frontmatter]": Can appear multiple times. If specify, require the present of the stated front matter. 
- "--not [fronmatter]": Can appear multiple times. If specify, the stated front matter must not be present
- "--eq [frontmatter] [value]": Can appear multiple times. If specify, the front matter must exist and the front matter's value must equal to the provided value
- "--ne [frontmatter] [value]": Can appear multiple times. If specify, the front matter must exist and the front matter's value must not equal to the provided value
- "--contain [frontmatter] [value]": Can appear multiple times. If specify, the front matter must exist and the front matter must be an array and one of its values must be equal to the provided value
- "--not-contain [frontmatter] [value]": Can appear multiple times. If specify, the front matter must exist and the front matter must be an array and none of its values is equal to the provided value
- "--match [frontmatter] [regex]": Can appear multiple times. If specify, the front matter must exist and the front matter's value must match the provided regex
- "--not-match [frontmatter] [regex]": Can appear multiple times. If specify, the front matter must exist and the front matter's value must not match the provided regex
- "--ignore-case [true|false]": default to false. Determine if the name and value matching should be case-sensitive or case-insensitive
- "--csv [file path]": optional. If provided, output the search results to the specified CSV file. The CSV file should contain columns for file path, front matter name, front matter value, and the reason for failure. The CSV contains column headings. If not provided, output each failed validation in the following format: [file path]:\n- \t[front matter name]: [front matter value] --> [failure reason]

There may be multiple validations per front matter and per input file

Update or expose correcting library function to support the above changes in CLI.

Save all dependencies in a requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README file with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI


# Version 0.4.0

Add a new capability/command: Update:

Support a new command "update [patterns]". This command supports the following options:
- "--frontmatter [frontmatter]": required. The name of the front matter to update
- "--deduplication [true|false]": default to true. Eliminate exact duplicates in the values of each front matter of type array.
- "--case [upper|lower|Sentence case|Title Case|snake_case|kebab-case]": transform the value or values (if array) of the front matter to the specified casing
- "--replace [from] [to]": Can appear multiple times. If specified and if the front matter's value (or one of front matter's values if array) match the [from], replace it by the [to] value . This option supports the following extra options:
     + "--ignore-case [true|false]: default to false. If true, ignore case when perform replacement.
     + "--regex [true|false]": default to false. If true, treat [from] and [to] as regex and perform regex replacement. If ignore case option is specified, perform regex replacement case-insensitively.
- "--remove [value]". Can appear multiple times. If specified and if the front matter's value (or one of front matter's values if array) match the [from], remove it. If the front matter is not of type array and the removal results in it having no value, remove the front matter. This option supports the same "--ignore-case" and "--regex [true|false]" option.
     + "--ignore-case [true|false]: default to false. If true, ignore case when perform removal.
     + "--regex [true|false]": default to false. If true, treat [value] as regex when perform removal. If ignore case option is specified, perform regex removal case-insensitively.

There may be multiple update per front matter and per input file. If deduplication option is specified, it must be the last to execute.

Update or expose correcting library function to support the above changes in CLI.

Save all dependencies in a requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README file with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI




# Version 0.5.0 - Create specs file from command

Add a new "--save-specs [short description] [yaml specs file]" option to "Read", "Search", "Validate" and "Update" command. If specified, save the command, patterns, and options to the specified specs file according to the specs file format and semantics detailed below. 
- If the file does not exist, create it
- If the file exist, update the file
- If the command inside the file does not exist, add the new command
- If the command inside the file already exists, append to the command's values

```
commands:            # Array of commands, new command are appended to the array
  - command: [command]
    description: [short description]
    [patterns]: [array of patterns]
    [option 1]: [option value or values, explicit or derived]
    [option 2]: [option value or values, explicit or derived]
```

Sample:

```
commands:
  - command: read
    description: read file
    patterns: [array of patterns]
    output: frontmatter|content|both
    skip_heading: true|false

  - command: search
    description: search folk tales
    patterns: [array of patterns]
    name: tags
    value: folk-tale
    regex: false

  - command: search
    description: search myths
    patterns: [array of patterns]
    name: tags
    value: myth.*
    regex: true

  - command: validate
    description: title required and less than 50 chars
    match: title ^.{0,50}$
    eq: status Published
    csv: validation_report.csv
  
  - command: update
    description: Title case
    name: title
    case: Title case

  - command: update
    decription: remove draft
    name: tags
    remove: "^test.*" 
    regex: true

```

Update or expose correcting library function to support the above changes in CLI.

Save all dependencies in a requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README file with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI
Create a SPECS.md file with specification and sample configurations of the specs file

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary


# Version 0.6.0 - Execute commands from specs files

Add a new command "execute [specs file]" to execute all commands inside the specs file.

Each command shall execute sequentially, with a print out of the command text e.g. `------------\n[command text]\n------------\n` before the execution.

By default, confirm with user if he/she want to execute the command: `Proceed with the above command? Answer yes or no`.

Add "--yes" option wto skip all confirmations.

When all command completed, print out a simple stats with the following info:
- Number of commands executed
- Total elapse time
- Total execution time (elapse time excluding waiting for user confirmation)
- Average execution time per command
- Number of execution per command types e.g. `read: 0, validate: 1, update: 3`

Update or expose correcting library function to support the above changes in CLI.

Save all dependencies in a requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README file with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary


# Version 0.8.0 - bug fixes and small enhancements

**New validate rule: --not-empty [front matter]**

Can appear multiple times. If specify, require the front matter to be of type array and has at least 1 value.

**New validate rule: --list-size [front matter] [min] [max]**

Can appear multiple times. If specify, require the front matter to be of type array and has values of count between min and max inclusively.


**Bug: Update command's `--deduplication true` is a valid update operation** 

Example: fmu update .\content\jokes\**\*.md --name categories --deduplication true
Expecation: deduplicate all values of front matter "categories"                         
Actual: "Error: No update operations specified"


**Bug: Incorrect capitalization of contraction form**

- Example: "can't": expect "Can't", actual "Can'T"
- Example: "aren't": expect "Aren't", actual "Aren'T"

**Bug: Arguments to an operation were combined when saved to specs file**

Example: `update --name categories --replace "dad-jokes" "dad jokes"`

Expectation:

```
commands:
- command: update
  name: categories
  replace:
  - dad-jokes
  - dad jokes
```

Actual:

```
commands:
- command: update
  name: categories
  replace:
  - dad-jokes dad jokes
```

Update or expose correcting library function to support the above changes in CLI.

Save all dependencies in a requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README file with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary



# Version 0.9.0 - Export content and matters to file 

Enhance the "read" command with the following features:

**Additional `--output` option: `template`**
- Updated syntax: "--output [frontmatter|content|both|template]": default to "both"
- When the value is "template", require a `--template` option (specification below)

**New `--espcape "[true|false]"` option**

Default to `false`. The frontmatters and content to be output are left unchanged as they were extracted from the input file

When `true`, escape the following special characters before output them:
- Newline `\n`
- Carriage return `\r`
- Tab `\t`
- Single quote `'`
- Double quote `"`


**New `--template [spec string]` option**

In conjunction of the `--output template` option, the CLI will output each file in the format specified in the `spec string`. The specification support the following placeholder
- $filename
- $filepath
- $content
- $frontmatter.name: a single value or an array
- $frontmatter.name[number] if `$frontmatter.name` is an array

Example:

```
{ \"title\": \"$frontmatter.title\", \"content\": \"$content\", \"path\": \"$filepath\" }

```



Update or expose correcting library function to support the above changes in CLI.

Save all dependencies in a requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README file with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary


# Future versions -- do not execute unless explicitly prompt


- analyze and summarize
- trim space, blank line
- expansive vs collapse e.g array: [value1, value2] vs arrays: - value1, - value2, "string" vs string
-- dry-run


 