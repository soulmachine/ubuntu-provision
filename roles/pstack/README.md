# pstack

Installs [pstack](https://github.com/cursor/plugins/tree/main/pstack), Cursor's skill pack, and
pins its per-role models.

## Claude Code

The role adds the `cursor-plugins` marketplace (`cursor/plugins`), installs
`pstack@cursor-plugins`, updates it on every run, and enables it once. Claude Code prefixes plugin
commands, so pstack's commands run as `/pstack:<name>`, such as `/pstack:setup-pstack`.

## Cursor

Cursor has no headless plugin install. Its CLI (checked up to v2026.11.19) has only
`agent plugin marketplace add|list|update|remove`. A marketplace install is stored on the Cursor
account, and each machine caches it at startup. So type this once, in the Cursor IDE or
`cursor-agent` on any host:

```
/add-plugin pstack
```

The role does not install Cursor. On a host with `~/.cursor` it deploys only the model rule.

## Model rules

The role owns two files and overwrites them on every run that finds a difference:

| Agent | File | Source |
|---|---|---|
| Claude Code | `~/.claude/rules/pstack-models.md` | `files/claude/pstack-models.md` |
| Cursor | `~/.cursor/rules/pstack-models.mdc` | `files/cursor/pstack-models.mdc` |

Both use budget `large (xhigh)` with `setup-pstack`'s defaults. Claude Code uses the mapping from
pstack's `docs/harness/claude-code.md`, where Gemini becomes `inherit-parent`. If you run
`/pstack:setup-pstack` on a host, the next provision run reverts the result. To change a model,
edit the file here and keep both files on the same budget.
