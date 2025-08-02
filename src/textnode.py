from enum import Enum
from htmlnode import LeafNode, HTMLNode

class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"

class TextNode:
    def __init__(self, text: str, text_type: TextType, url: str = None):
        """Represents the various types of inline text that can exist in HTML and Markdown."""
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, other):
        if not isinstance(other, TextNode):
            return False
        return (self.text == other.text) and (self.text_type == other.text_type) and (self.url == other.url)
    
    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"
    
def text_node_to_html_node(text_node: "TextNode") -> "HTMLNode":
    """Handles each type of the `TextType` enum. If it gets a `TextNode` that is none of those types, it should `raise` an excaption. Otherwise, it should return a new `LeafNode` object.
    - `TextType.TEXT`: Returns a `LeafNode` with no tag, just a raw text value.
    - `TextType.BOLD`: Returns a `LeafNode` with a "b" tag and the text.
    - `TextType.ITALIC`: Returns a `LeafNode` with an "i" tag and the text.
    - `TextType.CODE`: Returns a `LeafNode` with a "code" tag and the text.
    - `TextType.LINK`: Returns a `LeafNode` with an "a" tag, the anchor text, and an "href" prop.
    - `TextType.IMAGE`: Returns a `LeafNode` with an "img" tag, an empty string value, and "src" (image URL) and "alt" (alt text) props.
    """
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode(tag=None, value=text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode("img", "", {
            "src": text_node.url,
            "alt": text_node.text,
        })
        case _:
            raise ValueError("invalid TextType")