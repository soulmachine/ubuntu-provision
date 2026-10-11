#!/bin/bash
# Bootstrap a fresh Ubuntu host for the Ansible playbook: passwordless sudo, apt
# prerequisites, uv-managed Python, mise, Ansible. starship, zoxide and fzf, and Omarchy's
# aliases, are provisioned by the shell and omarchy roles in main.yml, not here.
#
# Usage: bash bootstrap.sh
# Idempotent: safe to re-run. One sudo password prompt on a fresh host; the rest runs
# unattended.
set -euo pipefail

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }

# ---------------------------------------------------------------- Passwordless sudo
# /etc/sudoers.d drop-in so later sudo subprocesses (apt installs, the apt-repo setup,
# Ansible `become`) run unattended. First sudo call prompts once.
log "Passwordless sudo"
SUDOERS_FILE="/etc/sudoers.d/$(whoami)-nopasswd"
if [[ ! -f "$SUDOERS_FILE" ]]; then
  echo "Configuring passwordless sudo for $(whoami) (one-time password prompt)..."
  echo "$(whoami) ALL=(ALL) NOPASSWD: ALL" | sudo tee "$SUDOERS_FILE" > /dev/null
  sudo chmod 0440 "$SUDOERS_FILE"
  if sudo visudo -cf "$SUDOERS_FILE"; then
    echo "DONE: passwordless sudo enabled for $(whoami)"
  else
    sudo rm -f "$SUDOERS_FILE"
    echo "REVERTED: validation failed, file removed" >&2
    exit 1
  fi
fi

# ------------------------------------------------------------------ apt prerequisites
# build-essential / curl / git: the toolchain and fetchers the installers below need, and
# headers for native npm and cargo builds later in the playbook.
# python3 / python3-apt: Ansible discovers the system python (ansible_python_interpreter=
# auto_silent) to run its modules, and the apt module needs the python3-apt bindings there.
log "apt prerequisites"
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  build-essential curl wget git file procps ca-certificates gnupg \
  python3 python3-apt

# ----------------------------------------------------------------------------- Python
# uv manages the Python that Ansible and the python role's tools run on. No `--default`:
# that would put a `python3` shim in ~/.local/bin ahead of /usr/bin/python3, and Ubuntu's own
# tools (apt, the python3-apt bindings above) need the distro interpreter under that name.
log "Python via uv"
if ! command -v uv >/dev/null 2>&1 && [[ ! -x "$HOME/.local/bin/uv" ]]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
export PATH="$HOME/.local/bin:$PATH"
uv python find --managed-python 3.14 >/dev/null 2>&1 || uv python install 3.14
uv python pin --global 3.14          # idempotent: rewrites the same user-level pin

# ------------------------------------------------------------------------ Install mise
# mise manages language runtimes (Go, nodejs, jdk, rust), except python (uv's job).
log "mise"
if ! command -v mise >/dev/null 2>&1 && [[ ! -x "$HOME/.local/bin/mise" ]]; then
  curl -fsSL https://mise.run | sh
fi
# The two PATH lines go ABOVE ~/.bashrc's `case $- in` guard, which returns early from every
# non-interactive shell, so `ssh host 'cmd'` and `bash -lc` see them. `mise activate bash`
# is interactive-only and goes at the end. The mise role keeps all three in place.
ensure_above_guard() {
  grep -qF "$1" ~/.bashrc 2>/dev/null && return
  if grep -q '^case \$- in' ~/.bashrc 2>/dev/null; then
    sed -i "/^case \\\$- in/i $1" ~/.bashrc
  else
    printf '%s\n' "$1" >> ~/.bashrc
  fi
}
ensure_above_guard 'export PATH="$HOME/.local/bin:$PATH"'
ensure_above_guard 'export PATH="$HOME/.local/share/mise/shims:$PATH"'
grep -q 'mise activate bash' ~/.bashrc 2>/dev/null || \
  echo 'eval "$(mise activate bash)"' >> ~/.bashrc
MISE_BIN="$(command -v mise || echo "$HOME/.local/bin/mise")"
eval "$("$MISE_BIN" activate bash)"

# ---------------------------------------------------------------------- Install Ansible
# ansible-core ships the console scripts; --with ansible adds the community-collections
# bundle (community.general, for the npm module and friends).
log "Ansible"
command -v ansible >/dev/null 2>&1 || uv tool install --with ansible ansible-core
ansible --version | head -1

# ------------------------------------------------------------------------------- Done
log "Bootstrap complete"
cat <<'EOF'
Next steps:
  1. Run the playbook (starship, zoxide, fzf, Omarchy's aliases, and everything else):
       ansible-playbook main.yml
  2. Then open a NEW shell and verify:
       - starship prompt renders, `z <fragment>` jumps after a few cd's,
         Ctrl-R opens fzf history search, Tab cycles a completion menu
  3. Secrets go in the repo .env (chmod 600); the dotenv role exports them into ~/.bashrc
     above the interactive guard, so non-interactive shells see them too.
EOF
