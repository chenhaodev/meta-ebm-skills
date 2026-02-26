# tests/test_preprocess.py
import json
import pytest
from builder.preprocess import extract_topic_markdown, strip_noise

SAMPLE_JS = '''var data={"title":"Asthma overview","body":"<div id=\\"topicContent\\"><h1>Overview</h1><p>Asthma is a chronic disease.</p><div class=\\"fee\\">Price: $100</div></div>","outline":""}'''

def test_extract_returns_title_and_markdown():
    result = extract_topic_markdown(SAMPLE_JS)
    assert result["title"] == "Asthma overview"
    assert "# Overview" in result["markdown"]
    assert "Asthma is a chronic disease" in result["markdown"]

def test_strip_noise_removes_pricing():
    result = extract_topic_markdown(SAMPLE_JS)
    assert "Price" not in result["markdown"]
    assert "$100" not in result["markdown"]

def test_extract_handles_invalid_js():
    with pytest.raises(ValueError, match="Could not parse topic JS"):
        extract_topic_markdown("not valid js")

def test_strip_noise_removes_brand_names_section():
    js = '''var data={"title":"Drug X","body":"<div><h1>Use</h1><p>Treats pain.</p><div id=\\"F999\\" class=\\"list fbnlist\\"><span>Brand Names: International</span><ul><li>DrugX (DE)</li></ul></div></div>","outline":""}'''
    result = extract_topic_markdown(js)
    assert "Brand Names: International" not in result["markdown"]
    assert "Treats pain" in result["markdown"]


def test_strip_noise_removes_by_id():
    """strip_noise removes elements matched by _NOISE_IDS (topicAgreement)."""
    js = (
        'var data={"title":"T","body":"<div><p>Keep this.</p>'
        '<div id=\\"topicAgreement\\"><p>Legal boilerplate</p></div></div>","outline":""}'
    )
    result = extract_topic_markdown(js)
    assert "Keep this" in result["markdown"]
    assert "Legal boilerplate" not in result["markdown"]


def test_strip_noise_removes_topic_agreement_alongside_class():
    """strip_noise removes both class-based and id-based noise in one pass."""
    js = (
        'var data={"title":"T","body":"<div><p>Main content</p>'
        '<div class=\\"fee\\">Price info</div>'
        '<div id=\\"topicAgreement\\">Agreement text</div></div>","outline":""}'
    )
    result = extract_topic_markdown(js)
    assert "Main content" in result["markdown"]
    assert "Price info" not in result["markdown"]
    assert "Agreement text" not in result["markdown"]
