# Ubuntu Provision

使用 Ansible 自动化 **Ubuntu** 开发环境配置：系统软件通过 **apt** 安装，语言运行时交给 mise，其余工具沿用各自官方的 `curl | sh` 安装脚本与 `npm` / `bun` / `uv` 全局包。shell 是 Ubuntu 自带的 **bash**，配 starship、zoxide、fzf 与 Omarchy 的 shell 环境。

本仓库是同目录 `macbook-provision`（macOS 版）的 Ubuntu 移植版，目标 **Ubuntu 26.04 LTS（amd64）**，服务于 supermicro 与 dev-server-frank 两台机器。与上游的对应关系（同步到的 commit、刻意省略的 role）记在 `AGENTS.md` 的 "Upstream" 一节，每一处有意的差异记在 `DECISIONS.md`。

## 语言运行时

本项目使用 [mise](https://github.com/jdx/mise) 安装语言运行时（Go、Node.js、JDK 等），而非系统包管理器。mise 是一个多语言版本管理工具，支持在同一台机器上安装和切换多个版本，例如在 JDK 22 和 JDK 23 之间自由切换。mise 跨平台，所以这部分与 macOS 版完全一致。Python 例外：它由 uv 管理（`bootstrap.sh` 安装 3.14，不覆盖系统的 `python3`）。

## 使用方法

### 1. 安装 Ansible

```bash
./bootstrap.sh
```

该脚本会配置免密 sudo（passwordless sudo），安装 apt 基础依赖（`build-essential`、`curl`、`git`、`python3` / `python3-apt` 等）、uv 与 Python 3.14、mise，最后用 `uv tool install --with ansible ansible-core` 安装 Ansible。它还会把 `~/.local/bin` 与 mise 的 shims 目录加到 `~/.bashrc` 的**非交互守卫之上**（`case $- in` 之前），让 `ssh host 'cmd'` 这类非交互 shell 也能找到它们。

> **关于免密 sudo**：Ansible 中标注 `become: true` 的任务（apt 安装、gh / Docker / Tailscale 的 apt 仓库配置等）都需要 `sudo` 在无人值守时不弹密码框。脚本通过在 `/etc/sudoers.d/<用户名>-nopasswd` 写入一条 `<用户名> ALL=(ALL) NOPASSWD: ALL` 规则（权限 0440，写入后用 `visudo -cf` 校验，校验失败自动回滚）来实现免密 sudo，使整个 provisioning 过程无需人工输入密码。
>
> 首次运行会一次性提示输入用户密码（用于写入 sudoers 文件），之后所有 `sudo` 调用都免密。`bootstrap.sh` 重复执行时若该 drop-in 文件已存在会自动跳过。
>
> **安全提示**：`NOPASSWD: ALL` 意味着以当前用户身份运行的任何进程都能静默取得 root 权限。如需收紧，可改为仅对特定命令免密。

### 2. 运行 Playbook

```bash
ansible-playbook main.yml
```

运行单个 role：

```bash
ansible-playbook role.yml -e role_name=hermes
```

`role.yml` 会先收集 facts。Ansible 自带的单 role 形式 `ansible localhost -m include_role -a name=<role>` 不收集 facts，所以读取 `ansible_facts` 的 role（agent-sync、python、apt）在那种形式下会失败。

上游用 `host-facts` role 判断机器是否常驻开机，再决定装不装 `hermes`、`ponytail`、`paseo`。本仓库没有这个 role：Linux 主机一律视为常驻开机，这三个 role **无条件安装**（DECISIONS Q9），所以单 role 命令不需要任何额外参数。

### 3. 试运行（不修改系统）

```bash
ansible-playbook main.yml --check
```

### 4. 可选：Tailscale 配置

`roles/tailscale` 通过官方 apt 仓库（`pkgs.tailscale.com`）安装 `tailscale`，并以 systemd 服务 `tailscaled` 运行。与 macOS 版不同，Linux 上**没有 GUI 应用、没有 Network Extension**，MagicDNS 由 `tailscaled` 直接处理；因此 macOS 版里基于 `systemextensionsctl` 的扩展检测与 CLI launcher 检查都不存在。

> **使用范围说明**：本 role 只把 Tailscale 当作**网络连接层**使用（私有 mesh + MagicDNS），**不启用 Tailscale SSH** 这个 feature。远程 shell 仍然走标准 OpenSSH，Tailscale 只负责提供可达的 mesh 地址。也正因为如此，role 里没有 `--ssh` flag、没有 `tag:server` / `tag:laptop` 这些 ACL tag、也没有 ACL `tagOwners` 自动管理。如果之后改用 Tailscale SSH，需要重新加回 `--ssh`，以及（如果想按机器粒度限制 ACL）`--advertise-tags` 和通过 API 维护 `tagOwners`。

#### 环境变量

将 `.env.example` 复制为 `.env`，按需填写以下变量，然后运行 `ansible-playbook main.yml`。`dotenv` role 会把 `.env` 的内容以托管块写进 `~/.bashrc` 的非交互守卫之上，所以非交互 shell 也读得到；交互 shell 则由 direnv（`.envrc`）加载。

| 变量 | 作用 | 必填 |
|------|------|------|
| `TAILSCALE_AUTH_KEY` | 自动执行 `sudo tailscale up --accept-dns --accept-routes --operator=$USER --auth-key=...` 把本机加入 tailnet。在 https://login.tailscale.com/admin/settings/keys 创建一个 **Reusable** key 即可。 | 否（不设则需手工 `tailscale up`） |
| `TAILSCALE_OAUTH_CLIENT_ID` + `TAILSCALE_OAUTH_CLIENT_SECRET` | 通过 Tailscale REST API 关闭本机 node-key 过期（避免节点定期下线）。在 https://login.tailscale.com/admin/settings/trust-credentials 创建 OAuth client，勾选 `devices:core` 写权限即可。client secret **不过期**，归属于 tailnet 而非个人。两个变量要么都设，要么都不设；只设一个会让 play 直接失败。 | 否 |
| `TYPESAFE_API_KEY` | `typesafe` role 用它给 fast-jev-compaction 与 claude-jev 两个 Claude Code 插件授权：写入 `~/.claude/settings.json` 的 `env`（同时写入 `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS=1`）。在 https://console.typesafe.ai/keys 创建。 | 否（不设则跳过这两个插件；`typesafe-ai` skill 仍会安装） |

`GITHUB_TOKEN` **不在 `.env` 里**：个人机器上由 mac-mini-m6 的 `gh-token-fleet` 写入 shell 启动文件，`github`、`bun`、`mise` 三个 role 从环境读取它，读不到时退回 `gh auth token`。见 `docs/secrets.md`。

`tailscale up` flag 说明：

- `--accept-dns`：启用 MagicDNS（需提前在 https://login.tailscale.com/admin/dns 的 tailnet 层面启用一次）。
- `--accept-routes`：接受其他节点广播的子网路由；同时因为 `tailscale up` 不允许悄悄丢弃上次设过的非默认 flag，必须把它一并列出。
- `--operator=$USER`：把当前用户登记为 operator，之后跑 `tailscale status`、`tailscale set` 等命令不再需要 `sudo`。

> `TAILSCALE_API_ACCESS_TOKEN`（个人 API access token）**已不再支持**：它是 fully-permitted（没有 scope）且 90 天后过期。`.env` 里若只有它而没有 OAuth client，role 会直接失败并给出迁移说明。

### 5. 可选：启用 pre-commit 检查

```bash
pre-commit install
```

仓库自带五条 `repo: local` 检查，针对的都是本仓库自身的不变量：`ansible-lint`（production profile）、`DECISIONS.md` 编号连续性、README role 表与 `main.yml` 的顺序一致性、`AGENTS.md` 里 `lookup('env', 'HOME')` 计数的准确性、skills role 孤儿规则的自测。五条在干净工作树上都通过，所以新出现的失败是**可见的**，而不会淹没在既有噪音里。

`pre-commit install` 写入的是 `.git/hooks/pre-commit`，**git 不携带这个文件**，所以每个 clone 都要各自执行一次。想手工跑一遍全部检查：

```bash
pre-commit run --all-files
```

## 包含的 Roles

### Playbook 中的 Roles（`main.yml`）

按 `main.yml` 中的执行顺序排列，顺序与上游 `macbook-provision` 一致，只是去掉了没有 Linux 版或属于 GUI 的 role（host-facts、homebrew、cua、cc-switch、ghostty、cmux、intellij-idea、obsidian、apple-container、moshi、removemacai、macos-connectors、ego-browser）。

| Role | 说明 |
|------|------|
| apt | 基础 CLI 软件包（git、curl、wget、jq、ripgrep、`fd-find`→`fd` 软链、tree、htop、ffmpeg、gnupg 等），配置 gh、Docker 官方 apt 仓库；每次运行先 `apt full-upgrade` 并 autoremove，失败时记录下来、在 play 末尾才报错，不阻断后面的 role（取代 macOS 的 `homebrew` role） |
| github | 通过 `setup_github.sh` 生成并上传 SSH 认证密钥与签名密钥，配置 git 签名（gh 由 apt role 安装）；需要环境中的 `GITHUB_TOKEN`，token 过期时只告警不中断 |
| shell | Ubuntu 自带 bash 的基础配置：apt 装 starship、zoxide、fzf、bash-completion；`~/.config/bash/` 放 Omarchy 的历史记录、补全、readline 设置与三者的 hook；登录 shell 设回 `/bin/bash`，并清掉旧 oh-my-zsh role 留下的 `~/.oh-my-zsh` |
| omarchy | Omarchy 的 shell 环境原样部署（Omarchy 本就是 bash）：aliases、envs、fns 与 Omarchy 的 `starship.toml`；apt 装 eza、bat（`batcat`→`bat` 软链）、neovim、gum、inotify-tools、rsync（依赖 shell） |
| direnv | 目录级环境变量管理（apt），并在 `~/.bashrc` 挂载 hook |
| dotenv | 不装任何软件；把 `.env` 以托管块写入 `~/.bashrc` 的非交互守卫之上，让非交互式 shell（`ssh host 'cmd'`、git hook、systemd）也能读到其中的变量 |
| uv | Python 包与工具管理器（通过官方 astral.sh 脚本安装）；每次 `uv self update`，按版本差异判定变更，并写入 bash 补全 |
| python | 用 `uv tool install <tool>@latest` 安装 Python 命令行工具：yamllint、ansible-lint、ruff、pre-commit、httpie；arm64/aarch64 另加 openai-whisper、whisper-ctranslate2（依赖 uv） |
| mise | 运行时版本管理器（由 bootstrap.sh 独立安装）；本 role 用 `mise self-update` 保持其最新，并维护 `~/.bashrc` 里的三行（`~/.local/bin` 与 shims 的 PATH 在守卫之上，`mise activate bash` 在末尾）；go、nodejs、jdk 都建立在它之上 |
| go | Go 语言（通过 mise 安装），按 `mise ls --json` 前后差异判定变更 |
| nodejs | Node.js LTS（通过 mise 安装）并 `mise upgrade node` 到最新 LTS 补丁版 |
| bun | Bun JavaScript 运行时；每次 `bun upgrade`，借用 `gh auth token` 绕过 GitHub API 限流，按版本差异判定变更 |
| rust | Rust 工具链（通过官方 rustup 安装；额外含 rust-src、rust-analyzer 组件），按组件列表差异判定变更 |
| jdk | JDK LTS（通过 mise 安装）并 `mise upgrade java` 到最新 LTS 补丁版 |
| claude-code | Claude Code CLI 及插件；`~/.claude/settings.json` 的合并与 `claude-yolo` 别名（依赖 nodejs） |
| claude-extras | Claude Code 周边工具：npm `@inulute/cux`、uv 工具 `claude-swap`（依赖 nodejs、uv、claude-code） |
| typesafe | TypeSafe Jev 模型相关的一切：官方 `typesafe-ai` skill（不需要 key），以及两个 Claude Code 插件 fast-jev-compaction 与 claude-jev；把 `CLAUDE_CODE_ENABLE_FUNCTION_HOOKS` 与 `TYPESAFE_API_KEY` 写入 `~/.claude/settings.json` 的 `env`；`.env` 无 `TYPESAFE_API_KEY` 时只跳过插件部分（依赖 claude-code、nodejs） |
| 1password | 1Password 桌面 App 与官方 CLI `op`，都来自 1Password 的 apt 仓库，由 apt role 升级；仓库的 keyring 与 `/etc/apt/sources.list.d/1password.sources` 和 `1password` 包的 postinst 写的逐字节相同，两边互不覆盖；没有桌面会话的主机（dev-server-frank）只装 CLI；再装官方 Claude Code 插件 [`1password@1password`](https://github.com/1Password/1password-claude-plugin)；App 的 Settings → Developer 中「Integrate with 1Password CLI」与「Integrate with MCP clients」两个开关和登录需手动（依赖 claude-code） |
| bitwarden | Bitwarden 客户端（用于自建的 Vaultwarden）：apt `rbw`（依赖 `pinentry-curses`，ssh 下可用）、npm 全局 `@bitwarden/cli`（命令 `bw`）；有桌面会话（`/usr/share/xsessions` 或 `/usr/share/wayland-sessions` 下有 `.desktop`）的主机再装官方 Electron 桌面 App：跟随 `vault.bitwarden.com` 下载链接的重定向得到最新 `.deb` 的版本，与 `dpkg-query` 不同才下载安装（supermicro 装，dev-server-frank 无桌面跳过）；再把 `bw` 的 server 与 `rbw` 的 `base_url`/`email` 设为 `https://vaultwarden.soulmachine.me` 与 `soulmachine@gmail.com`（先读、不同才写）；桌面 App 的服务器与所有登录仍需手动（依赖 nodejs） |
| codex | OpenAI Codex CLI（npm `@openai/codex`），并安装 [open-pstack](https://github.com/ericlitman/open-pstack) 的 `pstack` 插件（Claude Code 那一半在 claude-code role 的插件列表里；`/pstack:setup-pstack` 需手动运行）（依赖 nodejs） |
| opencode | OpenCode CLI（npm `opencode-ai`）；并用 `npx oh-my-openagent` 写入 `~/.config/opencode/opencode.json`，由版本戳门控，避免每次 play 重装（依赖 nodejs） |
| kimi-code | Kimi Code CLI（通过官方 code.kimi.com 脚本安装）；`kimi upgrade` 报告有新版时重跑安装脚本 |
| omp | oh-my-pi：bun 全局 `@oh-my-pi/pi-coding-agent`，bash 补全与 `omp-yolo` 别名（依赖 bun） |
| pi | pi coding agent：bun 全局 `@earendil-works/pi-coding-agent`，并下发 `~/.pi/agent/` 下的 settings、models 与扩展（依赖 bun） |
| copilot | GitHub Copilot CLI（npm `@github/copilot`）；只经 CLIProxyAPI 使用：`copilot-gw` 由 mac-mini-m2 上的 `cliproxy-tier` 写入（依赖 nodejs） |
| crush | Crush（Charm，npm `@charmland/crush`）；`~/.config/crush/crushrc` 里的网关 provider 由 `cliproxy-tier` 写入（依赖 nodejs） |
| gemini | Gemini CLI（npm `@google/gemini-cli`）；`gemini-gw` 与（没有 Google 登录时）`~/.gemini/settings.json` 由 `cliproxy-tier` 写入（依赖 nodejs） |
| grok | Grok CLI（xAI，npm `@xai-official/grok`，首次运行时下载原生二进制到 `~/.grok/bin`）；`~/.grok/config.toml` 的网关模型由 `cliproxy-tier` 写入（依赖 nodejs） |
| openclaw | OpenClaw（npm `openclaw`）；onboarding、网关 provider 与常驻 daemon 由 mac-mini-m2 上的 `cliproxy-tier` 负责（依赖 nodejs） |
| agent-sync | 把 `~/.agents/` 同步到每个已安装 agent 的技能目录与指令文件；从 GitHub release 下载 linux-x64/arm64 tar 包到 `~/.local/bin`，按最新 release 版本号更新，SHA256SUMS.txt 校验 |
| skills | 用 `npx skills@latest add` 安装所有技能源到 `~/.agents/skills`（每次运行都刷新，以 store 指纹判断 changed），部分源按名单安装；用 `agent-sync adopt` 收编 `~/github.com/soulmachine/skills` 与 OpenSWE 仓库中的自写技能，`agent-sync sync` 扇出，并检查各 agent 的指令接线；孤儿目录只报告不删除（依赖 claude-code、codex、agent-sync） |
| agent-reach | 多渠道触达工具；上游只提供面向 AI agent 的安装文档，故由 `claude-gw -p` 按文档驱动安装；不装 OpenCLI（依赖 claude-code、python、nodejs、github） |
| playwright | 浏览器自动化：npm 全局 `playwright@latest`，`install-deps` 安装系统依赖，按 `--dry-run` 判断是否需要下载 Chromium，锁冲突时重试（依赖 nodejs） |
| playwright-cli | Playwright CLI：npm 全局 `@playwright/cli@latest`，每次先删除再全局安装其 skill，按校验和判定变更（依赖 playwright） |
| claude-mem | Claude 记忆插件；`npx -y claude-mem install` 为 claude-code / codex-cli / opencode 三者接线，observer 走 fleet gateway（依赖 nodejs、bun、uv、claude-code、codex、opencode） |
| hermes | Hermes 个人 agent（Nous Research），并把 `~/.hermes/SOUL.md` 链接到 `~/.agents/AGENTS.md`；Linux 主机常驻开机，无条件安装 |
| browseros-neo | [BrowserOS neo](https://browseros.com)（给 agent 用的 Chromium 浏览器）：**仅 supermicro**（`browseros_neo_hosts`；dev-server-frank 无桌面）；apt 安装上游 `https://cdn.browseros.com/download/BrowserOS_neo.deb`（包名 `browserclaw`，每次下载、版本变了才升级）；把 MCP 端点 `http://127.0.0.1:9010/mcp`（neo 的 proxy 端口；文档里的 9200 不对）注册给每个已安装的 agent：Claude Code、codex、gemini、copilot、grok、hermes 用各自的 `mcp add`，kimi、omp、opencode、crush 合并进各自的 JSON 配置；URL 不对就替换（pi 不支持 MCP）；首次安装上游 `browseros-neo` skill，之后由运行中的 neo 自己更新。不开机自启（依赖 claude-code、nodejs） |
| ponytail | 给所有 agent 安装 [ponytail](https://github.com/DietrichGebert/ponytail) 插件：Claude Code / Codex / OpenCode / pi / oh-my-pi / Hermes 各用其原生安装方式（依赖 nodejs、claude-code、codex、opencode、pi、omp、hermes） |
| paseo | agent 多路复用：npm 全局 `@getpaseo/cli`（CLI + daemon），daemon 以 systemd user unit 运行（`bash -lc`，开启 linger），启用 relay（配对仍需手动 `paseo daemon pair`）与插件并安装 `npm:@oliexe/paseo-bots`；daemon 未运行时记录下来、在 play 末尾才报错；tag `agent-multiplexer`（依赖 nodejs、claude-code、codex） |
| orca | [Orca](https://onorca.dev)（多 agent IDE）的服务端：Orca 没有单独的服务端包，CLI 和 `orca serve` 都在应用里，所以从 GitHub release 装 `orca-ide_<版本>_<arch>.deb`（版本由 releases/latest 的跳转得出，与 `dpkg-query` 不同才装；CLI 是 `/usr/bin/orca-ide`），开启 linger，再用上游的 `orca-ide serve service install --port 6768` 装 systemd user unit `orca-serve`（`--supervise --no-pairing`），只在服务不是 `live` 时安装；当前 Orca 还没有这个子命令时跳过并提示；服务未 live 时在 play 末尾才报错。配对仍需手动；tag `agent-multiplexer`（依赖 claude-code、codex） |
| cloudflare | Cloudflare CLI：npm 全局 `cf`（其 skills 由 skills role 安装）（依赖 claude-code） |
| multica-cli | 通过官方 install.sh 安装 multica CLI，并以相对路径链接其 skill |
| purelymail | Purelymail API CLI，GitHub release 二进制装入 `~/.local/bin`，跟随最新 release；token 手工放在 `~/.profile` |
| email | Himalaya 邮件 CLI + ortie OAuth CLI（GitHub release 二进制装入 `~/.local/bin`，跟随最新 release，Ubuntu 无 apt 包）+ Proton Mail Bridge（GitHub release 的 amd64 .deb，Proton 无 apt 源）；账号配置手工完成 |
| tailscale | 从官方 apt 源安装 tailscale 并启用 systemd 服务；设了 `TAILSCALE_AUTH_KEY` 时自动加入 tailnet；设了 OAuth client 时关闭节点密钥过期 |
| zellij | 终端复用器（GitHub release 的静态二进制）；tag `terminal-multiplexer` |
| tmux | 终端复用器（apt）；tag `terminal-multiplexer` |
| herdr | 从 herdr.dev 安装脚本安装 herdr，按 `latest.json` 版本差异更新；安装 herdr skill 并以相对符号链接接入 `~/.claude/skills`，`~/.bashrc` 加入给终端标题加主机名的 `herdr()` 包装函数；并用 herdr-rename-hook skill 的 `install.sh` 接上 `/rename` 钩子（Claude Code 与 Codex 的 `/rename` 同步成 Herdr 的 agent、pane 和 tab 名）；tag `terminal-multiplexer` |

### 与 macOS 版的差异

- **shell 是 bash。** 上游用 zsh；这里每个 role 往 `~/.bashrc` 写别名、hook 与补全，都放在文件末尾（只对交互 shell 生效）；每个 shell 都要看到的行（PATH、`.env` 的密钥）放在 `case $- in` 守卫之上。
- **没有 host-facts。** 上游按机型判断是否常驻开机；这里 Linux 主机一律常驻，hermes、ponytail、paseo 无条件安装。
- **没有 GUI。** 上游的桌面应用、编辑器、cc-switch、ghostty、obsidian 等一概不装，也不留空 role。例外只有三个：browseros-neo 只装在 supermicro，bitwarden 与 1password 的桌面 App 只装在有桌面会话的主机。
- **apt 会升级。** `apt` role 每次 `full-upgrade`，对应上游的 `brew upgrade`；内核升级后需要手工重启。
- **gateway 是前提。** claude-mem 的 observer、agent-reach 与 pi 的默认模型都走 mac-mini-m2 上的 CLIProxyAPI（`CLIPROXY_API_KEY` / `CLIPROXY_BASE_URL` 与 `claude-gw` 包装脚本由 `cliproxy-tier` 写到每台机器）。没有这些的机器上，这几个 role 会直接失败，这是有意的。

### Agent CLI 与技能

`main.yml` 里有十来个 role 装的是各家 coding agent 的 CLI 和它们共用的技能（skills）。上面的表格每个 role 只有一行，而这一块恰恰有几处「一行说不清、说清了反而容易误解」的地方，集中写在这里。

#### 安装渠道各不相同

| 工具 | 安装渠道 | 落地位置 / 命令名 |
|------|----------|-------------------|
| claude-code | 官方 `install.sh` | `~/.local/bin/claude` |
| codex | npm 全局 `@openai/codex` | 命令 `codex` |
| opencode | npm 全局 `opencode-ai` | 命令 `opencode` |
| kimi-code | 官方 `install.sh`（curl \| bash） | `~/.kimi-code/bin/kimi`，命令是 **`kimi`** 而不是 `kimi-code` |
| omp | bun 全局 `@oh-my-pi/pi-coding-agent` | `~/.bun/bin/omp`，命令是 **`omp`** |
| pi | bun 全局 `@earendil-works/pi-coding-agent` | `~/.bun/bin/pi` |
| copilot | npm 全局 `@github/copilot` | 命令 `copilot`；经网关用 `copilot-gw` |
| crush | npm 全局 `@charmland/crush` | 命令 `crush` |
| gemini | npm 全局 `@google/gemini-cli` | 命令 `gemini`；经网关用 `gemini-gw` |
| grok | npm 全局 `@xai-official/grok` | 命令 `grok`；原生二进制在 `~/.grok/bin` |
| openclaw | npm 全局 `openclaw` | 命令 `openclaw`；常驻 daemon 由 `cliproxy-tier` 的 onboarding 安装 |
| claude-mem | `npx -y claude-mem install` | 不是独立命令，而是 Claude Code 插件，同时接线 codex-cli 和 opencode |
| agent-reach | **没有包管理器**，见下 | 由 `claude-gw -p` 按上游文档安装 |

这五个 agent（copilot、crush、gemini、grok、openclaw）只在没有别的渠道（mise 工具、`~/.local/bin` 里的原生安装器、Homebrew）提供同名命令时才用 npm 安装和升级，否则 role 只打印已有的路径，交给那个渠道去升级，免得 `PATH` 上出现两份。

#### 每次运行都会被覆盖的配置文件

**`~/.pi/agent/settings.json` 每次 play 都会被仓库里的版本整个覆盖。** `pi` role 用 `copy: src=agent/ dest=~/.pi/agent/` 下发整个目录，没有任何 gate，所以在 pi 里通过 `/settings` 改的东西会在下一次 provisioning 时被抹掉。要让改动活下来，得改 `roles/pi/files/agent/` 里的文件。这是一次**合并**而不是同步：`~/.pi/agent/` 下面没被 payload 覆盖到的东西（尤其是 `skills` role 维护的 `~/.pi/agent/skills/`）不受影响。

另一处是 `~/.config/opencode/opencode.json`，由 `npx oh-my-openagent` 重写。这一步有 gate：配置里没有 `oh-my-openagent` 字样，或者 npm 上的版本与 `~/.config/opencode/.oh-my-openagent-version` 记录的不一致时才跑。

#### 技能：一个存储 + 符号链接扇出

所有技能只存在一份，在 `~/.agents/skills/`。`skills` role 用 `npx skills@latest add` 安装各个源，然后由 CLI 扇出到各 agent。**不是每个 agent 都拿符号链接**：Claude Code、pi、Hermes 的技能目录是指回存储的符号链接农场；而 Codex、OpenCode、Kimi Code 属于 CLI 所说的「universal agent」，它们**直接读 `~/.agents/skills/`**，永远不会收到链接。

这个 role **故意不加 gate**，每次 play 都重新跑一遍安装器：这是唯一能把上游改动拉下来的机制。`changed` 由前后对 `~/.agents/skills/` 做校验和指纹比对得出。代价是每个源一次网络请求，是整个 playbook 里最慢的 role 之一。`skills add` **从不删除**任何东西，上游下架的技能会作为孤儿目录留在存储里，role 只报告不删除。

自写技能的收编（`agent-sync adopt`）需要本机有 `~/github.com/soulmachine/skills`、`~/github.com/OpenSWE/herdr-advisor`、`~/github.com/OpenSWE/skills` 这几个 clone；缺哪个就跳过哪个并打印出来。

#### 看起来像报错、其实是预期输出

- **每个技能源都会报两个 per-agent 失败**（Eve 和 PromptScript 拒绝全局安装）。属于正常噪音。
- **Hermes 拒绝安装 ponytail**，理由是插件扫描器给出 `dangerous` 判定。role 把这一种失败明确放行并打印补救办法。要接受这些发现，得自己在 `~/.hermes/config.yaml` 里设 `plugins.scan_on_install: false`。
- 万一某个「只取几个技能」的源里的技能被上游改名或下架，CLI 会退出 1 并打印 `● Available skills:` 加一整份清单。这类失败被**推迟到整个 play 的末尾**才抛出，PLAY RECAP 里依然是 `failed=1`。

#### role 代劳不了、需要人工的步骤

- **Codex 的 hook 信任**是一次性的、每台机器各做一次：跑 `codex`、打开 `/hooks`，审核并信任 ponytail 的三个生命周期 hook，然后开一个新 thread。
- **opencode 的 provider 认证**没有做：安装器带的是 `--skip-auth`。
- **新装的 agent 要在 mac-mini-m2 上跑一次 `cliproxy-tier <host>`。** `copilot-gw`、`gemini-gw`（主机有自己的 Google 登录时 Gemini 保持原生）、grok、crush、openclaw 的网关配置以及 OpenClaw 的 onboarding 都由它完成，而它只处理已经装好的 agent。
- **rename 钩子装上或更新后**，Codex 下次启动会问是否信任这个钩子，选「Trust all and continue」；已经在跑的 Claude Code 会话要打开一次 `/hooks` 或重启才会用上。
- **agent-reach 只配好了零配置的渠道。** 其余渠道要 cookie 或点一下浏览器扩展。要补齐就自己交互式跑一次 `agent-reach doctor`。
- **paseo 的配对**：`paseo daemon pair` 要人拿着设备扫码。
- **orca 的配对**：服务不打印配对链接；先停服务，在终端跑 `orca-ide serve --port 6768 --pairing-address <tailscale-ip>`，把链接贴进客户端的 **Add Server**。
- **`claude-mem` 的模型 id 要手工升级。** `roles/claude-mem/vars/main.yml` 里的模型 id 一旦下架就是一个硬错误，**会让 play 失败**。
