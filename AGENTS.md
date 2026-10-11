Ansible playbook that provisions Frank's Ubuntu hosts (supermicro, dev-server-frank) with apt,
mise, npm and agent installers. Every host runs it on itself. It is the Ubuntu port of the sibling
`macbook-provision` repo; see "Upstream" below for how the two stay in step.

## Commands

Run them from the repo root: `.env` and the single-role form both resolve against it.

```bash
./bootstrap.sh                                        # fresh host: passwordless sudo, apt prerequisites, uv Python, mise, Ansible
ansible-playbook main.yml --limit 127.0.0.1           # provision this machine
ansible-playbook main.yml --limit 127.0.0.1 --check   # dry run
ansible-playbook role.yml -e role_name=<role>         # one role, with facts gathered

# another host: over ssh in a login shell, so ~/.profile puts ~/.local/bin on PATH
ssh -o BatchMode=yes -o ConnectTimeout=15 <host> \
  'bash -lc "cd ~/github.com/soulmachine/ubuntu-provision && git pull && ansible-playbook main.yml --limit 127.0.0.1"'
```

## Every task

- **Runs per-host only.** `inventory` holds only `127.0.0.1 ansible_connection=local`, so each host
  provisions itself. Keep it that way, and reach other hosts with the ssh command above. The roles read
  `lookup('env', 'HOME')` in 114 places across 30 roles (`scripts/check-home-lookup-count.sh` checks
  this), with zero uses of `ansible_env.HOME`. Ansible evaluates every `lookup()` on the control node,
  so a fan-out writes one host's `$HOME` and `.env` secrets onto every target.
- **Self-update tasks: diff state, don't grep output.** A task that runs a tool's own updater measures
  a version, checksum or ledger before and after the call, and sets `changed_when` on the difference.
- **The shell is bash.** Interactive lines go to the end of `~/.bashrc`; lines every shell needs go
  above its `case $- in` guard. See [docs/writing-roles.md](docs/writing-roles.md).
- **Modules run on the distro Python.** `inventory` sets `ansible_python_interpreter=auto_silent`, which
  finds `/usr/bin/python3`; the `apt` module needs the `python3-apt` bindings there, which
  `bootstrap.sh` installs. Ansible itself runs from uv's tool environment.

## Upstream

Synced with `soulmachine/macbook-provision` at **bdd5333** (2026-10-11). To catch up again: run
`git -C ../macbook-provision log --oneline 321660b..HEAD`, port each commit role by role (apt for
brew, `~/.bashrc` for `~/.zshrc`, no always-on gate), then move this sha. `main.yml` keeps upstream's
role order; `apt` stands where `homebrew` stands and `shell` + `omarchy` are the bash versions of
upstream's zsh pair. Roles upstream has and this repo deliberately omits, with no stub: host-facts,
homebrew, cua, cc-switch, ghostty, cmux, intellij-idea, obsidian, apple-container, moshi.
`DECISIONS.md` records every other difference.

## Read before you act

| Before you… | Read |
|---|---|
| add a role, or write or change any role's tasks | [docs/writing-roles.md](docs/writing-roles.md) |
| touch `.env`, a secret, `GITHUB_TOKEN`, or the `dotenv` or `bun` role | [docs/secrets.md](docs/secrets.md) |
| change agent-reach, paseo, ponytail, tailscale or typesafe | that role's `roles/<name>/README.md` |
