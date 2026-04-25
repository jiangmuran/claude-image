#!/usr/bin/env bash
# Install the gpt-image-2 skill into ~/.claude/skills/ and (optionally) set
# credentials. Idempotent: re-running just refreshes things.

set -euo pipefail

SKILL_NAME="gpt-image-2"
TARGET="${HOME}/.claude/skills/${SKILL_NAME}"
SOURCE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

color() { printf "\033[%sm%s\033[0m\n" "$1" "$2"; }
green() { color "32" "$1"; }
yellow() { color "33" "$1"; }
red() { color "31" "$1"; }

green "→ Installing ${SKILL_NAME} skill"

# 1. Place the skill where Claude Code looks for it.
mkdir -p "$(dirname "$TARGET")"
if [[ "$SOURCE" == "$TARGET" ]]; then
  green "  Skill is already at $TARGET"
elif [[ -e "$TARGET" ]]; then
  if [[ -L "$TARGET" ]]; then
    yellow "  Replacing existing symlink at $TARGET"
    rm "$TARGET"
    ln -s "$SOURCE" "$TARGET"
  else
    yellow "  $TARGET exists. Backing up to $TARGET.bak.$(date +%s)"
    mv "$TARGET" "$TARGET.bak.$(date +%s)"
    ln -s "$SOURCE" "$TARGET"
    green "  Symlinked $SOURCE → $TARGET"
  fi
else
  ln -s "$SOURCE" "$TARGET"
  green "  Symlinked $SOURCE → $TARGET"
fi

# 2. Make the script executable.
chmod +x "$TARGET/scripts/gpt_image.py"
green "  Marked scripts/gpt_image.py executable"

# 3. Check Python.
if ! command -v python3 >/dev/null 2>&1; then
  red "  python3 not found in PATH — install Python 3.7+ before using the script."
  exit 1
fi
green "  python3: $(python3 --version)"

# 4. Credentials.
SHELL_RC=""
case "${SHELL:-}" in
  */zsh)  SHELL_RC="${HOME}/.zshrc" ;;
  */bash) SHELL_RC="${HOME}/.bashrc" ;;
esac

if [[ -n "${OPENAI_IMAGE_API_KEY:-}" ]]; then
  green "  OPENAI_IMAGE_API_KEY is already set in this shell"
else
  yellow ""
  yellow "  Credentials are not set. The script needs:"
  yellow "    OPENAI_IMAGE_API_KEY (required)"
  yellow "    OPENAI_IMAGE_BASE_URL (optional, default https://jmrai.net/v1)"
  yellow ""
  read -r -p "  Paste your API key now (or press enter to skip): " api_key
  if [[ -n "$api_key" ]]; then
    read -r -p "  Base URL (default https://jmrai.net/v1): " base_url
    base_url="${base_url:-https://jmrai.net/v1}"
    if [[ -n "$SHELL_RC" ]]; then
      {
        echo ""
        echo "# gpt-image-2 skill — added by install.sh on $(date '+%Y-%m-%d')"
        echo "export OPENAI_IMAGE_API_KEY=\"$api_key\""
        echo "export OPENAI_IMAGE_BASE_URL=\"$base_url\""
      } >> "$SHELL_RC"
      green "  Added exports to $SHELL_RC"
      yellow "  Run:  source $SHELL_RC   (or open a new shell) to load them."
    else
      yellow "  Couldn't detect zsh/bash rc. Add these to your shell rc manually:"
      echo "    export OPENAI_IMAGE_API_KEY=\"$api_key\""
      echo "    export OPENAI_IMAGE_BASE_URL=\"$base_url\""
    fi
  else
    yellow "  Skipped. Set OPENAI_IMAGE_API_KEY before using the script."
  fi
fi

# 5. Smoke-test option.
echo ""
read -r -p "Run a smoke test now? (generate a tiny image) [y/N] " yn
if [[ "${yn:-}" =~ ^[yY]$ ]]; then
  if [[ -z "${OPENAI_IMAGE_API_KEY:-}" ]]; then
    red "  OPENAI_IMAGE_API_KEY not set in this shell. Skipping."
  else
    OUT="${TMPDIR:-/tmp}/gpt-image-smoke-$(date +%s).png"
    green "  → generating $OUT"
    if python3 "$TARGET/scripts/gpt_image.py" generate \
        -p "a tiny red panda holding a bamboo leaf, flat vector illustration, plain background" \
        --size 1024x1024 -o "$OUT"; then
      green "  Smoke test OK. View: open \"$OUT\""
    else
      red "  Smoke test failed. Check API key and base URL."
    fi
  fi
fi

green ""
green "Done."
green "Claude will discover the skill next time it sees an image task."
green "Manual use:"
green "  python3 $TARGET/scripts/gpt_image.py generate -p \"...\" -o ./pic.png"
