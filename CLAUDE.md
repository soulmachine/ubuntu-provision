# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Ansible-based **Ubuntu** (headless server) development-environment provisioner. It is a
translation of the sibling `macbook-provision` repo from macOS to Ubuntu:

- System packages come from **apt** (replacing Homebrew). `gh`, Docker, and Tailscale
  each add their official apt repo.
- Language runtimes (Go, Node.js, JDK, Python) are managed by **mise** — identical to
  the macOS repo (mise is cross-platform).
- Everything else installs via the same cross-platform mechanisms as macOS: official
  `curl | sh` installers (mise, rustup, bun, uv, claude-code, smux, herdr, multica),
  `npm`/`bun` globals, and `npx skills add`.

This is the **headless server profile**: GUI desktop apps are not installed. Roles for
macOS-only tools and GUI apps are kept as documented skip-stubs (a `debug` no-op) so
`main.yml` stays 1:1 with the macOS repo — see "Skip-stub roles" below.

## Commands

```bash
# First-time setup (installs apt prerequisites, mise, Python, Ansible; configures
# passwordless sudo). Open a new shell afterwards so mise is on PATH.
./bootstrap.sh

# Run full provisioning
ansible-playbook main.yml

# Dry run
ansible-playbook main.yml --check

# Run a single role
ansible localhost -m include_role -a name=openclaw
```

## Architecture

- **main.yml** — Main playbook that runs roles in order. Add new roles here. Role order
  and tags mirror the macOS repo; the only swap is `homebrew` → `apt`.
- **bootstrap.sh** — Prepares a fresh Ubuntu box for Ansible. Installs apt prerequisites
  (`build-essential`, `curl`, `git`, `python3`/`python3-apt`, …), mise, Python (via mise),
  and Ansible (`mise exec -- pip install ansible`). Also configures **passwordless sudo**
  so the playbook's sudo subprocesses (apt installs, the gh/Docker/Tailscale apt-repo
  setup, Ansible `become`) run unattended: it installs a `/etc/sudoers.d/<user>-nopasswd`
  drop-in (`<user> ALL=(ALL) NOPASSWD: ALL`, mode 0440), validated with `visudo -cf` and
  rolled back if validation fails. The first `sudo` call prompts once; every `sudo` after
  is passwordless (so `ansible.cfg` uses plain `become_flags = -H`). Idempotent — skips
  the sudoers setup if the drop-in already exists. The macOS-specific steps (Xcode CLT,
  Homebrew, the python.org cleanup, and the AppleEvents/Automation consent priming) are
  intentionally absent.
- **`.env` / `.envrc`** — Optional. `.envrc` runs `dotenv_if_exists .env` so direnv loads
  `.env`. Consumed by `github` (`GH_TOKEN`, optional `GITHUB_SSH_KEY`) and `tailscale`
  (`TAILSCALE_AUTH_KEY`, optional `TAILSCALE_API_ACCESS_TOKEN`). New roles that need
  secrets should gate on `lookup('env', 'VAR') | length > 0` and document the var in
  `.env.example`.
- **roles/** — Each role provisions one tool or application.

### Ansible interpreter note

`inventory` sets `ansible_python_interpreter=auto_silent`, which discovers the system
`/usr/bin/python3` to run modules. The `apt` module needs the `python3-apt` bindings on
that interpreter, so bootstrap.sh installs `python3-apt` (and `python3`). The mise-managed
Python is what `pip3`/`ansible-playbook` themselves run under — separate from the module
interpreter.

### mise activation across shells

bootstrap.sh wires mise + `~/.local/bin` into `~/.bashrc` (the default Ubuntu login shell
at install time). The `oh-my-zsh` role switches the default shell to zsh and wires the
same two lines into `~/.zshrc`, so both shells get mise after provisioning. (On macOS the
bootstrap wrote these straight to `~/.zshrc`; on Ubuntu oh-my-zsh's installer owns
`~/.zshrc`, so the role re-adds them after install.)

### Tailscale role specifics

**Scope of usage:** Tailscale is used **only as a network-connectivity layer** (private
mesh + MagicDNS). Tailscale SSH is intentionally NOT enabled — remote shell access stays
on standard OpenSSH. This is why there is no `--ssh` flag, no `tag:server`/`tag:laptop`
advertisement, and no ACL `tagOwners` management.

- Installs `tailscale` from the official apt repo (`pkgs.tailscale.com`) and enables the
  `tailscaled` systemd service. Unlike macOS, there is **no GUI app and no Network
  Extension** — the macOS-only `systemextensionsctl` check + pause block is removed.
- **Auto-login when `TAILSCALE_AUTH_KEY` is set:** runs
  `tailscale up --accept-dns --accept-routes --operator=$USER --auth-key=...` under
  `become: true`. Skipped if the node is already `BackendState: Running`. `--accept-routes`
  is restated because `tailscale up` rejects dropping a previously-set non-default flag.
- **Key-expiry disable:** when `TAILSCALE_API_ACCESS_TOKEN` is also set, reads `Self.ID`
  from `tailscale status --json` and `POST`s `keyExpiryDisabled: true` to the device API.
  The token needs the `devices` write scope.

### Role Structure

Every role has `tasks/main.yml`. Some also have:
- `vars/main.yml` — Data (e.g. Python CLI tool list, claude-mem install params)
- `meta/main.yml` — Dependencies (e.g. `beads` depends on `go`, `playwright-cli` on `playwright`)

### Common Task Patterns

- System packages: `ansible.builtin.apt` with `become: true`
- Language runtimes: `mise use --global <tool>@<version>`
- CLI tools: `community.general.npm` (`global: true`), `bun install -g`, or official
  `curl | sh` installers guarded by `creates:`
- Agent skills: `npx skills add <repo> -g -y --all` guarded by `creates:`
- GitHub-release binaries (zellij): `ansible.builtin.unarchive` with `remote_src: true` + `creates:`

### Skip-stub roles (kept 1:1 with macOS, but no-op on headless Ubuntu)

- **macOS-only (no Linux build):** `moshi`, `paseo`. Also the GUI casks the macOS
  `homebrew` role installed (Claude/Codex/Gemini/ChatGPT desktop apps, pearcleaner) are
  simply omitted from `apt`.
- **GUI apps with Linux builds, skipped on headless:** `cc-switch`. The role's
  `tasks/main.yml` keeps the real Ubuntu install command in a comment, one uncomment away.

### Adding a New Role

1. Create `roles/<name>/tasks/main.yml`
2. Add the role name to the `roles:` list in `main.yml`
3. If it depends on another role, add `meta/main.yml` with `dependencies:`
