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
