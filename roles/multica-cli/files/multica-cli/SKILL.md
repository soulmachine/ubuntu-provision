---
name: multica-cli
description: Manage Multica resources (issues, agents, autopilots, skills, workspaces) and the local agent runtime daemon via the `multica` CLI. Use when the user runs `multica`, mentions Multica issues/agents/autopilots/skills/runtimes/workspaces, or needs to script Multica workflows.
---

# Multica CLI

Command-line interface for [Multica](https://multica.ai). Manage issues, assign agents, control the local daemon, and script everything that the web UI can do.

## Quick start

```bash
multica login                 # first-time auth (opens browser, saves PAT to ~/.multica/config.json)
multica auth status           # verify login + active workspace
multica daemon status         # daemon must be online for local-runtime agents
```

For scripting and parsing, always pass `--output json` — the default for `list` commands is `table` (human-readable).

## Common workflows

### Issues

```bash
multica issue list --status open --output json
multica issue get ABC-123                              # accepts issue key or UUID
multica issue create --title "..." --description "..." # decodes \n, \r, \t, \\
multica issue assign ABC-123 --to "agent-slug"         # triggers a task immediately
multica issue status ABC-123 --set done
multica issue comment add ABC-123 --body "..."
multica issue runs ABC-123                             # execution history
multica issue run-messages <task-id> --issue ABC-123   # follow an agent run's messages
multica issue rerun ABC-123                            # re-queue with current assignee
```

For multi-line descriptions or content with literal backslashes, prefer `--description-stdin`:

```bash
printf 'line 1\nline 2\n' | multica issue create --title "..." --description-stdin
```

### Agents and skills

```bash
multica agent list --output json
multica agent create --name "..." --runtime-id <id> --model claude-sonnet-4-6
multica agent skills attach <slug> --skill <skill-slug>
multica skill import --url https://github.com/org/repo   # also: clawhub.ai, skills.sh
```

Prefer `--model <id>` over passing `--model` inside `--custom-args` — some runtimes (codex app-server, openclaw) reject it there.

For secrets in `--custom-env`, use `--custom-env-stdin` or `--custom-env-file` (suggest mode `0600`). Inline values leak to shell history and `ps`.

### Autopilots (scheduled / triggered automations)

```bash
multica autopilot create --title "Daily triage" --agent <slug> --mode create_issue --description "..."
multica autopilot trigger-add <id> ...   # attach a schedule
multica autopilot trigger <id>           # run once now
multica autopilot runs <id>
```

Only `--mode create_issue` is fully supported end-to-end today; `run_only` is not.

### Daemon (local runtime)

```bash
multica daemon start            # background; add --foreground to attach
multica daemon status
multica daemon logs
multica daemon stop
```

If an assigned issue isn't being picked up, `multica daemon status` first — local-runtime agents won't run with the daemon offline.

## Global flags and env vars

| Flag | Env var | Purpose |
|------|---------|---------|
| `--workspace-id <id>` | `MULTICA_WORKSPACE_ID` | Override active workspace |
| `--server-url <url>` | `MULTICA_SERVER_URL` | Point at a non-default server (self-hosted) |
| `--profile <name>` | — | Isolated config/daemon/workspace set (e.g. `dev`) |
| `--output json` | — | Machine-readable output for `get`/`create`/`list` |

## Discover more

Every command supports `--help`:

```bash
multica issue create --help
multica agent update --help
```

See [REFERENCE.md](REFERENCE.md) for the full command tree, less-common subcommands (workspace admin, repo, attachment, config, runtime activity), and authentication notes.
