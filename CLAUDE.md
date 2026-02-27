# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

This project builds a "meta" agent-skill for OpenCode (Claude Code) that auto-generates Evidence-Based Medicine (EBM) clinical decision-support skills. The primary evidence source is an offline copy of UpToDate 2018 stored in `evidence/`.

## Evidence Data Structure

The `evidence/` directory contains ~18,968 medical topic articles from UpToDate 2018 (read-only reference data):

- **`evidence/d/topics/<id>.js`** — Each file exposes a single JS variable: `var data = { title: "...", body: "<html...>" }`. The `body` is HTML-formatted article content.
- **`evidence/d/sfiles/titles.js`** — Slug-to-title map: `var titles = { "slug": "Display Title", ... }`. Use this to find topics by name.
- **`evidence/d/sfiles/words.js`** — Full-text search index words.
- **`evidence/d/sfiles/grades.js`** — Evidence grading data (GRADE system).
- **`evidence/d/sfiles/types.js`** — Topic type classifications.
- **`evidence/d/sfiles/dict.js`** — Medical term dictionary.
- **`evidence/d/topics/<id>.js`** — IDs correspond to slugs in `titles.js`. To find a topic by title, search `titles.js` for the slug, then load the matching `<id>.js`.
- **`evidence/d/images/`** — Clinical algorithm images organized by specialty (e.g., `HEME/`, `PC/`, `ALLRG/`).

To extract plain text from a topic, strip HTML tags from the `body` field.

## Repository Layout

```
evidence/          # Read-only UpToDate 2018 offline database
  d/
    topics/        # ~18,968 JS files (one per article)
    sfiles/        # Search indices (titles, words, grades, types, dict)
    images/        # Clinical algorithm GIFs by specialty
docs/
  plans/           # Implementation planning documents
.claude/
  └── skills/
      └── build-cdss-skill/
          └── SKILL.md        # Meta skill, auto-loaded by Claude Code
```

## Development Notes

- No build system exists yet; this is a pre-implementation planning phase.
- Plans and skill designs go in `docs/plans/`.
- The evidence data is JavaScript-wrapped JSON; parse it by stripping the `var data=` prefix and trailing semicolon, then `JSON.parse()`.
