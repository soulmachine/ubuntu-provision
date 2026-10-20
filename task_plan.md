# Task Plan — Translate macbook-provision → ubuntu-provision

## Goal
Port the Ansible-based macOS dev-environment provisioner
(`~/github.com/soulmachine/macbook-provision`) to Ubuntu, producing a working
`ubuntu-provision` repo at `/Users/frankdai/github.com/soulmachine/ubuntu-provision`.
Preserve the architecture (bootstrap.sh + Ansible roles + mise + curl/npm installers,
idempotent tasks), swapping macOS-specific mechanisms (Homebrew/casks, dscl,
Network Extension, Apple frameworks) for Ubuntu equivalents (apt, official apt repos,
systemd, chsh). Drop tools with no Linux equivalent; document what was dropped.

## Open decisions — RESOLVED (user, session 1)
- Target environment: **Ubuntu Server / headless**. CLI + agent tooling only.
- **Keep all roles in main.yml 1:1 with the macOS repo via documented skip-stubs.**
  - macOS-only roles (apple-container, moshi, cmux, pearcleaner, desktop AI casks):
    skip-stub that no-ops with a "macOS-only — no Linux equivalent" debug message
    (+ pointer to the Linux-native alternative, e.g. Docker for apple-container).
  - GUI-desktop roles that DO have Linux builds (ghostty, intellij-idea, webstorm,
    cc-switch, paseo): skip-stub for the headless profile, with the real Ubuntu
    install command preserved in a tasks/main.yml comment (one uncomment to enable).
  - obsidian: GUI app skipped, but keep its headless-relevant parts (defuddle CLI +
    obsidian agent skills).
- Version/arch: target **Ubuntu 24.04 LTS, amd64 + arm64**.

## Phases

### Phase 1 — Discovery & analysis  — Status: complete
- Read all source files (bootstrap, ansible.cfg, inventory, main.yml, CLAUDE.md,
  README, .env, all ~50 role task/meta/vars + files). Captured in findings.md.

### Phase 2 — Decisions & scaffolding — Status: complete
- Confirm Desktop-vs-Server + drop-vs-stub with user (AskUserQuestion). [done: server, drop]
- Create repo skeleton: ansible.cfg, inventory, .gitignore, .envrc, .env.example,
  .claude/skills (copy verbatim).

### Phase 3 — Core framework translation — Status: complete
- bootstrap.sh (apt + mise + ansible + passwordless sudo; drop Xcode/brew/AppleEvents).
- apt role (replaces homebrew): base CLI pkgs + gh repo + docker repo + fd symlink.
- oh-my-zsh role (apt zsh + chsh instead of dscl).

### Phase 4 — Cross-platform roles (port near-verbatim) — Status: complete
- uv, python, go, nodejs, bun, rust, jdk, direnv, tmux, github,
  codex, gemini, opencode, claude-code(+CCB linux), claude-mem, beads, ralph-tui,
  openclaw, cloudflare, skills, playwright(+install-deps), playwright-cli, smux(sha256sum).

### Phase 5 — Translated-mechanism roles — Status: complete
- tailscale (apt repo + systemd), zellij, herdr, multica-cli.
  (GUI roles dropped per decision.)

### Phase 6 — Wiring & docs & validation — Status: complete
- main.yml (Ubuntu role order, homebrew→apt, GUI/macOS roles kept as skip-stubs).
- README.md (Chinese) + CLAUDE.md (English) rewritten for Ubuntu; README documents
  every dropped/stubbed tool.
- .ansible-lint + .yamllint added documenting project conventions.
- VALIDATED: ansible-lint **production** profile 0 failures; yamllint clean;
  `--syntax-check` pass; `--list-tasks` resolves full dep graph (543 tasks);
  `bash -n` on bootstrap.sh + setup_github.sh OK.
- git commit: PENDING user confirmation (repo is empty; not committing unprompted).

### Phase 7 — Live test on supermicro (Ubuntu server) — Status: complete
- Host is Ubuntu **26.04** (Resolute), user `fdai`, passwordless sudo, real/in-use box.
- Tested in a **fresh Ubuntu 26.04 LXD container** (clean fresh-box, safe, systemd-capable).
- bootstrap.sh ✓; full playbook ✓ (`ok=123 changed=30 failed=0`); fixed 6 bugs found live.
- **IDEMPOTENCY: second run `changed=0 failed=0`** — fully idempotent.
- Proof: zsh default shell (dscl→chsh ✓), mise runtimes, rust/bun/uv, claude/codex/gemini,
  zellij/herdr/multica/tmux, tailscaled enabled+active (systemd ✓), CCB amd64, fd symlink.
- Container deleted, host /tmp cleaned. (Test-harness only: launcher pre-installs node so
  npm-global CLIs resolve in a non-interactive ansible run — a real interactive user has
  mise active; this is NOT a repo change.)

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| oh-my-zsh tasks YAML parse error (`cut -d: -f7` colon-space) | 1 | Quoted the shell `cmd:` scalar |
| oh-my-zsh `command -v zsh` under the `command` module (builtin, not exec) | 1 | Switched task to `ansible.builtin.shell` + noqa |
| ansible-lint var-naming/literal-compare/line-length/braces (source idioms) | 1 | Added `.ansible-lint` skip_list + `.yamllint` (line-length 200, braces 1) |
| **[live test]** bootstrap.sh not executable (`./bootstrap.sh` → Permission denied) | 1 | `chmod +x bootstrap.sh` (Write created it 0644; source was 0755) |
| **[live test]** claude-code "Parse settings" — unguarded `.content` on fresh box (no ~/.claude/settings.json); inherited from source | 1 | Gate on `claude_code_settings_raw.content is defined` (both Parse tasks) |
| **[live test]** smux "Update" — bash array under `/bin/sh`=dash on Ubuntu | 1 | `args: executable: /bin/bash` (also added to oh-my-zsh pipefail task) |
| **[live test]** playwright install-deps as root — `env: node not found` (root PATH lacks mise node) | 1 | Inject node bin dir into task `environment.PATH` |
| **[live test]** `ansible_architecture` deprecation warning (zellij, claude-code) | 1 | Use `ansible_facts['architecture']` (consistent with apt role) |
| **[live test]** multica non-idempotent — installer ignores MULTICA_BIN_DIR (writes /usr/local/bin), `creates:` path never matched | 2 | Gate install on `command -v multica` (location-independent) |
| **[live test]** mattpocock skills non-idempotent — `creates:` marker `diagnose` (repo ships `diagnosing-bugs`); inherited from source | 1 | Point marker at `diagnosing-bugs` (a skill the repo actually provides) |

## Files created/modified
- findings.md, task_plan.md, progress.md (planning)
- (repo files created in later phases)
