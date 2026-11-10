#!/usr/bin/env python3
"""Merge the owner's MCP servers (~/coding-agent/.agents/mcp.json) into the Commons (~/.agents/mcp.json).

agent-sync can Source skills, commands and agents from a git repo, but not MCP servers (`adopt`
refuses mcp.json), so this keeps them in step instead (coding-agent Q1108). The names it added are
recorded in ~/.agents/.owner-mcp.json, so a server dropped from the owner file is removed again; a
server it did not add is never touched. Prints "changed" when it wrote. `--self-test` checks it.
"""
import json, os, sys, tempfile
from pathlib import Path


def merge(commons: dict, owner: dict, prev: list) -> tuple[dict, list]:
    servers = dict(commons.get("mcpServers", {}))
    for name in prev:
        if name not in owner:
            servers.pop(name, None)
    clash = [n for n in owner if n in servers and n not in prev]
    if clash:
        sys.exit(f"owner-mcp: {', '.join(clash)} already defined in the Commons by someone else")
    servers.update(owner)
    return {**commons, "mcpServers": servers}, sorted(owner)


def main(home: Path) -> None:
    src, dst, state = home / "coding-agent/.agents/mcp.json", home / ".agents/mcp.json", home / ".agents/.owner-mcp.json"
    owner = json.loads(src.read_text()).get("mcpServers", {}) if src.exists() else {}
    prev = json.loads(state.read_text()) if state.exists() else []
    if not owner and not prev:
        return
    commons = json.loads(dst.read_text()) if dst.exists() else {}
    new, names = merge(commons, owner, prev)
    if new != commons:
        dst.write_text(json.dumps(new, indent=2) + "\n")
        print("changed")
    state.write_text(json.dumps(names) + "\n")


if __name__ == "__main__":
    if sys.argv[1:] == ["--self-test"]:
        a, b, c = {"command": "a"}, {"command": "b"}, {"command": "c"}
        assert merge({"mcpServers": {"x": a}}, {"o": b}, []) == ({"mcpServers": {"x": a, "o": b}}, ["o"])
        assert merge({"mcpServers": {"x": a, "o": b}}, {}, ["o"]) == ({"mcpServers": {"x": a}}, [])  # dropped
        assert merge({"mcpServers": {"x": a, "o": b}}, {"o": c}, ["o"])[0]["mcpServers"]["o"] == c  # updated
        try:
            merge({"mcpServers": {"x": a}}, {"x": b}, []); raise AssertionError("clash must fail")
        except SystemExit:
            pass
        with tempfile.TemporaryDirectory() as t:  # no owner file and nothing added before: no write
            main(Path(t)); assert not os.listdir(t)
        print("ok")
    else:
        main(Path.home())
