# Multica CLI — Full reference

Authoritative one-line reference for every top-level command. For flag-level detail, run `multica <command> <subcommand> --help`.

## Authentication and setup

| Command | Purpose |
|---------|---------|
| `multica login` | Browser-based auth; saves a PAT (`mul_…`) to `~/.multica/config.json` |
| `multica login --token mul_...` | Non-interactive auth with an existing PAT |
| `multica auth status` | Show current login, user, workspace |
| `multica auth logout` | Clear the local PAT |
| `multica setup cloud` | One-shot Multica Cloud setup (login + install daemon) |
| `multica setup self-host` | One-shot self-hosted setup |
| `multica config show` | Print local CLI config |
| `multica config set <key> <value>` | Edit a config value |

Token types are documented at https://multica.ai/docs/auth-tokens (PAT vs. JWT vs. daemon token).

## Workspaces and members

| Command | Purpose |
|---------|---------|
| `multica workspace list` | List accessible workspaces |
| `multica workspace get <slug>` | Show one workspace |
| `multica workspace members` | List members of the current workspace |
| `multica workspace update <id> --name "..." [--description "..."] [--context "..."] [--issue-prefix "..."]` | Admin/owner only. Long fields accept `--description-stdin` / `--context-stdin`. |

## Issues

| Command | Purpose |
|---------|---------|
| `multica issue list` | Filterable by `--status`, `--priority`, `--project`, `--assignee[-id]`. Defaults: limit 50, `--output table`. |
| `multica issue get <id>` | Accepts issue key (e.g. `ABC-123`) or UUID. |
| `multica issue create --title "..."` | Title required. See description-handling notes below. |
| `multica issue update <id> ...` | Update status, priority, assignee, etc. |
| `multica issue assign <id> --to <name>` | Member or agent (fuzzy match). Use `--to-id <uuid>` for exact. `--unassign` to clear. Triggers a task immediately for agents. |
| `multica issue status <id> --set <status>` | Shortcut to change status. |
| `multica issue search <query>` | Keyword search. |
| `multica issue runs <id>` | List task executions for the issue. |
| `multica issue run-messages <task-id> --issue <id>` | Stream messages from a run; `--since <seq>` for incremental polling. |
| `multica issue rerun <id>` | Re-enqueue a fresh task for the current agent assignee. |
| `multica issue comment add/list/delete <id>` | Manage comments. |
| `multica issue subscriber <id> ...` | Subscribe / unsubscribe. |
| `multica issue label <id> ...` | Add / remove labels. |

### Issue create flags (key ones)

| Flag | Notes |
|------|-------|
| `--title` | Required. |
| `--description` | Decodes `\n`, `\r`, `\t`, `\\`. |
| `--description-stdin` | Read description verbatim from stdin — use for multi-line or literal backslashes. |
| `--assignee` / `--assignee-id` | Mutually exclusive. |
| `--priority` | none / low / medium / high / urgent. |
| `--status` | Initial status. |
| `--parent` | Parent issue ID. |
| `--project` | Project ID. |
| `--due-date` | RFC 3339. |
| `--attachment <path>` | Repeatable. |

## Projects

| Command | Purpose |
|---------|---------|
| `multica project list/get/create/update/delete` | CRUD. |
| `multica project status` | Project status info. |

## Agents

| Command | Purpose |
|---------|---------|
| `multica agent list` | List workspace agents. |
| `multica agent get <slug>` | Show agent config. |
| `multica agent create ...` | Create. `--name` and `--runtime-id` required. |
| `multica agent update <slug> ...` | Update. |
| `multica agent archive <slug>` / `restore <slug>` | Archive lifecycle. |
| `multica agent avatar <slug> --file <path>` | Upload avatar image. |
| `multica agent tasks <slug>` | Task history. |
| `multica agent skills attach/detach <agent-slug> --skill <slug>` | Manage skills. |

### Agent create flags (key ones)

| Flag | Notes |
|------|-------|
| `--name` | Required. |
| `--runtime-id` | Required. |
| `--model` | Preferred over passing `--model` in `--custom-args`. |
| `--instructions` | System prompt / instructions. |
| `--custom-args` | JSON array of extra CLI args. |
| `--custom-env` | JSON object of env vars. **Avoid for secrets** — leaks to shell history / `ps`. |
| `--custom-env-stdin` | Read env JSON from stdin (safer). |
| `--custom-env-file <path>` | Read env JSON from a file (suggest `0600`). |
| `--runtime-config` | Runtime-specific JSON. |
| `--max-concurrent-tasks` | Default 6. |
| `--visibility` | `private` (default) or `workspace`. |

## Skills

| Command | Purpose |
|---------|---------|
| `multica skill list/get/create/update/delete` | CRUD. |
| `multica skill import --url <url>` | Import from `clawhub.ai`, `skills.sh`, or `github.com`. |
| `multica skill files list/add/update/delete` | Manage a skill's files. |

## Autopilots

| Command | Purpose |
|---------|---------|
| `multica autopilot list` | List. |
| `multica autopilot get <id>` | Show one (includes triggers). |
| `multica autopilot create --title --agent --mode create_issue --description ...` | Create. Only `create_issue` mode is fully supported. |
| `multica autopilot update <id> ...` | Update. |
| `multica autopilot delete <id>` | Delete. |
| `multica autopilot runs <id>` | Run history. |
| `multica autopilot trigger <id>` | Run once now. |
| `multica autopilot trigger-add/update/delete` | Manage schedule triggers. |

## Daemon and runtimes

| Command | Purpose |
|---------|---------|
| `multica daemon start` | Background by default; `--foreground` for attached. |
| `multica daemon stop` / `restart` | Lifecycle. |
| `multica daemon status` | Online state + concurrency. |
| `multica daemon logs` | Tail logs. |
| `multica daemon disk-usage` | Workspace disk usage by task or workspace. |
| `multica runtime list` | Runtimes in current workspace. |
| `multica runtime usage` | Resource usage. |
| `multica runtime activity` | Recent activity log. |
| `multica runtime update <id> ...` | Update a runtime's configuration. |

## Miscellaneous

| Command | Purpose |
|---------|---------|
| `multica repo checkout <url>` | Clone a repo locally for agents to use. |
| `multica attachment download <id>` | Download an attachment by ID. |
| `multica label ...` | Manage workspace-wide issue labels. |
| `multica version` | Print CLI version. |
| `multica update` | Self-upgrade to the latest release. |

## Global flags

| Flag | Env var | Default | Notes |
|------|---------|---------|-------|
| `--workspace-id <id>` | `MULTICA_WORKSPACE_ID` | last selected | Override active workspace. |
| `--server-url <url>` | `MULTICA_SERVER_URL` | cloud | Required when targeting a self-hosted server. |
| `--profile <name>` | — | default | Isolates config, daemon state, and workspace selection — use to run a `dev` profile alongside production. |
| `--output <table\|json>` | — | varies | `list` defaults to `table`; most others default to `json`. Always set explicitly when scripting. |
| `--help` / `-h` | — | — | Per-command help. |

## Common pitfalls

- **Default output**: `list` commands print a human table. Add `--output json` before piping to `jq`.
- **Description escapes**: `--description "a\nb"` produces two lines. To pass a literal `\n`, use `--description-stdin` with the literal content on stdin.
- **Secrets in env**: `--custom-env '{"K":"v"}'` is visible to `ps` and shell history. Use `--custom-env-stdin` or `--custom-env-file` (mode `0600`).
- **Model selection**: pass `--model` directly to `agent create/update`, not inside `--custom-args` — some runtimes reject it there.
- **Daemon offline**: local-runtime agents silently wait. Check `multica daemon status` first when an assigned issue isn't running.
- **Issue IDs**: most commands accept either the human key (`ABC-123`) or a UUID; `--full-id` on `list` reveals full UUIDs.
- **Profiles**: `--profile dev` keeps config, daemon, and workspace state separate from the default — useful when switching between cloud and self-hosted servers.

## See also

- https://multica.ai/docs/cli — official one-page command reference (source for this skill)
- https://multica.ai/docs/auth-tokens — PAT vs. JWT vs. daemon token
- https://multica.ai/docs/daemon-runtimes — how the daemon works under the hood
- https://multica.ai/docs/agents-create — full guidance for `multica agent create`
