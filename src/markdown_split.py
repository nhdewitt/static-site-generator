from textnode import TextNode, TextType
from exceptions import InvalidMarkdownError
from markdown_extract import extract_markdown_images, extract_markdown_links
import re

# Escape character handling
ESCAPE_CHARS = ['\\', '*', '_', '~', '`', '[', ']', '(', ')', '!', '#', '-', '+', '.', '|']
LINE_BREAK_MARKER = chr(0xE0FF)  # Special marker for line breaks

def escape_markdown(text: str) -> str:
    """Replace escaped characters with placeholders before markdown processing"""
    # Use Unicode private use area characters as placeholders (U+E000 to U+F8FF)
    result = text
    for i, char in enumerate(ESCAPE_CHARS):
        # Match backslash followed by the special character
        escaped = f'\\{char}'
        # Use a unique Unicode character for each escaped character
        placeholder = chr(0xE000 + i)
        result = result.replace(escaped, placeholder)
    return result

def unescape_markdown(text: str) -> str:
    """Replace placeholders back with literal characters after markdown processing"""
    result = text
    for i, char in enumerate(ESCAPE_CHARS):
        placeholder = chr(0xE000 + i)
        result = result.replace(placeholder, char)
    return result

def split_nodes_delimiter(old_nodes: list["TextNode"], delimiter: str, text_type: "TextType") -> list[TextNode]:
    """Takes a list of old nodes, a delimiter and a text type. Returns a new list of nodes, where any "text" type nodes in the input list are (potentially) split into multiple nodes based on the syntax. For example, given the following input:
    ```
    node = TextNode("This is text with a `code block` word", TextType.TEXT)
    new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
    ```
    `new_nodes` becomes:
    ```
    [
        TextNode("This is text with a ", TextType.TEXT),
        TextNode("code block", TextType.CODE),
        TextNode(" word", TextType.TEXT),
    ]
    ```
    """
    node_list = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            node_list.append(node)
            continue
        if node.text.count(delimiter) % 2 != 0:
            raise InvalidMarkdownError("that's invalid Markdown syntax")
        split_nodes = node.text.split(delimiter)
        inner_nodes = []
        for i, split_node in enumerate(split_nodes):
            if split_node == "":
                continue
            if i % 2 == 0:
                inner_nodes.append(TextNode(split_node, TextType.TEXT))
            else:
                inner_nodes.append(TextNode(split_node, text_type))
        node_list.extend(inner_nodes)
    
    return node_list

def split_nodes_image(old_nodes: list["TextNode"]) -> list[TextNode]:
    node_list = []
    for node in old_nodes:
        text = node.text
        matches = extract_markdown_images(text)
        if len(matches) == 0:
            node_list.append(node)
        else:
            for image_alt, image_link in matches:
                inner_nodes = []
                sections = text.split(f"![{image_alt}]({image_link})", 1)
                if len(sections) != 2:
                    raise InvalidMarkdownError(f"image section not closed: {sections}")
                if sections[0] != "":
                    inner_nodes.append(TextNode(sections[0], TextType.TEXT))
                inner_nodes.append(TextNode(image_alt, TextType.IMAGE, image_link))
                text = sections[1]
                node_list.extend(inner_nodes)
            if text != "":
                node_list.append(TextNode(text, TextType.TEXT))
    return node_list

def split_nodes_link(old_nodes: list["TextNode"]) -> list[TextNode]:
    node_list = []
    for node in old_nodes:
        text = node.text
        matches = extract_markdown_links(text)
        if len(matches) == 0:
            node_list.append(node)
        else:
            for anchor_text, url in matches:
                inner_nodes = []
                sections = text.split(f"[{anchor_text}]({url})", 1)
                if len(sections) != 2:
                    raise InvalidMarkdownError(f"link section not closed: {sections}")
                if sections[0] != "":
                    inner_nodes.append(TextNode(sections[0], TextType.TEXT))
                inner_nodes.append(TextNode(anchor_text, TextType.LINK, url))
                text = sections[1]
                node_list.extend(inner_nodes)
            if text != "":
                node_list.append(TextNode(text, TextType.TEXT))
    return node_list

def split_nodes_line_break(old_nodes: list["TextNode"]) -> list[TextNode]:
    """Split nodes on line break markers"""
    node_list = []
    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            node_list.append(node)
            continue

        if LINE_BREAK_MARKER not in node.text:
            node_list.append(node)
            continue

        parts = node.text.split(LINE_BREAK_MARKER)
        for i, part in enumerate(parts):
            if part:
                node_list.append(TextNode(part, TextType.TEXT))
            # Add line break between parts (but not after the last part)
            if i < len(parts) - 1:
                node_list.append(TextNode("", TextType.LINE_BREAK))

    return node_list

def split_nodes_autolink(old_nodes: list["TextNode"]) -> list[TextNode]:
    """Convert bare URLs to links"""
    # Pattern to match http:// or https:// URLs
    url_pattern = re.compile(r'(https?://[^\s<>]+)')

    node_list = []
    for node in old_nodes:
        # Only process TEXT nodes (don't auto-link inside links, code, etc.)
        if node.text_type != TextType.TEXT:
            node_list.append(node)
            continue

        text = node.text
        matches = url_pattern.findall(text)

        if not matches:
            node_list.append(node)
            continue

        # Split text by URLs and create link nodes
        for url in matches:
            parts = text.split(url, 1)
            if parts[0]:
                node_list.append(TextNode(parts[0], TextType.TEXT))
            node_list.append(TextNode(url, TextType.LINK, url))
            text = parts[1] if len(parts) > 1 else ""

        # Add any remaining text
        if text:
            node_list.append(TextNode(text, TextType.TEXT))

    return node_list

def text_to_textnodes(text: str) -> list[TextNode]:
    # Escape special characters first
    text = escape_markdown(text)

    nodes = [TextNode(text, TextType.TEXT)]

    nodes = split_nodes_line_break(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "~~", TextType.STRIKETHROUGH)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_autolink(nodes)  # Auto-link bare URLs after explicit links

    # Unescape characters in all nodes
    for node in nodes:
        node.text = unescape_markdown(node.text)
        if node.url:
            node.url = unescape_markdown(node.url)

    return nodes

def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = []

    for block in markdown.split("\n\n"):
        block = block.strip()
        if block != "":
            blocks.append(block.strip())
    
    return blocks