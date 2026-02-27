---
name: build-cdss-skill
description: >
  Use when you want to generate a new disease-specific CDSS skill from the local
  UpToDate evidence files. Supports single disease, batch, or specialty-based generation.
---

# Build CDSS Skill (Meta Skill)

## Overview

This skill orchestrates the generation of a new CDSS (Clinical Decision Support)
skill for a specific disease or care path, using the local EBM evidence base.

**Announce at start:** "Using build-cdss-skill to generate the [disease] CDSS skill."

## Prerequisites

- `evidence/` directory must be present in the project root
- Python 3.10+ with dependencies installed: `pip install -r requirements.txt`
- Run from the `meta-ebm-skills/` project root

## Invocation Patterns

Single disease:
```
/build-cdss-skill asthma
```

All diseases in diseases.yaml:
```
/build-cdss-skill --all
```

All diseases in a specialty:
```
/build-cdss-skill --specialty allergy-and-immunology
```

## Execution Steps

### Step 1: Validate

Check that `evidence/d/table-of-contents/` and `evidence/d/topics/` exist.
If the disease argument is provided, check it exists in `builder/diseases.yaml`.
If not found, list available disease IDs and ask the user to pick or add one.

### Step 2: Discover Topics (show manifest to user)

Run:
```bash
python3 -c "
import yaml, json
from builder.extract_topics import discover_topics
config = yaml.safe_load(open('builder/diseases.yaml'))['diseases']['DISEASE_ID']
manifest = discover_topics(config)
print(f'Found {len(manifest)} topics')
for m in manifest[:20]:
    print(f'  - {m[\"name\"]}')
if len(manifest) > 20:
    print(f'  ... and {len(manifest)-20} more')
"
```

Present the topic count and first 20 topics to the user.
Ask: "Does this topic list look right? Should I proceed, or would you like to add/remove any topics?"

**Do NOT proceed to Step 3 without explicit user confirmation.**

### Step 3: Build the Skill

After user confirmation, run:
```bash
python3 -m builder.build_skill DISEASE_ID
```

Watch for `[warn]` lines — report any slug resolution failures to the user.

### Step 4: Verify Output

Check that these files exist:
- `skills/DISEASE_ID/SKILL.md`
- `skills/DISEASE_ID/README.md`
- `skills/DISEASE_ID/evidence/index.json`
- At least one `skills/DISEASE_ID/evidence/*.md` bucket file

Report the topic counts per bucket.

### Step 5: Install (Optional)

Ask the user: "Would you like to install this skill to ~/.claude/skills/ now?"

If yes:
```bash
cp -r skills/DISEASE_ID/ ~/.claude/skills/cdss-DISEASE_ID/
```

### Step 6: Commit

```bash
git add skills/DISEASE_ID/
git commit -m "feat(DISEASE_ID): generate CDSS skill (N topics)"
```

### Step 7: Tag Release (Optional)

Ask the user: "Would you like to tag this as a release?"

If yes:
```bash
git tag DISEASE_ID@1.0.0
```
