#!/usr/bin/env python3
"""Report skill-store directories the `skills` role will never refresh again.

`skills add` never deletes, so a skill that leaves the role's reach keeps its store
directory forever: it accumulates, and it diverges hosts. Reads a JSON config on stdin:

    {"store": "...", "lock": "...", "whole": [...], "partial": [{"source":..,"skills":[..]}]}

Prints nothing when there is nothing to report, so the caller's gate is `stdout != ""`.

Three reasons a directory qualifies, one per kind of source. They are kept apart on
purpose — the timestamp test is only sound for a source installed with `--all`:

  * source in neither list           — dropped from the role, or hand-installed and never in
                                       it. Either way nothing refreshes it now.
  * whole source (`--all`)           — `skills add` stamps `updatedAt` on every skill the
                                       source currently ships, so an entry left behind at
                                       an older stamp is one upstream no longer ships.
                                       Compared with a tolerance, never for equality: one
                                       run writes a source's skills milliseconds apart
                                       (mattpocock's 37, measured 2026-09-16: .511Z to
                                       .523Z), so an exact test calls every skill but the
                                       last-written one stale. A real orphan is months
                                       away, so the window below separates them with a
                                       margin of four orders of magnitude.
  * partial source (`--skill`)       — only the named skills are fetched, so the timestamp
                                       test would flag every unnamed sibling. The reference
                                       is the configured name list instead. A *named* skill
                                       that upstream withdrew is not reported here: the
                                       role's own install task already fails loudly on it.

Only real directories count. An `~/.agents/skills` entry that is a symlink belongs to
agentstow (authored in ~/github.com/soulmachine/skills), and one that is missing entirely
was already deleted — Q88 removed 28 of those while leaving their lock entries behind, so
without this test they would be reported on every host forever.
"""
import json
import os
import sys
from collections import defaultdict
from datetime import datetime

# How far below its source's newest stamp an entry may sit and still count as refreshed by
# the same run. The whole 14-source run writes its 111 entries in 61s, and one source's
# skills land within a few milliseconds of each other, so this is ~5x the entire run and
# ~25000x the per-source write. It only has to span one source's write — two runs minutes
# apart are fine, because the later one re-stamps every live skill and leaves orphans put.
SAME_RUN_SECONDS = 300


def _parse(stamp):
    """`2026-09-16T14:42:11.523Z`, with or without the fractional part."""
    stamp = stamp.rstrip("Z")
    fmt = "%Y-%m-%dT%H:%M:%S.%f" if "." in stamp else "%Y-%m-%dT%H:%M:%S"
    return datetime.strptime(stamp, fmt)


def find_orphans(skills, store, whole, partial, isdir):
    """skills: {name: {source, updatedAt}}. isdir(name) -> is it a real store directory.

    Returns [(source, name, reason)] sorted by source then name.
    """
    # A pin may name a subpath (`owner/repo/plugin`), which the lock still records as plain
    # `owner/repo`, and two pins may share one repo, so key by repo and merge their names.
    wanted = defaultdict(set)
    for p in partial:
        wanted["/".join(p["source"].split("/")[:2])] |= set(p["skills"])
    whole = set(whole)

    by_source = defaultdict(dict)
    for name, meta in skills.items():
        by_source[meta.get("source") or "?"][name] = _parse(meta["updatedAt"])

    out = []
    for source, entries in by_source.items():
        if source in wanted:
            flagged = [(n, "no longer requested") for n in entries if n not in wanted[source]]
        elif source in whole:
            newest = max(entries.values())
            flagged = [(n, "upstream no longer ships it") for n, u in entries.items()
                       if (newest - u).total_seconds() > SAME_RUN_SECONDS]
        else:
            flagged = [(n, "no source in this role installs it") for n in entries]
        out += [(source, n, why) for n, why in flagged if isdir(n)]
    return sorted(out)


def main():
    cfg = json.load(sys.stdin)
    store = os.path.expanduser(cfg["store"])

    def isdir(name):
        p = os.path.join(store, name)
        return os.path.isdir(p) and not os.path.islink(p)

    try:
        skills = json.load(open(os.path.expanduser(cfg["lock"])))["skills"]
    except (OSError, ValueError, KeyError):
        return 0  # no lock yet, or unreadable: nothing to say, and not this task's business

    orphans = find_orphans(skills, store, cfg["whole"], cfg["partial"], isdir)
    if not orphans:
        return 0

    print("%d store director%s the role no longer refreshes:"
          % (len(orphans), "y" if len(orphans) == 1 else "ies"))
    for source, name, why in orphans:
        print("  %-34s %-28s %s" % (source, name, why))
    print("Delete one with `rm -rf %s/<name>` and `agentstow sync`; this role never will."
          % cfg["store"])
    return 0


def self_test():
    old = "2026-07-17T11:51:16.555Z"
    # Three stamps from one run, milliseconds apart — the shape that made an exact
    # `u < max(...)` test report 43 of mattpocock's 45 skills as orphans.
    new, new_ms, newest = ("2026-09-16T14:42:11.511Z", "2026-09-16T14:42:11.517Z",
                           "2026-09-16T14:42:11.523Z")
    skills = {
        "kept":     {"source": "o/whole",   "updatedAt": new},
        "kept_ms":  {"source": "o/whole",   "updatedAt": new_ms},
        "kept_max": {"source": "o/whole",   "updatedAt": newest},
        "dropped":  {"source": "o/whole",   "updatedAt": old},
        "deleted":  {"source": "o/whole",   "updatedAt": old},  # stale but not on disk
        "linked":   {"source": "o/whole",   "updatedAt": old},  # stale but an agentstow link
        "asked":    {"source": "o/partial", "updatedAt": newest},
        "unasked":  {"source": "o/partial", "updatedAt": old},
        "sibling":  {"source": "o/partial", "updatedAt": newest},  # fresh, still unrequested
        "gone":     {"source": "o/retired", "updatedAt": newest},  # fresh, but source dropped
        "skipped1": {"source": "o/skipped", "updatedAt": old},  # whole source, wholly stale
        "skipped2": {"source": "o/skipped", "updatedAt": old},
        "nofrac":   {"source": "o/plain",   "updatedAt": "2026-09-16T14:42:11"},
        # Two subpath pins into one repo; the lock records both under the bare repo.
        "sub_a":    {"source": "o/split",   "updatedAt": newest},
        "sub_b":    {"source": "o/split",   "updatedAt": newest},
        "sub_c":    {"source": "o/split",   "updatedAt": newest},
    }
    on_disk = set(skills) - {"deleted", "linked"}
    got = find_orphans(skills, "/store", ["o/whole", "o/skipped", "o/plain"],
                       [{"source": "o/partial", "skills": ["asked"]},
                        {"source": "o/split/a", "skills": ["sub_a"]},
                        {"source": "o/split/b", "skills": ["sub_b"]}], lambda n: n in on_disk)

    assert got == [
        ("o/partial", "sibling", "no longer requested"),
        ("o/partial", "unasked", "no longer requested"),
        ("o/retired", "gone",    "no source in this role installs it"),
        ("o/split",   "sub_c",   "no longer requested"),
        ("o/whole",   "dropped", "upstream no longer ships it"),
    ], got
    # Two properties that make this safe to run unattended, asserted rather than assumed:
    # same-run siblings milliseconds apart are never flagged, and a source that failed or
    # was rate-limited has every entry at the same older stamp, so it yields nothing at all.
    assert not [o for o in got if o[1].startswith("kept")]
    assert not [o for o in got if o[0] == "o/skipped"]
    print("self-test OK")


if __name__ == "__main__":
    sys.exit(self_test() if "--self-test" in sys.argv else main())
