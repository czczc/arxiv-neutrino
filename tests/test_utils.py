from arxivnu.utils import normalize_collaboration, pick_collaboration


def test_normalize_strips_footnotes_parens_and_word():
    assert normalize_collaboration("(STAR Collaboration)*") == "STAR"
    assert normalize_collaboration("(XENON Collaboration)¶") == "XENON"
    assert normalize_collaboration("(XENON Collaboration)**") == "XENON"
    assert normalize_collaboration("NOvA Collaboration") == "NOvA"
    assert normalize_collaboration("  DUNE ") == "DUNE"
    assert normalize_collaboration("") == ""
    # Trailing digits are part of real names, never footnote marks
    for name in ("NA64", "COSINE-100", "DarkSide-50", "Darkside-20k"):
        assert normalize_collaboration(name) == name


def test_normalize_recovers_hyphen_split_name_from_title():
    assert normalize_collaboration("G", "The beamformed trigger of RNO-G: its design") == "RNO-G"
    assert normalize_collaboration("G", "A title without the name") == "G"
    assert normalize_collaboration("LZ", "Results from LUX-ZEPLIN (LZ)") == "LZ"  # 2 chars but no hyphenated match


def test_pick_prefers_curated_record():
    collabs = [{"value": "(STAR Collaboration)*"}, {"record": {"$ref": "x"}, "value": "STAR"}]
    assert pick_collaboration(collabs) == "STAR"
    assert pick_collaboration([{"value": "(STAR Collaboration)*"}]) == "STAR"
    assert pick_collaboration([]) == ""
