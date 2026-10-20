<!-- AI-maintained, append-only -->

## Q1 — interactive/catch-up — gate-resolution

**Question:** This repo was ported from macbook-provision at its commit 78b8cbe (2026-06-18) and upstream is now 367 commits ahead. Which Ubuntu release and which hosts does the catch-up target?
**Options considered:** keep the README's 24.04 LTS claim / target 26.04 LTS, the release both real Ubuntu hosts run
**Chosen:** Ubuntu 26.04 LTS on amd64. The hosts are supermicro (personal) and dev-server-frank (Nickel company host). arm64 stays only where a role already handles it.
**Decided-by:** human
**Justification:** Both hosts report 26.04 in `/etc/os-release` (surveyed 2026-10-11). Nothing in the fleet runs 24.04.
**Outcome:** applied
**Ref:** (pending)

## Q2 — interactive/catch-up — tradeoff

**Question:** How to catch up: port each upstream change role by role, or re-port from upstream HEAD from scratch?
**Options considered:** role-by-role translated port, one commit per role or topic citing the upstream hashes / re-port from scratch
**Chosen:** Role by role on `main`, one commit per role or topic, each message naming the upstream commits it ports. The first commit is the already-staged CLAUDE.md to AGENTS.md rename. AGENTS.md records the upstream commit the repo is synced to (321660b, upstream HEAD on 2026-10-11) so the next catch-up starts from a known baseline. Pushed only after the end-to-end run passes.
**Decided-by:** human
**Justification:** Keeps this repo's own fixes and makes each commit reviewable against a named upstream commit. The sync marker replaces the archaeology this catch-up needed.
**Outcome:** applied
**Ref:** (pending)

## Q3 — interactive/catch-up — deviation

**Question:** Upstream deleted beads, gemini, openclaw, ralph-tui and scrapy. This repo still has all five. Delete them here too?
**Options considered:** delete all five / keep gemini, which this repo installs with npm, so upstream's Homebrew reason does not apply
**Chosen:** Delete all five. Also delete the moshi and cc-switch skip-stubs under Q4.
**Decided-by:** human
**Justification:** Upstream's reasons: beads and ralph-tui unwanted (b1873f0), gemini's formula disabled (bbb3f7d, upstream Q38), openclaw crash-looped and was removed fleet-wide (40b87e3, 79c33bc), scrapy was dead code not in main.yml (9261c50). The user chose to drop gemini as well, knowing the Homebrew reason does not apply here.
**Outcome:** applied
**Ref:** (pending)

## Q4 — interactive/catch-up — deviation

**Question:** The original port kept macOS-only and GUI roles as no-op stubs so main.yml stayed 1:1 with upstream, then commit c53f623 removed six of them outright. What is the rule now, and does the repo install any GUI app?
**Options considered:** restore stubs / keep GUI roles out, no stubs / install the GUI apps that have Linux builds (cc-switch .deb, ghostty apt, IntelliJ and Obsidian snaps, VS Code, Sublime)
**Chosen:** No GUI apps and no stubs. GUI-only and macOS-only roles (cc-switch, ghostty, cmux, intellij-idea, obsidian, apple-container, moshi, cua, the desktop casks) are omitted. main.yml keeps upstream's order for the roles that exist. AGENTS.md says so instead of claiming 1:1.
**Decided-by:** human
**Justification:** The user first asked to keep GUI roles (round 2), then reversed to no GUI installs at all (round 4, reading A) because the hosts are used over ssh. supermicro has GNOME installed, but nothing in the repo targets a desktop session.
**Outcome:** applied
**Ref:** (pending)

## Q5 — interactive/catch-up — gate-resolution

**Question:** Upstream added DECISIONS.md, `docs/`, per-role READMEs, `scripts/` checks and a `.pre-commit-config.yaml`. Adopt them here?
**Options considered:** adopt all, translated / adopt only DECISIONS.md
**Chosen:** Adopt all, translated to Ubuntu. DECISIONS.md starts at Q1 for this repo. `docs/` gets writing-roles and secrets but no host-facts (Q9). `.yamllint` is dropped, as upstream has none. The two ansible-lint rules this repo skipped (`var-naming[no-role-prefix]`, `literal-compare`) are fixed instead of skipped. This repo's commit 902fa6c, which put `check_mode: false` on 40 install tasks, is reverted so only read-only probes carry the flag and a dry run installs nothing.
**Decided-by:** human
**Justification:** The user's global instructions already require decision logging. The README role-table check catches the drift the repo already had. Upstream's `--check` rule (docs/writing-roles.md) is the opposite of 902fa6c.
**Outcome:** applied
**Ref:** (pending)

## Q6 — interactive/catch-up — gate-resolution

**Question:** Where and how is the catch-up validated end to end?
**Options considered:** a fresh Ubuntu 26.04 container on the Mac, as the original port did / supermicro
**Chosen:** supermicro. Push a work branch, clone it to `~/github.com/soulmachine/ubuntu-provision` there, run `bootstrap.sh`, run the full play twice with the second run at `changed=0`, then fast-forward `main`, push, and switch that clone to `main`.
**Decided-by:** human
**Justification:** supermicro is the box the repo exists for, and the user named it. Known risks noted at the time: its jammy-era third-party apt sources could break `apt update`, and its nvm and mise both manage node in interactive shells.
**Outcome:** applied
**Ref:** (pending)

## Q7 — interactive/catch-up — gate-resolution

**Question:** Three adjacent things could be pulled in: the Arch host mac-mini-2018-omarchy, enrolling the Ubuntu hosts in the nightly `update-packages` sweep on mac-mini-m6, and a first run on dev-server-frank.
**Options considered:** include any of them / leave all three out
**Chosen:** All three out. The repo stays Ubuntu-only with no package-manager abstraction. Sweep enrollment is a `~/coding-agent` change. dev-server-frank is a company host with its own credential rules, and its first run is a separate step the user triggers.
**Decided-by:** human
**Justification:** The Arch host is not Ubuntu. The other two touch other repos or another company's host.
**Outcome:** applied
**Ref:** (pending)

## Q8 — interactive/catch-up — gate-resolution

**Question:** Upstream added 13 roles since the port. Which ones belong on an Ubuntu host?
**Options considered:** per role: adopt as-is / adopt with translation / skip
**Chosen:** Adopt dotenv, mise, agent-sync (GitHub release tarball instead of brew), claude-extras, typesafe, kimi-code, omp, pi, hermes, ponytail, agent-reach (without its OpenCLI task, which needs a Chrome extension click), and paseo (npm CLI plus a systemd user unit with linger, the Linux analogue of upstream's LaunchAgent). Skip cua (macOS TCC and a CuaDriver app) and host-facts (Q9).
**Decided-by:** human
**Justification:** The hermes, kimi-code and agent-sync installers all ship Linux x64 builds (checked 2026-10-11). Upstream's paseo README already describes the non-macOS install path.
**Outcome:** applied
**Ref:** (pending)

## Q9 — interactive/catch-up — deviation

**Question:** Upstream's host-facts role gates hermes, ponytail and paseo on `mac_is_always_on`, a MacBook blacklist read from `system_profiler`. What is the Linux rule?
**Options considered:** a DMI form-factor rule, fail-open like upstream / no gate at all
**Chosen:** No host-facts role. Linux hosts count as always-on, so hermes, ponytail and paseo install unconditionally. Upstream's docs/host-facts.md is not ported.
**Decided-by:** human
**Justification:** The user ruled that every Linux machine in the fleet is a server that stays up.
**Outcome:** applied
**Ref:** (pending)

## Q10 — interactive/catch-up — deviation

**Question:** This repo's oh-my-zsh role switches the login shell to zsh and owns the shell wiring, and every upstream role writes its aliases and inits to `~/.zshrc` or `~/.zshenv`. Keep zsh?
**Options considered:** keep oh-my-zsh and zsh / Ubuntu's built-in bash with a small CLI stack, as Omarchy does
**Chosen:** bash. The oh-my-zsh role is replaced by a `bash` role in the same main.yml slot that installs starship, zoxide and fzf from apt and appends their bash inits plus `mise activate bash` to `~/.bashrc`. No oh-my-zsh, no atuin, no zsh plugins. Every other role's zsh touch becomes a bash one: the yolo aliases, the herdr wrapper and the direnv hook go to `~/.bashrc`, omp completions use bash, paseo's unit runs `bash -lc`.
**Decided-by:** human
**Justification:** The user asked for the built-in bash plus starship, zoxide and fzf, "just like Omarchy". supermicro already runs bash, and its gateway and token exports live in `~/.bashrc`, so no fleet-tool re-run is needed. Ubuntu 26.04 ships all three from apt.
**Outcome:** applied
**Ref:** (pending)

## Q11 — interactive/catch-up — gate-resolution

**Question:** Upstream's dotenv role exports `.env` into `~/.zshenv`, the one file every zsh reads. Where does the bash port write?
**Options considered:** `~/.profile` / `~/.bashrc` above Ubuntu's non-interactive guard / `~/.bashrc` at the end
**Chosen:** `~/.bashrc` above the `case $- in` guard, validated with `bash -n` before the write, with ubuntu-provision markers.
**Decided-by:** human
**Justification:** Ubuntu's bash reads `~/.bashrc` for `ssh host 'cmd'`, but the stock file returns early for non-interactive shells, so an export appended at the end never reaches a non-interactive run. jev-fleet-host.py already inserts above that guard on supermicro, so this follows the fleet's precedent. `~/.profile` is read by login shells only.
**Outcome:** applied
**Ref:** (pending)

## Q12 — interactive/catch-up — tradeoff

**Question:** claude-mem now asserts the CLIPROXY variables, and agent-reach and pi call the claude-gw wrapper. Those come from the gateway on mac-mini-m2 (`gateway/cliproxy-tier`), not from the playbook. Port verbatim, or make the gateway blocks optional?
**Options considered:** verbatim, fail loudly without the gateway / skip the blocks when the variables are absent
**Chosen:** Verbatim.
**Decided-by:** human
**Justification:** Both Ubuntu hosts are already in cliproxy-tier's host list, and supermicro has the variables, the wrappers and the 8317 tunnel live. An optional branch would hide a broken gateway.
**Outcome:** applied
**Ref:** (pending)

## Q13 — interactive/catch-up — gate-resolution

**Question:** Upstream renamed `GH_TOKEN` to `GITHUB_TOKEN`, moved the PAT out of `.env`, replaced the Tailscale PAT with an OAuth client pair, and added `TYPESAFE_API_KEY`. Follow?
**Options considered:** follow upstream exactly / keep this repo's `.env.example`
**Chosen:** Follow upstream. `.env.example` lists the Tailscale OAuth pair and `TYPESAFE_API_KEY`, no GitHub token. The github role reads `GITHUB_TOKEN` from the environment with a `gh auth token` fallback. supermicro needs no `.env` for its first run because its secrets are already exported from `~/.bashrc`.
**Decided-by:** human
**Justification:** Matches upstream docs/secrets.md and the fleet's gh-token-fleet and jev-fleet tools, which already write supermicro's `~/.bashrc`.
**Outcome:** applied
**Ref:** (pending)

## Q14 — interactive/catch-up — gate-resolution

**Question:** Upstream's homebrew role runs `brew upgrade` every play and raises a failure in post_tasks. Should the apt role upgrade packages?
**Options considered:** no upgrade, leave it to unattended-upgrades / `apt full-upgrade` plus autoremove with the same deferred failure
**Chosen:** `apt full-upgrade` plus autoremove at the top of the apt role, failure recorded as a fact and raised in post_tasks. A kernel update still needs a manual reboot.
**Decided-by:** human
**Justification:** The user corrected my assumption that supermicro is shared. It is a personal asset, so the playbook may upgrade it like `brew upgrade` does on the Macs.
**Outcome:** applied
**Ref:** (pending)

## Q15 — interactive/catch-up — gate-resolution

**Question:** Upstream's main.yml defers failures (skills partial failures, wiring, adopt refusals, paseo daemon down) to post_tasks so one broken role does not skip the rest. Adopt?
**Options considered:** adopt for the roles this repo has / fail inline
**Chosen:** Adopt for the apt upgrade (Q14), the skills failures and the paseo daemon.
**Decided-by:** human
**Justification:** Same reason as upstream: a sweep's only success test is `failed=0` in the recap, and a deferred failure keeps that signal without hiding the roles after it.
**Outcome:** applied
**Ref:** (pending)

## Q16 — interactive/catch-up — gate-resolution

**Question:** Q10 and Q11 settle that the shell is bash and that dotenv writes above `~/.bashrc`'s interactive guard. Where do the other startup lines go, and does bootstrap's uv-managed Python shadow the distro `python3`?
**Options considered:** every line at the end of `~/.bashrc`, as the old bootstrap did / PATH lines above the guard and interactive lines at the end / `uv python install --default` as upstream, or without the shim
**Chosen:** The two PATH lines (`~/.local/bin`, mise shims) go above the guard, written by bootstrap.sh and kept by the mise role with `insertbefore`. `mise activate bash`, the direnv hook, the uv completions, the aliases and the shell and omarchy `source` lines go at the end. bootstrap installs Python 3.14 without `--default`, so `/usr/bin/python3` keeps its name and its python3-apt bindings.
**Decided-by:** agent
**Justification:** Ubuntu's stock `~/.bashrc` returns at `case $- in` for every non-interactive shell, and `ssh host 'cmd'` runs exactly such a shell. Upstream's split is the same (shims in `~/.zprofile`, activation in `~/.zshrc`). A `python3` shim ahead of the distro interpreter would break `import apt` for anything that calls bare `python3`, while Ansible's own interpreter discovery does not use PATH. Mirrors supermicro's existing layout, where jev-fleet-host.py already writes above the guard.
**Outcome:** assumed
**Ref:** (pending)

## Q17 — interactive/catch-up — gate-resolution

**Question:** Upstream's omarchy role ports Omarchy's bash files to zsh and installs `try`. What does the bash version deploy?
**Options considered:** copy upstream's zsh port back to bash / copy Omarchy's files as shipped from the Arch host, choosing which to deploy
**Chosen:** Copied as shipped from `/usr/share/omarchy/default/bash` on mac-mini-2018-omarchy (Omarchy 4.0.0.alpha, 2026-10-11). Deployed: envs (minus BROWSER, the locale block and the PATH append), aliases (minus `a`, which runs omarchy-agent), functions, and fns/compression, herdr, rsyncing, ssh-port-forwarding, ssh-reconnect, tmux, worktrees, with upstream's one-line `$editor_pane` fix in tmux. Not deployed: shell and inputrc (the shell role deploys those two under `~/.config/bash`), init (mise and the three tool hooks have their own roles; `try` is not installed, it needs Ruby), completions (the `omarchy` command), env-bootstrap, fns/drives (omarchy-drive-select). Packages: eza, bat with a `batcat` symlink, neovim, gum, inotify-tools, rsync.
**Decided-by:** agent
**Justification:** Omarchy is bash, so the originals need no porting and the next refresh is a plain diff against that directory. rsyncing is Linux-native and costs one apt package; drives calls an Omarchy-only helper.
**Outcome:** assumed
**Ref:** (pending)

## Q18 — interactive/catch-up — deviation

**Question:** Q10 named the replacement for oh-my-zsh a `bash` role. Upstream's commit 2619275 of the same day names its two roles `shell` and `omarchy`. Which names does this repo use?
**Options considered:** `bash`, as agreed in the interview / `shell` and `omarchy`, as upstream
**Chosen:** `shell` and `omarchy`, in upstream's main.yml positions.
**Decided-by:** agent
**Justification:** The user asked for the shell "just like Omarchy" and then asked me to read upstream's latest commits, which introduced exactly that split. Matching the names keeps every future catch-up a one-to-one diff.
**Outcome:** assumed
**Ref:** (pending)

## Q19 — interactive/catch-up — deviation

**Question:** Upstream's codex role now takes the CLI bundled inside ChatGPT.app (d05ab3f, upstream Q197/Q200). What installs codex here?
**Options considered:** a Linux ChatGPT desktop build (none exists) / keep this repo's npm install
**Chosen:** npm `@openai/codex` with `state: latest`; the module's own installed-versus-latest comparison is the change signal. The open-pstack marketplace, the `codex-yolo` alias and the `no_log` on `~/.codex/config.toml` are ported.
**Decided-by:** agent
**Justification:** There is no ChatGPT desktop app on Linux, and upstream's reason for leaving npm (a Gatekeeper prompt from the cask's `codex completion`) is macOS-only.
**Outcome:** assumed
**Ref:** (pending)

## Q20 — interactive/catch-up — tradeoff

**Question:** agent-sync comes from a Homebrew tap upstream. How does the Ubuntu role find and verify the latest release without spending the GitHub API budget?
**Options considered:** the releases API with the `gh auth token` fallback / the `releases/latest` redirect plus `SHA256SUMS.txt`
**Chosen:** Read the version from the `Location` header of `releases/latest` (`uri` with `follow_redirects: none`), fetch the linux-x64 or linux-arm64 tarball with `get_url checksum: sha256:<SHA256SUMS.txt url>`, and install only when the version differs from `agent-sync --version`.
**Decided-by:** agent
**Justification:** The unauthenticated API returned 403 from mac-mini-m6 while this was written (rate limit spent); the redirect has no limit and needs no token, and the checksum file covers integrity. supermicro's hand-installed 1.2.0 converges without a reinstall.
**Outcome:** assumed
**Ref:** (pending)

## Q21 — interactive/catch-up — gate-resolution

**Question:** Upstream's paseo role owns a launchd LaunchAgent. How does the daemon run on Ubuntu from boot, on a box nobody logs into?
**Options considered:** a system unit running as the user / a `systemd --user` unit with lingering / a cron `@reboot`
**Chosen:** `files/paseo.service` as a user unit running `bash -lc "exec paseo daemon run"`, `loginctl enable-linger <user>` under `become` gated on `loginctl show-user`, and `systemd_service scope: user` with `XDG_RUNTIME_DIR=/run/user/<uid>` so Ansible reaches the user bus.
**Decided-by:** agent
**Justification:** Ansible tasks inherit no user bus, and without lingering a user manager exists only while a session does. A user unit keeps the daemon under the user's own environment and mise shims, as the LaunchAgent's `zsh -lc` does on macOS. Known risk: right after lingering is first enabled the user manager can be slow to appear, and the first `systemctl --user` call can fail; a re-run converges.
**Outcome:** assumed
**Ref:** (pending)

## Q22 — interactive/catch-up — tradeoff

**Question:** The ported skills and claude-code comments cite upstream DECISIONS numbers (Q81, Q139-Q155, Q193-Q205) that collide with this repo's own numbering. Rewrite them?
**Options considered:** rewrite every citation / one header line per file saying the Q-numbers refer to upstream's DECISIONS.md
**Chosen:** One header line per file; the prose stays as upstream wrote it. The same applies to the `remoteControlAtStartup: true` settings key, ported verbatim as part of the full claude-code settings merge.
**Decided-by:** agent
**Justification:** Rewriting dozens of citations would make the next catch-up diff noisy for no information gain. The remote-control key is one line to delete if a server should not start that surface in every session.
**Outcome:** assumed
**Ref:** (pending)

## Q23 — interactive/catch-up — gate-resolution

**Question:** Four small calls made while porting the group A roles: the python role's whisper gate, the herdr pane-title wrapper, the tailscale GUI gates, and the go role's upgrade step.
**Options considered:** per item: drop whisper / keep it on arm; `$HOST` / `${HOSTNAME%%.*}`; keep the GUI gates in some form / drop them; add `mise upgrade go` / match upstream
**Chosen:** whisper stays, gated on `architecture in ['arm64', 'aarch64']` because Linux reports `aarch64`; the `herdr()` wrapper is a `blockinfile` in `~/.bashrc` with its own marker, using `${HOSTNAME%%.*}` since bash has no `$HOST`; the Network Extension and CLI-launcher gates are dropped outright, the systemd enable is the only daemon step; go keeps upstream's asymmetry (no `mise upgrade go`, `@latest` re-resolves on every `mise use`). The python role's `--force` heal path will report supermicro's pip-era tools in `~/.local/bin` as changed once.
**Decided-by:** agent
**Justification:** Each keeps the role in step with upstream at zero cost on amd64, or has no Linux equivalent to port.
**Outcome:** assumed
**Ref:** (pending)

## Q24 — interactive/catch-up — gate-resolution

**Question:** The end-to-end run on supermicro (2026-10-11) was meant to finish with a second play at `changed=0`. It finished at `failed=0, changed=2`, both in the skills role: the store fingerprint and the `agent-sync sync` that follows it. Is that a role defect or a real change?
**Options considered:** accept as-is / treat the fingerprint as volatile and gate it / measure
**Chosen:** measured. A third run of the skills role alone, with sha256 snapshots of `~/.agents/skills` taken outside Ansible before and after, reported `changed=0` and no file differed. So the two changes were upstream skill content moving between run 1 (13:36) and run 2 (13:40), which the role is designed to pull down and report. Accepted; nothing changed in the role.
**Decided-by:** agent
**Justification:** The role refreshes every source on every play by design (upstream 244db02); a `changed` on a real upstream edit is the signal, not noise. Gating it away would hide the one mechanism that keeps skills current.
**Outcome:** validated
**Ref:** a7e905b..de6b37f (the catch-up), run logs `~/ubuntu-provision-run{1,2}.log` on supermicro

## Q25 — interactive/dev-server-frank — hard-to-undo

**Question:** dev-server-frank was a zsh host: oh-my-zsh as a real clone, and the fleet-managed cliproxy and jev export blocks in `~/.zshenv`, which bash never reads. The shell role switches the login shell to bash and removes oh-my-zsh, so after the first play every `ssh dev-server-frank 'cmd'` would lose the gateway and jev keys. How does a zsh host migrate?
**Options considered:** keep zsh on that host (contradicts "the shell is bash") / teach the shell role to move fleet-managed blocks (host-specific knowledge the repo should not carry) / move the blocks by hand before the play and retire `~/.zshenv` after it / leave `~/.zshenv` in place (the fleet tools prefer it while it exists, so `~/.bashrc` would go stale on the next key rotation)
**Chosen:** by hand, before the play: copy the cliproxy block verbatim and wrap the jev exports in the `# --- jev-browser-use-mcp (managed) ---` markers the tools write in bash mode, insert both above the `case $- in` guard, `bash -n`, mode 600, keep `~/.bashrc.bak-20261011`. Run the play under `bash -lc`. After the play: rename `~/.zshenv` to `~/.zshenv.bak-20261011` so the fleet tools fall back to `~/.bashrc`, and record the host as a bash host in `~/.agents/docs/shell-startup.md` and `jev-fleet.md` (dot-agents 8d506ef).
**Decided-by:** agent
**Justification:** The repo cannot know which blocks a fleet tool owns, and the markers are the only contract those tools have; replicating them keeps the next key rotation working without a re-run of cliproxy-tier or jev-fleet.
**Outcome:** validated: run 1 `failed=0`; a fresh non-login ssh command sees all eight exports, claude-gw, node and agent-sync. The migration also exposed the above-guard blind spot fixed in e97fe97.
**Ref:** e97fe97, dot-agents 8d506ef

## Q26 — interactive/dev-server-frank — gate-resolution

**Question:** The end-to-end run on dev-server-frank (2026-10-11) was meant to end at `changed=0` on the second play. It ended at `failed=0, changed=3`: the task that makes Claude Code's transcript directories private, and the skills pair (fingerprint plus fan-out), the same pair supermicro showed on its second play (Q24). Defect or convergence?
**Options considered:** accept at face value / measure a third play with checksum snapshots around it and a skills-only pass after it
**Chosen:** measured. The third full play reported `changed=0`, the skills-only pass after it `changed=0`, and both sha256 diffs of `~/.agents/skills` were empty, so no role rewrites a store directory another role owns. The privacy task changed once because the directories it protects exist only after later roles ran `claude` for the first time. The skills pair changed on the second play of both hosts and on neither third play; whether that is upstream content moving twice (Q24's reading) or a one-time second-run effect of the installer is not settled, and it converges either way. Accepted.
**Decided-by:** agent
**Justification:** Three consecutive plays with the last at `changed=0`, plus empty content diffs, is a stronger idempotency check than the two-play rule asked for; nothing remains to fix in the roles. Two real defects the run did expose are fixed in the repo: the above-guard PATH blind spot (e97fe97) and kimi's installer writing to the `$SHELL` startup file (872875b).
**Outcome:** validated
**Ref:** e97fe97, 872875b, run logs `~/ubuntu-provision-run{1,2,3}.log` on dev-server-frank

## Q27 — interactive/purelymail-cli — gate-resolution

**Question:** How does the `purelymail` CLI (github.com/soulmachine/purelymail, Frank's Rust tool for the Purelymail API) reach every personal host, and where do its credentials live?
**Options considered:** `cargo install purelymail` on each host / a role that installs the GitHub release tarball into `~/.local/bin` / by hand over ssh with nothing in the playbook
**Chosen:** A `purelymail` role modelled on ubuntu-provision's `agent-sync` role: resolve the newest release from the releases/latest redirect, download the tarball for the host's architecture, unpack the one binary into `~/.local/bin`, converge on the reported version. No cargo needed. The two tokens, `PURELYMAIL_API_TOKEN` and `CARGO_REGISTRY_TOKEN`, are free-standing exports placed by hand in ~/.profile (mode 600, outside the dotenv managed block, like `GITHUB_TOKEN`), so the role never touches credentials and the dotenv role cannot clobber them.
**Decided-by:** human
**Justification:** Frank chose the token files on 2026-10-11 (`~/.zshenv` on macOS, `~/.profile` on Linux). The tarball avoids a Rust toolchain on hosts that have none (supermicro, mac-mini-2018-omarchy) and a minute of compile on the rest.
**Outcome:** applied
**Ref:** purelymail DECISIONS Q30, release v0.1.0

## Q28 — interactive/email-role — gate-resolution

**Question:** How do the Himalaya CLI (github.com/pimalaya/himalaya), its OAuth helper ortie (github.com/pimalaya/ortie) and Proton Mail Bridge (proton.me/mail/bridge) reach the Ubuntu hosts, where none of the three is in the Ubuntu or Debian archives?
**Options considered:** himalaya and ortie from the GitHub release tarball into `~/.local/bin` / upstream's `install.sh` with `PREFIX=~/.local` / `cargo install`; Bridge from the amd64 .deb on its GitHub release / the .deb from proton.me's download page / skipped on Linux; a gate for the company host dev-server-frank / none
**Chosen:** One `email` role on both hosts, no gate. himalaya and ortie come from their release tarballs through `tasks/pimalaya.yml`, a parametrised copy of the purelymail role (Q27): resolve the tag from the releases/latest redirect, unpack the one binary, converge on the first line of `--version`. Bridge comes from the `.deb` on the ProtonMail/proton-bridge GitHub release, gated on `dpkg-query`'s version and on `uname -m` being `x86_64`, because Proton ships amd64 only; the .deb's `.sig` is not verified, which the task's `shortcut:` comment records. Accounts are configured by hand.
**Decided-by:** human
**Justification:** Frank picked the tarball over `install.sh` (which re-downloads every run, so it would need the same version probe) and over cargo (minutes of compile per release, rejected for purelymail in Q27), and chose no gate for dev-server-frank, on 2026-10-12. Both Ubuntu hosts are x86_64.
**Outcome:** applied
**Ref:** macbook-provision Q223, omarchy-provision Q16

## Q29 — interactive/whats-next-audit — gate-resolution

**Question:** The port's eight `assumed` calls, Q16 to Q23 (startup-line placement, the bash omarchy role, the `shell`/`omarchy` role names, codex via npm, agent-sync's release lookup, paseo's systemd user unit, keeping upstream's DECISIONS citations, four small group-A calls), were listed to Frank on 2026-10-12. Ratify them?
**Options considered:** ratify all eight / revisit any / leave them assumed
**Chosen:** Ratified all eight as applied, in one batch.
**Decided-by:** human
**Justification:** Every one has been running in the nightly sweep on both hosts since the port; none was questioned.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q224
**Supersedes:** Q16, Q17, Q18, Q19, Q20, Q21, Q22, Q23 — assumed calls ratified by the user

## Q30 — interactive/omp-update-rate-limit — deviation

**Question:** Upstream macbook-provision Q225 gives `omp update` `failed_when: false` and a warning task, after an unauthenticated GitHub API rate limit aborted a whole play at that task on 2026-10-12. Port it?
**Options considered:** port it / leave the task failing here
**Chosen:** Ported as is. The two Ubuntu hosts carry a GitHub token today, but the same per-IP budget is shared with every other tool, so the failure is possible here too.
**Decided-by:** human (upstream, 2026-10-12); agent (the port)
**Justification:** One tool's update check must not skip every role after it; the mise role here already handles the same failure this way.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q225

## Q31 — interactive/npm-global-stale-shim — bugfix

**Question:** Upstream macbook-provision Q227 fixes the shared `npm_global` probe after dev-server-frank's openclaw and gemini were stranded under node 24.17.0 with a stale mise shim that made the role skip the install. Port it?
**Options considered:** port it / fix the two hosts by hand
**Chosen:** Ported as is; the file is identical in both repos. dev-server-frank is repaired by rerunning its openclaw and gemini roles.
**Decided-by:** agent
**Justification:** The bug was found on this repo's host and the file is shared verbatim with upstream.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q227

## Q32 — interactive/lcu-role — scope

**Question:** Upstream macbook-provision Q228 adds an `lcu` role (Local Computer Use, amontlabs/lcu). Port it?
**Options considered:** a role gated on `/usr/lib/chatgpt` that skips today / also install the ChatGPT .deb / no role
**Chosen:** No role. supermicro and dev-server-frank have no ChatGPT desktop app and no X11 desktop session (`XDG_SESSION_TYPE=tty`), and LCU needs both. Should a desktop host appear, the Linux path is `/opt/lcu` through `sudo ./scripts/install.sh --user "$(id -un)" --runtime-only`, then `lcu setup --agent <x> --session direct --yes` from inside the desktop session. AGENTS.md lists the omission.
**Decided-by:** human
**Justification:** Frank chose "skip the Linux roles" on 2026-10-12 when the prerequisites were laid out; a role that always skips is dead code.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q228

## Q33 — interactive/removemacai — scope

**Question:** Upstream macbook-provision Q229 adds a `removemacai` role (RemoveMacAI's CLI, its configuration profile and per-user tweaks). Port it?
**Options considered:** port it / no role
**Chosen:** No role. RemoveMacAI changes macOS settings only: Apple Intelligence, a macOS configuration profile, and Finder, Dock and macOS defaults. Linux has none of them. AGENTS.md and README list the omission, and the upstream sync point moves to fdb74fc.
**Decided-by:** agent
**Justification:** Precedent macbook-provision Q222 (`1password`): a macOS-only role is not ported, and the sibling repos list it among the roles they leave out.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q229

## Q34 — interactive/browseros-neo — gate-resolution

**Question:** Upstream macbook-provision Q237 adds `browseros-neo`. Frank wants it on supermicro, not on every Ubuntu host. Upstream's docs say neo has no Linux build yet. How is it installed, and on which hosts?
**Options considered:** the CDN's undocumented `.deb` / its AppImage / no Linux role; gate by hostname / by the presence of a desktop session / no gate
**Chosen:** apt installs `https://cdn.browseros.com/download/BrowserOS_neo.deb` (package `browserclaw`) on each run, and only on the hostnames in `browseros_neo_hosts`, which holds supermicro alone. The MCP entry and skill steps are upstream's.
**Decided-by:** human (the hosts: Frank, 2026-10-12); agent (the package and the gate)
**Justification:** The CDN alias returns the 0.51.0 build (182 MB). Its postinst adds no apt repo and only registers `x-www-browser` alternatives, so the deb URL is the only upgrade path. The apt module's version compare keeps `changed` honest. dev-server-frank is headless (no xsessions) and a company host. A hostname list states Frank's ask directly. The hostname comes from `hostname -s` because single-role runs gather no facts.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q237

## Q35 — interactive/browseros-neo — deviation

**Question:** Upstream macbook-provision Q240 registers neo's MCP server in every agent and corrects two parts of upstream Q237: the port and the skill refresh. Port it?
**Options considered:** port it as is / keep Q237's shape
**Chosen:** Ported as is: URL `http://127.0.0.1:9010/mcp`; the same `mcp add` and JSON-merge tables; an entry with another URL is replaced; the skill installs only when missing. This repo's install steps are unchanged.
**Decided-by:** human (the other agents: Frank, 2026-10-12); agent (the port)
**Justification:** The Linux build is the same Chromium with the same `kDefaultProxyPort = 9010` patch, so the port fix applies here too. The agents and their config paths are the same as on macOS.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q240, ubuntu-provision Q34
**Supersedes:** ubuntu-provision Q34 — its MCP port 9200 and its skill refresh on every play

## Q36 — interactive/bitwarden — gate-resolution

**Question:** Upstream macbook-provision Q242 adds a `bitwarden` role: the Electron app, `bw` and `rbw`. Frank wants the app skipped on headless Linux hosts. Where does each client come from here, and what counts as headless?
**Options considered:** for the app: the official `.deb` / snap / Flathub (community build); for `bw`: npm `@bitwarden/cli` / the release zip; for `rbw`: apt / cargo; for the gate: a hostname list like Q34 / a desktop session file
**Chosen:** apt `rbw`; npm `@bitwarden/cli` through `nodejs/npm_global`; the official `.deb`, whose version comes from the redirect of Bitwarden's download link and is compared with `dpkg-query`. The app installs only when `/usr/share/xsessions` or `/usr/share/wayland-sessions` holds a `*.desktop` file. The upstream sync sha stays at fdb74fc, as it did for Q34 and Q35, because upstream's ego-browser commits are still not ported.
**Decided-by:** human (the headless rule: Frank, 2026-10-12); agent (the sources)
**Justification:** Ubuntu 26.04 universe ships rbw 1.15.0, the same version as Homebrew. npm is how this repo installs other Node CLIs. The `.deb` is Bitwarden's own build; the redirect names the version with no GitHub API call (the Proton Bridge pattern in roles/email). Frank stated the rule as "headless", and Q34 already describes dev-server-frank as headless because it has no xsessions, so the session-file test states the rule directly and needs no list to maintain.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q242

## Q37 — interactive/bitwarden — deviation

**Question:** Q36 says Ubuntu 26.04 ships rbw 1.15.0, the same version as Homebrew. The first run on supermicro and dev-server-frank installed 1.13.2-7. Keep apt?
**Options considered:** keep apt `rbw` 1.13.2 / the `.deb` on doy/rbw's GitHub release / `cargo install rbw`
**Chosen:** Keep apt. `apt` role upgrades bring a newer rbw when the archive gets one.
**Decided-by:** agent
**Justification:** 1.15.0 is in a newer Ubuntu series, not in resolute. 1.13.2 talks to Vaultwarden the same way, and the apt package keeps rbw on the repo's normal upgrade path with no second channel.
**Outcome:** applied
**Ref:** (this commit)
**Supersedes:** Q36 — only its claim that resolute ships rbw 1.15.0

## Q38 — interactive/macos-connectors — scope

**Question:** Upstream macbook-provision Q236 adds a `macos-connectors` role: CLIs for Reminders, Messages, Notes and the other Apple apps. Port it?
**Options considered:** port it / no role
**Chosen:** No role. AGENTS.md and README list the omission.
**Decided-by:** agent
**Justification:** Each CLI drives a macOS app that Linux does not have. Precedent Q33 (`removemacai`): a macOS-only role is not ported and is listed with the omitted roles.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q236

## Q39 — interactive/ego-browser — scope

**Question:** Upstream macbook-provision Q239 and Q241 add an `ego-browser` role: the `ego-browser` skill, Ego Lite through the skill's `install.sh`, an onboarding check and a nightly upgrade. Port it?
**Options considered:** port it for supermicro, as Q34 did for BrowserOS neo / no role
**Chosen:** No role, and no `citrolabs/ego-lite` entry in the skills role. AGENTS.md and README list the omission. The upstream sync point moves to 5b2ec85. The other commits since fdb74fc need no port here: lcu (Q229, Q230, Q233, Q234) and removemacai (Q235) are omitted roles, fec7f1c is a cask `--adopt` fix, Q231, Q232 and Q238 change only upstream's journal, and Q237, Q240 and Q242 are ported as Q34, Q35 and Q36.
**Decided-by:** agent
**Justification:** Ego Lite ships no Linux build. The skill's `scripts/install.sh` downloads only `cdn.ego.app/setup/macos/{arm64,x64}` DMGs, and lite.ego.app offers only macOS and Windows (checked 2026-10-12). Without the app, the skill has nothing to drive. Revisit when a Linux build appears.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q239, Q241

## Q40 — interactive/orca — gate-resolution

**Question:** Upstream macbook-provision Q243 adds an `orca` role: the desktop app on MacBooks, plus the server from upstream's `orca serve service install` on always-on Macs. Where does Orca come from on Ubuntu, and which hosts run the server?
**Options considered:** the `.deb` / the AppImage from the GitHub release; the server on every host / only on headless hosts
**Chosen:** The `.deb` (`orca-ide_<tag>_<arch>.deb`), versioned from the `releases/latest` redirect, on every host, with the server on every host through `orca-ide serve service install --port 6768` and lingering enabled. As upstream does, the role skips the server with a message while the installed Orca predates `serve service`. The upstream sync point moves to 734e118. 81b7b61 (OpenSWE/lessons) was ported already.
**Decided-by:** human (the server on always-on hosts, and waiting for the upstream installer: Frank, 2026-10-12); agent (the `.deb`)
**Justification:** Every host here is a server (Q9), so the always-on gate is always true. Orca ships no apt repo. The `.deb`'s post-install script links `/usr/bin/orca-ide`, a stable path that the service unit can pin. An AppImage would need its own link and FUSE. The redirect gives the tag without a GitHub API call, as in roles/email.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q243

## Q41 — interactive/bitwarden — deviation

**Question:** Upstream macbook-provision Q244 has the `bitwarden` role point `bw` and `rbw` at Vaultwarden, except on archs-mac-mini. Port it?
**Options considered:** port it as is / keep install-only
**Chosen:** Ported: the same `tasks/config.yml` (read, write only when different, report a `bw` that is logged in to another server) and the same URL and email vars. No host gate: archs-mac-mini, the one host with its own Vaultwarden, is a Mac.
**Decided-by:** human (configure every host except archs-mac-mini: Frank, 2026-10-12); agent (the port)
**Justification:** `bw config server` and `rbw config` behave the same on Linux. Frank already had both set by hand on this repo's hosts, so the role keeps that across a rebuild.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q244
**Supersedes:** Q36 — only its "install only" part

## Q42 — interactive/1password — deviation

**Question:** Frank asked for the `1password` role here too (upstream Q245 drops its `~/personal-agent` gate): the desktop app, the `op` CLI and the Claude Code plugin. How does it port to apt?
**Options considered:** the documented `.list` repo setup / the exact files the package's postinst writes; app on every host / app only with a desktop session
**Chosen:** The role writes `/usr/share/keyrings/1password-archive-keyring.gpg` and `/etc/apt/sources.list.d/1password.sources` with the same bytes as the `1password` package's postinst, then apt-installs `1password-cli`, and `1password` only when a desktop session exists (the Q36 probe). The plugin steps are upstream's, unchanged. No debsig policy: Ubuntu does not run debsig-verify by default, and the app's postinst adds the policy where the app is installed.
**Decided-by:** human (every host, plugin too, skip the app when headless: Frank, 2026-10-13); agent (the repo files)
**Justification:** The postinst rewrites the `.sources` file and keyring on every upgrade, and comments out a `1password.list`, so any other path or content would flip back and forth between the package and the role. dev-server-frank has no session file, so it gets the CLI and plugin only.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q220, Q245
**Supersedes:** the "omits 1password (upstream Q222)" line in AGENTS.md

## Q43 — interactive/herdr-ui — deviation

**Question:** Frank asked for Herdr UI (`curl -fsSL https://herdrui.dev/install.sh | sh`) on the Linux hosts. Does the herdr role install it on a headless host too?
**Options considered:** every host / only a host with a desktop session
**Chosen:** Only a host with an X11 or Wayland session file (the Q36 probe), so supermicro gets it and dev-server-frank does not; the role says so in a debug message. A `creates: /usr/bin/herdr-gpui` guard keeps it to one install, and updates come from the app's own App Updates panel.
**Decided-by:** agent
**Justification:** Herdr UI is a GUI client, and its package pulls in X11, Wayland and Vulkan libraries that a host without a display cannot use. Q42 settled the same case for the 1Password app the same way.
**Outcome:** assumed
**Ref:** (pending); macbook-provision herdr role (`penso/tap/herdr-gpui` cask)

## Q44 — interactive/herdr-ui — deviation

**Question:** Keep Herdr UI in the herdr role?
**Options considered:** keep it / remove it
**Chosen:** Removed, on every host. 39ea1d1 is reverted, here and in the other two repos.
**Decided-by:** human (Frank, 2026-10-16: Herdr UI is not needed)
**Justification:** Frank does not need the GUI client, so the headless question in Q43 is moot.
**Outcome:** applied
**Ref:** (this commit)
**Supersedes:** Q43 — Herdr UI is not installed at all

## Q45 — interactive/1password-token — deviation

**Question:** Port upstream 08751d9, which documents OP_SERVICE_ACCOUNT_TOKEN in .env.example and the 1password role?
**Options considered:** port it / skip it
**Chosen:** Skipped. b71065e is reverted, and the token stays out of this repo's .env.example and 1password role.
**Decided-by:** human (Frank, 2026-10-16: only the control-plane hosts need headless `op`)
**Justification:** Only mac-mini-m6, mac-mini-m2 and macbook-air get a 1Password service account (~/.agents/docs/1password.md), and all three are Macs. No host this repo provisions gets one.
**Outcome:** applied
**Ref:** (this commit); macbook-provision 08751d9

## Q46 — interactive/open-pstack-removal — deviation

**Question:** Port macbook-provision Q247, which removes open-pstack from every host through retire tasks in the claude-code and codex roles?
**Options considered:** port it / skip it
**Chosen:** Ported unchanged: the claude-code role uninstalls `pstack@open-pstack` and removes the `open-pstack` marketplace where present; the codex role removes the plugin, the marketplace and its hook-trust entry. The install steps are gone.
**Decided-by:** human
**Justification:** open-pstack is on every host, Linux ones included, and the user wants it gone everywhere. Delete the retire tasks once every host is clean.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q247

## Q47 — interactive/context-mode — gate-resolution

**Question:** Port the macOS context-mode role, and with which agents?
**Options considered:** port it / skip it
**Chosen:** Ported. The agents and installers are the same as on macOS: Claude Code, Codex, OpenCode, pi, oh-my-pi, Gemini CLI, Copilot CLI, kimi-code and OpenClaw. Hermes, Crush and Grok are skipped. The OpenClaw half has no always-on gate, because every Ubuntu host is always-on, but it still waits for OpenClaw's onboarding.
**Decided-by:** human
**Justification:** The user asked for context-mode in all three provision repos, each agent through its own installer. The reasons for the per-agent calls are in macbook-provision Q248–Q251.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q248–Q251

## Q48 — interactive/context-mode — tradeoff

**Question:** Should OpenClaw's capability consent for context-mode be given on install and on update?
**Options considered:** install and update / install only / neither
**Chosen:** Install only. A consent refusal on update is tolerated and reported, and the plugin keeps its version.
**Decided-by:** agent
**Justification:** Same call as macbook-provision Q252. On this repo's hosts OpenClaw 2026.10.5 refused the install without `--accept-capabilities` (dev-server-frank, 2026-10-18).
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q252

## Q49 — interactive/context-mode — irreversible-action

**Question:** Trust context-mode's six Codex hooks on this repo's hosts?
**Options considered:** leave it to the per-host `/hooks` step / trust them headlessly
**Chosen:** Trusted headlessly on dev-server-frank (plugin installed), and ahead of time on supermicro. grok-bot did not answer ssh and was skipped.
**Decided-by:** agent
**Justification:** The user asked for it. Same review, method and revert path as macbook-provision Q253; dev-server-frank's hashes matched mac-mini-m6's.
**Outcome:** applied
**Ref:** (this commit); macbook-provision Q253

## Q50 — interactive/grokbot-box — scope-change

**Question:** grokbot-box, the rebuilt grok-bot, runs Debian 13 (trixie), not Ubuntu. Provision it with this repo?
**Options considered:** patch the Ubuntu-only apt URLs, then bootstrap / install only Claude Code and pstack / stop and rebuild on Ubuntu
**Chosen:** Patch, then bootstrap. The Docker and Tailscale apt URLs take the distro from `ansible_facts['distribution'] | lower`, which is still `ubuntu` on supermicro and dev-server-frank. Other Debian gaps get fixed as the first run finds them.
**Decided-by:** human
**Justification:** Both vendors publish a `debian/trixie` repo (checked 2026-10-19, HTTP 200). With the Ubuntu URL, Docker's source would 404 and break every later `apt update` on the host.
**Outcome:** applied
**Ref:** (this commit)

## Q51 — interactive/grokbot-box — deviation

**Question:** On Debian, Ansible stops with "could not initialize the preferred locale", because ssh forwards `LANG=en_US.UTF-8` and the image has no such locale. Where should the fix go?
**Options considered:** generate en_US.UTF-8 in `bootstrap.sh` / force `LC_ALL=C.UTF-8` in each ssh command / stop forwarding LANG from the Macs
**Chosen:** `bootstrap.sh` installs `locales` and generates en_US.UTF-8 when `locale -a` lacks it. It skips that step on Ubuntu, where the locale is already present.
**Decided-by:** agent
**Justification:** It fixes the host once, so the nightly sweep's ssh command stays the same for every host. Measured on grokbot-box 2026-10-19: `locale -a` listed only C, C.utf8 and POSIX.
**Outcome:** applied
**Ref:** (this commit)

## Q52 — interactive/grokbot-box — deviation

**Question:** grokbot-box is a container whose PID 1 is `tini`, not systemd, so the paseo role stopped at `loginctl enable-linger`. orca and tailscale need systemd too. How should the play handle it?
**Options considered:** skip the three roles when `service_mgr` is not systemd / guard each systemd task inside the roles / run the daemons another way (supervisor, a bashrc launcher)
**Chosen:** `main.yml` skips paseo, orca and tailscale when `ansible_facts['service_mgr'] != 'systemd'`. Every systemd host still runs them unchanged.
**Decided-by:** agent
**Justification:** All three roles exist to run a systemd daemon, so guarding task by task would leave half-configured roles. tailscaled already runs on the box in userspace mode, started outside Ansible (checked 2026-10-19). Paseo and Orca servers there are not needed for the gateway work; run them another way only if Frank wants them.
**Outcome:** applied
**Ref:** (this commit)

## Q53 — interactive/grokbot-box — deviation

**Question:** Debian 13 has no `rbw` package, so the bitwarden role failed. How should it get `rbw`?
**Options considered:** build it with cargo on Debian / skip bitwarden on Debian / download a release binary
**Chosen:** On Debian, install `pinentry-curses`, `cargo install rbw`, and link it to `/usr/local/bin/rbw`, where the config tasks expect it. Ubuntu keeps the apt package.
**Decided-by:** agent
**Justification:** cargo is already on the host from the rust role, and the build needs no new trust root. The rest of the role stays the same on both distros.
**Outcome:** applied
**Ref:** 101b246

## Q54 — interactive/grokbot-box — deviation

**Question:** On grokbot-box, Playwright's `install-deps` failed in 2 of 4 full runs because deb.debian.org returned HTTP 500 to its `apt-get update`. Twelve test requests a few minutes later all returned 200. How should the play handle a mirror error that comes and goes?
**Options considered:** retry the task / switch the host to another mirror / rerun the play by hand
**Chosen:** The task retries up to 3 times, 30 s apart.
**Decided-by:** agent
**Justification:** The error is on the mirror's side and short, so a retry fixes it on every host without changing any host's apt sources. A mirror change touches the host's config and needs Frank.
**Outcome:** applied
**Ref:** (this commit)

## Q55 — interactive/pi-default-deepseek — deviation

**Question:** Pi's new default is deepseek-v4.1-flash at thinking level high, but the gateway catalog marks that model non-reasoning, so Pi would ignore "high". Which side should change, and how far should the change reach?
**Options considered:** flip the model to reasoning in Pi's payload / keep it non-reasoning, so "high" applies only to reasoning models; change the three provision repos only / also change the m2 gateway scripts
**Chosen:** In `roles/pi/files/agent`, `defaultModel: cliproxy/deepseek-v4.1-flash` and `defaultThinkingLevel: high`, and the deepseek-v4.1-flash entry gets `reasoning: true`. Only the three provision repos change.
**Decided-by:** human
**Justification:** Frank chose both. A test request through the gateway (Anthropic messages API, thinking enabled) returned a thinking block from deepseek-v4.1-flash, so the flag was wrong. Known conflict: macbook-provision `gateway/cliproxy-assert-pi` still re-asserts `cliproxy/claude-opus-5-5` and `reasoning: false` every hour, and `cliproxy-tier-host.py` reports pi as `DEFAULT=…`. Until those scripts change, the playbook and the hourly job undo each other's change on each host.
**Outcome:** applied
**Ref:** (pending)

## Q56 — interactive/pi-default-deepseek — deviation

**Question:** Pi 1.3.0 ignored `defaultModel: "cliproxy/<id>"` and fell back to the first provider with a key (`anthropic/claude-opus-4-8`). How should the payload name the default?
**Options considered:** keep the combined `provider/id` string / split it into `defaultProvider` + `defaultModel`
**Chosen:** `"defaultProvider": "cliproxy"` and `"defaultModel": "deepseek-v4.1-flash"`.
**Decided-by:** agent
**Justification:** Pi's `dist/core/model-resolver.js` (step 2, "saved default") uses the saved default only when both `defaultProvider` and `defaultModel` are set, and it looks the model up by bare id. A `pi -p --mode json` run afterwards answered from `cliproxy`/`deepseek-v4.1-flash`, with a thinking block. So the earlier `cliproxy/claude-opus-5-5` value probably never took effect either. `cliproxy-assert-pi` and `cliproxy-tier-host.py` still write and check the combined form, so the hourly re-assert would set an id Pi cannot resolve.
**Outcome:** applied
**Ref:** (pending)
