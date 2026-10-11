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
