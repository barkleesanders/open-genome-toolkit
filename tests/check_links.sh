#!/usr/bin/env bash
# Verify every external URL in the docs still resolves.
#
# A directory of "where to get affordable testing" is worthless if half the
# links 404. Programs in this space shut down constantly, so this is the
# maintenance signal: run it, and fix or annotate whatever it reports.
#
# Note: 403 from a .gov or lab site usually means the CI runner's IP is
# bot-blocked, not that the page is gone. Those are reported separately from
# real 404s and do not fail the run.
set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Trailing markdown punctuation (**bold**, _em_, `code`, parens, commas) is part
# of the prose, not the URL. Strip it or every bolded link reports as dead.
urls=$(grep -rhoE 'https?://[A-Za-z0-9._~:/?#@!$&*+,;=%-]+' \
         README.md SKILL.md references/ 2>/dev/null \
       | sed -E 's/[*_`).,;:>]+$//' \
       | grep -viE 'example\.(com|org)' \
       | sort -u)

total=0; ok=0; blocked=0; dead=0
declare -a dead_urls=() blocked_urls=()

while IFS= read -r url; do
  [ -z "$url" ] && continue
  total=$((total + 1))
  code=$(curl -sS -o /dev/null -w '%{http_code}' -L --max-time 20 \
           -A 'Mozilla/5.0 (compatible; open-genome-toolkit link check)' \
           "$url" 2>/dev/null || echo "000")
  case "$code" in
    2*|3*)   ok=$((ok + 1)) ;;
    401|403|429|000)
             blocked=$((blocked + 1)); blocked_urls+=("$code  $url") ;;
    *)       dead=$((dead + 1));    dead_urls+=("$code  $url") ;;
  esac
done <<< "$urls"

echo "checked $total URLs: $ok ok, $blocked bot-blocked/rate-limited, $dead dead"

if [ "$blocked" -gt 0 ]; then
  echo
  echo "Bot-blocked or rate-limited (verify by hand in a browser):"
  printf '  %s\n' "${blocked_urls[@]}"
fi

if [ "$dead" -gt 0 ]; then
  echo
  echo "DEAD LINKS -- fix or remove these:"
  printf '  %s\n' "${dead_urls[@]}"
  exit 1
fi
