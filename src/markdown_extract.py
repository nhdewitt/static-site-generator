import re

from exceptions import InvalidHTMLError

def extract_link_definitions(markdown: str) -> dict[str, tuple[str, str]]:
    """
    Extract link reference definitions from markdown.
    Returns a dictionary mapping reference IDs to (url, title) tuples.

    Example:
    [ref]: https://example.com "Title"
    Returns: {"ref": ("https://example.com", "Title")}
    """
    # Pattern matches: [id]: url "optional title" or [id]: url
    # Explicitly exclude footnotes which start with [^
    pattern = re.compile(r'^\[(?!\^)([^\]]+)\]:\s+(\S+)(?:\s+"([^"]*)")?', re.MULTILINE)

    definitions = {}
    for match in pattern.finditer(markdown):
        ref_id = match.group(1).lower()  # Reference IDs are case-insensitive
        url = match.group(2)
        title = match.group(3) if match.group(3) else ""
        definitions[ref_id] = (url, title)

    return definitions

def remove_link_definitions(markdown: str) -> str:
    """Remove link reference definitions from markdown text"""
    # Pattern matches: [id]: url "optional title" or [id]: url
    # Explicitly exclude footnotes which start with [^
    pattern = re.compile(r'^\[(?!\^)([^\]]+)\]:\s+\S+(?:\s+"[^"]*")?\s*$', re.MULTILINE)
    return pattern.sub('', markdown).strip()

def extract_footnote_definitions(markdown: str) -> dict[str, str]:
    """
    Extract footnote definitions from markdown.
    Returns a dictionary mapping footnote IDs to content.

    Example:
    [^1]: This is a footnote.
    Returns: {"1": "This is a footnote."}
    """
    # Pattern matches: [^id]: content (content can span multiple lines if indented)
    pattern = re.compile(r'^\[\^([^\]]+)\]:\s+(.+)$', re.MULTILINE)

    definitions = {}
    for match in pattern.finditer(markdown):
        fn_id = match.group(1)
        content = match.group(2).strip()
        definitions[fn_id] = content

    return definitions

def remove_footnote_definitions(markdown: str) -> str:
    """Remove footnote definitions from markdown text"""
    # Pattern matches: [^id]: content
    pattern = re.compile(r'^\[\^([^\]]+)\]:\s+.+$', re.MULTILINE)
    return pattern.sub('', markdown).strip()

def extract_markdown_images(text: str) -> list[tuple]:
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text: str) -> list[tuple]:
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_title(markdown: str) -> str:
    """Pulls the h1 header (`# `) from the markdown file and returns it - raises an exception if no h1 header is present."""
    for line in markdown.splitlines():
        if line.startswith("# "):
            return line.replace("# ", "").strip()
    raise InvalidHTMLError("No h1 header present")
