#!/usr/bin/env python3
"""Remove context-mode from the agent configs that list it, keeping each file's mode.

The JSON configs name its plugin or MCP server. Codex's config.toml keeps a
`[hooks.state."context-mode@context-mode:..."]` trust section per hook after the plugin is gone.

Prints one `changed <path>` line per file it rewrote, nothing for a clean host. The files
carry API keys, so it never prints their content.
"""
import json
import os
import re
import sys

home = os.path.expanduser("~")
# (path, how context-mode is listed there)
TARGETS = [
    (f"{home}/.config/opencode/opencode.json", "plugin-list"),
    (f"{home}/.copilot/mcp-config.json", "mcp-server"),
    (f"{home}/.kimi-code/mcp.json", "mcp-server"),
    (f"{home}/.codex/config.toml", "codex-trust"),
]
# A trust section's header and every line up to the next header, its trailing blank line included.
CODEX_TRUST = re.compile(r'^\[hooks\.state\."context-mode@context-mode:[^\n]*\]\n(?:(?!\[)[^\n]*\n)*', re.M)


def strip(data, kind):
    if kind == "codex-trust":
        text = CODEX_TRUST.sub("", data)
        return text if text != data else None
    if kind == "plugin-list":
        plugins = data.get("plugin", [])
        if "context-mode" not in plugins:
            return None
        data["plugin"] = [p for p in plugins if p != "context-mode"]
        return data
    return data if data.get("mcpServers", {}).pop("context-mode", None) is not None else None


for path, kind in TARGETS:
    if not os.path.exists(path):
        continue
    with open(path) as f:
        data = f.read() if kind == "codex-trust" else json.load(f)
    data = strip(data, kind)
    if data is None:
        continue
    if "--check" in sys.argv[1:]:
        print(f"changed {path}")
        continue
    mode = os.stat(path).st_mode & 0o777
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        if kind == "codex-trust":
            f.write(data)
        else:
            json.dump(data, f, indent=2)
            f.write("\n")
    os.chmod(tmp, mode)
    os.replace(tmp, path)
    print(f"changed {path}")
