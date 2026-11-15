#!/usr/bin/env python3
"""Settle a Codex plugin's cache folder, then re-trust its hooks that Codex marks `modified`.

Usage: codex-plugin-retrust.py <plugin>@<marketplace> [--if-rebuilt]

--if-rebuilt is the watcher's fast path (tasks/retrust-watch.yml, coding-agent Q899): every Codex
session start touches the watched cache folder, and a rebuild always drops the `.npmrc` guard this
script writes, so a guard in every version folder means nothing changed since the last settle and
the script exits at once. A plugin without package.json never gets a guard, so it takes the full path.

`codex plugin marketplace upgrade` rebuilds ~/.codex/plugins/cache/<marketplace>/<plugin>/<version>
whenever upstream moves. That changes every hook's content hash, so Codex stops running the hooks
until they are trusted again, and for an npm plugin it drops the `.npmrc` guard: the plugin's
next dependency install writes node_modules/.bin symlinks, which Codex refuses to hash ("unsupported
plugin entry type"). Re-trusting automatically was Frank's call on 2026-10-29 (coding-agent Q759):
upstream changes to these plugins run without a review. A hook never trusted (`untrusted`) is left
alone, so the first review after an install stays manual.

Prints one line per change, then `changed` or `ok`.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys
import time

plugin = sys.argv[1]
name, market = plugin.split("@")
codex = shutil.which("codex") or sys.exit("codex not on PATH")
config = os.path.expanduser("~/.codex/config.toml")
changed = False
dirs = sorted(glob.glob(os.path.expanduser(f"~/.codex/plugins/cache/{market}/{name}/*/")))
if "--if-rebuilt" in sys.argv[2:] and all(os.path.exists(d + ".npmrc") for d in dirs):
    print("ok")
    sys.exit(0)

for d in dirs:
    if os.path.exists(d + "package.json") and not os.path.exists(d + ".npmrc"):
        with open(d + ".npmrc", "w") as f:
            f.write("bin-links=false\n")
        print(f"guard {d}")
        changed = True
    links = [os.path.join(r, f) for r, ds, fs in os.walk(d) for f in fs + ds if os.path.islink(os.path.join(r, f))]
    for link in links:
        os.unlink(link)
    if links:
        print(f"removed {len(links)} symlinks in {d}")
        changed = True


def hooks():
    p = subprocess.Popen([codex, "app-server"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.DEVNULL, text=True)

    def call(i, method, params):
        p.stdin.write(json.dumps({"jsonrpc": "2.0", "id": i, "method": method, "params": params}) + "\n")
        p.stdin.flush()
        for line in p.stdout:
            msg = json.loads(line)
            if msg.get("id") == i:
                return msg

    call(1, "initialize", {"clientInfo": {"name": "codex-plugin-retrust", "version": "1"}})
    p.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "initialized"}) + "\n")
    p.stdin.flush()
    r = call(2, "hooks/list", {})
    p.kill()
    return [h for d in r["result"]["data"] for h in d["hooks"] if h["key"].startswith(plugin + ":")]


todo = [h for h in hooks() if h["trustStatus"] == "modified"]
if todo:
    text = open(config).read()
    shutil.copy(config, f"{config}.bak-hooktrust-{time.strftime('%Y%m%d%H%M%S')}")
    for h in todo:
        parts = h["currentHash"].split("/")
        body = f'trusted_hash = "{parts[0]}"' + (f'\ntrusted_content_hash = "{parts[1]}"' if len(parts) > 1 else "")
        head = f'[hooks.state."{h["key"]}"]'
        pat = re.escape(head) + r'\n(?:trusted_hash = "[^"]*"\n?)?(?:trusted_content_hash = "[^"]*"\n?)?'
        if head in text:
            text = re.sub(pat, lambda _: head + "\n" + body + "\n", text, count=1)
        else:
            text = text.rstrip("\n") + f"\n\n{head}\n{body}\n"
        print(f"trust {h['key']}")
    open(config, "w").write(text)
    left = [h["key"] for h in hooks() if h["trustStatus"] == "modified"]
    assert not left, f"still modified after re-trust: {left}"
    changed = True

print("changed" if changed else "ok")
