#!/usr/bin/env bash
# Deploy the latest main on the server: git pull, uv sync, npm build, restart.
#
# Host-specific values live in scripts/deploy.env (gitignored, sourced here):
#   ARXIV_REPO     checkout to update          (default: this repo)
#   ARXIV_SERVICE  systemd unit to restart     (default: arxiv-neutrino)
#   ARXIV_PORT     uvicorn port for /health    (default: 8000)
#   VITE_BASE      SPA base, trailing slash    (default: /); must match --root-path
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[[ -f "$SCRIPT_DIR/deploy.env" ]] && source "$SCRIPT_DIR/deploy.env"
REPO="${ARXIV_REPO:-$(cd "$SCRIPT_DIR/.." && pwd)}"
SERVICE="${ARXIV_SERVICE:-arxiv-neutrino}"
PORT="${ARXIV_PORT:-8000}"
cd "$REPO"

echo "==> git pull";      git pull --ff-only
echo "==> uv sync";       uv sync
echo "==> build SPA (base='${VITE_BASE:-/}')"
( cd frontend && npm ci --silent && npm run build )
echo "==> restart";       sudo systemctl restart "$SERVICE"
echo "==> waiting for /health"
for _ in $(seq 1 10); do
  curl -fsS http://127.0.0.1:$PORT/health >/dev/null 2>&1 && { echo "    OK"; break; }
  sleep 1
done
sudo systemctl status "$SERVICE" --no-pager | sed -n '1,8p'
