from textnode import TextNode, TextType
from exceptions import InvalidMarkdownError
from markdown_extract import extract_markdown_images, extract_markdown_links

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

def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    
    return nodes

def markdown_to_blocks(markdown: str) -> list[str]:
    blocks = []

    for block in markdown.split("\n\n"):
        block = block.strip()
        if block != "":
            blocks.append(block.strip())
    
    return blocks