# Ubuntu Provision

使用 Ansible 自动化 **Ubuntu（无头服务器）** 开发环境配置：系统软件通过 **apt** 安装，其余工具沿用官方的 `curl | sh` 安装脚本与 `npm` / `bun` 全局包。

本仓库是同目录 `macbook-provision`（macOS 版）的 Ubuntu 移植版，目标 **Ubuntu 24.04 LTS（amd64 + arm64）**，并在 Ubuntu 26.04 上实测通过。

## 语言运行时

本项目使用 [mise](https://github.com/jdx/mise) 安装语言运行时（Go、Node.js、JDK 等），而非系统包管理器。mise 是一个多语言版本管理工具，支持在同一台机器上安装和切换多个版本，例如在 JDK 22 和 JDK 23 之间自由切换。mise 跨平台，所以这部分与 macOS 版完全一致。

## 使用方法

### 1. 安装 Ansible

```bash
./bootstrap.sh
```

该脚本会自动安装 apt 基础依赖（`build-essential`、`curl`、`git`、`python3` / `python3-apt` 等）、mise、Python 和 Ansible，并配置免密 sudo（passwordless sudo）。运行结束后请打开一个新的 shell（或 `source ~/.bashrc`），以便 mise 进入 PATH。

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
ansible localhost -m include_role -a name=openclaw
```

### 3. 试运行（不修改系统）

```bash
ansible-playbook main.yml --check
```

### 4. 可选：Tailscale 配置

`roles/tailscale` 通过官方 apt 仓库（`pkgs.tailscale.com`）安装 `tailscale`，并以 systemd 服务 `tailscaled` 运行。与 macOS 版不同，Linux 上**没有 GUI 应用、没有 Network Extension**，MagicDNS 由 `tailscaled` 直接处理；因此 macOS 版里基于 `systemextensionsctl` 的扩展检测与暂停步骤被整段移除。

> **使用范围说明**：本 role 只把 Tailscale 当作**网络连接层**使用（私有 mesh + MagicDNS），**不启用 Tailscale SSH** 这个 feature。远程 shell 仍然走标准 OpenSSH，Tailscale 只负责提供可达的 mesh 地址。也正因为如此，role 里没有 `--ssh` flag、没有 `tag:server` / `tag:laptop` 这些 ACL tag、也没有 ACL `tagOwners` 自动管理。如果之后改用 Tailscale SSH，需要重新加回 `--ssh`，以及（如果想按机器粒度限制 ACL）`--advertise-tags` 和通过 API 维护 `tagOwners`。

#### 环境变量

将 `.env.example` 复制为 `.env`，按需填写以下变量，然后 `direnv allow`，最后运行 `ansible-playbook main.yml`：

| 变量 | 作用 | 必填 |
|------|------|------|
| `GH_TOKEN` | 供 `github` role 配置 SSH key 与 git 签名（需要 `admin:ssh_signing_key,admin:public_key,user:email,read:user` 权限）。 | 否（不设则跳过 GitHub 配置） |
| `TAILSCALE_AUTH_KEY` | 自动执行 `sudo tailscale up --accept-dns --accept-routes --operator=$USER --auth-key=...` 把本机加入 tailnet。在 https://login.tailscale.com/admin/settings/keys 创建一个 **Reusable** key 即可。 | 否（不设则需手工 `tailscale up`） |
| `TAILSCALE_API_ACCESS_TOKEN` | 通过 Tailscale REST API 关闭本机 node-key 过期（避免节点定期下线）。token 需要 `devices` 写权限。 | 否 |

`tailscale up` flag 说明：

- `--accept-dns`：启用 MagicDNS（需提前在 https://login.tailscale.com/admin/dns 的 tailnet 层面启用一次）。
- `--accept-routes`：接受其他节点广播的子网路由；同时因为 `tailscale up` 不允许悄悄丢弃上次设过的非默认 flag，必须把它一并列出。
- `--operator=$USER`：把当前用户登记为 operator，之后跑 `tailscale status`、`tailscale set` 等命令不再需要 `sudo`。

## 包含的 Roles

### Playbook 中的 Roles（`main.yml`）

| Role | 说明 |
|------|------|
| apt | 基础 CLI 软件包（git、curl、wget、jq、ripgrep、`fd-find`→`fd` 软链、tree、htop、ffmpeg、gnupg 等），并配置 gh、Docker 官方 apt 仓库（取代 macOS 的 `homebrew` role） |
| github | 配置 GitHub SSH key 与 git 签名（gh 由 apt role 安装；需 `GH_TOKEN`） |
| oh-my-zsh | Zsh 框架及插件；用 `chsh` 设为默认 shell（取代 macOS 的 `dscl`） |
| direnv | 目录级环境变量管理（apt） |
| uv | Python 包/项目管理器（官方安装脚本） |
| python | Python CLI 工具（yamllint、ansible-lint、ruff、pre-commit、httpie） |
| go | Go 语言（通过 mise 安装） |
| nodejs | Node.js（通过 mise 安装） |
| bun | Bun JavaScript 运行时（官方安装脚本） |
| rust | Rust 工具链（通过官方 rustup 安装；额外含 rust-src、rust-analyzer 组件） |
| jdk | JDK（通过 mise 安装） |
| claude-code | Claude Code CLI、插件及 Claude Code Bridge（依赖 nodejs；CCB 仅 amd64） |
| codex | OpenAI Codex CLI（依赖 nodejs） |
| gemini | Google Gemini CLI（依赖 nodejs） |
| opencode | opencode CLI 及 oh-my-openagent（依赖 nodejs） |
| skills | 为各 agent 安装技能集（baoyu、mattpocock、soulmachine、last30days） |
| smux | smux 多路复用器及技能 |
| playwright | Playwright 及 Chromium（含 Linux `install-deps`，依赖 nodejs） |
| playwright-cli | Playwright CLI 及技能 |
| openclaw | OpenClaw 及 ClawHub CLI 与配置（依赖 nodejs） |
| claude-mem | claude-mem 记忆插件，接入各 agent（依赖 nodejs/bun/uv 等） |
| beads | Beads 任务追踪工具（依赖 go、nodejs） |
| ralph-tui | Ralph TUI 及技能（依赖 bun、claude-code、codex、gemini、beads） |
| cloudflare | cf CLI 及 Cloudflare 技能（依赖 claude-code） |
| multica-cli | multica CLI 及技能（官方安装脚本，取代 brew tap） |
| tailscale | Tailscale（官方 apt 仓库 + `tailscaled` systemd 服务）；若 `.env` 中有 `TAILSCALE_AUTH_KEY` 则自动登录，可选通过 API token 关闭 key 过期 |
| zellij | Zellij 多路复用器（GitHub release 二进制，取代 brew） |
| tmux | tmux 多路复用器（apt） |
| herdr | herdr 多路复用器（官方安装脚本，取代 brew） |

### 占位（skip-stub）Roles

为与 macOS 版 `main.yml` 保持 **1:1**，以下 role 仍保留在 playbook 中，但在无头 Ubuntu 上只打印一条 `debug` 说明、不做任何安装：

| Role | 原因 |
|------|------|
| moshi、paseo | 仅 macOS，无 Linux 版 |
| cc-switch | GUI 桌面应用，无头 profile 跳过；真实 Ubuntu 安装命令保留在 `tasks/main.yml` 注释中 |

此外，macOS `homebrew` role 里安装的 GUI cask（Claude / Codex / Gemini / ChatGPT 桌面版、pearcleaner、PyCharm、Sublime Text、VS Code）在无头 Ubuntu 上直接省略，未单独建 stub。

### 可选 Roles（未包含在 `main.yml` 中）

| Role | 说明 |
|------|------|
| scrapy | Scrapy 网络爬虫框架（用 apt 的 `libdb-dev` 取代 brew 的 berkeley-db） |

## 致谢

本项目移植自 [soulmachine/macbook-provision](https://github.com/soulmachine/macbook-provision)，后者参考了 [hayajo/macbook-provision](https://github.com/hayajo/macbook-provision)。
