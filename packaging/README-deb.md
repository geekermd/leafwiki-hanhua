# LeafWiki 简体中文版（leafwiki-zh）

基于上游 [LeafWiki](https://github.com/perber/leafwiki) v0.13.0 构建的**社区汉化包**。

## 与上游的差异

1. 新增简体中文语言包 `ui/leafwiki-ui/src/locales/zh/`（19 个命名空间、1212 条文案），
   并设置 `language.selfName = 简体中文`，语言切换器里会显示「简体中文」。
2. 后端 `internal/usersettings/language.go` 的语言白名单补入 `"zh"` —— 否则保存语言设置会被拒绝。
3. 后端 `internal/usersettings/models.go` 的 `DefaultLanguage` 由 `en` 改为 `zh` ——
   否则「没有保存过偏好」的用户会被前端用 `en` 覆盖掉站点默认语言，实际仍看到英文界面。
4. 前端语言目录是构建时自动 glob 的，无需其它代码改动。

除此之外与上游 v0.13.0 完全一致（页面以 Markdown 存磁盘、元数据用 SQLite、无外部数据库依赖）。

## 安装后

| 项目 | 位置 |
|---|---|
| 程序 | `/usr/bin/leafwiki` |
| systemd 单元 | `/usr/lib/systemd/system/leafwiki.service` |
| 配置（含密钥，600） | `/etc/leafwiki/leafwiki.env` |
| 初始管理员口令 | `/etc/leafwiki/admin-password.txt` |
| 数据目录 | `/var/lib/leafwiki`（SQLite + Markdown + snapshots） |
| 配置模板 | `/usr/share/doc/leafwiki-zh/leafwiki.env.example` |

初始管理员用户名 `admin`，口令在安装时随机生成并打印、同时写入 `/etc/leafwiki/admin-password.txt`。
**已有 `/etc/leafwiki/leafwiki.env` 时安装脚本不会覆盖**，因此升级不会丢失密钥、登录态或数据。

服务默认只监听 `127.0.0.1:8080`（`LEAFWIKI_HOST=127.0.0.1`）。要对外提供 HTTPS，
请用 nginx 之类做 TLS 终结（示例见 `/usr/share/doc/leafwiki-zh/nginx-leafwiki.conf`），
再由 cloudflared 隧道以 `https://localhost:8443` 回源。

## 常用运维

```bash
sudo systemctl status leafwiki        # 状态
sudo systemctl restart leafwiki       # 改完 /etc/leafwiki/leafwiki.env 后重启
sudo journalctl -u leafwiki -f        # 实时日志
```

## 删除

`apt remove leafwiki-zh` 只停服务、删程序，**保留** `/etc/leafwiki` 与 `/var/lib/leafwiki`。
彻底清理需手动 `sudo rm -rf /etc/leafwiki /var/lib/leafwiki`。
