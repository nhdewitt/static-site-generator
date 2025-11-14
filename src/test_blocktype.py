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

    def test_unordered_list_asterisk(self):
        block = "* item one\n* item two\n* item three"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.UNORDERED_LIST
        )

    def test_unordered_list_plus(self):
        block = "+ item one\n+ item two\n+ item three"
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

    def test_horizontal_rule_dashes(self):
        block = "---"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.HORIZONTAL_RULE
        )

    def test_horizontal_rule_asterisks(self):
        block = "***"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.HORIZONTAL_RULE
        )

    def test_horizontal_rule_underscores(self):
        block = "___"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.HORIZONTAL_RULE
        )

    def test_horizontal_rule_with_spaces(self):
        block = "- - -"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.HORIZONTAL_RULE
        )

    def test_horizontal_rule_many_chars(self):
        block = "-----"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.HORIZONTAL_RULE
        )

    def test_task_list_unchecked(self):
        block = "- [ ] Task one\n- [ ] Task two"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.TASK_LIST
        )

    def test_task_list_checked(self):
        block = "- [x] Completed task"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.TASK_LIST
        )

    def test_task_list_mixed(self):
        block = "- [ ] Todo\n- [x] Done\n- [ ] Another todo"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.TASK_LIST
        )

    def test_task_list_uppercase_x(self):
        block = "- [X] Completed with uppercase"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.TASK_LIST
        )

    def test_table_basic(self):
        block = "| Header 1 | Header 2 |\n|----------|----------|\n| Cell 1   | Cell 2   |"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.TABLE
        )

    def test_table_with_alignment(self):
        block = "| Left | Center | Right |\n|:-----|:------:|------:|\n| L    | C      | R     |"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.TABLE
        )

    def test_table_multiple_rows(self):
        block = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n| 5 | 6 |"
        self.assertEqual(
            block_to_block_type(block),
            BlockType.TABLE
        )

if __name__ == "__main__":
    unittest.main()