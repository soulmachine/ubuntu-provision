# context-mode role (removal only)

[context-mode](https://github.com/mksglu/context-mode) is retired fleet-wide. Claude Code's
experimental code mode (`CLAUDE_CODE_EXPERIMENTAL_CODE_MODE=1`, set in the `claude-code` role's
`env` map) takes over its job of keeping bulky tool output out of the context.

This role removes context-mode from every agent the old install role put it into:

| Agent | How it goes |
|---|---|
| Claude Code | `claude plugin uninstall context-mode@context-mode`, then `claude plugin marketplace remove context-mode` |
| Codex | `codex plugin remove context-mode@context-mode`, then `codex plugin marketplace remove context-mode` |
| OpenCode | `files/strip-context-mode.py` drops it from `plugin` in `~/.config/opencode/opencode.json` |
| Copilot CLI | the script drops the MCP server from `~/.copilot/mcp-config.json`; the role deletes the hooks file and the `/ctx-*` skills |
| kimi-code | the script drops the MCP server from `~/.kimi-code/mcp.json` |
| pi | the `pi` role no longer lists `npm:context-mode`; this role runs `npm uninstall` in pi's prefix |
| oh-my-pi | `omp plugin uninstall context-mode` |
| OpenClaw | `openclaw plugins uninstall context-mode`, where OpenClaw is onboarded |
| global CLI | `npm uninstall -g context-mode`, last, because the hooks called it |

Each step reads state first and does nothing on a clean host. The last task fails if anything is
left. The JSON files carry API keys: the script never prints them and keeps each file's mode.

Delete this role, and its lines in `main.yml`, `README.md` and `AGENTS.md`, once every host passes.
