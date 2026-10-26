# agent-reach role

- **An agent installs it, not a script.** Upstream ships `docs/install.md` and `docs/update.md` as
  prompts addressed "For AI Agents". They branch on environment detection, `agent-reach doctor`
  output, and which upstream CLIs exist, so there is no idempotent one-liner. The role runs
  `claude -p "<instruction> <doc URL>"` and lets the sub-agent execute the doc. Plain `claude` reaches
  the gateway with the key in `~/.claude/settings.json` (coding-agent Q665), so it works over the
  nightly sweep's non-interactive ssh, where a claude.ai login cannot unlock the keychain.
  Both calls `chdir` to `$HOME`: `install.md` forbids writing inside the working
  directory, and `$HOME` keeps this repo's `AGENTS.md` out of the sub-agent's context.
- **Idempotency hinges on `agent-reach check-update`'s stdout, not its exit code.** The command
  always exits 0. Install runs only when `command -v agent-reach` fails. Update runs only when
  `check-update` prints the **positive** sentinel `有更新` (Chinese, hardcoded upstream). Keep it
  positive: `check-update` also has a rate-limit/network-error branch (`无法检查更新`) and a
  no-releases branch that prints the latest commit SHA (`最新提交:`), and a negated match fires on
  both, burning a full agent run on every converged play. `有更新` appears in exactly one branch, and
  not in the update instructions that branch prints.
- **The install is verified.** An LLM following prose can report success while landing nothing on
  PATH, so a post-install `command -v agent-reach` fails the play instead of letting every later run
  re-attempt the install.
- **Optional channels are not provisioned.** Twitter, 小红书, Reddit and others need cookies or a
  Chrome-extension click, and headless `claude -p` cannot answer the doc's "which channels?" prompt.
  Only the zero-config core channels are set up. Run `agent-reach doctor` interactively for the rest.
- **OpenCLI is not installed.** Upstream's `tasks/opencli.yml` adds it as agent-reach's X
  fallback, but its Chrome extension needs one manual click in a browser, which a host used over
  ssh never gets.
