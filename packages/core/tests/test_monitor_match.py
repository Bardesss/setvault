from setvault_core.services.monitor_match import normalize_tokens, score_confidence


def test_normalize_tokens_lowercases_and_strips_punctuation():
    assert normalize_tokens("Boiler Room!") == ["boiler", "room"]
    assert normalize_tokens("  DJ-Bicep  ") == ["dj", "bicep"]


def test_high_when_all_query_tokens_in_uploader():
    assert score_confidence("Bicep", uploader="Bicep", title="Live at Field Day") == "high"


def test_high_when_all_query_tokens_in_title():
    assert score_confidence(
        "Boiler Room", uploader="Some Channel", title="Boiler Room: London 2024"
    ) == "high"


def test_low_when_only_partial_match():
    assert score_confidence(
        "Boiler Room", uploader="Boiler Co", title="Boiler maintenance"
    ) == "low"


def test_whole_word_only_no_substring_false_positive():
    assert score_confidence("room", uploader="Mushroom Jazz", title="x") == "low"


def test_empty_query_is_low():
    assert score_confidence("", uploader="anything", title="anything") == "low"
