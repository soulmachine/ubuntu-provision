# Secrets, `.env` and GitHub tokens

## `.env`

`.env` and `.envrc` are optional, gitignored and per-machine. `.env.example` lists every variable.
Values legitimately differ across hosts: a Tailscale auth key is tailnet-scoped, so hosts on
different tailnets carry different keys. That divergence is correct, not drift to reconcile.

- The `tailscale` role reads `TAILSCALE_AUTH_KEY` (to run `tailscale up`) and, optionally, a
  `devices:core` OAuth client as `TAILSCALE_OAUTH_CLIENT_ID` + `TAILSCALE_OAUTH_CLIENT_SECRET` (to
  disable node-key expiry). See `roles/tailscale/README.md`.
- The `typesafe` role reads `TYPESAFE_API_KEY`. `GITHUB_SSH_KEY` is optional.
- **`GITHUB_TOKEN` is not in `.env`.** On Frank's personal hosts `~/.local/bin/gh-token-fleet` on
  mac-mini-m6 owns the PAT and writes the export into the host's startup file outside the `dotenv`
  managed block. A copy in `.env` made the two overwrite each other. See
  `~/.agents/docs/github-auth.md`. The `github`, `bun` and `mise` roles read it from the
  environment, with a `gh auth token` fallback.
- supermicro's secrets were already exported from `~/.bashrc` by the fleet tools when this repo
  first ran there (2026-10-11), so it needs no `.env` at all.

## The `dotenv` role

direnv loads `.env` only in an interactive shell: `.envrc` runs `dotenv_if_exists .env`, and direnv
is hooked from the end of `~/.bashrc`. Every other shell sees none of it: `ssh host 'cmd'`, git
hooks, systemd units, and the `bash -lc "… ansible-playbook …"` remote-run form, which is a login
shell but not an interactive one. Roles that gate on `lookup('env', VAR) | length > 0` then skip
silently. So the role exports `.env` into `~/.bashrc`, inside a managed block ABOVE Ubuntu's
`case $- in` guard, the one spot bash reads in every shell (upstream DECISIONS Q68/Q69, this repo's
Q11).

Four things are load-bearing:

- **It reads the `.env` file, never `lookup('env', ...)`.** The lookup reads the ambient environment,
  which is exactly what is missing. On a fresh host it would write an empty block; on a host whose
  `.env` changed it would write back the stale values from the old block.
- **An empty parse fails the play.** `blockinfile` would write a block with no exports and strip
  every variable from every non-interactive shell. A `.env` that yields no assignment is a parse bug,
  so an `assert` stops it. A missing `.env` is legitimate (the file is per-machine): that path skips
  and says so, because "no `.env` here" and "run from the wrong directory" look the same in the recap.
- **`no_log: true` is affordable only because of `validate: bash -n %s`.** The block is the
  credentials, so without `no_log` any `-v` or `--diff` prints them, but `no_log` also hides a failure
  message. `validate` checks the candidate before anything is written, so a bad parse leaves the live
  file untouched, and `bash -n ~/.bashrc` reproduces the error. A broken `~/.bashrc` breaks every
  bash on the host.
- **`{% set %}` inside the `block:` template renders as empty.** Ansible's inline templating does not
  carry the binding out, so the names and values are built as two parallel lists in `vars/main.yml`,
  and the template only indexes them.

The markers are `# --- ubuntu-provision .env (managed) ---` / `# --- end ubuntu-provision .env ---`,
the same shape as the `cliproxyapi` and `jev-browser-use-mcp` blocks the fleet tools write to the
same file.

## Borrowing gh's token for GitHub API rate limits

The unauthenticated GitHub API allows 60 calls an hour per IP, shared by every tool on the box, so
the allowance is often spent before a play runs. `bun upgrade` feels it most: it resolves the newest
release from the GitHub API and, on a 403, exits non-zero even when bun is current. An authenticated
call gets 5000 an hour. bun reads `GITHUB_TOKEN`, mise reads `GITHUB_API_TOKEN`, so each role maps
the exported PAT to the name its tool expects. The `gh auth token` lookup is only the fallback for a
host with no exported token.

**Blank both `GH_TOKEN` and `GITHUB_TOKEN` when you shell out to `gh auth token`.** gh resolves
`GH_TOKEN`, then `GITHUB_TOKEN`, then the keyring, so either variable makes the command echo back the
value the fallback exists to replace. With a stale PAT the request then fails 401 instead of 403,
which reads as an unrelated bug. Set `environment: {GH_TOKEN: "", GITHUB_TOKEN: ""}` on the lookup
task to force the keyring credential. A spent rate limit is an expected outcome, so that task uses
`failed_when: false` (see [writing-roles.md](writing-roles.md)).
