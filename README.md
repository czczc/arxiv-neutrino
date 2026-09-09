# ArXiv Neutrino

Daily digest of neutrino-physics papers from arXiv (hep-ex, nucl-ex,
physics.ins-det, physics.data-an), filtered by keyword and InspireHEP metadata,
summarised and tagged by Claude, served as a small web app.

There is no login. Stars and read marks are stored in the visitor's browser
(localStorage) and can be exported/imported as JSON.

```
arxivnu/          Python package
  fetch.py        arXiv RSS/API + InspireHEP → DB + pending.json      (arxiv-fetch)
  apply.py        results.json → DB                                    (arxiv-apply)
  backfill.py     re-run fetch for a date range                        (arxiv-backfill)
  exclude.py      hide a paper for good; curation, server-side only    (arxiv-exclude)
  api.py          FastAPI: read-only /api/* + serves frontend/dist
  db.py           SQLite schema; ARXIV_DB / ARXIV_WORK env overrides
frontend/         Vite + Vue 3 SPA ("Triage Inbox": facets · list · reader)
scripts/          daily.sh (pipeline), deploy.sh (server), export_local_state.py
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
2. `claude -p "/arxiv-summarize"` (Claude Code CLI, Haiku) writes `results.json`
3. `arxiv-apply` writes summaries and tags to the DB

Backfill: `uv run arxiv-backfill --from 2026-05-08 --to 2026-05-10 && scripts/daily.sh`.
Exclude a paper: `uv run arxiv-exclude 2609.12345` (`--undo` to restore).

## Production

`arxivnu.api:app` under uvicorn on a loopback port behind a reverse proxy,
optionally under a URL sub-path (build the SPA with `VITE_BASE=/<prefix>/` and
start uvicorn with `--root-path /<prefix>`). `scripts/daily.sh` runs from a
systemd timer or cron; the Claude Code CLI authenticates headless with a
long-lived token from `claude setup-token` in `CLAUDE_CODE_OAUTH_TOKEN`.
Host-specific values go in `scripts/deploy.env` (gitignored), read by
`scripts/deploy.sh`. Environment variables: `ARXIV_DB`, `ARXIV_WORK`,
`CLAUDE_MODEL`.

## Moving your old read marks into the browser

The pre-0.2 app kept read/star state in the database. Export it once and use
the Import button in the app's left pane:

```bash
uv run python scripts/export_local_state.py > my-marks.json
```
