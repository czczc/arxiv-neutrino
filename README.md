# Neutrino Daily

A daily feed of new experimental neutrino-physics papers on arXiv, served as a
small triage-inbox web app.

Each morning the pipeline reads the previous day's listings in `hep-ex`,
`nucl-ex`, `physics.ins-det` and `physics.data-an`, keeps the papers that are
about neutrino physics, enriches them with collaboration and document-type
metadata from InspireHEP, and has an LLM write a short summary and assign tags
from a fixed taxonomy. The result is browsable by day, collaboration and tag,
with full-text search.

There is no login. Everything a visitor does (stars, read marks, deletions,
user-defined folders) is stored in their own browser and can be moved between
browsers as a JSON file from the top bar.

## How papers are selected

1. **Keyword pass** over title and abstract. Neutrino terms and experiment
   names mark a paper as *certain*; generic detector words only (scintillator,
   PMT, SiPM, dark matter) mark it *ambiguous*; anything else is dropped.
2. **InspireHEP lookup** for the survivors. Conference proceedings are dropped,
   as are papers from collider collaborations with no neutrino programme.
   Results from liquid-noble direct-detection experiments (LZ, XENON, PandaX,
   DarkSide, DEAP) are promoted to *certain*.
3. **LLM review.** Each remaining paper gets a two-to-three sentence summary
   written for a physicist and tags from the taxonomy in
   `.claude/commands/arxiv-summarize.md`. Ambiguous papers are also judged for
   relevance and dropped if they are not applicable to neutrino experiments.

The rules live in `arxivnu/fetch.py`.

## Layout

```
arxivnu/          Python package
  fetch.py        arXiv RSS/API + InspireHEP → DB + pending.json      (arxiv-fetch)
  apply.py        results.json → DB                                    (arxiv-apply)
  backfill.py     re-run fetch for a date range                        (arxiv-backfill)
  exclude.py      hide a paper for good; curation, server-side only    (arxiv-exclude)
  api.py          FastAPI: read-only /api/* + serves frontend/dist
  db.py           SQLite schema; ARXIV_DB / ARXIV_WORK env overrides
frontend/         Vite + Vue 3 SPA (nav · paper list · reader; calendar archive; about)
scripts/          daily.sh (pipeline), deploy.sh (server)
.claude/commands/arxiv-summarize.md   the Claude Code skill used by the pipeline
```

## Local development

```bash
uv sync
cd frontend && npm install && cd ..

uv run uvicorn arxivnu.api:app --reload        # API on :8000 (also serves frontend/dist if built)
cd frontend && npm run dev                      # Vite on :5173, proxies /api to :8000
```

Open http://127.0.0.1:5173. The database defaults to `./arxiv.db`.

Tests: `uv run pytest`.

## Daily pipeline

```bash
scripts/daily.sh
```

1. `arxiv-fetch` pulls today's papers, filters, enriches via InspireHEP, writes `pending.json`
2. `claude -p "/arxiv-summarize"` (Claude Code CLI) writes `results.json`
3. `arxiv-apply` writes summaries and tags to the DB

Backfill a date range: `uv run arxiv-backfill --from 2026-05-08 --to 2026-05-10 && scripts/daily.sh`.
Hide a paper for everyone: `uv run arxiv-exclude 2609.12345` (`--undo` to restore).
