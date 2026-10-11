#!/bin/sh
# README's role table must list every role in main.yml, in the same order.
#
# Order is the load-bearing half. An unordered table is what let four rows that
# were not roles at all sit in it for months (DECISIONS Q102) — nothing could be
# checked against anything. Keeping the sequence identical to main.yml turns the
# table into a diff: a role added to the playbook and not to README shows up as
# one line here instead of as a silent omission.
#
# Note `sed -E` with [[:space:]] rather than \s — BSD/macOS sed does not
# understand \s, and fails open by not matching, which reads as "no roles found".
set -eu

cd "$(dirname "$0")/.."

order=$(mktemp) || exit 1
table=$(mktemp) || exit 1
trap 'rm -f "$order" "$table"' EXIT

# roles: block of main.yml, unwrapping `- role: x` as well as `- x`.
#
# Two exit rules, not one. `/^[^ ]/` ends the block at a top-level key, but `roles:` is
# itself indented, so a SIBLING key under the play — `post_tasks:`, `vars:`, `handlers:` —
# never matches it and the walk runs past the roles into that block and on to EOF. Today
# that is harmless only by luck: every line in main.yml's post_tasks fails the
# `^[a-z][a-z0-9-]*$` filter below. One post_task line that happened to render as a bare
# lowercase token would be read as a role name, and this check would then demand a README
# row for something that is not a role — pointing the blame at the table, which is correct.
# `/^  [a-z_]+:/` stops at the sibling key instead. Role entries are indented four spaces
# (`    - host-facts`), so they cannot match it.
awk '/^  roles:/ { f = 1; next } f && /^[^ ]/ { exit } f && /^  [a-z_]+:/ { exit } f' main.yml \
  | sed -E 's/^[[:space:]]*-[[:space:]]*(role:[[:space:]]*)?//' \
  | grep -E '^[a-z][a-z0-9-]*$' > "$order"

# first column of the role table
sed -n '/^| Role |/,/^$/p' README.md \
  | grep -E '^\| [a-z]' \
  | awk -F'|' '{ gsub(/ /, "", $2); print $2 }' > "$table"

if [ ! -s "$order" ]; then
  echo "could not parse the roles: block out of main.yml — check this script, not main.yml"
  exit 1
fi

if ! diff -u "$order" "$table" > /tmp/roles-diff.$$ 2>&1; then
  echo "README role table does not match main.yml (-main.yml +README):"
  sed -n '3,$p' /tmp/roles-diff.$$ | sed 's/^/  /'
  rm -f /tmp/roles-diff.$$
  exit 1
fi
rm -f /tmp/roles-diff.$$

# a row naming a directory that does not exist passes the diff only if main.yml
# names it too, which would be a broken playbook — but check anyway, cheaply.
missing=""
while read -r r; do
  [ -d "roles/$r" ] || missing="$missing $r"
done < "$table"
if [ -n "$missing" ]; then
  echo "README rows with no roles/ directory:$missing"
  exit 1
fi

echo "README role table: $(wc -l < "$table" | tr -d ' ') roles, order matches main.yml"
