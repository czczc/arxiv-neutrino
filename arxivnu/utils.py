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


_FOOTNOTE_MARKS = "*¶†‡§# "


def normalize_collaboration(value: str, title: str = "") -> str:
    """Clean an InspireHEP collaboration string.

    Handles the raw author-affiliation form "(STAR Collaboration)*" → "STAR",
    and Inspire's hyphen-split names ("G" for a title mentioning "RNO-G").
    """
    s = (value or "").strip().rstrip(_FOOTNOTE_MARKS).strip()
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()
    s = re.sub(r"\s+collaboration$", "", s, flags=re.IGNORECASE).strip()
    if len(s) <= 2 and title:
        # Inspire sometimes keeps only the part after a hyphen. Recover the
        # full hyphenated token from the title, e.g. "G" → "RNO-G".
        m = re.search(rf"\b([\w]+(?:-[\w]+)*-{re.escape(s)})\b", title)
        if m:
            s = m.group(1)
    return s


def pick_collaboration(collabs: list[dict], title: str = "") -> str:
    """Choose the best of InspireHEP's `collaborations` entries.

    Entries linked to an experiment record are curated; prefer those over
    free-text ones copied from the author list.
    """
    if not collabs:
        return ""
    curated = [c for c in collabs if c.get("record")]
    raw = (curated or collabs)[0].get("value", "")
    return normalize_collaboration(raw, title)
