from textnode import TextNode, TextType
from exceptions import InvalidMarkdownError
import re

def split_nodes_delimiter(old_nodes: list["TextNode"], delimiter: str, text_type: "TextType") -> list[TextNode]:
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

def extract_markdown_images(text: str) -> list[tuple]:
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text: str) -> list[tuple]:
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes: list["TextNode"]) -> list[TextNode]:
    node_list = []
    for node in old_nodes:
        text = node.text
        matches = extract_markdown_images(text)
        for image_alt, image_link in matches:
            inner_nodes = []
            sections = text.split(f"![{image_alt}]({image_link})", 1)
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
