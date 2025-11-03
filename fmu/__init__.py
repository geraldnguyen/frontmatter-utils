"""
fmu - Front Matter Utils

A Python library and CLI tool for parsing and searching front matter in files.
"""

__version__ = "0.17.0"
__author__ = "Gerald Nguyen The Huy"

from .core import parse_frontmatter, extract_content, parse_file
from .search import search_frontmatter
from .validation import validate_frontmatter, validate_and_output
from .update import update_frontmatter, update_and_output
from .specs import save_specs_file, execute_specs_file

__all__ = [
    "parse_frontmatter",
    "extract_content", 
    "parse_file",
    "search_frontmatter",
    "validate_frontmatter",
    "validate_and_output",
    "update_frontmatter",
    "update_and_output",
    "save_specs_file",
    "execute_specs_file",
    "__version__"
]