#!/usr/bin/env python3
"""Remove context-mode from the agent JSON configs that list it, keeping each file's mode.

Prints one `changed <path>` line per file it rewrote, nothing for a clean host. The files
carry API keys, so it never prints their content.
"""
import json
import os
import sys

home = os.path.expanduser("~")
# (path, how context-mode is listed there)
TARGETS = [
    (f"{home}/.config/opencode/opencode.json", "plugin-list"),
    (f"{home}/.copilot/mcp-config.json", "mcp-server"),
    (f"{home}/.kimi-code/mcp.json", "mcp-server"),
]


def strip(data, kind):
    if kind == "plugin-list":
        plugins = data.get("plugin", [])
        if "context-mode" not in plugins:
            return False
        data["plugin"] = [p for p in plugins if p != "context-mode"]
        return True
    return data.get("mcpServers", {}).pop("context-mode", None) is not None


changed = False
for path, kind in TARGETS:
    if not os.path.exists(path):
        continue
    with open(path) as f:
        data = json.load(f)
    if not strip(data, kind):
        continue
    if "--check" in sys.argv[1:]:
        print(f"changed {path}")
        continue
    mode = os.stat(path).st_mode & 0o777
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    os.chmod(tmp, mode)
    os.replace(tmp, path)
    print(f"changed {path}")
