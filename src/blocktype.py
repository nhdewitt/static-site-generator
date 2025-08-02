from enum import Enum
import re

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"

HEADING_PREFIXES = [f"{'#' * i} " for i in range(6, 0, -1)]
ORDERED_PATTERN = re.compile(r'^(?P<index>\d+)\.\s+(?P<text>.+)$')

def block_to_block_type(block: str) -> BlockType:
    lines = block.splitlines() or [""]
    first = lines[0]

    checks = [
        (lambda: any(first.startswith(pref) for pref in HEADING_PREFIXES),  BlockType.HEADING),
        (lambda: first.startswith("```") and block.endswith("```"),         BlockType.CODE),
        (lambda: all(line.startswith(">") for line in lines),               BlockType.QUOTE),
        (lambda: all(line.startswith("- ") for line in lines),              BlockType.UNORDERED_LIST),
        (lambda: all(ORDERED_PATTERN.match(line) for line in lines),        BlockType.ORDERED_LIST),
    ]

    for predicate, block_type in checks:
        if predicate():
            return block_type
    
    return BlockType.PARAGRAPH