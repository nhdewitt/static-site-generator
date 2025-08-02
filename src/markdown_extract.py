import re

from exceptions import InvalidHTMLError

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
