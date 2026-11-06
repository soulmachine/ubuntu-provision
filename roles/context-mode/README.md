# context-mode role

`context-mode` installs one upstream tool, [context-mode](https://github.com/mksglu/context-mode),
into nine agents (Claude Code, Codex, OpenCode, pi, oh-my-pi, Gemini CLI, Copilot CLI, kimi-code,
OpenClaw). Each agent gets it through its own installer, one task file per agent under `tasks/`,
in the shape of the `ponytail` role. `main.yml` first installs the global `context-mode` CLI from
npm, because the Gemini, Copilot and kimi hooks and MCP servers run it.

- **Skipped agents.** Hermes, Crush and Grok are left out: upstream has no adapter for them. An
  MCP-only entry would add the tools with no hooks or routing, which upstream does not test.
- **Idempotency markers and refresh diffs:**
  - Claude Code: `known_marketplaces.json` and `installed_plugins.json`; refresh diffs
    `gitCommitSha` around `claude plugin update`.
  - Codex: `[marketplaces.context-mode]` and `[plugins."context-mode@context-mode"]` in
    `~/.codex/config.toml`; refresh diffs the `revision` in
    `~/.codex/.tmp/marketplaces/context-mode/.codex-marketplace-install.json`. The reasons are in
    the ponytail README.
  - OpenCode: the bare `context-mode` entry in `plugin` resolves as `@latest`, so there is no
    refresh.
  - pi: none here; the pi role installs and refreshes the package (see below).
  - oh-my-pi: `omp plugin list --json` against `npm view context-mode version`, the ponytail gate.
  - Copilot CLI: `~/.copilot/hooks/context-mode.json` must name the package that `context-mode`
    resolves to; otherwise the role reruns `context-mode setup --yes --agents copilot-cli`. That
    also repairs the absolute node paths setup writes, after mise moves to a new node.
  - OpenClaw: `openclaw plugins list --json`; refresh diffs the listed version around
    `openclaw plugins update`.
  - Gemini CLI and kimi-code: no installer, so the role edits their config files (next bullets).
- **The pi package entry lives in `roles/pi/files/settings.json`.** The pi role installs and
  refreshes every package listed there, `npm:context-mode` included, so this role has no pi
  task. pi needs no `mcp.json`: the extension registers the tools through its own MCP bridge.
- **Gemini CLI: one merge into `~/.gemini/settings.json`.** The merge adds the `mcpServers` entry
  and appends the four upstream hooks to the existing hook lists (`list_merge='append_rp'`), so
  other tools' hooks stay. It runs only while no context-mode hook is present, and writes at 0600.
- **kimi-code: two files.** The MCP server goes into `~/.kimi-code/mcp.json` (the shape
  jev-register-agents writes). The six `[[hooks]]` tables go into a marked `blockinfile` block at
  the end of `~/.kimi-code/config.toml`; a trailing array-of-tables block is valid TOML whatever
  precedes it. Omarchy has no kimi-code, so its copy of this role has no kimi half.
- **OpenClaw needs `--force` on install.** An npm source sits outside ClawHub review, so
  `openclaw plugins install` refuses without it. The flag also overwrites an existing plugin, so
  the install is gated on the list. OpenClaw 2026.10.5 also wants `--accept-capabilities` for a
  plugin that declares capabilities. The install passes it, because installing is the consent. The
  update does not: a release that widens the capabilities is reported with the command to review
  and accept it, and the plugin stays at its version until then. The role uses OpenClaw's own installer rather than upstream's
  `npm run install:openclaw` script. On macOS the OpenClaw half runs only on always-on Macs, and on
  every OS only once OpenClaw is onboarded (`~/.openclaw/openclaw.json`).
- **The first Codex hook trust is a manual, per-host step**, as for ponytail. The
  role prints a reminder when it installs the plugin: open `/hooks` in `codex` and trust the six
  context-mode hooks. Without the trust, the MCP tools still work; only routing stays quiet. After that, each refresh re-trusts hooks an upstream change marks `modified`, and settles the
  plugin cache first (`.npmrc` guard, dependency install, no `.bin` symlinks) with
  `roles/codex/files/codex-plugin-retrust.py`, so updates run without a review (coding-agent Q759). The codex role's `codex-plugin-retrust` watcher (a WatchPaths LaunchAgent, a systemd `.path` unit on Linux) also runs the helper 30 s after Codex rebuilds the cache by itself at session start (coding-agent Q899).
- **Copilot uses `context-mode setup`, not a plugin.** context-mode v2 deleted the v1
  `configs/copilot-cli` bundle and ships no Copilot marketplace, so upstream documents setup as the
  install path. The role uninstalls the v1 direct install where it finds one.
- **npm skips context-mode's install scripts, and that is harmless.** npm 11's install-scripts
  policy skips context-mode's `postinstall` and `better-sqlite3`'s build. `better-sqlite3` ships a
  prebuilt binary, and `context-mode doctor` reports "FTS5 / SQLite: PASS". On Linux, Node >= 22.5
  uses the built-in `node:sqlite` instead.
- **Left out on purpose:** upstream's optional routing-file copies (`AGENTS.md`, `GEMINI.md`) and
  the Claude Code `statusLine`. The hooks inject the routing instructions at session start.
