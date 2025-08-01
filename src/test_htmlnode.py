import unittest

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import TextNode

class TestHTMLNode(unittest.TestCase):
    def test_tag(self):
        node = HTMLNode(tag="a")
        self.assertEqual(
            "HTMLNode(a, None, children: None, None)", repr(node)
        )

    def test_repr(self):
        node = HTMLNode(tag="a", value="Google", props={
            "href": "https://www.google.com",
            "target": "_blank",
        })
        self.assertEqual(
            "HTMLNode(a, Google, children: None, {'href': 'https://www.google.com', 'target': '_blank'})", repr(node)
        )

    def test_props_to_html(self):
        node = HTMLNode(tag="a", value="Google", props={
            "href": "https://www.google.com",
            "target": "_blank",
        })
        self.assertEqual(
            ' href="https://www.google.com" target="_blank"', node.props_to_html()
        )

    def test_values(self):
        node = HTMLNode(
            "div",
            "I wish I could read",
        )
        self.assertEqual(
            node.tag,
            "div",
        )
        self.assertEqual(
            node.value,
            "I wish I could read",
        )
        self.assertEqual(
            node.children,
            None,
        )
        self.assertEqual(
            node.props,
            None,
        )

class TestLeafNode(unittest.TestCase):
    def test_leaf_to_html_p(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

    def test_a_href(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(node.to_html(), '<a href="https://www.google.com">Click me!</a>')

    def test_plaintext(self):
        node = LeafNode(None, "Click me!")
        self.assertEqual(node.to_html(), "Click me!")

    def test_no_value(self):
        node = LeafNode("a", None)
        self.assertRaises(ValueError, node.to_html)

class TestParentNode(unittest.TestCase):
    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )

    def test_to_html_many_children(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
        )

    def test_headings(self):
        node = ParentNode(
            "h2",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            node.to_html(),
            "<h2><b>Bold text</b>Normal text<i>italic text</i>Normal text</h2>",
        )

    def test_to_html_deeply_nested(self):
        # Deeply nested structure:
        # div
        #   section
        #     p "Paragraph 1"
        #     article
        #       h1 "Heading"
        #       span "Some span text"
        #   "Just some loose text after the section" (LeafNode with no tag)
        #   ul (with id="list")
        #     li "Item 1"
        #     li
        #       b "Bold Item"
        #       i "Italic Item"
        #     li "Item 3"

        grandchild_h1 = LeafNode("h1", "Heading")
        grandchild_span = LeafNode("span", "Some span text")
        child_article = ParentNode("article", [grandchild_h1, grandchild_span])
        child_p = LeafNode("p", "Paragraph 1")

        child_section = ParentNode("section", [child_p, child_article])

        loose_text_node = LeafNode(None, "Just some loose text after the section")

        list_item_bold = LeafNode("b", "Bold Item")
        list_item_italic = LeafNode("i", "Italic Item")
        list_item_2 = ParentNode("li", [list_item_bold, list_item_italic]) # li containing b and i
        list_item_1 = LeafNode("li", "Item 1")
        list_item_3 = LeafNode("li", "Item 3")
        
        child_ul = ParentNode("ul", [list_item_1, list_item_2, list_item_3], {"id": "my-list"})

        parent_div = ParentNode("div", [child_section, loose_text_node, child_ul])

        expected_html = (
            "<div>"
            "<section>"
            "<p>Paragraph 1</p>"
            "<article>"
            "<h1>Heading</h1>"
            "<span>Some span text</span>"
            "</article>"
            "</section>"
            "Just some loose text after the section"
            '<ul id="my-list">'
            "<li>Item 1</li>"
            "<li><b>Bold Item</b><i>Italic Item</i></li>"
            "<li>Item 3</li>"
            "</ul>"
            "</div>"
        )
        self.assertEqual(parent_div.to_html(), expected_html)

if __name__ == "__main__":
    unittest.main()