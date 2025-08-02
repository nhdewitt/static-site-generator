import unittest, re
from blocktype import BlockType, block_to_block_type

class TestBlockToBlockType(unittest.TestCase):
    def test_heading_levels_1_to_6(self):
        for level in range(1, 7):
            hashes = "#" * level
            block = f"{hashes} Heading {level}"
            with self.subTest(level=level):
                self.assertEqual(
                    block_to_block_type(block),
                    BlockType.HEADING,
                    f"Failed for heading level {level}"
                )
    
    def test_too_many_hashes_is_paragraph(self):
        block  = "####### Too many hashes"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.PARAGRAPH
        )

    def test_code_single_line(self):
        block = "```print('hello')```"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.CODE
        )

    def test_code_multiline(self):
        block = "```\ndef foo():\n    return 42\n```"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.CODE
        )

    def test_quote(self):
        block = "> Quote line one\n> Quote line two"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.QUOTE
        )

    def test_unordered_list(self):
        block = "- item one\n- item two\n- item three"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.UNORDERED_LIST
        )

    def test_ordered_list_multiline(self):
        block = "1. first\n2. second\n10. tenth"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.ORDERED_LIST
        )

    def test_ordered_list_single_line(self):
        block = "1. only item"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.ORDERED_LIST
        )

    def test_mixed_list_falls_back_to_paragraph(self):
        block = "1. one\n- two"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.PARAGRAPH
        )

    def test_paragraph_default(self):
        block = "Just a normal paragraph\nwith nothing special."
        self.assertEqual(
            block_to_block_type(block),
            BlockType.PARAGRAPH
        )

    def test_heading_precedence_over_ordered_list(self):
        block = "# 1. Not a list"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.HEADING
        )

if __name__ == "__main__":
    unittest.main()