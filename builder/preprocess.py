# builder/preprocess.py
import json
import re
import html2text
from bs4 import BeautifulSoup, Tag

_NOISE_CLASSES = {"fee", "fbnlist", "drugBrandNames"}
_NOISE_IDS = {"topicAgreement"}


def extract_topic_markdown(js_content: str) -> dict:
    """Parse a UpToDate topic .js file and return {title, markdown}."""
    match = re.match(r'^var data=(.+)$', js_content.strip(), re.DOTALL)
    if not match:
        raise ValueError("Could not parse topic JS")
    data = json.loads(match.group(1))
    title = data.get("title", "")
    body_html = data.get("body", "")
    cleaned_html = strip_noise(body_html)
    markdown = _html_to_markdown(cleaned_html)
    return {"title": title, "markdown": markdown}


def strip_noise(html: str) -> str:
    """Remove pricing, brand name lists, legal boilerplate from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    # Collect tags to remove upfront to avoid mutation during iteration
    tags_to_remove = []
    for tag in soup.find_all(True):
        if not isinstance(tag, Tag):
            continue
        classes = set(tag.get("class") or [])
        if classes & _NOISE_CLASSES:
            tags_to_remove.append(tag)
            continue
        tag_id = tag.get("id", "")
        if tag_id in _NOISE_IDS:
            tags_to_remove.append(tag)
    for tag in tags_to_remove:
        tag.decompose()
    return str(soup)


def _html_to_markdown(html: str) -> str:
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.ignore_images = True
    converter.body_width = 0
    return converter.handle(html).strip()
