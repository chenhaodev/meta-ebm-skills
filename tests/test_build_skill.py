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
