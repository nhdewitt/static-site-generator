import unittest
from markdown import split_nodes_delimiter, extract_markdown_images, extract_markdown_links, split_nodes_image
from textnode import TextNode, TextType
from exceptions import InvalidMarkdownError

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

class TestExtractMarkdownImages(unittest.TestCase):
    def test_extract_markdown_images(self):
        matches = extract_markdown_images(
            "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        )
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_multiple_images(self):
        matches = extract_markdown_images(
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        )
        self.assertListEqual([("rick roll", "https://i.imgur.com/aKaOqIh.gif"), ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg")], matches)

class TestExtractMarkdownLinks(unittest.TestCase):
    def test_extract_markdown_links(self):
        matches = extract_markdown_links(
            "This is a link [to google.com](https://www.google.com)"
        )
        self.assertListEqual([("to google.com", "https://www.google.com")], matches)

    def test_multiple_links(self):
        matches = extract_markdown_links(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        )
        self.assertListEqual([("to boot dev", "https://www.boot.dev"), ("to youtube", "https://www.youtube.com/@bootdotdev")], matches)

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

if __name__ == "__main__":
    unittest.main()