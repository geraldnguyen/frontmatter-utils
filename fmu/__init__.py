"""
fmu - Front Matter Utils

A Python library and CLI tool for parsing and searching front matter in files.
"""

__version__ = "0.1.0"
__author__ = "Gerald Nguyen The Huy"

from .core import parse_frontmatter, extract_content, parse_file
from .search import search_frontmatter

__all__ = [
    "parse_frontmatter",
    "extract_content", 
    "parse_file",
    "search_frontmatter",
    "__version__"
]