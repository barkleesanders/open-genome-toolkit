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
#
# Worse, some hosts serve a misleading *404* to datacenter IPs. fda.gov does
# exactly this: all three FDA pages cited in references/pharmacogenomics.md
# return 404 to a CI runner and render fine in a browser (each verified by hand
# in a real browser on 2026-07-21 -- 33KB, 68KB, and 8KB of real content).
# Treating those as dead would mean removing correct citations, so they are
# listed below with the date a human last checked them. Re-verify periodically;
# this list is a promise, not a suppression.
set -uo pipefail

# host<TAB>date-last-verified-by-a-human-in-a-real-browser
MANUALLY_VERIFIED_HOSTS="www.fda.gov	2026-07-21"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Trailing markdown punctuation (**bold**, _em_, `code`, parens, commas) is part
# of the prose, not the URL. Strip it or every bolded link reports as dead.
urls=$(grep -rhoE 'https?://[A-Za-z0-9._~:/?#@!$&*+,;=%-]+' \
         README.md SKILL.md references/ 2>/dev/null \
       | sed -E 's/[*_`).,;:>]+$//' \
       | grep -viE 'example\.(com|org)' \
       | sort -u)

total=0; ok=0; blocked=0; dead=0; manual=0
declare -a dead_urls=() blocked_urls=() manual_urls=()

# Is this URL on a host known to serve misleading status codes to automation?
manually_verified() {
  local host; host=$(printf '%s' "$1" | sed -E 's#^https?://([^/]+).*#\1#')
  while IFS=$'\t' read -r h d; do
    [ -n "$h" ] || continue
    [ "$host" = "$h" ] && { printf '%s' "$d"; return 0; }
  done <<< "$MANUALLY_VERIFIED_HOSTS"
  return 1
}

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
    *)
      # A non-2xx from a host that lies to bots is not evidence the page is gone.
      if when=$(manually_verified "$url"); then
        manual=$((manual + 1)); manual_urls+=("$code  (hand-verified $when)  $url")
      else
        dead=$((dead + 1)); dead_urls+=("$code  $url")
      fi ;;
  esac
done <<< "$urls"

echo "checked $total URLs: $ok ok, $blocked bot-blocked/rate-limited, $manual hand-verified, $dead dead"

if [ "$manual" -gt 0 ]; then
  echo
  echo "Hosts that serve misleading codes to automation (verified by hand, re-check periodically):"
  printf '  %s\n' "${manual_urls[@]}"
fi

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
