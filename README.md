# meta-ebm-skills

A meta Claude Code skill that auto-generates disease-specific Clinical Decision Support System (CDSS) skills from a local UpToDate EBM evidence library.

## Overview

Invoke the `build-cdss-skill` meta skill to generate a self-contained Claude Code skill for any disease or care path. Each generated skill acts as a disease-management expert, backed by pre-processed EBM evidence, and supports three clinical interaction modes:

- **Q&A Consultation** — reason through a patient scenario
- **Document Generation** — produce a structured care plan or clinical note
- **Protocol Lookup** — retrieve drug doses, diagnostic criteria, or guidelines

## Requirements

- Python 3.10+
- Claude Code
- Local UpToDate offline export in `evidence/` (not included in this repo)

```bash
pip install -r requirements.txt
```

## Usage

### Build a single disease skill

Invoke the meta skill from Claude Code (run from this project's root):

```
/build-cdss-skill asthma
```

Claude will:
1. Discover relevant topics from the evidence library (TOC + cross-specialty keyword search)
2. Show you the topic list for review before proceeding
3. Extract and pre-process evidence into Markdown buckets
4. Generate a `skills/<disease>/` directory with `SKILL.md`, evidence files, and `README.md`
5. Optionally install the skill to `~/.claude/skills/` and tag a release

### Build all diseases in `diseases.yaml`

```
/build-cdss-skill --all
```

### Build by specialty

```
/build-cdss-skill --specialty allergy-and-immunology
```

### Run the builder directly (without Claude)

```bash
python3 -m builder.build_skill asthma
python3 -m builder.build_skill --all
python3 -m builder.build_skill --specialty endocrinology-and-diabetes
```

## Repository Structure

```
meta-ebm-skills/
├── evidence/                   # Local UpToDate offline export (not tracked)
│   └── d/
│       ├── topics/             # ~18,968 topic JS files
│       ├── table-of-contents/  # 620 specialty TOC files
│       └── sfiles/             # titles.js, grades.js, etc.
│
├── builder/                    # Generation tooling
│   ├── build_skill.py          # Main CLI orchestrator
│   ├── extract_topics.py       # TOC + keyword topic discovery
│   ├── preprocess.py           # HTML → Markdown converter
│   ├── classify.py             # Clinical bucket classifier
│   ├── diseases.yaml           # Disease config (add new diseases here)
│   └── templates/
│       ├── SKILL.md.j2         # Runtime CDSS skill template
│       └── README.md.j2        # Skill README template
│
├── .claude/
│   └── skills/
│       └── build-cdss-skill/
│           └── SKILL.md        # The build-cdss-skill meta skill (auto-loaded by Claude Code)
│
├── skills/                     # Generated CDSS skills
│   └── asthma/                 # Example: Asthma CDSS skill
│       ├── SKILL.md            # Runtime skill (invoke with /cdss-asthma)
│       ├── evidence/
│       │   ├── index.json      # Topic index (74 entries)
│       │   ├── overview.md     # 1,330 KB — pathogenesis, epidemiology
│       │   ├── diagnosis.md    # 621 KB — evaluation, testing
│       │   ├── treatment.md    # 1,431 KB — management protocols
│       │   └── monitoring.md   # 114 KB — adherence, follow-up
│       └── README.md
│
└── tests/                      # 36 tests, 96% coverage
```

## Adding a New Disease

Edit `builder/diseases.yaml`:

```yaml
diseases:
  copd:
    display_name: "COPD"
    specialty: pulmonary-and-critical-care-medicine
    toc_file: pulmonary-and-critical-care-medicine_copd.js
    keywords:
      - COPD
      - chronic obstructive
      - emphysema
      - bronchitis
    cross_specialty_tocs:
      - cardiovascular-medicine_coronary-heart-disease.js
```

Then run:

```bash
python3 -m builder.build_skill copd
```

Or invoke via Claude Code:

```
/build-cdss-skill copd
```

## Installing a Generated Skill

```bash
cp -r skills/asthma/ ~/.claude/skills/cdss-asthma/
```

Then in any Claude Code session:

```
/cdss-asthma
```

## Releasing a Skill

```bash
git tag asthma@1.0.0
git push origin asthma@1.0.0
```

## Testing

```bash
pytest tests/ -v --cov=builder --cov-report=term-missing
```

## Available Skills

| Skill | Topics | Evidence |
|-------|--------|----------|
| `asthma` | 74 | 3.5 MB |

## Evidence Buckets

The builder classifies each topic into one of five clinical buckets:

| Bucket | Contents |
|--------|----------|
| `overview.md` | Pathogenesis, epidemiology, natural history |
| `diagnosis.md` | Evaluation, testing, diagnostic criteria |
| `treatment.md` | Management protocols, medications, interventions |
| `monitoring.md` | Follow-up, adherence, patient education |
| `drugs.md` | Drug information, dosing, interactions |

## Architecture

Two-layer design:

1. **Meta skill** (`meta-skill/SKILL.md`) — instructs Claude to run the builder script
2. **Runtime CDSS skill** (`skills/<disease>/SKILL.md`) — instructs Claude to act as a disease expert using the pre-processed evidence

The builder is deterministic and makes no LLM calls — it runs in seconds per disease.
