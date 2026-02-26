# tests/test_extract_topics.py
import json
import pytest
from pathlib import Path
from unittest.mock import patch, mock_open
from builder.extract_topics import (
    load_toc,
    walk_toc_items,
    keyword_search_toc,
    build_manifest,
    topic_url_to_id,
)

SAMPLE_TOC = json.dumps({
    "name": "Asthma",
    "type": "SECTION",
    "sections": [
        {
            "name": "Treatment",
            "type": "SUBSECTION",
            "items": [
                {"name": "Asthma overview", "type": "TOPIC", "url": "topic.htm?path=asthma-overview"},
                {"name": "Severe asthma", "type": "TOPIC", "url": "topic.htm?path=severe-asthma"},
            ]
        }
    ]
})

def test_walk_toc_items_returns_all_topics():
    data = json.loads(SAMPLE_TOC)
    items = list(walk_toc_items(data))
    assert len(items) == 2
    assert items[0]["name"] == "Asthma overview"
    assert items[0]["path"] == "asthma-overview"

def test_keyword_search_returns_matching_topics():
    data = json.loads(SAMPLE_TOC)
    matches = keyword_search_toc(data, ["severe"])
    assert any(m["path"] == "severe-asthma" for m in matches)
    assert not any(m["path"] == "asthma-overview" for m in matches)

def test_topic_url_to_id_extracts_path():
    assert topic_url_to_id("topic.htm?path=asthma-overview") == "asthma-overview"

def test_build_manifest_deduplicates():
    data = json.loads(SAMPLE_TOC)
    # Same topic appears twice
    manifest = build_manifest(
        primary_items=list(walk_toc_items(data)),
        cross_items=list(walk_toc_items(data)),
    )
    paths = [m["path"] for m in manifest]
    assert len(paths) == len(set(paths))

import json
import re
from unittest.mock import patch, mock_open
from builder.extract_topics import load_toc, walk_toc_items, discover_topics


def test_load_toc_real_file():
    """load_toc successfully parses an actual TOC file from evidence/."""
    data = load_toc("allergy-and-immunology_asthma.js")
    assert isinstance(data, dict)
    assert "name" in data or "sections" in data or "items" in data or "type" in data


def test_load_toc_file_not_found():
    """load_toc raises FileNotFoundError for a missing file."""
    with pytest.raises(FileNotFoundError):
        load_toc("nonexistent-specialty_nonexistent.js")


def test_load_toc_invalid_format(tmp_path, monkeypatch):
    """load_toc raises ValueError when JS file has unrecognised format."""
    import builder.extract_topics as et
    # Point TOC_DIR to tmp_path
    monkeypatch.setattr(et, "TOC_DIR", tmp_path)
    (tmp_path / "bad.js").write_text("not_valid_js_here", encoding="utf-8")
    with pytest.raises(ValueError, match="Could not parse TOC"):
        load_toc("bad.js")


def test_walk_toc_items_empty():
    """walk_toc_items yields nothing for a section with no nested topics."""
    data = {"name": "Empty", "type": "SECTION", "sections": [], "items": []}
    items = list(walk_toc_items(data))
    assert items == []


def test_walk_toc_items_topic_without_path_in_url():
    """walk_toc_items handles TOPIC with a URL that has no path= param."""
    data = {
        "name": "Odd Topic",
        "type": "TOPIC",
        "url": "topic.htm",
        "sections": [],
        "items": [],
    }
    items = list(walk_toc_items(data))
    assert len(items) == 1
    # topic_url_to_id returns the original url when no path= found
    assert items[0]["path"] == "topic.htm"


def test_discover_topics_no_cross_specialty():
    """discover_topics works with an empty cross_specialty_tocs list."""
    disease_config = {
        "toc_file": "allergy-and-immunology_asthma.js",
        "keywords": ["asthma"],
        "cross_specialty_tocs": [],
    }
    result = discover_topics(disease_config)
    assert isinstance(result, list)
    assert len(result) > 0
    for item in result:
        assert "name" in item
        assert "path" in item


def test_discover_topics_with_cross_specialty():
    """discover_topics merges cross-specialty hits and deduplicates."""
    disease_config = {
        "toc_file": "allergy-and-immunology_asthma.js",
        "keywords": ["asthma"],
        "cross_specialty_tocs": [
            "pulmonary-and-critical-care-medicine_asthma.js",
        ],
    }
    result = discover_topics(disease_config)
    paths = [item["path"] for item in result]
    assert len(paths) == len(set(paths)), "discover_topics should deduplicate"
    assert len(result) > 0
