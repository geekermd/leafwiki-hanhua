# 🌿 LeafWiki 简体中文版 · leafwiki-zh

**简体中文** | [English](./README.en.md)

[![zh-ci](https://github.com/geekermd/leafwiki-hanhua/actions/workflows/zh-ci.yml/badge.svg)](../../actions/workflows/zh-ci.yml)
[![Release](https://img.shields.io/github/v/release/geekermd/leafwiki-hanhua?style=flat-square&label=%E4%B8%8B%E8%BD%BD)](../../releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Upstream](https://img.shields.io/badge/upstream-v0.13.0-blue.svg)](https://github.com/perber/leafwiki/releases/tag/v0.13.0)
[![Go](https://img.shields.io/badge/Go-1.26-00ADD8.svg)](https://go.dev)

**自托管 wiki。单个 Go 二进制，SQLite + 磁盘 Markdown。**
不需要 Node.js、Redis 或 Postgres —— 一个二进制和一个数据目录就够了。

> [!IMPORTANT]
> 本仓库（`leafwiki-hanhua`）是 [perber/leafwiki](https://github.com/perber/leafwiki) 的**非官方简体中文衍生版**，
> 基于上游 **v0.13.0**，上游不对此衍生版负责。
> 改动只有 **3 处代码 + 1 处用例同步**，逐条列在 **[NOTICE](./NOTICE)** 与下方[差异表](#与上游的差异)；
> 上游原始英文说明保留在 **[README.upstream.md](./README.upstream.md)**。
> 仓库名是 `leafwiki-hanhua`，**安装包与二进制名是 `leafwiki-zh`**（便于与上游区分）。

---

## 🚀 30 秒上手

```bash
# 1) 从 Releases 页面下载 deb 并安装（ARM 设备请换 arm64 那个文件）
sudo apt install ./leafwiki-zh_0.13.0+zh2-1_amd64.deb

# 2) 查看初始管理员口令（首次安装时随机生成）
sudo cat /etc/leafwiki/admin-password.txt

# 3) 浏览器打开 http://localhost:8080
#    用户名 admin，口令见上一步 —— 装完就是中文界面
```

默认只监听 `127.0.0.1`（安全默认值）。要对外提供 HTTPS 访问，见
[反向代理与 HTTPS](#反向代理--https)；其他安装方式（源码构建 / Docker）见[安装](#安装)。

---

## 目录

- [特性](#特性)
- [与上游的差异](#与上游的差异)
- [安装](#安装)
- [快速开始](#快速开始)
- [反向代理与 HTTPS](#反向代理与-https)
- [配置](#配置)
- [中文界面与翻译](#中文界面与翻译)
- [数据、备份与恢复](#数据备份与恢复)
- [目录结构](#目录结构)
- [开发与构建](#开发与构建)
- [升级上游版本](#升级上游版本)
- [常见问题](#常见问题)
- [许可证与致谢](#许可证与致谢)

---

## 特性

基于上游 v0.13.0。标 ★ 的功能需要显式开启对应参数（见[配置](#配置)）。

**内容组织**

- 树状页面结构（页面 / 章节 / 子页面），支持排序
- Markdown 编辑，支持相对链接（仓库内互链）
- 全文搜索、标签、反向链接（backlinks）
- 失效链接检查
- 附件上传，默认单个上限 50 MiB
- ★ 修订历史（`--enable-revision`）：默认保留每页最近 100 个版本，5 分钟内的连续保存自动合并
- 外部编辑：直接改磁盘上的 Markdown 文件后自动重建索引

**用户与权限**

- 角色：管理员 / 编辑者 / 访客
- 三种访问模式：需登录（默认）、公开只读、完全开放
- ★ 邮件邀请与找回密码（需配置 SMTP）
- ★ TOTP 两步验证（需 `--totp-encryption-key`）
- ★ API 密钥管理
- ★ 反向代理认证：信任 `Remote-User` 头，可自动建号（适配企业 SSO）

**备份与运维**

- 快照备份：默认每 24 h 打一个 ZIP（含 SQLite），保留最近 10 个，支持在线恢复与灾难恢复
- ★ Git 备份：定时把 Markdown 推送到 Git 远端（SSH / HTTP(S)）
- ★ Prometheus 指标：独立监听端口
- 结构化日志（text / json）、可关闭逐请求访问日志

**外观与语言**

- 品牌定制：站点名、Logo、网站图标
- 自定义样式表、页头注入自定义 HTML/JS
- 界面语言：**简体中文（本衍生版新增）**、English、Deutsch、Español

---

## 与上游的差异

**3 处代码改动 + 1 处用例同步**，全部是为了让中文界面真正生效：

| 位置 | 改动 | 不改会怎样 |
|---|---|---|
| `ui/leafwiki-ui/src/locales/zh/`（新增目录） | 简体中文语言包：19 个命名空间、**1212 条**文案 | 界面里根本没有中文可选 |
| `internal/usersettings/language.go` | 语言白名单允许 `zh`（经 `DefaultLanguage` 常量），并显式保留 `en` | 在界面上选中文，保存时报 `Language must be one of: ...` |
| `internal/usersettings/models.go` | 常量 `DefaultLanguage` 由 `"en"` 改为 `"zh"` | **登录页中文、登录后变回英文** |
| `internal/usersettings/language_test.go` | 用例同步：白名单期望值加入 `zh` | 上游用例硬断言只有 `de/en/es`，不改则 Go 测试失败 |

第三处最容易漏，原因值得说明：前端 `stores/userSettings.ts` 在加载用户设置时，会用后端返回的语言值
**覆盖**站点级 `--default-language`；而"从未设置过偏好"的用户拿到的正是 `DefaultLanguage`。
所以仅设置默认语言参数只能让登录页变中文。

> ⚠️ 因为 `DefaultLanguage` 已是 `zh`，语言白名单里**不能再显式写 `"zh": true`**，
> 否则 Go 编译报 `duplicate key "zh" in map literal`。

---

## 安装

### 方式一：deb 包（推荐，Debian / Ubuntu）

```bash
sudo apt install ./leafwiki-zh_0.13.0+zh2-1_amd64.deb     # ARM64 请换用 arm64 那个文件
```

装完即得：

| 项目 | 位置 |
|---|---|
| 程序 | `/usr/bin/leafwiki` |
| systemd 服务 | `leafwiki.service`（开机自启，已做加固） |
| 配置（含密钥，600） | `/etc/leafwiki/leafwiki.env` |
| 初始管理员口令 | `/etc/leafwiki/admin-password.txt` |
| 数据目录 | `/var/lib/leafwiki` |
| 默认监听 | `127.0.0.1:8080` |

首次安装会随机生成 JWT 密钥与管理员口令，并**在安装输出里打印**。
升级**不会覆盖**已有的 `/etc/leafwiki/leafwiki.env`，因此密钥、登录态与数据都不受影响。
`apt remove` 只删程序，保留配置与数据（`purge` 也只删系统用户，数据仍保留）。

### 方式二：源码构建

```bash
packaging/build-from-source.sh          # 只出二进制，默认 ./leafwiki
packaging/build-deb.sh ./releases       # 出 deb（默认 amd64 + arm64）
```

依赖 Go **1.26.x**、Node **22+**、`dpkg-deb`。脚本在 `go` 不在 PATH 时会自动使用 `~/.local/go`。

### 方式三：Docker（自建镜像）

仓库保留了上游的 `Dockerfile` / `docker-entrypoint.sh`，它是**从本仓库源码构建**的，
所以自建镜像会包含中文界面：

```bash
docker build -t leafwiki-zh --build-arg APP_VERSION=v0.13.0 .
docker run -d --name leafwiki -p 127.0.0.1:8080:8080 \
  -e LEAFWIKI_JWT_SECRET=your-secret \
  -e LEAFWIKI_ADMIN_PASSWORD=your-password \
  -e LEAFWIKI_ALLOW_INSECURE=true \
  -v leafwiki-data:/app/data leafwiki-zh
```

> 本衍生版未随附预构建镜像，也未对 Docker 路径做单独验证。

### ⚠️ 不要用上游的 `install.sh`

仓库里的 `install.sh` 会从 **GitHub 上游 releases 下载官方二进制**，那里面**不含中文界面**。
需要中文请使用上面三种方式之一。

---

## 快速开始

### 从 deb 安装后

1. 浏览器打开 `http://localhost:8080`
2. 用 `admin` + `/etc/leafwiki/admin-password.txt` 里的口令登录
3. 界面若为英文，去 **设置 → 账户 → 偏好设置 → 语言** 选「简体中文」

服务默认只监听回环地址，这是刻意的安全默认值。要对外提供访问，请看下一节。

### 从源码 / 二进制运行

```bash
# 1) 内部 wiki：全部需要登录（默认）
./leafwiki --jwt-secret=your-secret --admin-password=your-password

# 2) 公开可读，登录后才能编辑
./leafwiki --jwt-secret=your-secret --admin-password=your-password --public-access

# 3) 完全开放，任何人可读可写（仅限可信网络！）
./leafwiki --disable-auth
```

常用参数：`--host`（默认 `127.0.0.1`）、`--port`（默认 `8080`）、`--data-dir`（默认 `./data`）。

### 首次登录后建议做的三件事

1. 在 **设置 → 账户 → 偏好设置** 里把语言固定为简体中文（若默认已是则无需操作）
2. 改掉初始管理员口令
3. 检查数据与快照目录是否符合预期（见[数据、备份与恢复](#数据备份与恢复)）

---

## 反向代理与 HTTPS

LeafWiki 自身只提供 HTTP，**HTTPS 应由反向代理终结**。示例配置见
[`packaging/nginx-leafwiki.conf`](./packaging/nginx-leafwiki.conf)（nginx 监听 `127.0.0.1:8443` 并反代到 `127.0.0.1:8080`）。

```nginx
location / {
    proxy_pass         http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
}
client_max_body_size 50M;   # 与 --max-asset-upload-size 对齐
```

同时把 LeafWiki 的 `LEAFWIKI_TRUSTED_PROXY_IPS` 设为代理所在地址（如 `127.0.0.1`），
它才会信任 `X-Forwarded-*`。若在子路径下提供服务，用 `--base-path=/wiki` 并同步调整代理。

**Cloudflare Tunnel 等内网穿透**：把源站指向 `https://localhost:8443` 即可，
证书建议自带（自签并在系统信任库登记，或 Cloudflare Origin 证书 + 把 Origin CA 根装进信任库）；
若直接用 `http://localhost:8080` 回源，则需接受回源段为明文。

> ⚠️ **纯 HTTP 下无法登录**：LeafWiki 在非 HTTPS 环境会拒绝签发认证 Cookie
> （报 `auth_cookie_failed: HTTPS is required for auth cookies`）。
> 仅在本机可信环境（如本机实验）才可设 `LEAFWIKI_ALLOW_INSECURE=true`，
> 此时 Cookie 会以明文传输。

---

## 配置

优先级：**命令行参数 > 环境变量 > 默认值**（所有参数都有对应的 `LEAFWIKI_*` 环境变量）。
完整列表见 `leafwiki --help`。最常用的几项：

| 参数 | 环境变量 | 默认 | 说明 |
|---|---|---|---|
| `--jwt-secret` | `LEAFWIKI_JWT_SECRET` | — | **必填**（除非 `--disable-auth`）。改动会使所有登录态失效 |
| `--admin-password` | `LEAFWIKI_ADMIN_PASSWORD` | — | 初始管理员口令，**仅在没有管理员时生效** |
| `--admin-username` | `LEAFWIKI_ADMIN_USERNAME` | `admin` | 初始管理员用户名 |
| `--host` / `--port` | `LEAFWIKI_HOST` / `LEAFWIKI_PORT` | `127.0.0.1` / `8080` | 监听地址与端口 |
| `--data-dir` | `LEAFWIKI_DATA_DIR` | `./data` | 数据目录 |
| `--default-language` | `LEAFWIKI_DEFAULT_LANGUAGE` | — | 站点默认语言，本版建议 `zh` |
| `--public-access` | `LEAFWIKI_PUBLIC_ACCESS` | 关 | 允许未登录只读 |
| `--disable-auth` | `LEAFWIKI_DISABLE_AUTH` | 关 | 完全关闭认证（危险） |
| `--allow-insecure` | `LEAFWIKI_ALLOW_INSECURE` | 关 | 允许纯 HTTP 下签发 Cookie（仅限本机） |
| `--trusted-proxy-ips` | `LEAFWIKI_TRUSTED_PROXY_IPS` | — | 信任哪些代理的 `X-Forwarded-*` |
| `--base-path` | `LEAFWIKI_BASE_PATH` | — | 反代子路径，如 `/wiki` |
| `--enable-revision` | `LEAFWIKI_ENABLE_REVISION` | 关 | 开启页面修订历史 |
| `--snapshot` | `LEAFWIKI_SNAPSHOT` | 开 | 快照备份 |
| `--snapshot-interval` | `LEAFWIKI_SNAPSHOT_INTERVAL` | `24h` | 快照间隔，`0` = 只手动 |
| `--snapshot-retention` | `LEAFWIKI_SNAPSHOT_RETENTION` | `10` | 保留最近多少个快照 |
| `--max-asset-upload-size` | `LEAFWIKI_MAX_ASSET_UPLOAD_SIZE` | `50MiB` | 附件单文件上限 |
| `--enable-metrics` | `LEAFWIKI_ENABLE_METRICS` | 关 | 开启 Prometheus `/metrics` |
| `--log-format` | `LEAFWIKI_LOG_FORMAT` | `text` | 日志格式：`text` / `json` |

deb 安装方式下，这些写在 `/etc/leafwiki/leafwiki.env`（权限 600），改完
`sudo systemctl restart leafwiki` 生效。

---

## 中文界面与翻译

**切换语言**：登录后进入 **设置 → 账户 → 偏好设置 → 语言**，选「简体中文」。
该偏好按用户保存；**未设置过偏好的用户**会使用 `DefaultLanguage`，本衍生版已设为 `zh`。

**语言包位置**：`ui/leafwiki-ui/src/locales/zh/`（19 个命名空间文件，共 1212 条）。
前端在构建时自动 glob 该目录，**新增语言无需改动前端代码**；语言切换器的选项也由它生成。

**校验译文**：

```bash
python3 validate_zh.py                  # 校验全部命名空间
python3 validate_zh.py viewer editor    # 只查指定命名空间
```

输出示例（全部 `[OK]` 才算通过）：

```
[OK] common           键   23  缺失  0  多余  0  占位符不符  0  与英文相同   0
[OK] viewer           键  158  缺失  0  多余  0  占位符不符  0  与英文相同   0
结果: 全部通过 ✅
```

**修改译文的硬性规则**（完整术语表见 [`TRANSLATION-SPEC.md`](./TRANSLATION-SPEC.md)）：

1. **键名一个都不能改**：不新增、不删除、不改名、不改层级。
2. **占位符 `{{...}}` 一个不少、不多**，位置可按中文语序调整。
3. 复数键 `_one` / `_other` 都保留，中文两边写一样。
4. **不翻译**：`LeafWiki`、`Markdown`、`Git`、`API`、`JWT`、`TOTP`、`SMTP`、`URL`、快捷键（`Ctrl+K`）、
   文件扩展名、示例域名与路径、`<bold>` 之类标签。
5. 中文用 UTF-8 原文（不要写成 `\uXXXX`）；句子用中文全角标点，短标签不加句末标点。

改完跑一遍 `validate_zh.py`，再重新构建。CI（[`.github/workflows/zh-ci.yml`](./.github/workflows/zh-ci.yml)）
会校验键对齐、占位符、`language.selfName` 是否为「简体中文」，以及后端白名单口径是否正确。

> `validate_zh.py` 中"与英文相同"一列不为 0 是**允许**的：`URL`、`Slug`、`2FA`、
> `application/octet-stream`、排序箭头 `A → Z`、日期格式示例、Git 示例路径等本就该保留英文。

---

## 数据、备份与恢复

数据目录（deb 安装为 `/var/lib/leafwiki`）布局：

```
├── users.db  sessions.db  favorites.db  links.db
├── properties.db  search.db  tags.db  usersettings.db     SQLite（WAL 模式）
├── root/            页面正文（Markdown 存在磁盘上）
├── assets/          上传的附件
├── avatars/  branding/
└── snapshots/       完整备份 ZIP（含 SQLite）
```

**恢复快照**（需先停服务）：

```bash
sudo systemctl stop leafwiki
sudo -u leafwiki /usr/bin/leafwiki --data-dir /var/lib/leafwiki \
     restore-snapshot /var/lib/leafwiki/snapshots/<某个>.zip
sudo systemctl start leafwiki
```

管理员界面里也支持在线恢复（设置 → Full Backup）。

**忘记管理员密码**：

```bash
sudo systemctl stop leafwiki
sudo -u leafwiki /usr/bin/leafwiki --data-dir /var/lib/leafwiki reset-admin-password
sudo systemctl start leafwiki
```

---

## 目录结构

★ = 本衍生版新增或修改；其余为上游 v0.13.0 原样。

```
├── cmd/leafwiki/                程序入口与命令行参数
├── internal/                    后端
│   ├── http/                    路由、中间件、嵌入前端产物
│   ├── wiki/                    页面树、搜索、修订
│   └── usersettings/            ★ language.go / models.go 有改动
├── ui/leafwiki-ui/              前端（React + i18next + Vite）
│   └── src/locales/             语言包目录
│       ├── en/ de/ es/          上游
│       └── zh/                  ★ 简体中文，19 个文件
├── docs/  assets/  e2e/  e2e-proxy/  hacks/  loadtest/  scripts/     上游
├── packaging/                   ★ 构建与打包
│   ├── build-from-source.sh         构建二进制
│   ├── build-deb.sh                 构建并打包 deb（amd64 / arm64）
│   ├── leafwiki.service             加固过的 systemd 单元
│   ├── leafwiki.env.example         配置模板
│   ├── nginx-leafwiki.conf          HTTPS 终结示例
│   ├── README-deb.md                打进 deb 的说明
│   └── DEBIAN/                      control.in 与 preinst/postinst/prerm/postrm
├── .github/workflows/zh-ci.yml  ★ 本衍生版 CI
├── validate_zh.py               ★ 语言包校验脚本
├── TRANSLATION-SPEC.md          ★ 术语表与翻译规范
├── CHANGELOG.md                 ★ 本衍生版变更记录
├── NOTICE                       ★ 归属声明与全部改动
├── README.md                    本文件（中文）
├── README.upstream.md           上游原始英文 README（原样保留）
├── LICENSE                      上游 MIT，原样保留
├── CONTRIBUTING.md / CODE_OF_CONDUCT.md / SECURITY.md / CODEOWNERS   上游
├── Makefile / Dockerfile / docker-entrypoint.sh / install.sh / update.sh   上游
└── go.mod / go.sum / package.json 等                                  上游
```

---

## 开发与构建

**依赖**：Go `1.26.x`（`go.mod` 声明 1.26.0）、Node `22+`（实测 24 可用）。

```bash
# 上游的 Makefile 目标
make ui          # 构建前端到 internal/http/dist
make build       # 构建带嵌入前端的二进制
make test        # Go 测试
make run         # 本地运行

# 本衍生版
packaging/build-from-source.sh       # 一键：校验语言包 → 构建前端 → 编译二进制
packaging/build-deb.sh ./releases    # 一键：出 amd64/arm64 的 deb
python3 validate_zh.py               # 只校验语言包
```

`CGO_ENABLED=0` 即可完成编译（SQLite 用的是纯 Go 实现 `modernc.org/sqlite`），
因此产物是全静态二进制，也能直接交叉编译 arm64。

---

## 升级上游版本

1. 切到新的上游 tag（本仓库基线是 v0.13.0）；
2. 把 `ui/leafwiki-ui/src/locales/zh/` 整个目录复制过去（新增目录，一般无冲突）；
3. 重做两处 Go 改动（`language.go` 白名单、`models.go` 默认语言）。
   若上游改动了这两个文件的结构，注意 `DefaultLanguage` 为 `zh` 时白名单里**不能**再显式写 `"zh": true`；
4. 跑 `python3 validate_zh.py` 与 `packaging/build-deb.sh`，通过后发版；
5. 更新 `CHANGELOG.md` 的版本号与 `NOTICE` 中的基准版本。

翻译是独立目录，与上游代码基本不冲突，升级成本很低。

---

## 常见问题

**Q：界面里没有中文可选？**
说明你用的不是本衍生版的产物。上游官方二进制只内置 `en` / `de` / `es`；
请用本仓库的 deb，或按[方式二](#方式二源码构建)自行构建。特别注意不要用上游的 `install.sh`。

**Q：登录页是中文，登录后变回英文？**
你的账号以前保存过语言偏好（保存过就会覆盖默认值）。去
**设置 → 账户 → 偏好设置 → 语言 → 简体中文** 即可；新用户默认就是中文。

**Q：浏览器打开正常，但登录报错 `auth_cookie_failed`？**
你在用纯 HTTP 访问。LeafWiki 在非 HTTPS 下拒绝签发认证 Cookie：
请配上反向代理提供 HTTPS；本机实验可临时设 `LEAFWIKI_ALLOW_INSECURE=true`。

**Q：为什么默认只监听 `127.0.0.1`？**
安全默认值。请通过反向代理或隧道对外暴露，而不是直接 `--host 0.0.0.0`。

**Q：忘记管理员密码？**
见[数据、备份与恢复](#数据备份与恢复)里的 `reset-admin-password`。
deb 首次安装生成的口令在 `/etc/leafwiki/admin-password.txt`。

**Q：改配置后怎么生效？**
deb 安装方式：改 `/etc/leafwiki/leafwiki.env` 后 `sudo systemctl restart leafwiki`。

**Q：附件上传失败？**
检查 `--max-asset-upload-size`（默认 50 MiB）**以及反向代理的 `client_max_body_size`**，两处都要放开。

**Q：上游的功能和缺陷去哪反馈？**
上游问题请提到[上游仓库](https://github.com/perber/leafwiki/issues)；
本衍生版特有的问题（翻译、deb 打包）请提到本仓库。

---

## 许可证与致谢

- 上游 LeafWiki：**MIT**，Copyright (c) 2025 perber —— [`LICENSE`](./LICENSE) **原样保留，未作修改**。
- 本衍生版新增的翻译与脚本同样以 **MIT** 发布。
- 再次分发时请保留 `LICENSE` 与 [`NOTICE`](./NOTICE)，并说明其非官方性质。
- 上游的商标与项目名归上游作者所有；本衍生版使用 `leafwiki-zh` 作包名与二进制名以作区分。
- 感谢上游作者与所有贡献者 🌿
