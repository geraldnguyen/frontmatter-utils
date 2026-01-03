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


# Version 0.10.0 - Export content and matters to file: --file [file path] option

Enhance the "read" command with the following option:

**New `--file [file path]` option**

When specify, save the output of the command to a file at `[file path]` location instead of console.

Different command in a specs file may have different output destination e.g. console, file1, file2... The `execute` command must handle each command's output independently.


Update or expose correcting library function to support the above changes in CLI.

Save all dependencies in a requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README file with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary



# Version 0.11.0 - Reorganize project documentation

Revise the project documentation: Ensure informationa and examples about the commands and supported options (both global and command-specific) are captured and updated to the current source code

- README.md:
  + Retain the Features, Installation, Getting started, Changelog, and Mics sections
  + Spin-off the CLI command references and Library API references to their own .md files
- SPECS.md: ensure informationa and examples about the commands and supported options (both global and command-specific) are captured and updated to the current source code


Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary

# Version 0.12.0 - introduce feature: update command's --compute option

Enhance the "update" command with a new "--compute [formula]" option:

**Only for the "--compute" option**: 
- if the front matter does not exist, create the front matter and assign it the value obtained from executing the "--compute" option. If the front matter exist, replace its current value by the new value.
- If the front matter is a list, add the new value to the end of the list

`[formula]` can be:
- A literal value e.g. `1` or `2nd` or `just any thing`
- A placeholder reference (see below)
- A function call e.g. `=function_name(parameter1, parameter2, ...)`. Each parameter can be either a literal value or a placeholder reference

The specification support the same placeholder reference as with the Read command's template output specification
- $filename
- $filepath
- $content
- $frontmatter.name: a single value or an array
- $frontmatter.name[number] if `$frontmatter.name` is an array

The following function are supported:
- `now()`: return current date time e.g. `2025-10-20T00:30:00Z`
- `list()`: return an empty list
- `hash(string, hash_length)`: create a fixed-length `hash_length` random alphanumeric hash of the `string` parameter.
- `concat(string, string, string, ...)`: concatenate 2 or more string parameters

## Example 1: update a front matter's value

Assume we have the following front matter:

```
title: a book title
edition: 1
last_update: 2024-01-31T00:30:00Z
url: /post/original/a-book-title
aliases:
- /old-alias
- /newer-alias
```

- `update index.md --name edition --compute 2`: formula evaluated to a literal value `2` --> update the front matter "edition" to `edition: 2`
- `update index.md --name edition --compute 2nd`: formula evaluated to a literal value `2nd` --> update the front matter "edition" to `edition: 2nd`
- `update index.md --name last_update --compute "=now()"`: formula evaluated to the `now()` function  --> update the front matter "last_update" to `last_update: 2025-10-20T00:30:00Z`
- `update index.md --name aliases --compute "/newest-alias"`: formula evaluated to a literal value `/newest-alias`. Because `aliases` front matter's value is a list, the literal is added to the end of the list

```
aliases:
- /old-alias
- /newer-alias
- /newest-alias
```

## Example 2: Create a front matter if it does not exists

```
title: a book title
```

- `update index.md --name edition --compute =1`: create a new front matter `edition: 1`
- `update index.md --name edition --compute 2nd`: formula evaluated to a literal value `2nd` --> create a new front matter `edition: 2nd`
- `update index.md --name last_update --compute "=now()"`: formula evaluated to the `now()` function  --> create a new front matter  `last_update: 2025-10-20T00:30:00Z`
- `update index.md --name aliases --compute "=list()"`: formula evaluated to the `list()` function  --> create a new front matter  `aliases: []`
- `update index.md --name content_id --compute "=hash($frontmatter.url, 10)"`: formula evaluated to the `hash` function taking in the value of `url` front matter and a length of 10. Assume the hash function return `ad2121343c` value, the `content_id` front matter is updated to: `content_id: ad2121343c`

## Example 3: combining multiple `--compute` to calculate an alias

We start with the following front matter

```
title: a book title
```

**Step 1**: create a empty `aliases` front matter: `update index.md --name aliases --compute "=list()"`

```
title: a book title
aliases: []
content_id: ad2121343c
```

**Step 2**: create a `content_id` front matter derived from the `url` front matter: `update index.md --name content_id --compute "=hash($frontmatter.url, 10)"`

```
title: a book title
aliases: []
content_id: ad2121343c
```

**Step 3**: Add an actual shorten alias to the `aliases` front matter: `update index.md --name aliases --compute "=concat(/post/, $frontmatter.content_id)`. The `concat` function concatenate the literal `/post/` with the value of `content_id` and return the string `/post/ad2121343c`

```
title: a book title
aliases: [ '/post/ad2121343c']
content_id: ad2121343c
```


## General requirements

Update or expose correcting library functions to support the above changes in CLI.

Save all dependencies in the requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README.md, SPECS.md, CLI.md and API.md files with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI. Capture the changelog in the README.md too.

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary




# Version 0.13.0 - Add `slice` function to command's --compute option

Enhance the "update" command's "--compute [formula]" option with the following functions:

- `slice(list, start)`: Slice from the `start` index till the end
- `slice(list, start, stop)`: Slice from the `start` index till the `stop`
- `slice(list, start, stop, step)`: Slice from the `start` index till the `stop` interval by `step`

The `slice` function support negative `start`, `stop` and `step`. 

The `slice` function should behave similar to how they are in Python

**Example**:

Given the below front matter

```
aliases: 
- /old-alias
- /newest-alias
```


`update index.md --name aliases --compute "=slice($frontmatter.aliases, -1)"`: formula evaluated to the `slice(list, start=-1)` function taking in a list value from `aliases` front matter and one `start` parameter with -1 value. This function return a new list containing only the last element from the input list --> update the front matter "aliases" to: 

```
aliases: 
- /newest-alias
```

## General requirements

Update or expose correcting library functions to support the above changes in CLI.

Save all dependencies in the requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README.md, SPECS.md, CLI.md and API.md files with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI. Capture the changelog in the README.md too.

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary



# Version 0.14.0 - `validate` command returns non-zero exit code if validation fails

Enhance the `validate` command to return non-zero exit code if any validation fails

This applies even when the result is written into a CSV file using `--csv` option

## General requirements

Update or expose correcting library functions to support the above changes in CLI.

Save all dependencies in the requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README.md, SPECS.md, CLI.md and API.md files with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI. Capture the changelog in the README.md too.

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary

# Version 0.15.0 - Modify the `execute` command when executing commands from a specs file 

If it executed **any** command (not necessarily `validate`) and the exit code is non-zero, return the same non-zero exit code

If it executed **any** command and the exit code is zero, proceed to the next command, or stop if that is already the last command in the specs file.

## General requirements

Update or expose correcting library functions to support the above changes in CLI.

Save all dependencies in the requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README.md, SPECS.md, CLI.md and API.md files with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI. Capture the changelog in the README.md too.

Update the setup.py file and pyproject.toml with correct version number and other relevant information if necessary


# Version 0.16.0 - Bugfix

Investigate why the `fmu validate <path> --not-empty themes` failed to detect the syntax error in the below front matter sections. Specifically, the "themes" front matter had a preceeding space that make the whole section invalid.

Once you have identified the root cause and mechanism of the bug, proceed with the fix.

While preparing the fix, remember to meet all instructions specified in the `# General requiremts` section below

```
---
title: The Trial by Fire of Neang Seda
date: 2025-01-19T16:00:00Z
draft: false
featured: false
author: Traditional Khmer
source: 'Reamker: Phleung Neang Seda'
reading_time: 9
genres:
- Epic
- Spiritual
origins: [Cambodia]
 themes:
 - Perseverance
age_groups: [Children, Young Adults, Adults]
reading_times: [Medium Read]
tags:
- reamker
- trial
- fire
- purity
- divine-test
- drama
- divine justice
- faith
- truth revealed
description: Princess Neang Seda faces the ultimate test of fire to prove her 
  purity and innocence after her rescue from Ravana's captivity.
url: /stories/cambodia/epic/the-trial-by-fire-of-neang-seda/
images: [illustration.webp]
original_title: 'Reamker: Phleung Neang Seda'
---

Sample content


```


# Version 0.17.0 - Preserving frontmatter order

Update the implementation of the "update" command, so that when it dumps frontmatter back to the file, it should preserve the order of the frontmatters as they were originally loaded.

While `sort_keys=False` can help with this requirement, you are free to explore other approach if they are superior. Add your consideration to the PR description if that is the case.

While preparing the fix, remember to meet all instructions specified in the `# General requiremts` section below


# Version 0.18.0 - New compute function: coalesce(value, values, ....) 

Update the "update" command to support a new function: `coalesce(value, values, ....)`
- It supports variable number of parameters
- and return the first parameter that is not nil, not empty, not blank


While implement the requirements, remember to meet all instructions specified in the `# General requiremts` section below

# Version 0.19.0 - Bugfix

- Argument to the "update" command's `--compute` was not captured in the spec file when used in conjunction with the `--save-specs` option
- The version 0.18.0 was not reflected when enter `fmu version`. Instead 0.17.0 was returned.

While implement the requirements, remember to meet all instructions specified in the `# General requiremts` section below

# Version 0.20.0 - Minor update to `--remove VALUE` option in `update` command

Make "VALUE" optional in `--remove VALUE` option of the `update` command.

If "VALUE" is provided, perform the action as usual.

If "VALUE" is not provided, remove the selected front matter if it exists regardless of its value. If it is an list, remove the whole list and the front matter. If it does not exist, skip the file, do not printout any warning.


While implement the requirements, remember to meet all instructions specified in the `# General requiremts` section below


# Version 0.21.0 - Implement a new `--individual` option for the `read` command

If specified: for each file `F` matched by the 'read' command's pattern, the `--file FILE` option apply relatively to the file `F`'s folder.

Illustration:
- Given a content root folder with 2 files: `<content root>/folder1/file1.md` and `content root/folder2/subfolder/file2.md`
- When executing `<content root>$ fmu read *.md --file output.txt` **without** the `--individual` option, the command create a single `<content root>/output.txt` with information extracted from the 2 `.md` files
- When executing `<content root>$ fmu read *.md --file output.txt --individual` **with** the `--individual` option, the command create 2 output files at:
  + `<content root>/folder1/output.txt` with info extracted from `<content root>/folder1/file1.md` 
  + `content root/folder2/subfolder/outut.txt` with info extracted from `content root/folder2/subfolder/file2.md`

While implement the requirements, remember to meet all instructions specified in the `# General requiremts`


# Version 0.22.0 - Provide official support for JSON and YAML output in `read` command

**Add `--output json` and `--output yaml` options**

Existing: `--output [frontmatter|content|both|template]`

To-be: `--output [frontmatter|content|both|template|json|yaml]`

**Add `--map [key] [value] option`**

Build an internal map (or dictionary) of `key` to `value`. The value can be any literal (e.g. string, number, boolean...), or any template placeholder (e.g. `$filepath`, `$frontmatter.fieldname`... - all current or future template placeholders must be supported), or any built-in function (e.g. `now()`, `list()`... - - all current or future template placeholders must be supported)

Can be specified multiple times

When output to file or console, if the `--output [json|yaml]` was specified, serialize the map to json or yaml format.

**Add `--pretty` option**

When output to file or console, if the `--output [json|yaml]` was specified, pretify the json/yaml output

**Add `--compact` option**

When output to file or console, if the `--output [json|yaml]` was specified, minify the json/yaml output

**General requirements**

While implement the requirements, remember to meet all instructions specified in the `# General requiremts`


## Version 0.23.0 - Additional built-in variables and functions

Implement the following built-in variables and functions, available for use in **all** commands inlcuding `read` and `update` commands

- `$folderpath`: full path to folder
- `$foldername`: folder name
- `=basename(file path)`: function, return the base name (without extension) of the file
- `=ltrim(str)`, `=rtrim(str)`, and `=trim(str)`: functions, trim the left, right, and both left and right of the string
- `=truncate(string, max_length)`: function, truncate the string up to the max_length
- `=wtruncate(string, max_length, suffix)`: function, truncate the string to the word boundary, append the `suffix` afterward. Example `=wtruncate('hello world', 10, '...')` will return `'hello...'`. Because the whole string is longer than 10 characters, break by word boundary would result in the string `'hello'`, then append suffx `...`.

While implement the requirements, remember to meet all instructions specified in the `# General requiremts` section


# General requirements

- For every new command, new option introduced or modified or removed, ensure the specs file is updated to support and reflect the changes. For example, the specs must support the new `--compute <value>` option of "update" command, the new validation rules of the "validate" commands etc...`

Update or expose correcting library functions to support the above changes in CLI.

Save all dependencies in the requirements.txt file

Create or update extensive unit tests for both the library mode and CLI modes. 

Update README.md, SPECS.md, CLI.md and API.md files with comprehensive instruction on getting started and how to use the new enhancement or capability of the library and CLI. Capture the changelog in the README.md too.

Update the __init__.py, setup.py file and pyproject.toml with correct version number and other relevant information to reflec the new version and just implemented changes



# Future versions -- do not execute unless explicitly prompt


- analyze and summarize
- trim space, blank line
- expansive vs collapse e.g array: [value1, value2] vs arrays: - value1, - value2, "string" vs string
-- dry-run


 
