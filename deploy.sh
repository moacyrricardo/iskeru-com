#!/usr/bin/env bash
# Build the static site and ship it to a remote folder over SSH.
#
# Parametrized by environment variables:
#   ISKERU_SSH   user@host of the target box (or an ~/.ssh/config host)   [required]
#   ISKERU_PATH  destination folder on the box (the web root)             [required]
#
# Example:
#   ISKERU_SSH=ubuntu@1.2.3.4 ISKERU_PATH=/var/www/iskeru ./deploy.sh
#
# Note: iskeru.com may be proxied by Cloudflare, so ISKERU_SSH must be the box's
# real address (or an ssh-config host alias), not the public domain.
set -euo pipefail
cd "$(dirname "$0")"

SSH_TARGET="${ISKERU_SSH:?set ISKERU_SSH=user@host (the real IP of the box or an ssh-config host)}"
DEST="${ISKERU_PATH:?set ISKERU_PATH=/var/www/iskeru (the web root folder on the box)}"

# 1. Build the site fresh into dist/.
python3 build.py

# 2. Ship dist/ into the remote web root.
#    rsync mirrors the folder (--delete removes files deleted from the build);
#    falls back to scp where rsync isn't available (stale files are NOT pruned then).
if command -v rsync >/dev/null 2>&1; then
  rsync -az --delete dist/ "$SSH_TARGET:$DEST/"
else
  echo "rsync not found — using scp (stale remote files won't be removed)."
  scp -r dist/. "$SSH_TARGET:$DEST/"
fi

echo "Deployed iskeru.com to $SSH_TARGET:$DEST"
