#!/bin/bash
# Create or refresh HTML symlinks so that webapp/public points to the authoritative
# copies stored in webapi/wwwroot.

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
WEBAPP_DIR="$ROOT_DIR/webapp/public"
WEBAPI_DIR="$ROOT_DIR/webapi/wwwroot"
# Optional build directory (may not exist in dev environment)
WEBAPP_BUILD_DIR="$ROOT_DIR/webapp/build"

SYMLINKS=(
  "control-panel.html"
  "applications.html"
  "index.html"
)

for file in "${SYMLINKS[@]}"; do
  src="$WEBAPI_DIR/$file"
  dest="$WEBAPP_DIR/$file"

  # Ensure source exists
  if [[ ! -f "$src" ]]; then
    echo "[WARN] Source $src does not exist – skipping"
    continue
  fi

  # Skip if regular file exists (don't override real files)
  if [[ -e "$dest" && ! -L "$dest" ]]; then
    echo "[SKIP] $dest exists as regular file - not overriding"
    continue
  fi

  # Create/refresh symlink
  ln -sf "../../webapi/wwwroot/$file" "$dest"
  echo "[OK] $dest → ../../webapi/wwwroot/$file"
 done

# --- Duplicate links in webapp/build if directory exists (keeps Docker webapp nginx in sync) ---

if [[ -d "$WEBAPP_BUILD_DIR" ]]; then
  for file in "${SYMLINKS[@]}"; do
    src="$WEBAPI_DIR/$file"
    dest="$WEBAPP_BUILD_DIR/$file"

    if [[ ! -f "$src" ]]; then
      continue
    fi

    if [[ -e "$dest" && ! -L "$dest" ]]; then
      rm -f "$dest"
    fi

    ln -sf "../webapi/wwwroot/$file" "$dest"
    echo "[OK] $dest → ../webapi/wwwroot/$file"
  done
fi

echo "Symlink refresh complete." 