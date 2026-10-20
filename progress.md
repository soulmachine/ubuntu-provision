# Progress Log

## Session 1 — 2026-06-18

### Done
- Discovered target repo `ubuntu-provision` is EMPTY (git init only). Source is the
  sibling `macbook-provision` Ansible repo → task = port macOS provisioner to Ubuntu.
- Read entire source: bootstrap.sh, ansible.cfg, inventory, main.yml, CLAUDE.md,
  README.md, .env.example/.envrc/.gitignore, ghostty config, and all ~50 role files.
- Wrote findings.md (full per-role macOS→Ubuntu translation map) + task_plan.md.

### Decisions pending (asking user)
- Ubuntu Desktop vs Server/headless (controls GUI roles).
- Drop vs stub macOS-only tools.

### Next
- Get answers → scaffold repo → translate framework → roles → docs → commit.

### Update — translation complete
- Decisions: headless server profile; macOS-only/GUI roles kept as documented skip-stubs (1:1 main.yml).
- Researched (subagents) + verified install methods for zellij, herdr, multica, CCB(amd64-only).
- Wrote 39 roles + bootstrap.sh + ansible.cfg/inventory/main.yml + .env.example/.envrc/.gitignore
  + CLAUDE.md (EN) + README.md (中文) + .ansible-lint/.yamllint; copied .claude/skills,
  setup_github.sh, multica skill, ghostty config verbatim.
- Fixed 2 real bugs (oh-my-zsh YAML colon-space; `command -v` under command module).
- VALIDATED: ansible-lint production 0 failures · yamllint clean · syntax-check ok ·
  --list-tasks resolves (543 tasks) · bash -n ok.
- Git: NOT committed (empty repo; awaiting user go-ahead).

### Update — live tested on supermicro (Ubuntu 26.04) in a fresh LXD container
- bootstrap.sh ✓; full playbook ✓ end-to-end (failed=0); **idempotent re-run changed=0**.
- 6 bugs found & fixed via live testing (see task_plan errors table): bootstrap +x,
  claude-code unguarded .content (fresh box), smux bash-array-under-dash, playwright
  install-deps root PATH, ansible_architecture deprecation, multica idempotency guard,
  mattpocock skills marker. All fixes re-validated (ansible-lint production, idempotent).
- Verified provisioned: zsh default shell, mise (node/go/java), rust/bun/uv,
  claude/codex/gemini/CCB, zellij/herdr/multica/tmux, tailscaled (systemd) enabled+active,
  fd symlink, docker/gh. Container torn down; host cleaned.
- Repo still NOT committed (awaiting user go-ahead).
