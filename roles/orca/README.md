# orca role

[Orca](https://onorca.dev) is an IDE that runs coding agents across worktrees. Upstream's role puts
the desktop app on MacBooks and the Orca server on always-on Macs. Every host here is a server
(DECISIONS Q9), so every host gets the server (DECISIONS Q40, upstream Q243).

## The .deb

Orca has no separate server package. The CLI and `orca serve` ship inside the app, so the role
installs the app's `.deb` from the GitHub release. Its post-install script links the CLI as
`/usr/bin/orca-ide`. Orca uses that name on Linux because GNOME's screen reader already owns
`orca`. The newest tag comes from the redirect of `releases/latest`, as in `roles/email`. The role
installs `orca-ide_<tag>_<amd64|arm64>.deb` when `dpkg-query` reports a different version. The
`.deb` pulls in Electron's GTK and NSS libraries, even on a headless host.

The role also registers the CLI as the app's Settings → General → Orca CLI does: it links
`~/.local/bin/orca-ide` to `/opt/Orca/resources/bin/orca-ide`. The app checks only that link on
Linux. If a file that is not a link already sits there, the task fails rather than replace it, as
the app does.

## The server

The role does not write its own unit. It runs upstream's `orca-ide serve service install --port
6768`, which writes, enables and restarts the systemd user unit `orca-serve.service`. That unit runs
`orca-ide serve --supervise --no-pairing`. The supervisor restarts the server with growing delays
and waits while an update replaces the app, so an upgrade needs no restart from the role. After 6
failures in 15 minutes it gives up. `orca-ide serve service install` is also what clears a
supervisor that gave up.

- **It installs only when `orca-ide serve service status --json` is not `live`.** A reinstall
  restarts the server and kills its sessions. A change of flags (port, address, PATH) needs a manual
  `orca-ide serve service install --port 6768 --pairing-address <tailscale-ip>`.
- **Port 6768 is fixed,** so paired clients keep their address across restarts.
- **It advertises the host's Tailscale IPv4** (`tailscale ip -4`) with `--pairing-address`, so a
  pairing offer names an address that macbook-pro-m3 reaches. It is an IP, not a MagicDNS name,
  because one fleet host answers `*.ts.net` from a fake-IP resolver. Without Tailscale, the role
  leaves the flag out.
- **It runs through `bash -lc`.** The unit pins the PATH it was installed with, and the agent CLIs
  the server spawns live on mise's shims.
- **`systemctl --user` needs the user manager's bus.** The tasks set `XDG_RUNTIME_DIR`, and the role
  enables lingering first, as `roles/paseo` does, so the server outlives a logout.
- **An active unit is not a live server.** After installing, the role polls the status for up to 60
  s. If the server is not `live`, it sets `orca_serve_down`, and a `main.yml` post_task tagged
  `agent-multiplexer` fails the play after the other roles have run.
- **Orca 1.4.224 has no `serve service`.** The subcommand and `--supervise` landed upstream on
  2026-10-12 (stablyai/orca #27716, #27744), after the latest release. Until a release has them, the
  CLI answers `invalid_argument`, and the role skips the server with a message instead of failing.

## By hand

- **Pairing.** The service never prints a pairing link. On the server:
  1. `orca-ide serve service uninstall`, which frees the profile.
  2. `orca-ide serve --port 6768 --pairing-address <tailscale-ip>` in a terminal. It prints a
     pairing link.
  3. On the client, paste the link into **Add Server**, or run
     `orca environment add --name <host> --pairing-code '<link>'`.
  4. Ctrl+C the server, then `orca-ide serve service install --port 6768 --pairing-address
     <tailscale-ip>`.

  The link is a secret: do not paste it into a file or a chat. Each client gets its own grant, and
  a new link replaces the last unused one. If the client shows the server as Disconnected, click
  **Connect**.
- **Agent accounts and skills** must be set up in the server's own shell, because a paired client
  disables Add account, and remote sessions use the server's PATH, home and logins:
  `orca-ide account add --agent claude|codex`, `orca-ide skills install --skill orca-cli --skill
  orchestration`, and later `orca-ide skills update --all`.

Source for the steps: <https://www.onorca.dev/docs/remote-servers>.
