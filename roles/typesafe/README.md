# typesafe role

`typesafe` installs the two Claude Code plugins built on TypeSafe's Jev model, plus the official
`typesafe-ai` skill from `typesafe-ai/skills` (moved here from `roles/skills` on 2026-09-19, Q165):

- `fast-jev-compaction@fast-jev-compaction`, a function-hook plugin that replaces the compaction
  summary with per-tool-call Jev keep/drop decisions.
- `claude-jev@claude-jev`, an MCP-server plugin: five `jev_*` tools plus `/jev-review`, `/jev-pick`,
  `/jev-why` and `/jev-ask`.

Facts that are easy to get wrong:

- **One `env` entry serves both plugins.** Each declares a `sensitive` `apiKey` userConfig and falls
  back to `TYPESAFE_API_KEY` in Claude Code's process environment: the hook runs in-process, and the
  MCP server is a child that inherits it. So the role leaves every userConfig option alone and writes
  `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1` + `TYPESAFE_API_KEY` into the `env` map of
  `~/.claude/settings.json` (upstream's own install step), with the same read-merge-write and
  `recursive=true` combine as the `claude-code` role, and *before* the plugin install, so function
  hooks are on the first time fast-jev loads. Not the keychain: it is locked in the non-interactive
  ssh sessions the fleet is provisioned from, and a value set through an install-time flag cannot be
  rotated by re-running.
- **The plugins gate on the key; the skill does not.** `TYPESAFE_API_KEY` comes from the repo `.env`,
  so it reaches a non-interactive run only through the `dotenv` role's `~/.bashrc` block. Without it,
  the role reports why and installs no plugins, so a host gets them only after its `.env` carries the
  key. The skill is guidance for writing code against TypeSafe, useful before a key exists, and
  `roles/skills` installed it unconditionally on every host, so gating it would have silently narrowed
  where it lands.
- **The skill install is unguarded and diffed by checksum.** No `creates:`: re-running
  `npx skills@latest add` is the only thing that pulls upstream edits. A `find … get_checksum` runs on
  either side of the call, and the second one carries the `changed_when`. The four agents are named
  rather than `--agent '*'`, mirroring `skills_agents`, which also makes a single-role run
  self-sufficient, since the `agent-sync sync` that would otherwise fan the store out runs in a later
  role. A pin that stops matching upstream is `failed_when: false` plus a report, because failing here
  would stop every later role in the nightly sweep, the blast radius `roles/skills` refuses for its own
  pins. The skill's entry there is in `skills_sources_foreign`, which keeps that role's orphan detector
  accounting for a store directory it no longer refreshes.
- **`settings.json` is written 0600, by this role and by `claude-code`.** The file holds a credential,
  and Claude Code itself keeps it at 0600 (measured 2026-09-18). The two tasks that carry the key (the
  `set_fact` merge and the `copy`) are `no_log`.
- **Every gate reads a ledger, none reads stdout:** marketplace add is gated on the *name* in
  `known_marketplaces.json` (Q154), install on the id in `installed_plugins.json`, update on
  `gitCommitSha` diffed around the call, and enable on the key being absent from `enabledPlugins`, so a
  manual `/plugin` disable survives. The marketplace names (`fast-jev-compaction`, `claude-jev`) come
  from each repo's `.claude-plugin/marketplace.json` and cannot be derived from `owner/repo`, so both
  are carried in `vars/main.yml`.
