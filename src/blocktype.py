from enum import Enum
import re

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    HORIZONTAL_RULE = "horizontal_rule"
    TASK_LIST = "task_list"
    TABLE = "table"

HEADING_PREFIXES = [f"{'#' * i} " for i in range(6, 0, -1)]
ORDERED_PATTERN = re.compile(r'^(?P<index>\d+)\.\s+(?P<text>.+)$')
HORIZONTAL_RULE_PATTERN = re.compile(r'^(\*\s*\*\s*\*+|-\s*-\s*-+|_\s*_\s*_+)\s*$')
UNORDERED_LIST_PATTERN = re.compile(r'^[-*+]\s+')
TASK_LIST_PATTERN = re.compile(r'^[-*+]\s+\[([ xX])\]\s+')
TABLE_SEPARATOR_PATTERN = re.compile(r'^\|?(\s*:?-+:?\s*\|)+\s*:?-+:?\s*\|?\s*$')

def is_table(block: str) -> bool:
    """Check if a block is a valid table (has pipes, at least 2 rows, second row is separator)"""
    lines = block.splitlines()
    if len(lines) < 2:
        return False

    # All lines should contain pipes
    if not all('|' in line for line in lines):
        return False

    # Second line should be a separator line (dashes and pipes)
    if not TABLE_SEPARATOR_PATTERN.match(lines[1]):
        return False

    return True

def block_to_block_type(block: str) -> BlockType:
    lines = block.splitlines() or [""]
    first = lines[0]

    checks = [
        (lambda: any(first.startswith(pref) for pref in HEADING_PREFIXES),  BlockType.HEADING),
        (lambda: first.startswith("```") and block.endswith("```"),         BlockType.CODE),
        (lambda: len(lines) == 1 and HORIZONTAL_RULE_PATTERN.match(first), BlockType.HORIZONTAL_RULE),
        (lambda: is_table(block),                                           BlockType.TABLE),
        (lambda: all(line.startswith(">") for line in lines),               BlockType.QUOTE),
        (lambda: all(TASK_LIST_PATTERN.match(line) for line in lines),      BlockType.TASK_LIST),
        (lambda: all(UNORDERED_LIST_PATTERN.match(line) for line in lines), BlockType.UNORDERED_LIST),
        (lambda: all(ORDERED_PATTERN.match(line) for line in lines),        BlockType.ORDERED_LIST),
    ]

    for predicate, block_type in checks:
        if predicate():
            return block_type
    
    return BlockType.PARAGRAPH