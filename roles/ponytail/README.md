# ponytail role

`ponytail` installs one upstream plugin into six agents (Claude Code, Codex, pi, oh-my-pi, OpenCode,
Hermes), each through that agent's own installer, one task file per agent under `tasks/`. kimi-code
has no plugin mechanism and is skipped.

- **Every refresh diffs state, never stdout:**
  - Claude Code: `gitCommitSha` in `installed_plugins.json`.
  - Codex: the `revision` in `~/.codex/.tmp/marketplaces/ponytail/.codex-marketplace-install.json`.
    That is Codex's own ledger, not the snapshot's git HEAD: `codex plugin marketplace upgrade`
    compares upstream with that record, so a snapshot rewound one commit still reads "already up to
    date", while a record pointing at an older commit triggers a real upgrade (both verified). The
    refresh is gated on `[marketplaces.ponytail]` being registered, not on the record, because codex
    0.161.0's `marketplace add` writes no record (only the first `upgrade` does), so a record gate
    never opened on a fresh host (Q193, Q196).
  - pi and Hermes: their checkouts' HEADs. Both refresh blocks are gated on a `stat` of the checkout,
    so `--check` on a fresh host passes.
  - OpenCode needs no refresh: a bare npm name in `opencode.json` resolves as `@latest` at startup.
- **oh-my-pi has no upgrade path for npm plugins.** `omp plugin upgrade` takes only
  `name@marketplace` IDs, and the package is pinned `^x.y.z` in `~/.omp/plugins/package.json`. So the
  role re-runs `omp plugin install` (a `bun install` there), gated on `npm view … version` differing
  from the version `omp plugin list --json` reports, the claude-mem role's shape. The gate matters: a
  re-install resets the plugin to `enabled: true` with default features, which would undo a manual
  `omp plugin disable` on every play. oh-my-pi is not documented upstream; it works because omp reads
  the same `pi` manifest key ponytail publishes. If it ever stops loading, drop `tasks/omp.yml`.
- **Idempotency markers are the hosts' own records:** `[marketplaces.ponytail]` and
  `[plugins."ponytail@ponytail"]` in `~/.codex/config.toml`; `known_marketplaces.json`,
  `installed_plugins.json` and `enabledPlugins` for Claude Code; the pi checkout (`creates:`); and the
  Hermes plugin directory (a `stat` gate, for the reason below).
- **The pi package entry lives in `roles/pi/files/agent/settings.json`.** The pi role copies that
  file over `~/.pi/agent/settings.json` on every run, and `pi install` records the source string
  verbatim, so listing the same bare `git:github.com/DietrichGebert/ponytail` there keeps the copy
  from stripping it. It is unpinned on purpose, so the refresh tracks upstream.
- **The OpenCode write keeps `opencode.json` at 0600**, the mode `jev-register-agents` sets.
- **Hermes's plugin scanner blocks ponytail, and the role treats that as expected.** `hermes plugins
  install` scans the tree first (`plugins.scan_on_install`, on by default). ponytail 4.9.0 gets a
  `dangerous` verdict from exactly two findings: the literal `/etc/passwd` in two
  `benchmarks/agentic/` files, which trips the CRITICAL `system_passwd_access` pattern (upstream:
  ponytail #781/#783, hermes-agent #93927). `--force` cannot override a dangerous verdict; only
  `plugins.scan_on_install: false` in `~/.hermes/config.yaml` can, and the role will not set that
  security posture for you. So the install task tolerates the failure (`failed_when` on the
  `Security scan blocked` line on stdout), prints the remedy, and reports `changed` from the plugin
  directory appearing. That is why it cannot use `creates:`: a tolerated failure would report a change
  on every run. The install is retried each run and lands once upstream or the scanner changes.
- **Hermes also rejects ponytail's manifest, and that is tolerated too** (Q172). Since Hermes
  `27c02f632` (2026-10-04) the installer requires plugin.json to declare
  `"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"`, and ponytail's has only
  `{"name": "ponytail"}`. **Ponytail omits the field on purpose** (ponytail#1021): it makes Codex,
  VS Code and Qwen load the plugin as an Agent Plugin and drop its hooks. So do not ask upstream to
  add it; the fix is Hermes letting a native `plugin.yaml` win (NousResearch/hermes-agent#125937). The
  same `failed_when` matches `search('Agent\s+Plugins\s+schema')`, because Rich wraps that stdout line
  at 80 columns. These two are the only tolerated errors; any other fails the play.
- **Codex hook trust is a one-time, per-host step the role does not perform.** Codex runs a plugin's
  hooks only once each is trusted: a `trusted_hash` under
  `[hooks.state."<plugin>@<marketplace>:<hooks file>:<event>:<group>:<handler>"]` in
  `~/.codex/config.toml`, which the `/hooks` screen writes through the app-server's
  `config/batchWrite`. It can be done headlessly: `hooks/list` over a stdio `codex app-server` reports
  each hook's `currentHash` and `trustStatus`, and writing that hash back flips it to `trusted` (done
  for ponytail's SessionStart, UserPromptSubmit and SubagentStart hooks on mac-mini-m2, 2026-09-08).
  The hash covers the unsubstituted command, so it is the same on every host running the same version.
  The role only prints a reminder: an unpinned trust would accept whatever upstream ships next, which
  is what the review exists to catch, and a pinned hash goes stale on every release. It also leaves
  `[features] hooks` alone; `bypass_hook_trust` is a blanket policy bypass, not a trust.
