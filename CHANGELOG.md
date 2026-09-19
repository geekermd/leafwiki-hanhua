# 变更记录

本文件记录 **leafwiki-zh**（简体中文衍生版）的变更。
上游 LeafWiki 自身的变更请见 <https://github.com/perber/leafwiki/releases>。

版本号格式：`<上游版本>+zh<N>-<打包修订>`。
例如 `0.13.0+zh2-1` = 基于上游 v0.13.0 的第 2 版汉化，第 1 次打包修订。

---

## [0.13.0+zh2-1] — 2026-09-19

### 修复

- **默认语言仍然显示英文的问题**：`internal/usersettings/models.go` 的
  `DefaultLanguage` 由 `"en"` 改为 `"zh"`。
  前端 `stores/userSettings.ts` 会用后端返回的该值覆盖站点级 `--default-language`，
  因此仅设置 `LEAFWIKI_DEFAULT_LANGUAGE=zh` 只能让登录页变中文，
  用户登录后会被改回英文。
- **语言白名单重复键**：`DefaultLanguage` 变为 `zh` 后，白名单中
  不能再显式写 `"zh": true`，否则编译报
  `duplicate key "zh" in map literal`。改为显式保留 `"en"`。
- **同步上游用例**：`internal/usersettings/language_test.go` 硬断言白名单只有
  `de/en/es`，加入 `zh` 后必须一并更新，否则 Go 测试失败。
- **版权声明**：`LICENSE` **原样保留上游 MIT 文本（未修改一字）**，这样 GitHub 也能正确识别为 MIT；
  本衍生版自身的修改版权改在 `NOTICE` 的「版权声明」一节单独声明，二者不冲突。

### 仓库工程

- 仓库内容改为**完整源码树**（此前只放了构建产物的压缩包，无法检索、无法 review、CI 跑不了）。
- 二进制改为通过 **GitHub Releases** 分发，不再提交进 git（避免每次发版给历史永久增加约 28 MB）。
- 新增 `validate_zh.py --all`：一次校验语言包键对齐/占位符/JSON，以及
  语言自称、默认语言、白名单口径、用例是否同步；CI 使用同一条命令。
- 新增 `packaging/build-from-source.sh`、`packaging/build-deb.sh`
  （`CGO_ENABLED=0` 静态编译，amd64/arm64 交叉编译）。
- 新增 CI `.github/workflows/zh-ci.yml`：校验 + 双架构出 deb 工件，
  并遵守本仓库 `lint-actions.yml` 的 action-SHA 固定要求。
- 移除上游与本衍生版无关、且会在推送 tag 时误触发上游发布流程的 workflow：
  `release.yml`、`e2e.yml`、`proxy-auth-e2e.yml`、`rebase-command.yml`。
- 移除 `.github/dependabot.yml` 与 `lint-dependabot.yml`：本衍生版刻意与上游使用同一套依赖，
  不做独立的依赖升级，避免与上游分叉、后续合并上游版本时产生冲突。
- 修正 README 中的死链与语言互链，补齐中文/英文双语说明；
  中文 README 顶部新增「30 秒上手」，并把差异表补全为 3 处代码 + 1 处用例。

### 变更

- 语言白名单显式保留 `en`，用户仍可在“设置 → 账户 → 偏好设置”切回英文。

### 打包

- 提供 `.deb`（amd64 / arm64），包名 `leafwiki-zh`：
  安装 `/usr/bin/leafwiki` 与 systemd 单元 `/usr/lib/systemd/system/leafwiki.service`；
  `postinst` 会自动备份非 dpkg 管理的手工安装残留；
  升级不会覆盖既有的 `/etc/leafwiki/leafwiki.env`，因此密钥、登录态与数据都不受影响。

---

## [0.13.0+zh1-1] — 2026-09-19

### 新增

- 简体中文语言包 `ui/leafwiki-ui/src/locales/zh/`：
  **19 个命名空间、1212 条文案**，`language.selfName = "简体中文"`。
- `internal/usersettings/language.go` 语言白名单允许 `zh`
  （不改则界面保存中文时被拒绝）。
- 翻译规范 `TRANSLATION-SPEC.md`（术语表）与校验脚本 `validate_zh.py`
  （键对齐 / 占位符 / JSON 合法性）。
- 构建与打包脚本 `packaging/`，支持 `CGO_ENABLED=0` 静态编译与 arm64 交叉编译。

### 校验

`validate_zh.py` 全量通过：键 1212 条零缺失、零多余，占位符零偏差；
其中 19 处与英文相同，均为有意保留（`URL`、`Slug`、`2FA`、
`application/octet-stream`、排序箭头 `A → Z`、日期格式示例、
Git 示例路径/邮箱/分支名、品牌名占位符 `LeafWiki`）。

### 说明

- 上游 v0.13.0 只内置 `en` / `de` / `es`；前端语言目录在构建时自动 glob，
  新增 `zh` 目录即可被语言切换器识别，无需改动前端代码。
- 基线与上游 v0.13.0 严格对齐，避免引入数据库 schema 迁移。
