import unittest
from blocktype import BlockType, block_to_block_type
from htmlnode import HTMLNode, LeafNode
from markdown_split import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image, split_nodes_link, text_to_textnodes, markdown_to_blocks
from textnode import TextNode, TextType
from exceptions import InvalidMarkdownError
from markdown_to_html_node import markdown_to_html_node

class TestSplitNodes(unittest.TestCase):
    def test_no_delimiters(self):
        node = TextNode("This is plain text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("This is plain text", TextType.TEXT)])

    def test_bold_delimiter(self):
        node = TextNode("This is **bold** text", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes,
                         [
                             TextNode("This is ", TextType.TEXT),
                             TextNode("bold", TextType.BOLD),
                             TextNode(" text", TextType.TEXT),
                         ])
        
    def test_input_node_not_text(self):
        node = TextNode("bold", TextType.BOLD)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        self.assertEqual(new_nodes, [TextNode("bold", TextType.BOLD)])

    def test_multiple_code_blocks(self):
        node = TextNode("This is text `with` multiple `code blocks` present", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(new_nodes,
                         [
                             TextNode("This is text ", TextType.TEXT),
                             TextNode("with", TextType.CODE),
                             TextNode(" multiple ", TextType.TEXT),
                             TextNode("code blocks", TextType.CODE),
                             TextNode(" present", TextType.TEXT),
                         ])
        
    def test_mismatched_delimiters(self):
        node = TextNode("This is _invalid markdown", TextType.TEXT)
        with self.assertRaises(InvalidMarkdownError):
            new_nodes = split_nodes_delimiter([node], "_", TextType.ITALIC)

    def test_delim_bold_and_italic(self):
        node = TextNode("**bold** and _italic_", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "**", TextType.BOLD)
        new_nodes = split_nodes_delimiter(new_nodes, "_", TextType.ITALIC)
        self.assertListEqual(
            [
                TextNode("bold", TextType.BOLD),
                TextNode(" and ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
            ],
            new_nodes,
        ) 

class TestSplitNodesImage(unittest.TestCase):
    def test_plaintext(self):
        node = TextNode("just some plain text", TextType.TEXT)
        images = split_nodes_image([node])
        self.assertEqual(images, [TextNode("just some plain text", TextType.TEXT)])

    def test_single_image_in_middle(self):
        node = TextNode("foo ![alt](link) bar", TextType.TEXT)
        images = split_nodes_image([node])
        self.assertEqual(images, [
            TextNode("foo ", TextType.TEXT),
            TextNode("alt", TextType.IMAGE, "link"),
            TextNode(" bar", TextType.TEXT),
        ])

    def test_image_at_beginning(self):
        node = TextNode("![start](L)", TextType.TEXT)
        images = split_nodes_image([node])
        expected = TextNode("start", TextType.IMAGE, "L")       
        self.assertEqual(images, [expected])

    def test_image_at_end(self):
        node = TextNode("end ![E](u)", TextType.TEXT)
        images = split_nodes_image([node])
        expected = [
            TextNode("end ", TextType.TEXT),
            TextNode("E", TextType.IMAGE, "u"),
        ]
        self.assertEqual(images, expected)

    def test_multiple_images(self):
        node = TextNode("one![a](1)two ![b](2) three", TextType.TEXT)
        images = split_nodes_image([node])
        expected = [
            TextNode("one", TextType.TEXT),
            TextNode("a", TextType.IMAGE, "1"),
            TextNode("two ", TextType.TEXT),
            TextNode("b", TextType.IMAGE, "2"),
            TextNode(" three", TextType.TEXT),
        ]
        self.assertEqual(images, expected)

    def test_only_images_converted(self):
        node = TextNode("see [link](url) and image ![i](x)", TextType.TEXT)
        images = split_nodes_image([node])
        expected = [
            TextNode("see [link](url) and image ", TextType.TEXT),
            TextNode("i", TextType.IMAGE, "x"),
        ]
        self.assertEqual(images, expected)

class TestSplitNodesLink(unittest.TestCase):
    def test_plaintext(self):
        node = TextNode("just some plain text", TextType.TEXT)
        links = split_nodes_link([node])
        expected = [TextNode("just some plain text", TextType.TEXT)]
        self.assertEqual(links, expected)

    def test_single_link_in_middle(self):
        node = TextNode("foo [bar](baz) qux", TextType.TEXT)
        links = split_nodes_link([node])
        expected = [
            TextNode("foo ", TextType.TEXT),
            TextNode("bar", TextType.LINK, "baz"),
            TextNode(" qux", TextType.TEXT),
        ]
        self.assertEqual(links, expected)

    def test_link_at_start(self):
        node = TextNode("[start](L)", TextType.TEXT)
        links = split_nodes_link([node])
        expected = [TextNode("start", TextType.LINK, "L")]
        self.assertEqual(links, expected)

    def test_link_at_end(self):
        node = TextNode("end [E](U)", TextType.TEXT)
        links = split_nodes_link([node])
        expected = [
            TextNode("end ", TextType.TEXT),
            TextNode("E", TextType.LINK, "U"),
        ]
        self.assertEqual(links, expected)

    def test_multiple_links(self):
        node = TextNode("see [a](1) and [b](2) done", TextType.TEXT)
        links = split_nodes_link([node])
        expected = [
            TextNode("see ", TextType.TEXT),
            TextNode("a", TextType.LINK, "1"),
            TextNode(" and ", TextType.TEXT),
            TextNode("b", TextType.LINK, "2"),
            TextNode(" done", TextType.TEXT),
        ]
        self.assertEqual(links, expected)

    def test_image_with_link(self):
        node = TextNode("![i](I) then [l](L) here", TextType.TEXT)
        links = split_nodes_link([node])
        expected = [
            TextNode("![i](I) then ", TextType.TEXT),
            TextNode("l", TextType.LINK, "L"),
            TextNode(" here", TextType.TEXT),
        ]
        self.assertEqual(links, expected)

class TestTextToTextNodes(unittest.TestCase):
    def test_all(self):
        self.maxDiff = None
        text = "This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),            
        ]
        self.assertEqual(nodes, expected)

    def test_plain_text(self):
        text = "Just plain text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode(text, TextType.TEXT, None)
        ]
        self.assertEqual(nodes, expected)

    def test_bold_text(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.TEXT, None),
            TextNode("bold", TextType.BOLD, None),
            TextNode(" text", TextType.TEXT, None),
        ]
        self.assertEqual(nodes, expected)

    def test_multiple_bold(self):
        text = "**first** and **second**"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("first", TextType.BOLD),
            TextNode(" and ", TextType.TEXT),
            TextNode("second", TextType.BOLD),
        ]
        self.assertEqual(nodes, expected)

    def test_italic_text(self):
        text = "Make this _italic_ please"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Make this ", TextType.TEXT, None),
            TextNode("italic", TextType.ITALIC, None),
            TextNode(" please", TextType.TEXT, None),
        ]
        self.assertEqual(nodes, expected)

    def test_code_text(self):
        text = "Use `code` here"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Use ", TextType.TEXT, None),
            TextNode("code", TextType.CODE, None),
            TextNode(" here", TextType.TEXT, None),
        ]
        self.assertEqual(nodes, expected)

    def test_image_syntax(self):
        text = "Look at this image: ![alt text](http://example.com/img.png)!"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Look at this image: ", TextType.TEXT, None),
            TextNode("alt text", TextType.IMAGE, "http://example.com/img.png"),
            TextNode("!", TextType.TEXT, None),
        ]
        self.assertEqual(nodes, expected)

    def test_link_syntax(self):
        text = "Visit [Google](https://google.com) now"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Visit ", TextType.TEXT, None),
            TextNode("Google", TextType.LINK, "https://google.com"),
            TextNode(" now", TextType.TEXT, None),
        ]
        self.assertEqual(nodes, expected)

    def test_combined_formatting(self):
        text = "Start **bold** middle _italic_ end `code`"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Start ", TextType.TEXT),
            TextNode("bold", TextType.BOLD),
            TextNode(" middle ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" end ", TextType.TEXT),
            TextNode("code", TextType.CODE),
        ]
        self.assertEqual(nodes, expected)

    def test_invalid_markdown_odd_bold(self):
        text = "Invalid **bold* here"
        with self.assertRaises(InvalidMarkdownError):
            text_to_textnodes(text)

    def test_invalid_markdown_odd_italic(self):
        text = "Invalid _italic here"
        with self.assertRaises(InvalidMarkdownError):
            text_to_textnodes(text)

class TestMarkdownToBlocks(unittest.TestCase):
    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_markdown_to_blocks_newlines(self):
        md = """
This is **bolded** paragraph




This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

class TestMarkdownToHTMLNode(unittest.TestCase):
    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
    ```
    This is text that _should_ remain
    the **same** even with inline stuff
    ```
    """

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

    def test_heading(self):
        md = "## Test Heading"
        root = markdown_to_html_node(md)
        # should produce a single <h2> child
        h2 = root.children[0]
        self.assertEqual(h2.tag, "h2")
        self.assertEqual(len(h2.children), 1)
        # heading text should be "Test Heading"
        text_child = h2.children[0]
        self.assertIsInstance(text_child, LeafNode)
        self.assertEqual(text_child.value.strip("# ").strip(), "Test Heading")

    def test_block_to_block_types(self):
        block = "# heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        block = "```\ncode\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
        block = "> quote\n> more quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
        block = "- list\n- items"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)
        block = "1. list\n2. items"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)
        block = "paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p></div>",
        )

    def test_paragraphs(self):
        md = """
This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_lists(self):
        md = """
- This is a list
- with items
- and _more_ items

1. This is an `ordered` list
2. with items
3. and more items

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><ul><li>This is a list</li><li>with items</li><li>and <i>more</i> items</li></ul><ol><li>This is an <code>ordered</code> list</li><li>with items</li><li>and more items</li></ol></div>",
        )

    def test_headings(self):
        md = """
# this is an h1

this is paragraph text

## this is an h2
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>this is an h1</h1><p>this is paragraph text</p><h2>this is an h2</h2></div>",
        )

    def test_blockquote(self):
        md = """
> This is a
> blockquote block

this is paragraph text

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><blockquote>This is a blockquote block</blockquote><p>this is paragraph text</p></div>",
        )

    def test_code(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

if __name__ == "__main__":
    unittest.main()