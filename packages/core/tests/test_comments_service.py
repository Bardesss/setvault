import pytest
from setvault_core.services.comments import (
    extract_mention_usernames,
    render_markdown_safe,
)


def test_render_markdown_strips_script():
    raw = "Hello <script>alert(1)</script> **world**"
    html = render_markdown_safe(raw)
    assert "<script>" not in html
    assert "<strong>world</strong>" in html


def test_render_markdown_preserves_links_with_rel():
    raw = "Check [this](https://example.com)"
    html = render_markdown_safe(raw)
    assert 'rel="noopener noreferrer"' in html
    assert 'href="https://example.com"' in html


def test_render_markdown_strips_raw_html():
    raw = "Hello <iframe src=evil></iframe>"
    html = render_markdown_safe(raw)
    assert "<iframe" not in html


def test_extract_mention_usernames_finds_all():
    body = "Hey @bart and @alice — also @carlos_99"
    assert extract_mention_usernames(body) == ["bart", "alice", "carlos_99"]


def test_extract_mention_usernames_ignores_emails():
    body = "Contact me@example.com or @bart"
    assert extract_mention_usernames(body) == ["bart"]
