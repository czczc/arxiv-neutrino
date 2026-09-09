import json
import re


def split_author_string(s: str) -> list[str]:
    """Split 'Author1 (aff1, aff2), Author2 (aff3)' into ['Author1', 'Author2'].

    Splits on commas that are outside parentheses, then strips the affiliation.
    """
    parts = []
    depth = 0
    start = 0
    for i, ch in enumerate(s):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ',' and depth == 0:
            part = re.sub(r'\s*\(.*', '', s[start:i]).strip()
            if part:
                parts.append(part)
            start = i + 1
    last = re.sub(r'\s*\(.*', '', s[start:]).strip()
    if last:
        parts.append(last)
    return parts


def normalize_authors(authors_json: str) -> list[str]:
    """Parse authors from stored JSON, handling the single-blob RSS format."""
    raw = json.loads(authors_json or "[]")
    if len(raw) == 1 and ', ' in raw[0]:
        return split_author_string(raw[0])
    return raw
