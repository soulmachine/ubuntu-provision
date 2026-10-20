# Findings — Translating macbook-provision → ubuntu-provision

## Source repo
`/Users/frankdai/github.com/soulmachine/macbook-provision` — Ansible playbook that
provisions a macOS dev box via Homebrew/casks + `mise` (language runtimes) + curl
installers + npm/bun globals. Target repo `ubuntu-provision` is currently **empty**
(git init only, no commits). Goal: produce the Ubuntu equivalent.

## Framework structure (to mirror)
- `bootstrap.sh` — preps a fresh box for Ansible; configures passwordless sudo.
- `ansible.cfg` — `inventory=./inventory`, `roles_path=./roles`, `become_method=sudo`, `become_flags=-H`.
- `inventory` — `127.0.0.1 ansible_connection=local`.
- `main.yml` — ordered role list (dependency-aware via each role's `meta/main.yml`).
- `roles/<name>/{tasks,meta,vars,files}/` — one tool per role.
- `.env`/`.envrc` (direnv `dotenv_if_exists`) — secrets (GH_TOKEN, TAILSCALE_*).
- `.claude/skills/{ansible-idempotency-check,playwright-cli}` — repo-local dev skills (copy verbatim).

## Key cross-platform anchors (UNCHANGED on Ubuntu)
- **mise** — installer `curl https://mise.run | sh`; identical on Linux. Drives go/node/jdk/python.
- **rustup, bun, uv, claude-code, smux** — official curl installers are cross-platform.
- **npm/bun/npx globals** — codex, gemini, opencode, beads, ralph-tui, openclaw, cloudflare,
  playwright, claude-mem, defuddle, skills — all platform-agnostic once node/bun exist.
- Passwordless-sudo `/etc/sudoers.d/<user>-nopasswd` drop-in mechanism works identically on Ubuntu.

## Per-role translation map

### A. Cross-platform — keep nearly verbatim
| Role | Note for Ubuntu |
|------|-----------------|
| uv | curl installer + oh-my-zsh `uv` plugin — unchanged |
| python | `pip3 --user` CLI tools (yamllint, ansible-lint, ruff, pre-commit, httpie); pip3 = mise python, no PEP668 issue — unchanged |
| go / nodejs / jdk | `mise use --global` — unchanged |
| bun | curl `bun.com/install` — unchanged |
| rust | rustup curl + components + oh-my-zsh `rust` plugin — unchanged |
| codex / gemini / opencode | npm globals — unchanged |
| beads / openclaw / cloudflare | npm globals (+ skills/config) — unchanged |
| ralph-tui | `bun install -g` + skills — unchanged |
| claude-mem | `npx claude-mem` — unchanged |
| skills | `npx skills add ...` — unchanged |
| playwright-cli | npm global + skills — unchanged |
| direnv | apt `direnv` instead of brew; oh-my-zsh plugin part unchanged |
| tmux | apt `tmux` instead of brew |

### B. Needs real translation
| Role | macOS mechanism | Ubuntu translation |
|------|-----------------|--------------------|
| **bootstrap.sh** | Xcode CLT, Homebrew, python.org cleanup, AppleEvents prime, mise, ansible | apt update + `build-essential curl wget git file ca-certificates`, mise, `mise use python@3`, `mise exec -- pip install ansible`. Keep passwordless-sudo block. DROP Xcode/brew/AppleEvents/python.org cleanup. |
| **homebrew** → **apt** | brew formulae + casks | apt: git curl wget jq ripgrep `fd-find` tree htop ffmpeg gnupg. gh → official cli.github.com apt repo. docker → official Docker apt repo (docker-ce…) + add user to `docker` group. fd-find ships binary `fdfind` → symlink `~/.local/bin/fd`. GUI casks handled by their own roles or dropped (see C). |
| **oh-my-zsh** | `dscl` shell read/change | `apt install zsh` first; current shell via `getent passwd $USER`; set default via `chsh -s $(command -v zsh)` (or `sudo usermod -s`). Rest (git clone plugin, .zshrc edits, ~/.local/bin PATH) unchanged. |
| **github** | gh via brew | gh via apt repo (or depend on apt role); setup_github.sh is cross-platform (`hostname -s` ok on Linux). |
| **tailscale** | `tailscale-app` cask + Network Extension + systemextensionsctl | Official Tailscale apt repo → `tailscale` pkg; `systemctl enable --now tailscaled`. DROP Network-Extension dance. `tailscale up`/auth-key/API-key-expiry flow unchanged. Much simpler. |
| **ghostty** | brew cask | Linux: needs a build/community repo (no official apt). Config file copy unchanged. ⚠ verify install method. GUI-only. |
| **obsidian** | brew cask | Linux .deb from GitHub releases (or snap/flatpak). defuddle npm + skills unchanged. GUI-only. |
| **intellij-idea** | brew cask | snap `intellij-idea-community`/`-ultimate` (classic). GUI-only. |
| **webstorm** | brew cask | snap `webstorm` (classic). GUI-only. |
| **zellij** | brew core formula | GitHub release binary or `cargo install zellij` (rust present) or mise. ⚠ pick one. |
| **herdr** | brew core formula (herdr.dev) | ⚠ verify Linux installer (likely curl script). |
| **smux** | curl installer; update uses `shasum -a 256` | curl installer cross-platform; replace `shasum -a 256` → `sha256sum`. |
| **multica-cli** | brew tap multica-ai/tap | ⚠ verify Linux install (curl/npm?). Skill-file copy + symlink unchanged. |
| **cc-switch** | brew tap farion1231/ccswitch cask | farion1231/cc-switch is a cross-platform Tauri app → download .deb/AppImage from GitHub releases. GUI. ⚠ verify. |
| **playwright** | npm + `playwright install chromium` | add `playwright install-deps` (or `--with-deps`) for Linux system libs. |
| **claude-code** | curl install + plugins + CCB `ccb-macos-universal.tar.gz` | install/plugins unchanged; CCB → use Linux release asset (`ccb-linux-x64.tar.gz`?). ⚠ verify asset name; the self-bundled-tar-member workaround may differ. |

### C. macOS-only — DROP or stub (no real Linux equivalent)
| Role / item | Why macOS-only | Disposition |
|-------------|----------------|-------------|
| **apple-container** | Apple Virtualization framework, arm64 Mac only | DROP — Docker covers containers natively on Linux |
| **moshi** | macOS menu-bar hook app, brew service/launchd | DROP (or skip) — getmoshi.app is macOS-only |
| **cmux** | macOS-native app (SwiftUI/AppKit/ExtensionKit/GhosttyKit) | DROP — no Linux build |
| homebrew casks: **claude, codex(desktop), gemini(desktop), chatgpt** | desktop apps, no official Linux build | DROP |
| **pearcleaner** | macOS app-uninstaller | DROP |
| **paseo** | brew cask | ⚠ verify if Linux build exists; else DROP |
| **scrapy** (optional, not in main.yml) | berkeley-db via brew | apt `libdb-dev` if kept; low priority |

## Open decisions (need user input)
1. **Target: Ubuntu Desktop vs Server/headless?** Determines whether GUI roles
   (ghostty, intellij-idea, webstorm, obsidian, cc-switch) are included at all.
2. **macOS-only tools** (apple-container, moshi, cmux, pearcleaner, desktop AI apps):
   drop entirely, or keep as documented no-op/skip roles?
3. Ubuntu version/arch — default assumption: **24.04 LTS, amd64 + arm64**.

## Verified install methods (research agents, 2026-06-18)
- **zellij**: GitHub release tarball (static musl), single `zellij` binary at root.
  `unarchive` from `https://github.com/zellij-org/zellij/releases/latest/download/zellij-{{x86_64|aarch64}}-unknown-linux-musl.tar.gz`
  → `~/.local/bin/zellij`. amd64 + arm64. (latest v0.44.3; use latest/download.)
- **herdr**: `curl -fsSL https://herdr.dev/install.sh | sh` → `~/.local/bin/herdr`
  (env `HERDR_INSTALL_DIR`, default `$HOME/.local/bin`). amd64 + arm64. Run as user (become:false).
- **multica**: `MULTICA_BIN_DIR=$HOME/.local/bin curl -fsSL https://raw.githubusercontent.com/multica-ai/multica/main/scripts/install.sh | bash`
  → `~/.local/bin/multica`. amd64 + arm64. (.deb assets are the GUI app, not the CLI.)
  Skill-file copy + ~/.claude symlink unchanged from macOS. → REAL role, not a stub.
- **CCB**: `ccb-linux-x86_64.tar.gz` from `/releases/latest/download/`; bundles a prebuilt
  `ccb-agent-sidebar` → NO Rust needed. install.sh → `~/.local/bin/ccb`.
  **amd64 ONLY** (no arm64 asset) → gate the CCB block on `ansible_architecture == 'x86_64'`.
- **GUI (stubbed, install command kept in role comment)**: intellij-idea →
  `snap install intellij-idea-community --classic`; webstorm → `snap install webstorm --classic`;
  obsidian → `.deb` from obsidian.md/download or `flatpak ... md.obsidian.Obsidian` (role keeps
  defuddle + skills on headless); ghostty → see ghostty.org/docs/install (Linux); cc-switch →
  `.deb`/AppImage from farion1231/cc-switch releases; paseo, cmux, moshi, apple-container,
  pearcleaner, desktop AI apps → macOS-only, pure skip-stubs.
