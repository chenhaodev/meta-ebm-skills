# builder/extract_topics.py
import json
import re
from pathlib import Path
from typing import Iterator

EVIDENCE_BASE = Path(__file__).parent.parent / "evidence" / "d"
TOC_DIR = EVIDENCE_BASE / "table-of-contents"


def load_toc(toc_filename: str) -> dict:
    """Load and parse a table-of-contents .js file."""
    path = (TOC_DIR / toc_filename).resolve()
    if not path.is_relative_to(TOC_DIR.resolve()):
        raise ValueError(f"TOC path escapes evidence directory: {toc_filename}")
    content = path.read_text(encoding="utf-8")
    match = re.match(r'^var data=(.+)$', content.strip(), re.DOTALL)
    if not match:
        raise ValueError(f"Could not parse TOC: {toc_filename}")
    return json.loads(match.group(1))


def walk_toc_items(toc_data: dict) -> Iterator[dict]:
    """Recursively yield all TOPIC items from a TOC structure."""
    if toc_data.get("type") == "TOPIC":
        url = toc_data.get("url", "")
        yield {
            "name": toc_data.get("name", ""),
            "path": topic_url_to_id(url),
            "url": url,
        }
    for section in toc_data.get("sections", []):
        yield from walk_toc_items(section)
    for item in toc_data.get("items", []):
        yield from walk_toc_items(item)


def keyword_search_toc(toc_data: dict, keywords: list[str]) -> list[dict]:
    """Return topics whose name contains any of the keywords (case-insensitive)."""
    lower_kw = [k.lower() for k in keywords]
    return [
        item for item in walk_toc_items(toc_data)
        if any(kw in item["name"].lower() for kw in lower_kw)
    ]


def topic_url_to_id(url: str) -> str:
    """Extract path slug from 'topic.htm?path=<slug>'."""
    match = re.search(r'path=([^&]+)', url)
    return match.group(1) if match else url


def build_manifest(primary_items: list[dict], cross_items: list[dict]) -> list[dict]:
    """Merge primary and cross-specialty items, deduplicating by path."""
    seen: set[str] = set()
    result: list[dict] = []
    for item in primary_items + cross_items:
        if item["path"] not in seen:
            seen.add(item["path"])
            result.append(item)
    return result


def discover_topics(disease_config: dict) -> list[dict]:
    """Full discovery pipeline for a disease config entry."""
    primary_toc = load_toc(disease_config["toc_file"])
    primary_items = list(walk_toc_items(primary_toc))

    cross_items: list[dict] = []
    for specialty_toc_name in disease_config.get("cross_specialty_tocs", []):
        cross_toc = load_toc(specialty_toc_name)
        cross_items.extend(
            keyword_search_toc(cross_toc, disease_config.get("keywords", []))
        )

    return build_manifest(primary_items, cross_items)
