#!/usr/bin/env python3
"""Remove the claude-mem wiring that `npx claude-mem uninstall` leaves behind.

The uninstaller never touches Gemini CLI (upstream dropped it), and it does nothing at all on a
host whose plugin is already gone, though Codex or opencode may still be wired there. This
covers both cases:

  * ~/.claude/settings.json         drop claude-mem's plugin, marketplace and permission entries
  * ~/.gemini/settings.json         drop each hook group that runs a claude-mem hook
  * GEMINI.md, opencode AGENTS.md   strip the <claude-mem-context> block; delete the file if
                                    nothing else is left (claude-mem wrote these files)
  * ~/.config/opencode/opencode.json  drop ./plugins/claude-mem.js from `plugin`
  * ~/.codex/*.toml                 drop every [table] whose header names claude-mem

Each edited file is copied to <file>.pre-claude-mem-removal first, once. Prints a JSON list of
the paths it changed, so the caller's gate is `stdout != "[]"`. `--self-test` runs the rules
on fixtures.
"""
import json
import os
import re
import shutil
import sys

HOME = os.path.expanduser("~")
BLOCK = re.compile(r"<claude-mem-context>.*?</claude-mem-context>", re.S)
HEADING = re.compile(r"^# Claude-Mem Memory Context\s*$", re.M)


def strip_markdown(text):
    """Return the text without claude-mem's block and heading, or None if nothing is left."""
    rest = HEADING.sub("", BLOCK.sub("", text))
    if not rest.strip():
        return None
    return re.sub(r"\n{3,}", "\n\n", rest).strip("\n") + "\n"


def strip_gemini_hooks(settings):
    hooks = settings.get("hooks", {})
    for event in list(hooks):
        groups = [g for g in hooks[event] if "claude-mem" not in json.dumps(g)]
        if groups:
            hooks[event] = groups
        else:
            del hooks[event]
    return settings


def strip_claude_settings(settings):
    for key in ("enabledPlugins", "extraKnownMarketplaces"):
        block = settings.get(key, {})
        for name in [n for n, v in block.items() if "claude-mem" in n + json.dumps(v)]:
            del block[name]
    for rule in ("allow", "ask", "deny"):
        rules = settings.get("permissions", {}).get(rule)
        if isinstance(rules, list):
            settings["permissions"][rule] = [r for r in rules if "claude-mem" not in r]
    return settings


def strip_opencode(config):
    if isinstance(config.get("plugin"), list):
        config["plugin"] = [p for p in config["plugin"] if "claude-mem" not in p]
    return config


def strip_toml(text):
    out, skip = [], False
    for line in text.splitlines(keepends=True):
        if re.match(r"^\s*\[", line):
            skip = "claude-mem" in line
        if not skip:
            out.append(line)
    return "".join(out)


def write(path, new, changed):
    backup = path + ".pre-claude-mem-removal"
    if not os.path.exists(backup):
        shutil.copy2(path, backup)
    if new is None:
        os.remove(path)
    else:
        with open(path, "w") as f:
            f.write(new)
    changed.append(path)


def run():
    changed = []

    def edit(path, fn):
        if not os.path.isfile(path):
            return
        with open(path) as f:
            old = f.read()
        if "claude-mem" not in old:
            return
        write(path, fn(old), changed)

    edit(f"{HOME}/.claude/settings.json",
         lambda t: json.dumps(strip_claude_settings(json.loads(t)), indent=2) + "\n")
    edit(f"{HOME}/.gemini/settings.json",
         lambda t: json.dumps(strip_gemini_hooks(json.loads(t)), indent=2) + "\n")
    edit(f"{HOME}/.config/opencode/opencode.json",
         lambda t: json.dumps(strip_opencode(json.loads(t)), indent=2) + "\n")
    for md in ("GEMINI.md", "GEMINI.md.claude-mem.bak"):
        edit(f"{HOME}/.gemini/{md}", strip_markdown)
    edit(f"{HOME}/.config/opencode/AGENTS.md", strip_markdown)
    for toml in ("config.toml", "cliproxy.config.toml"):
        edit(f"{HOME}/.codex/{toml}", strip_toml)
    print(json.dumps(changed))


def self_test():
    stub = "# Claude-Mem Memory Context\n\n<claude-mem-context>\n# Memory\n\nNo context yet.\n</claude-mem-context>\n"
    assert strip_markdown(stub) is None
    assert strip_markdown("# Mine\n\n" + stub) == "# Mine\n"
    hooks = {"hooks": {
        "AfterTool": [{"hooks": [{"name": "claude-mem", "command": "bun worker-service.cjs"}]},
                      {"hooks": [{"name": "context-mode", "command": "ctx"}]}],
        "Notification": [{"hooks": [{"name": "claude-mem", "command": "x"}]}]}}
    assert strip_gemini_hooks(hooks) == {"hooks": {"AfterTool": [{"hooks": [{"name": "context-mode", "command": "ctx"}]}]}}
    assert strip_opencode({"plugin": ["./plugins/claude-mem.js", "ponytail"]}) == {"plugin": ["ponytail"]}
    claude = {"enabledPlugins": {"claude-mem@thedotmack": True, "ponytail@ponytail": True},
              "extraKnownMarketplaces": {"thedotmack": {"source": {"repo": "thedotmack/claude-mem"}},
                                         "ponytail": {"source": {"repo": "a/ponytail"}}},
              "permissions": {"allow": ["mcp__plugin_claude-mem_mcp-search__search", "Bash(ls)"]}}
    assert strip_claude_settings(claude) == {
        "enabledPlugins": {"ponytail@ponytail": True},
        "extraKnownMarketplaces": {"ponytail": {"source": {"repo": "a/ponytail"}}},
        "permissions": {"allow": ["Bash(ls)"]}}
    toml = ('model = "x"\n[marketplaces.claude-mem-local]\nsource = "/p"\n\n'
            '[plugins."claude-mem@thedotmack"]\nenabled = false\n'
            '[hooks.state."claude-mem@claude-mem-local:hooks/codex-hooks.json:stop:0:0"]\ntrusted_hash = "s"\n\n'
            '[hooks.state."ponytail@ponytail:hooks/h.json:session_start:0:0"]\ntrusted_hash = "t"\n')
    assert strip_toml(toml) == 'model = "x"\n[hooks.state."ponytail@ponytail:hooks/h.json:session_start:0:0"]\ntrusted_hash = "t"\n'
    print("ok")


if __name__ == "__main__":
    self_test() if "--self-test" in sys.argv else run()
