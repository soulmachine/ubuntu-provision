# Writing roles

## Add a role

1. Create `roles/<name>/tasks/main.yml`.
2. Add the name to the `roles:` list in `main.yml` at the position upstream macbook-provision
   gives it, and a row at the same position in README's role table.
   `scripts/check-readme-roles.sh` checks that the two orders match.
3. If it depends on another role, list that role under `dependencies:` in `meta/main.yml`.
4. Verify it with the repo's `ansible-idempotency-check` skill
   (`.claude/skills/ansible-idempotency-check/`), which runs each changed role standalone.

## Conventions

- **Secrets come from the repo's `.env`.** Gate the task on `lookup('env', 'VAR') | length > 0`, and
  list the variable in `.env.example`. See [secrets.md](secrets.md).
- **Sudo is passwordless.** `bootstrap.sh` installs a `/etc/sudoers.d/<user>-nopasswd` drop-in, so
  `become` and the apt-repo setup run unattended. No task needs `SUDO_ASKPASS` or sudo priming, and
  `ansible.cfg` keeps plain `become_flags = -H`.
- **System packages come from apt, with `become: true`.** A tool Ubuntu ships under another name
  gets a symlink in `~/.local/bin` (`fd`, `bat`), the way the apt and omarchy roles do it.
- **The shell is bash.** An alias, hook or completion line goes to the end of `~/.bashrc` with
  `lineinfile`, where it runs only in interactive shells. A line every shell must see (a `PATH`
  entry, a secret) goes ABOVE Ubuntu's `case $- in` guard, which returns early from every
  non-interactive shell; the mise and dotenv roles show both placements.
- **No always-on gate.** Upstream gates hermes, ponytail and paseo on `mac_is_always_on`. Every
  Linux host here counts as always-on (DECISIONS Q9), so those roles install unconditionally and
  there is no host-facts role.
- **Expected failures use `failed_when: false`, not `ignore_errors: true`.** `ignore_errors` still
  prints a red `fatal:` block and counts under `ignored=`, so a real failure hides among routine
  ones. Pair `failed_when: false` with a `when: rc != 0` debug task that reports the outcome.
- **A read-only probe that a later task reads gets `check_mode: false`.** `command` and `uri` tasks
  skip under `--check`, which leaves their register undefined and breaks the `set_fact` or `when:`
  below. Leave the flag off the task that writes, so it stays skipped in a dry run.
- **Reads of files that hold keys are `no_log: true`.** `~/.codex/config.toml`,
  `~/.claude/settings.json` and `~/.config/opencode/opencode.json` carry keys, and an ad-hoc
  `include_role` run prints every `slurp` and `set_fact` result in full. Write `settings.json` and
  `opencode.json` back at 0600.
- **A `debug` task's `changed_when` is invisible in ad-hoc output.** The `minimal` callback strips a
  debug result to its `msg` before it picks the label, so under `ansible localhost -m include_role`
  such a task always prints `SUCCESS`, and `grep -c CHANGED` misses it. Put `changed_when` on the task
  that measures (a `slurp`, `find` or `command`). `ansible-playbook`'s recap does count debug tasks.
- **A failure worth reporting but not worth stopping the play goes to `post_tasks`.** Record it as
  a host fact with `set_fact`, print it where it happened, and let `main.yml`'s post_tasks raise it
  after every role has run. The apt upgrade, the skills role and the paseo daemon do this.

## Self-update tasks: diff state, don't grep output

A role that shells out to a tool's own updater (`claude update`, `npx skills update`) decides
`changed` from state measured before and after the call. Record the version or checksum, run the
updater with `changed_when: false`, then measure again and set `changed_when` on the difference.

Matching a phrase in the updater's stdout looks equivalent and is not. These updaters exit 0 on
every path, so a missing phrase looks the same as success, and each has no-op branches that never
print it. `skills update` stays silent about being current when a source is skipped, when there is
nothing to check, and when the check itself fails, which is routine because the unauthenticated
GitHub API allows only 60 calls an hour. Each of those branches reports a phantom change on a
converged machine.

**Both sides of the diff must read the same release channel.** The `claude-mem` role once compared
`npm view claude-mem version` with the version in the marketplace clone's `plugin.json`. That clone
is pulled several times a day, so it carries upstream's in-development version, and the gate was
always true. The fix reads Claude Code's own ledger, `~/.claude/plugins/installed_plugins.json`,
which the installer stamps and which therefore follows npm.

**The exception is agent-reach.** It has no version to compare, so it matches a positive sentinel,
never a negated one. See `roles/agent-reach/README.md`.
