#!/bin/bash
set -euo pipefail

# Configure passwordless sudo so the playbook's sudo subprocesses (apt installs,
# the GitHub/Docker/Tailscale apt-repo setup, Ansible `become`) run unattended via
# a /etc/sudoers.d drop-in. The first sudo call prompts once on a fresh box; every
# sudo after is passwordless.
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

if command -v ansible >/dev/null 2>&1; then
  echo "Ansible is already installed: $(ansible --version | head -1)"
  exit 0
fi

# 1. Base prerequisites.
#    - build-essential / curl / git: toolchain + fetchers the installers below need,
#      and headers for native npm/cargo builds later in the playbook.
#    - python3 / python3-apt: Ansible discovers the system python (ansible_python_interpreter=
#      auto_silent) to run its apt module, which requires the python3-apt bindings.
#    - software-properties-common: apt-repo helpers used by some roles.
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  build-essential curl wget git file procps ca-certificates gnupg \
  python3 python3-apt python3-pip software-properties-common

# 2. Install mise (multi-language runtime manager; same installer as macOS).
if ! command -v mise >/dev/null 2>&1; then
  curl -fsSL https://mise.run | sh
  # Persist mise + ~/.local/bin in bash (the default Ubuntu login shell). The
  # oh-my-zsh role wires the same two lines into ~/.zshrc once zsh is set up, so
  # both shells get mise after provisioning.
  # shellcheck disable=SC2016
  grep -q 'export PATH="$HOME/.local/bin:$PATH"' ~/.bashrc 2>/dev/null || echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
  grep -q 'mise activate bash' ~/.bashrc 2>/dev/null || echo 'eval "$(mise activate bash)"' >> ~/.bashrc
fi
# Activate mise in the current shell (needed for the steps below).
export PATH="$HOME/.local/bin:$PATH"
eval "$(mise activate bash)"

# 3. Install Python via mise if not already managed by mise.
if ! command -v python 2>/dev/null | grep -q mise; then
  mise use --global python@3
fi

# 4. Install Ansible into the mise-managed Python.
mise exec -- pip install --quiet ansible
