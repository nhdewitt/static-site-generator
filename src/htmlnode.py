from exceptions import InvalidHTMLError

class HTMLNode:
    """Represents a "node" in an HTML document tree (like a `<p>` tag and its contents, or an `<a>` tag and its contents). It can be block level or inline, and is designed to only output HTML.
    """
    def __init__(
            self, tag: str = None, value: str = None, children: list = None, props: dict = None
            ):
        """Initialize an HTMLNode with 4 data members:
        - tag: A string representing the HTML tag name (e.g. "p", "a", "h1", etc.)
        - value: A string representing the value of the HTML tag (e.g. the text inside a paragraph)
        - children: A list of HTMLNode objects representing the children of this node
        - props: A dictionary of key-value pairs representing the attributes of the HTML tag.
                 For example: a link might have {"href": "https://www.google.com"}
        
        Every data member is optional and defaults to None:
        - An HTMLNode without a tag will render as raw text
        - An HTMLNode without a value will be assumed to have children
        - An HTMLNode without children will be assumed to have a value
        - An HTMLNode without props won't have any attributes"""
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def to_html(self):
        """Child classes will override this method to render themselves as HTML."""
        # if self.tag is None:
        #     raise InvalidHTMLError("Class must have a tag")
        # if self.children:
        #     children = []
        #     for child in self.children:
        #         children.append(child.to_html())
        #     return f"<{self.tag}>{''.join(children)}</{self.tag}>"
        # else:
        #     if self.value is None:
        #         raise InvalidHTMLError("Class must have a value")
        #     return f"<{self.tag}>{self.value}</{self.tag}>"
        
        
    
    def props_to_html(self) -> str:
        """Returns a string that represents the HTML attributes of the node:
        For example, if `self.props` is:
        ```
        {
            "href": "https://www.google.com",
            "target": "_blank",
        }
        ```
        Then `self.props_to_html()` should return:
        ```
         href="https://www.google.com" target="_blank"
        ```
        Notice the leading space character before `href` and `target`. _This_ _is_ _important_.
        HTML attributes are always separated by spaces.
        """
        if not self.props:
            return ""
        atts = []
        for k, v in self.props.items():
            atts.append(f' {k}="{v}"')
        return "".join(atts)
    
    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, children: {self.children}, {self.props})"
    
class LeafNode(HTMLNode):
    """A type of `HTMLNode` that represents a single HTML tag _with_ _no_ _children_. For example, a simple `<p>` tag with some text inside of it:
    ```
    <p>This is a paragraph of text.</p>
    ```
    It's a leaf node because it's a leaf in the tree of HTML nodes. It's a node with no children. In the next example, ``p>` is _not_ a leaf node, but `<b>` is.
    ```
    <p>
        This is a paragraph. It can have a lot of text tbh.
        <b>This is bold text.</b>
        This is the last sentence.
    </p>
    ```
    """
    def __init__(
            self, tag: str, value: str, props: dict = None
    ):
        """Differs from the `HTMLNode` class because:
        - It should _not_ allow for any children
        - The `value` data member should be required (and `tag` even though the tag's value may be `None`), while `props` can remain optional."""
        super().__init__(tag=tag, value=value, props=props)

    def to_html(self) -> str:
        """Renders a leaf node as an HTML string (by returning a string).
        - If the leaf node has no `value`, it should raise a ValueError. All leaf nodes _must_ have a value.
        - If there is no `tag` (e.g. it's `None`), the `value` should be returned as raw text.
        - Otherwise, it should render an HTML tag. For example, these leaf nodes:

        ```
        LeafNode("p", "This is a paragraph of text.").to_html()
        "<p>This is a paragraph of text.</p>
        ```

        ```
        LeafNode("a", "Click me!", {"href": "https://www.google.com"}).to_html()
        "<a href="https://www.google.com">Click me!</a>"
        ```
        """
        if self.value is None:
            raise ValueError("LeafNode must have a value")
        if self.tag is None:
            return f"{self.value}"
        return f"<{self.tag}{self.props_to_html()}>{self.value}</{self.tag}>"
    
class ParentNode(HTMLNode):
    """Handles the nesting of HTML nodes inside of one another. Any HTML node that's not a "leaf" node (i.e. it _has_ children) is a "parent" node."""
    def __init__(
            self, tag: str, children: list, props: dict = None
    ):
        """Differs from `HTMLNode` in that:
        - The `tag` and `children` arguments _are_ _not_ _optional_
        - It doesn't take a `value` argument
        - `props` is optional
        - (It's the exact opposite of the `LeafNode` class)
        """
        super().__init__(tag=tag, children=children, props=props)

    def to_html(self) -> str:
        """
        - If the object doesn't have a `tag`, raise a ValueError
        - If children is a missing value, raise a ValueError
        - Otherwise, return a string representing the HTML tag of the node _and_ _its_ _children_. This is a recursive method (each recursion is called on a nested child node).

        For example, this node and its children:
        ```
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "Italic text"),
                LeafNode(None, "Normal text"),
            ],
        )

        node.to_html()
        ```
        Should convert to:
        ```
        <p><b>Bold text</b>Normal text<i>Italic text</i>Normal text</p>
        ```
        """
        if self.tag is None:
            raise ValueError("ParentNode must have a tag")
        if self.children is None:
            raise ValueError("ParentNode must have children")
        
        children_html = ""
        for child in self.children:
            children_html += child.to_html()

        return f"<{self.tag}{self.props_to_html()}>{children_html}</{self.tag}>"