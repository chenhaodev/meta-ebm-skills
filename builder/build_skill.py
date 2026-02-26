# builder/build_skill.py
import json
import re
import sys
import yaml
import argparse
from datetime import date
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from builder.extract_topics import discover_topics
from builder.preprocess import extract_topic_markdown
from builder.classify import classify_topic

BUILDER_DIR = Path(__file__).parent
EVIDENCE_TOPICS_DIR = BUILDER_DIR.parent / "evidence" / "d" / "topics"
SKILLS_DIR = BUILDER_DIR.parent / "skills"
TEMPLATES_DIR = BUILDER_DIR / "templates"
BUCKETS = ["overview", "diagnosis", "treatment", "monitoring", "drugs"]


def load_diseases_config() -> dict:
    """Load disease definitions from diseases.yaml."""
    config_path = BUILDER_DIR / "diseases.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)["diseases"]


def group_topics_by_bucket(topics: list[dict]) -> dict:
    """Classify topics into clinical buckets."""
    groups = {b: [] for b in BUCKETS}
    for topic in topics:
        bucket = classify_topic(topic["name"])
        groups[bucket].append(topic)
    return groups


def render_skill_files(
    disease_id: str,
    display_name: str,
    specialty: str,
    groups: dict,
    output_dir: Path,
) -> None:
    """Render SKILL.md, README.md, and evidence files into output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    evidence_dir = output_dir / "evidence"
    evidence_dir.mkdir(exist_ok=True)

    index = {}
    non_empty_buckets = []

    for bucket, topics in groups.items():
        if not topics:
            continue
        non_empty_buckets.append(bucket)
        bucket_file = evidence_dir / f"{bucket}.md"
        sections = [f"# {t['name']}\n\n{t.get('markdown', '')}" for t in topics]
        bucket_file.write_text("\n\n---\n\n".join(sections), encoding="utf-8")
        for t in topics:
            index[t["path"]] = {
                "name": t["name"],
                "bucket": bucket,
                "file": f"{bucket}.md",
            }

    (evidence_dir / "index.json").write_text(
        json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)))
    context = {
        "disease_id": disease_id,
        "display_name": display_name,
        "specialty": specialty,
        "evidence_path": f"skills/{disease_id}/evidence",
        "topic_count": sum(len(v) for v in groups.values()),
        "generated_date": str(date.today()),
        "buckets": non_empty_buckets,
        "version": "1.0.0",
    }
    (output_dir / "SKILL.md").write_text(
        env.get_template("SKILL.md.j2").render(**context), encoding="utf-8"
    )
    (output_dir / "README.md").write_text(
        env.get_template("README.md.j2").render(**context), encoding="utf-8"
    )


def _build_slug_index() -> dict:
    """Build mapping from topic slug -> Path of .js file.

    Uses titles.js (slug->title) combined with a scan of topic files (title->id)
    to build the complete slug->filepath mapping.
    """
    # Step 1: Parse titles.js to get slug->title
    titles_path = BUILDER_DIR.parent / "evidence" / "d" / "sfiles" / "titles.js"
    if not titles_path.exists():
        return {}
    titles_content = titles_path.read_text(encoding="utf-8", errors="ignore")
    match = re.match(r"^var titles=(.+);$", titles_content.strip(), re.DOTALL)
    if not match:
        return {}
    slug_to_title = json.loads(match.group(1))

    # Step 2: Scan topic files to build title->file mapping
    title_to_file: dict[str, Path] = {}
    for topic_file in EVIDENCE_TOPICS_DIR.glob("*.js"):
        file_content = topic_file.read_text(encoding="utf-8", errors="ignore")
        title_match = re.search(r'"title":"([^"]+)"', file_content)
        if title_match:
            title_to_file[title_match.group(1)] = topic_file

    # Step 3: Combine slug->title->file
    slug_to_file = {}
    for slug, title in slug_to_title.items():
        if title in title_to_file:
            slug_to_file[slug] = title_to_file[title]
    return slug_to_file


def build_disease(disease_id: str, config: dict) -> None:
    """Run the full build pipeline for a single disease."""
    print(f"[build] Discovering topics for: {disease_id}")
    manifest = discover_topics(config)
    print(f"[build] Found {len(manifest)} topics")

    slug_to_file = _build_slug_index()

    topics_with_markdown = []
    for item in manifest:
        slug = item["path"]
        js_file = slug_to_file.get(slug)
        if js_file is None:
            print(f"[warn] No topic file found for slug: {slug}")
            topics_with_markdown.append({**item, "markdown": ""})
            continue
        try:
            parsed = extract_topic_markdown(js_file.read_text(encoding="utf-8"))
            topics_with_markdown.append({**item, "markdown": parsed["markdown"]})
        except Exception as e:
            print(f"[warn] Failed to parse {js_file.name}: {e}")
            topics_with_markdown.append({**item, "markdown": ""})

    groups = group_topics_by_bucket(topics_with_markdown)
    output_dir = SKILLS_DIR / disease_id
    render_skill_files(
        disease_id,
        config["display_name"],
        config["specialty"],
        groups,
        output_dir,
    )
    print(f"[build] Skill written to: {output_dir}")


def main() -> None:
    """Entry point for the build CLI."""
    parser = argparse.ArgumentParser(description="Build CDSS skills from EBM evidence")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("disease", nargs="?", help="Disease ID from diseases.yaml")
    group.add_argument("--all", action="store_true", help="Build all diseases")
    group.add_argument("--specialty", help="Build all diseases in a specialty")
    args = parser.parse_args()

    config = load_diseases_config()

    if args.all:
        targets = list(config.items())
    elif args.specialty:
        targets = [(k, v) for k, v in config.items() if v["specialty"] == args.specialty]
    else:
        if args.disease not in config:
            print(f"Error: '{args.disease}' not found in diseases.yaml")
            sys.exit(1)
        targets = [(args.disease, config[args.disease])]

    for disease_id, disease_config in targets:
        build_disease(disease_id, disease_config)


if __name__ == "__main__":
    main()
