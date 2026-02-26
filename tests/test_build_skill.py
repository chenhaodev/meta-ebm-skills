# tests/test_build_skill.py
import json
from pathlib import Path
from builder.build_skill import (
    load_diseases_config,
    group_topics_by_bucket,
    render_skill_files,
)

def test_load_diseases_config():
    config = load_diseases_config()
    assert "asthma" in config
    assert "toc_file" in config["asthma"]
    assert "keywords" in config["asthma"]

def test_group_topics_by_bucket():
    topics = [
        {"name": "Asthma overview", "path": "asthma-overview", "markdown": "# Overview\nContent"},
        {"name": "Diagnosis of asthma", "path": "diagnosis-asthma", "markdown": "# Diagnosis\nContent"},
        {"name": "Albuterol: Drug information", "path": "albuterol-drug", "markdown": "# Drug\nContent"},
    ]
    groups = group_topics_by_bucket(topics)
    assert "asthma-overview" in [t["path"] for t in groups["overview"]]
    assert "diagnosis-asthma" in [t["path"] for t in groups["diagnosis"]]
    assert "albuterol-drug" in [t["path"] for t in groups["drugs"]]

def test_render_skill_files_creates_expected_files(tmp_path):
    groups = {
        "overview": [{"name": "Asthma overview", "path": "asthma-overview", "markdown": "content"}],
        "diagnosis": [],
        "treatment": [],
        "monitoring": [],
        "drugs": [],
    }
    render_skill_files("asthma", "Asthma", "allergy-and-immunology", groups, tmp_path)
    assert (tmp_path / "SKILL.md").exists()
    assert (tmp_path / "README.md").exists()
    assert (tmp_path / "evidence" / "overview.md").exists()
    assert (tmp_path / "evidence" / "index.json").exists()

def test_render_skill_index_json(tmp_path):
    groups = {
        "overview": [{"name": "Asthma overview", "path": "asthma-overview", "markdown": "content"}],
        "diagnosis": [], "treatment": [], "monitoring": [], "drugs": [],
    }
    render_skill_files("asthma", "Asthma", "allergy-and-immunology", groups, tmp_path)
    index = json.loads((tmp_path / "evidence" / "index.json").read_text())
    assert "asthma-overview" in index
    assert index["asthma-overview"]["bucket"] == "overview"
    assert index["asthma-overview"]["file"] == "overview.md"

def test_build_slug_index_returns_dict():
    from builder.build_skill import _build_slug_index
    result = _build_slug_index()
    assert isinstance(result, dict)
    # Should resolve at least some slugs if titles.js exists
    assert len(result) > 0

import sys
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_build_slug_index_no_titles_js(monkeypatch, tmp_path):
    """_build_slug_index returns empty dict when titles.js does not exist."""
    from builder import build_skill as bs
    monkeypatch.setattr(bs, "BUILDER_DIR", tmp_path / "builder")
    (tmp_path / "builder").mkdir()
    # titles.js not created → path does not exist
    result = bs._build_slug_index()
    assert result == {}


def test_build_slug_index_unparseable_titles(monkeypatch, tmp_path):
    """_build_slug_index returns empty dict when titles.js has unexpected format."""
    from builder import build_skill as bs
    builder_dir = tmp_path / "builder"
    builder_dir.mkdir()
    sfiles_dir = tmp_path / "evidence" / "d" / "sfiles"
    sfiles_dir.mkdir(parents=True)
    (sfiles_dir / "titles.js").write_text("not valid titles js", encoding="utf-8")
    # Patch BUILDER_DIR so the path resolution works
    monkeypatch.setattr(bs, "BUILDER_DIR", builder_dir)
    result = bs._build_slug_index()
    assert result == {}


def test_build_disease_missing_slug(tmp_path, monkeypatch):
    """build_disease handles missing slug gracefully (appends empty markdown)."""
    from builder import build_skill as bs

    manifest = [{"name": "Some Topic", "path": "no-such-slug", "url": "topic.htm?path=no-such-slug"}]
    fake_groups = {b: [] for b in bs.BUCKETS}
    fake_groups["overview"] = [{"name": "Some Topic", "path": "no-such-slug", "markdown": ""}]

    with patch("builder.build_skill.discover_topics", return_value=manifest), \
         patch("builder.build_skill._build_slug_index", return_value={}), \
         patch("builder.build_skill.group_topics_by_bucket", return_value=fake_groups), \
         patch("builder.build_skill.render_skill_files") as mock_render:
        disease_config = {
            "display_name": "Test",
            "specialty": "test-specialty",
            "toc_file": "test.js",
            "keywords": [],
            "cross_specialty_tocs": [],
        }
        bs.build_disease("test-disease", disease_config)
        mock_render.assert_called_once()


def test_build_disease_parse_failure(tmp_path, monkeypatch):
    """build_disease handles extract_topic_markdown failure gracefully."""
    from builder import build_skill as bs

    fake_js_file = tmp_path / "bad_topic.js"
    fake_js_file.write_text("invalid js content", encoding="utf-8")

    manifest = [{"name": "Bad Topic", "path": "bad-slug", "url": "topic.htm?path=bad-slug"}]
    fake_groups = {b: [] for b in bs.BUCKETS}
    fake_groups["overview"] = [{"name": "Bad Topic", "path": "bad-slug", "markdown": ""}]

    with patch("builder.build_skill.discover_topics", return_value=manifest), \
         patch("builder.build_skill._build_slug_index", return_value={"bad-slug": fake_js_file}), \
         patch("builder.build_skill.group_topics_by_bucket", return_value=fake_groups), \
         patch("builder.build_skill.render_skill_files") as mock_render:
        disease_config = {
            "display_name": "Test",
            "specialty": "test-specialty",
            "toc_file": "test.js",
            "keywords": [],
            "cross_specialty_tocs": [],
        }
        bs.build_disease("test-disease", disease_config)
        mock_render.assert_called_once()


def test_main_single_disease(monkeypatch):
    """main() invokes build_disease for a valid single disease argument."""
    from builder import build_skill as bs

    with patch.object(sys, "argv", ["build_skill", "asthma"]), \
         patch("builder.build_skill.build_disease") as mock_build:
        bs.main()
        mock_build.assert_called_once()
        assert mock_build.call_args[0][0] == "asthma"


def test_main_unknown_disease(monkeypatch, capsys):
    """main() exits with error for unknown disease."""
    from builder import build_skill as bs

    with patch.object(sys, "argv", ["build_skill", "nonexistent-disease"]):
        with pytest.raises(SystemExit):
            bs.main()

    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_main_all_flag(monkeypatch):
    """main() with --all calls build_disease for every disease in config."""
    from builder import build_skill as bs

    with patch.object(sys, "argv", ["build_skill", "--all"]), \
         patch("builder.build_skill.build_disease") as mock_build:
        bs.main()
        assert mock_build.call_count >= 2


def test_main_specialty_flag(monkeypatch):
    """main() with --specialty builds only diseases matching that specialty."""
    from builder import build_skill as bs

    with patch.object(sys, "argv", ["build_skill", "--specialty", "allergy-and-immunology"]), \
         patch("builder.build_skill.build_disease") as mock_build:
        bs.main()
        assert mock_build.call_count >= 1
        called_ids = [call[0][0] for call in mock_build.call_args_list]
        assert "asthma" in called_ids
        assert "diabetes-type2" not in called_ids
