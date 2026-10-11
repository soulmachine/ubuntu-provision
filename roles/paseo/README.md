# paseo role

Every host here is a server (DECISIONS Q9), so this role has one install path, upstream's
documented server install: `npm install -g @getpaseo/cli`, the CLI and the daemon, which serves
the web UI itself. There is no desktop app and no always-on gate; upstream's macOS role
branches on both. The npm install is diffed with `npm ls -g`, the same gate as `playwright-cli`.
A hand-written `"npm:@getpaseo/cli"` pin in mise's global config would shadow the npm global, so
the role removes one wherever it finds it.

## The daemon

The role owns the systemd user unit `~/.config/systemd/user/paseo.service` (`files/paseo.service`),
the Linux analogue of upstream's `sh.paseo.daemon` LaunchAgent (upstream DECISIONS Q176). It runs
`bash -lc "exec paseo daemon run"`, enables lingering for the user so the unit runs from boot with
no login session, enables it, and starts or restarts it. It also turns on the relay
(`daemon.relay.enabled`, off by default). The daemon listens on 127.0.0.1 only, so the relay is the
only way a paired device reaches it. `paseo daemon config set` only saves the file, so a change goes
through the same restart. Pairing (`paseo daemon pair`) stays manual, because the pairing link is a
per-host secret.

Four things are easy to get wrong:

- **`paseo` is launched by name, through a login shell, on purpose.** The nodejs role's
  `mise upgrade node` deletes the old Node version, and the npm global with it. The daemon's workers
  run on the full path of the Node they started on, so even a running daemon breaks. The role then
  sees `@getpaseo/cli` go from absent to present, and the restart starts the daemon on the new Node.
  The login shell is what brings in `CLIPROXY_*` and mise's shims, which `~/.bashrc` exports above
  its interactive guard.
- **Every change leaves the daemon on deleted code or stale config.** An npm install replaces its
  files, the pin removal prunes the tree it was launched from, and a relay change is only read at
  start. So any change, or a new unit file, restarts the service. Otherwise the task only makes sure
  it is enabled and running, which also brings back a unit someone stopped by hand.
- **`systemctl --user` needs the user manager's bus.** A login gets it from pam; an Ansible task
  does not. The task sets `XDG_RUNTIME_DIR` to `/run/user/<uid>`, and lingering is enabled first so
  the manager exists on a host nobody is logged into.
- **An active unit is not a running daemon.** Upstream's archs-mac-mini daemon failed on every start
  for about a week (a stale, empty `~/.paseo/paseo.pid`) while launchd still listed the agent. So
  after starting, the role asks `paseo daemon status --json` for up to 60 s. If the daemon is not
  `running`, it sets the host fact `paseo_daemon_down`, and a `main.yml` post_task fails the play on
  it, so a sweep's `failed=0` check sees it while the roles after paseo still run. The post_task is
  tagged `agent-multiplexer`, because untagged post_tasks are skipped in a tag-limited run.

## The paseo-bots plugin

The role installs `npm:@oliexe/paseo-bots` (upstream DECISIONS Q192). Paseo ships with its global
`pluginsEnabled` switch off, and an installed plugin stays `disabled` until it is on, so the role
turns it on first. That was the user's choice, made after reading Paseo's warning that plugins are
unsandboxed code. It applies the switch with `paseo reload`, not a unit restart, because a restart
kills the daemon's running agents. Both steps wait for the daemon to be running. The role installs
the plugin only when `paseo plugin ls` lacks it and never runs `paseo plugin update`, because each
update trusts new code. Run that by hand.
