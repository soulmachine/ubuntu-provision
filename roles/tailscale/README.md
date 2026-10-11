# tailscale role

**Scope:** Tailscale is only a network layer here (private mesh + MagicDNS). The role does not enable
Tailscale SSH; standard OpenSSH handles remote shells. That is why there is no `--ssh` flag, no
`tag:server`/`tag:laptop` advertisement, no ACL `tagOwners` management, and no laptop-vs-server
branching. If you turn Tailscale SSH back on, add `--ssh` and, for per-machine ACL gating,
`--advertise-tags` plus the API-driven `tagOwners` update.

- **It installs `tailscale` from the official apt repo** (`pkgs.tailscale.com`, the release for this
  host's Ubuntu codename) and enables the `tailscaled` systemd service. Unlike upstream's macOS
  role there is no GUI app, no Network Extension and no CLI launcher step, so none of upstream's
  GUI gates exist here. MagicDNS is handled by tailscaled's own resolver integration.
- **Auto-login when `TAILSCALE_AUTH_KEY` is set.** The role runs `tailscale up --accept-dns
  --accept-routes --operator=$USER --auth-key=...` under `become: true`, skipped when the node is
  already `BackendState: Running`. `tailscale up` rejects a call that drops a previously set
  non-default flag (it needs `--reset` or every non-default flag restated), so the role lists every
  non-default flag the daemon was last brought up with. `--accept-routes` is there for that reason and
  to receive subnet routes from other nodes. `--operator=$USER` lets the user run `tailscale` without
  sudo afterwards; the status reads keep `become: true` so they also work before that.
- **Key-expiry disable takes an OAuth client and nothing else.** With `TAILSCALE_OAUTH_CLIENT_ID` and
  `TAILSCALE_OAUTH_CLIENT_SECRET` both set, the role form-`POST`s them to `/api/v2/oauth/token` (no
  `grant_type`; Tailscale's documented curl omits it), reads `Self.ID` from `tailscale status --json`,
  and `POST`s `keyExpiryDisabled: true` to `/api/v2/device/{id}/key`. The bearer token lives exactly
  one hour (`expires_in: 3600`, not configurable). The client needs only the `devices:core` scope,
  whose endpoint list names that POST.
  - **No personal access token.** A PAT carries no scopes and expires after 90 days, which made
    this task a 401 on a timer. An OAuth client secret does not expire, belongs to the tailnet, and
    is revocable alone. A host still carrying `TAILSCALE_API_ACCESS_TOKEN` from this repo's earlier
    `.env.example` without an OAuth client fails the play with migration instructions.
  - **Half a pair fails the play.** The block is otherwise gated on a credential being present, so a
    half-configured host would silently skip key-expiry disable and drift back to expiring keys.
  - An OAuth client secret cannot be a bearer token directly, hence the exchange. It can go straight
    to `tailscale up --auth-key=`, but that needs the `auth_keys` scope and forces tag ownership on the
    node, so `TAILSCALE_AUTH_KEY` stays a separate credential.
- **The two credentials gate different halves of the role, deliberately unchained.**
  `TAILSCALE_AUTH_KEY` enrols the node once; the OAuth client authenticates control-plane calls
  ongoing. The key-expiry block is gated on `tailscale_oauth_configured` alone, and all credentials
  load up front.
  - The block reads `Self.ID` **first**, before minting a token, so an unenrolled host does not burn a
    credential, and it emits a `debug` no-op when there is no ID: an unenrolled machine is a legitimate
    mid-setup state. Every extraction step defaults, because an unenrolled node yields an empty
    stdout, a null `Self`, or a `Self` without `ID`, depending on how far setup got. The read is a
    fresh `tailscale status`; the enrolment block's copy predates `tailscale up` on a first run.
- **The key-expiry POST is gated on a read.** `GET /api/v2/device/{id}?fields=all` returns
  `keyExpiryDisabled` (only with `?fields=all`), and the POST is skipped when it is already `true`. The
  POST returns 200 either way, so without the read the role reports a change on every run. A 403 or
  404 on that read means the OAuth client belongs to another tailnet than the node; the role says so
  and skips.
- **The OAuth and device-read `uri` tasks carry `check_mode: false`;** the final POST does not, so it
  stays skipped under `--check`. Minting a one-hour token changes no durable state.
