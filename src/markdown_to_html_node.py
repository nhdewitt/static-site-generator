from htmlnode import HTMLNode, ParentNode
from textnode import TextNode, TextType, text_node_to_html_node
from blocktype import BlockType, block_to_block_type
from markdown_split import markdown_to_blocks, text_to_textnodes
import textwrap

def markdown_to_html_node(markdown: str) -> ParentNode:
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)

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
    paragraph = " ".join(lines)
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
    text = block.strip("```").strip("\n")
    text = textwrap.dedent(text)
    if not text.endswith("\n"):
        text += "\n"
    raw_text = TextNode(text, TextType.TEXT)
    child = text_node_to_html_node(raw_text)
    code = ParentNode("code", [child])
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
        text = item[2:]
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