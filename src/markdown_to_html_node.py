from htmlnode import HTMLNode, ParentNode, LeafNode
from textnode import TextNode, TextType, text_node_to_html_node
from blocktype import BlockType, block_to_block_type
from markdown_split import markdown_to_blocks, text_to_textnodes, LINE_BREAK_MARKER
from markdown_extract import (extract_link_definitions, remove_link_definitions,
                               extract_footnote_definitions, remove_footnote_definitions)
import textwrap
import re

# Global storage for link reference definitions (set during markdown processing)
_link_definitions = {}
_footnote_definitions = {}

def markdown_to_html_node(markdown: str) -> ParentNode:
    global _link_definitions, _footnote_definitions

    # Extract and remove link reference definitions
    _link_definitions = extract_link_definitions(markdown)
    markdown = remove_link_definitions(markdown)

    # Extract and remove footnote definitions
    _footnote_definitions = extract_footnote_definitions(markdown)
    markdown = remove_footnote_definitions(markdown)

    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)

    # Add footnotes section if there are any
    if _footnote_definitions:
        footnotes_node = create_footnotes_section(_footnote_definitions)
        children.append(footnotes_node)

    # Clear definitions after processing
    _link_definitions = {}
    _footnote_definitions = {}

    return ParentNode("div", children, None)

def create_footnotes_section(footnotes: dict[str, str]) -> ParentNode:
    """Create a footnotes section at the end of the document"""
    footnote_items = []

    # Sort footnotes by ID
    for fn_id in sorted(footnotes.keys()):
        content = footnotes[fn_id]

        # Create proper HTML nodes for the footnote
        backref_link = LeafNode("a", fn_id, {"href": f"#fnref-{fn_id}"})
        separator = LeafNode(None, ": ")
        content_node = LeafNode(None, content)

        # Create list item with these children
        li_children = [backref_link, separator, content_node]
        footnote_items.append(ParentNode("li", li_children, {"id": f"fn-{fn_id}"}))

    footnotes_list = ParentNode("ol", footnote_items)
    hr = LeafNode("hr", "")
    heading = LeafNode("h2", "Footnotes")

    return ParentNode("div", [hr, heading, footnotes_list], {"class": "footnotes"})

def block_to_html_node(block: str) -> BlockType:
    block_type = block_to_block_type(block)
    match block_type:
        case BlockType.PARAGRAPH:
            return paragraph_to_html_node(block)
        case BlockType.HEADING:
            return heading_to_html_node(block)
        case BlockType.CODE:
            return code_to_html_node(block)
        case BlockType.ORDERED_LIST:
            return olist_to_html_node(block)
        case BlockType.UNORDERED_LIST:
            return ulist_to_html_node(block)
        case BlockType.QUOTE:
            return quote_to_html_node(block)
        case BlockType.HORIZONTAL_RULE:
            return horizontal_rule_to_html_node(block)
        case BlockType.TASK_LIST:
            return task_list_to_html_node(block)
        case BlockType.TABLE:
            return table_to_html_node(block)
        case _:
            raise ValueError("invalid BlockType:", block)
        
def text_to_children(text: str) -> list[HTMLNode]:
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children

def paragraph_to_html_node(block: str) -> ParentNode:
    lines = block.split("\n")
    # Detect hard line breaks (two spaces or backslash at end of line)
    processed_lines = []
    for i, line in enumerate(lines):
        # Check if this line (except the last one) ends with a line break marker
        if i < len(lines) - 1:  # Not the last line
            if line.endswith("  ") or line.endswith("\\"):
                # Remove the line break marker and add our special marker
                if line.endswith("\\"):
                    line = line[:-1]  # Remove backslash
                elif line.endswith("  "):
                    line = line.rstrip()  # Remove trailing spaces
                processed_lines.append(line + LINE_BREAK_MARKER)
            else:
                processed_lines.append(line)
        else:
            processed_lines.append(line)

    paragraph = " ".join(processed_lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)

def heading_to_html_node(block: str) -> ParentNode:
    level = block.count("#")
    if level + 1 >= len(block):
        raise ValueError("Invalid heading level:", level)
    text = block[level + 1:]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)

def code_to_html_node(block: str) -> ParentNode:
    if not block.startswith("```") or not block.endswith("```"):
        raise ValueError("Invalid code block:", block)

    # Remove opening ``` and ending ```
    content = block[3:-3]

    # Check if first line contains language identifier
    lines = content.split("\n", 1)
    first_line = lines[0].strip()

    language = None
    code_text = content

    # If first line is a valid language identifier (alphanumeric + dashes/underscores)
    if first_line and first_line.replace("-", "").replace("_", "").isalnum():
        language = first_line
        # Remove the language line from the code
        code_text = lines[1] if len(lines) > 1 else ""

    # Process the code text
    text = code_text.strip("\n")
    text = textwrap.dedent(text)
    if not text.endswith("\n"):
        text += "\n"

    raw_text = TextNode(text, TextType.TEXT)
    child = text_node_to_html_node(raw_text)

    # Add language class if specified (follows Prism.js/highlight.js convention)
    code_props = {"class": f"language-{language}"} if language else None
    code = ParentNode("code", [child], code_props)
    return ParentNode("pre", [code])

def olist_to_html_node(block: str) -> ParentNode:
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[3:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)

def ulist_to_html_node(block: str) -> ParentNode:
    items = block.split("\n")
    html_items = []
    for item in items:
        # Remove the list marker (-, *, or +) and the following space
        if item.startswith(("- ", "* ", "+ ")):
            text = item[2:]
        else:
            text = item
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)

def quote_to_html_node(block: str) -> ParentNode:
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block:", block)
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

def horizontal_rule_to_html_node(block: str) -> LeafNode:
    return LeafNode("hr", "")

def task_list_to_html_node(block: str) -> ParentNode:
    items = block.split("\n")
    html_items = []
    task_pattern = re.compile(r'^([-*+])\s+\[([ xX])\]\s+(.+)$')

    for item in items:
        match = task_pattern.match(item)
        if match:
            checkbox_state = match.group(2)
            text = match.group(3)

            # Create checkbox input element
            checked = checkbox_state.lower() == 'x'
            checkbox_props = {"type": "checkbox", "disabled": ""}
            if checked:
                checkbox_props["checked"] = ""

            checkbox = LeafNode("input", "", checkbox_props)

            # Create text nodes for the rest of the content
            text_children = text_to_children(text)

            # Combine checkbox and text
            li_children = [checkbox] + text_children
            html_items.append(ParentNode("li", li_children))

    return ParentNode("ul", html_items)

def table_to_html_node(block: str) -> ParentNode:
    lines = block.splitlines()
    if len(lines) < 2:
        raise ValueError("Table must have at least 2 lines")

    # Parse header row
    header_cells = [cell.strip() for cell in lines[0].split('|') if cell.strip()]

    # Parse separator row for alignment
    separator_cells = [cell.strip() for cell in lines[1].split('|') if cell.strip()]
    alignments = []
    for cell in separator_cells:
        if cell.startswith(':') and cell.endswith(':'):
            alignments.append('center')
        elif cell.endswith(':'):
            alignments.append('right')
        else:
            alignments.append('left')

    # Create table header
    thead_cells = []
    for i, header in enumerate(header_cells):
        align = alignments[i] if i < len(alignments) else 'left'
        props = {"style": f"text-align: {align}"} if align != 'left' else None
        children = text_to_children(header)
        thead_cells.append(ParentNode("th", children, props))

    thead_row = ParentNode("tr", thead_cells)
    thead = ParentNode("thead", [thead_row])

    # Create table body
    tbody_rows = []
    for line in lines[2:]:
        data_cells = [cell.strip() for cell in line.split('|') if cell.strip()]
        row_cells = []
        for i, cell in enumerate(data_cells):
            align = alignments[i] if i < len(alignments) else 'left'
            props = {"style": f"text-align: {align}"} if align != 'left' else None
            children = text_to_children(cell)
            row_cells.append(ParentNode("td", children, props))
        tbody_rows.append(ParentNode("tr", row_cells))

    tbody = ParentNode("tbody", tbody_rows)

    return ParentNode("table", [thead, tbody])