#!/usr/bin/env bash
# Daily pipeline: fetch → summarise (Claude Code CLI) → apply.
#
# Runs from the repo root (cwd matters: the /arxiv-summarize skill reads
# pending.json and writes results.json in the current directory, and Claude
# Code picks up .claude/ from here). Env:
#   ARXIV_DB                 database path (default: ./arxiv.db)
#   ARXIV_WORK               where pending.json / results.json live (default: repo root)
#   CLAUDE_CODE_OAUTH_TOKEN  from `claude setup-token`, for headless runs on the server
#   CLAUDE_MODEL             default claude-haiku-4-5-20251001
set -euo pipefail
cd "$(dirname "$0")/.."
export ARXIV_WORK="${ARXIV_WORK:-$PWD}"
MODEL="${CLAUDE_MODEL:-claude-haiku-4-5-20251001}"

# Wait for network (a laptop may run this right after wake; harmless on a server).
for i in $(seq 1 12); do
  curl -sf -m 5 -o /dev/null "https://rss.arxiv.org/rss/hep-ex" && break
  echo "No network yet (attempt $i/12); waiting 10s..."
  sleep 10
done

uv run arxiv-fetch

total=$(python3 -c "
import json, os
try:
    d = json.load(open(os.path.join(os.environ['ARXIV_WORK'], 'pending.json')))
    print(len(d.get('certain', [])) + len(d.get('ambiguous', [])))
except Exception:
    print(0)
")
if [ "$total" -eq 0 ]; then
  echo "No papers to process. Skipping Claude."
  exit 0
fi

# Run from the repo root so Claude Code finds .claude/commands/arxiv-summarize.md;
# the skill takes the work directory as its argument, and --add-dir lets it
# read/write there when ARXIV_WORK is outside the repo. File I/O only.
claude --model "$MODEL" --permission-mode acceptEdits --max-turns 5 \
  --add-dir "$ARXIV_WORK" -p "/arxiv-summarize $ARXIV_WORK"

uv run arxiv-apply
