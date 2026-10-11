#!/bin/sh
# Every `## Q<n>` in DECISIONS.md must equal its own 1-based position among ALL
# `##` entries. A gap or duplicate is not cosmetic: `Supersedes:` lines and prose
# cite entries BY NUMBER, so a broken sequence silently redirects every later
# citation at a different decision.
#
# "All entries" spans both forms on purpose — this journal predates Q-numbering,
# so its first entries are timestamps. A file whose 4th entry is the first `## Q4`
# is correct, not broken, because the count includes the timestamped ones.
set -eu

cd "$(dirname "$0")/.."

awk '
  /^## / {
    i++
    if ($2 ~ /^Q[0-9]+$/) {
      n = substr($2, 2) + 0
      if (n != i) {
        printf "  line %d: %s is entry #%d — expected Q%d\n", NR, $2, i, i
        bad++
      }
    }
  }
  END {
    if (bad) {
      printf "DECISIONS.md: %d entries, %d numbering break(s)\n", i, bad
      print  "Renumber FORWARD only, and update every Supersedes: / prose citation"
      print  "that names a number you move — the numbers are addresses."
      exit 1
    }
    printf "DECISIONS.md: %d entries, numbering continuous\n", i
  }
' DECISIONS.md
