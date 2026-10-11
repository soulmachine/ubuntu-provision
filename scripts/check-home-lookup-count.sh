#!/bin/sh
# AGENTS.md states how many places the roles read `lookup('env', 'HOME')`, because that
# count is the whole argument for "never fan this playbook out" — Ansible resolves every
# lookup() on the control node, so each one is a place another host's $HOME would leak in.
#
# The number drifts the moment a role gains or loses a lookup, and it has: it was
# corrected to 87 on 2026-09-15 and was wrong again hours later, when a fix to the hermes
# role added two `chdir: "{{ lookup('env', 'HOME') }}/..."` lines. A doc claim nobody can
# check is a doc claim that rots, so check it.
#
# Deliberately checks ONE number. AGENTS.md used to carry a second ("convert all 79
# lookups"), fourteen lines below the first and disagreeing with it; that one was reworded
# to carry no figure at all rather than be kept in sync.
set -eu
cd "$(dirname "$0")/.."

# The literal being counted, e.g. lookup('env', 'HOME') — tolerant of quote style and
# spacing so a reformat does not silently drop matches.
# The parens MUST be escaped: unescaped, ERE reads them as a group and the pattern
# silently matches nothing, which reads as "0 lookups" rather than as an error.
pattern="lookup\\([[:space:]]*['\"]env['\"][[:space:]]*,[[:space:]]*['\"]HOME['\"][[:space:]]*\\)"

actual_places=$(grep -rhoE "$pattern" roles/ | wc -l | tr -d ' ')
actual_roles=$(grep -rlE "$pattern" roles/ | sed 's|^roles/||; s|/.*||' | sort -u | wc -l | tr -d ' ')

# "... in N places across M roles". Matched on the phrase alone rather than on the
# backticked `lookup('env', 'HOME')` that precedes it — quoting and backticks make that
# prefix fiddly to match portably, and the phrase is unique in the file anyway.
stated=$(grep -oE 'in [0-9]+ places across [0-9]+ roles' AGENTS.md || true)
if [ "$(printf '%s\n' "$stated" | grep -c .)" != "1" ]; then
  echo "check-home-lookup-count: expected exactly one claim in AGENTS.md, found this:" >&2
  printf '%s\n' "$stated" >&2
  echo "  Expected prose of the form: ... in N places across M roles" >&2
  exit 1
fi

stated_places=$(printf '%s\n' "$stated" | grep -oE 'in [0-9]+ places' | grep -oE '[0-9]+')
stated_roles=$(printf '%s\n' "$stated" | grep -oE 'across [0-9]+ roles' | grep -oE '[0-9]+')

rc=0
if [ "$stated_places" != "$actual_places" ]; then
  echo "check-home-lookup-count: AGENTS.md says $stated_places places, found $actual_places" >&2
  rc=1
fi
if [ "$stated_roles" != "$actual_roles" ]; then
  echo "check-home-lookup-count: AGENTS.md says $stated_roles roles, found $actual_roles" >&2
  rc=1
fi

# The claim is only meaningful while the alternative really is unused.
env_home=$(grep -rE 'ansible_env\.HOME' roles/ main.yml | wc -l | tr -d ' ')
if [ "$env_home" != "0" ]; then
  echo "check-home-lookup-count: AGENTS.md claims zero uses of ansible_env.HOME, found $env_home" >&2
  rc=1
fi

if [ "$rc" -ne 0 ]; then
  echo "  Update the sentence in AGENTS.md (\"Runs per-host only\") to match." >&2
  exit 1
fi

echo "lookup('env', 'HOME'): $actual_places places across $actual_roles roles — matches AGENTS.md"
