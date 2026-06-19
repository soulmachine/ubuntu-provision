# Ubuntu Provision

使用 Ansible 自动化 **Ubuntu（无头服务器）** 开发环境配置：系统软件通过 **apt** 安装，语言运行时通过 [mise](https://github.com/jdx/mise) 管理，其余工具沿用官方的 `curl | sh` 安装脚本与 `npm` / `bun` 全局包。

本仓库是同目录 `macbook-provision`（macOS 版）的 Ubuntu 移植版，目标 **Ubuntu 24.04 LTS（amd64 + arm64）**。

## 语言运行时

本项目使用 [mise](https://github.com/jdx/mise) 安装语言运行时（Go、Node.js、JDK 等），而非系统包管理器。mise 是一个多语言版本管理工具，支持在同一台机器上安装和切换多个版本，例如在 JDK 22 和 JDK 23 之间自由切换。mise 跨平台，所以这部分与 macOS 版完全一致。

## 使用方法

### 1. 安装 Ansible

```bash
./bootstrap.sh
```

该脚本会自动安装 apt 基础依赖（`build-essential`、`curl`、`git`、`python3` / `python3-apt` 等）、mise、Python 和 Ansible，并配置免密 sudo（passwordless sudo）。运行结束后请打开一个新的 shell（或 `source ~/.bashrc`），以便 mise 进入 PATH。

> **关于免密 sudo**：Ansible 中标注 `become: true` 的任务（apt 安装、gh / Docker / Tailscale 的 apt 仓库配置等）都需要 `sudo` 在无人值守时不弹密码。脚本通过在 `/etc/sudoers.d/<用户名>-nopasswd` 写入一条 `<用户名> ALL=(ALL) NOPASSWD: ALL` 规则（权限 0440，写入后用 `visudo -cf` 校验，校验失败自动回滚）来实现免密 sudo。
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

`roles/tailscale` 通过官方 apt 仓库（`pkgs.tailscale.com`）安装 `tailscale`，并以 systemd 服务 `tailscaled` 运行。与 macOS 版不同，Linux 上**没有 GUI 应用、没有 Network Extension**，因此 macOS 版里基于 `systemextensionsctl` 的检测与暂停步骤被整段移除。

> **使用范围说明**：本 role 只把 Tailscale 当作**网络连接层**使用（私有 mesh + MagicDNS），**不启用 Tailscale SSH**。远程 shell 仍然走标准 OpenSSH，Tailscale 只负责提供可达的 mesh 地址。因此 role 里没有 `--ssh` flag、没有 `tag:server` / `tag:laptop` 这些 ACL tag、也没有 ACL `tagOwners` 自动管理。

#### 环境变量

将 `.env.example` 复制为 `.env`，按需填写以下变量，然后 `direnv allow`，最后运行 `ansible-playbook main.yml`：

| 变量 | 作用 | 必填 |
|------|------|------|
| `GH_TOKEN` | 供 `github` role 配置 SSH key、git 签名等（需要 `admin:ssh_signing_key,admin:public_key,user:email,read:user` 权限）。 | 否（不设则跳过 GitHub 配置） |
| `TAILSCALE_AUTH_KEY` | 自动执行 `sudo tailscale up --accept-dns --accept-routes --operator=$USER --auth-key=...` 把本机加入 tailnet。在 https://login.tailscale.com/admin/settings/keys 创建一个 **Reusable** key 即可。 | 否（不设则需手工 `tailscale up`） |
| `TAILSCALE_API_ACCESS_TOKEN` | 通过 Tailscale REST API 关闭本机 node-key 过期（避免节点定期下线）。token 需要 `devices` 写权限。 | 否 |

## 与 macOS 版（macbook-provision）的差异

本仓库与 macOS 版的 `main.yml` 保持 **1:1** 的 role 列表（仅把 `homebrew` 换成 `apt`）。无法在无头 Ubuntu 上落地的 role 以「带说明的空操作（skip-stub）」形式保留，运行时仅打印一条 `debug` 说明，便于日后排查与对照。

| 类别 | Role | 处理方式 |
|------|------|----------|
| 系统包管理 | `homebrew` → `apt` | 用 apt 安装基础 CLI（git、curl、jq、ripgrep、fd-find、ffmpeg…）；gh、Docker 各加官方 apt 仓库；`fdfind` 软链为 `fd` |
| 仅 macOS，无 Linux 版 | `apple-container` | skip-stub（Linux 用 Docker，已由 apt role 安装） |
| 仅 macOS，无 Linux 版 | `moshi`、`cmux`、`paseo` | skip-stub |
| GUI 桌面应用（有 Linux 版，但无头不装） | `ghostty`、`intellij-idea`、`webstorm`、`cc-switch` | skip-stub，真实安装命令保留在各自 `tasks/main.yml` 注释里 |
| 部分保留 | `obsidian` | 跳过 GUI 应用，仍安装 Defuddle CLI 与 obsidian 技能 |
| 机制翻译 | `tailscale` | apt 仓库 + systemd（取代 cask + Network Extension） |
| 机制翻译 | `zellij` | GitHub release 二进制（取代 brew） |
| 机制翻译 | `herdr`、`multica-cli` | 官方 `curl` 安装脚本（取代 brew tap） |
| 机制翻译 | `direnv`、`tmux` | apt（取代 brew） |
| 机制翻译 | `oh-my-zsh` | 先 apt 装 zsh，再用 `chsh`/`user` 模块改默认 shell（取代 macOS 的 `dscl`） |

macOS `homebrew` role 里安装的 GUI cask（Claude / Codex / Gemini / ChatGPT 桌面版、pearcleaner、PyCharm、Sublime Text、VS Code）在无头 Ubuntu 上直接省略，未单独建 stub。

## 致谢

本项目移植自 [soulmachine/macbook-provision](https://github.com/soulmachine/macbook-provision)，后者参考了 [hayajo/macbook-provision](https://github.com/hayajo/macbook-provision)。
