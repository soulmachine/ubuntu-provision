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
  - Copilot CLI: the cache directory under `~/.copilot/installed-plugins/_direct/`; refresh diffs
    the cached `.github/plugin/plugin.json` version around `copilot plugin update`.
  - OpenClaw: `openclaw plugins list --json`; refresh diffs the listed version around
    `openclaw plugins update`.
  - Gemini CLI and kimi-code: no installer, so the role edits their config files (next bullets).
- **The pi package entry lives in `roles/pi/files/settings.json`.** The pi role installs and
  refreshes every npm package listed there, `npm:context-mode` included, so this role has no pi
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
  `npm run install:openclaw` script. It runs only once OpenClaw is onboarded (`~/.openclaw/openclaw.json`).
- **Codex hook trust is a one-time, per-host step the role does not perform**, as for ponytail. The
  role prints a reminder when it installs the plugin: open `/hooks` in `codex` and trust the six
  context-mode hooks. Without the trust, the MCP tools still work; only routing stays quiet.
- **Copilot prints a deprecation warning.** Direct repo installs are deprecated in favour of
  `plugin@marketplace`, but upstream ships no Copilot marketplace yet. Its Claude marketplace
  serves the Claude bundle, so `owner/repo:configs/copilot-cli` is still the documented path.
- **SQLite needs no native build here.** On Linux, Node >= 22.5 uses the built-in `node:sqlite`
  instead of `better-sqlite3`, so npm skipping context-mode's install scripts does no harm.
- **Left out on purpose:** upstream's optional routing-file copies (`AGENTS.md`, `GEMINI.md`) and
  the Claude Code `statusLine`. The hooks inject the routing instructions at session start.
