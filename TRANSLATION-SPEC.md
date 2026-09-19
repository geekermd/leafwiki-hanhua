# LeafWiki 简体中文语言包 · 翻译规范

本文件是翻译工作的**唯一权威规范**，所有译者（人或 AI）必须严格遵守，以保证 19 个文件之间术语一致。

## 一、任务

把 LeafWiki 前端的英文文案翻译成**简体中文（zh-Hans）**。

- 项目路径：`/tmp/leafwiki-src`（LeafWiki v0.13.0 源码）
- 英文源文件：`ui/leafwiki-ui/src/locales/en/<命名空间>.json`
- 中文输出文件：`ui/leafwiki-ui/src/locales/zh/<命名空间>.json`
- `zh/` 目录已存在（当前是 en 的副本），**用翻译后的完整内容覆盖对应文件**

## 二、硬性规则

1. **键必须与 en 完全一致**：不新增、不删除、不改名、不改层级嵌套顺序无关但键名与结构必须相同。
   `validate_zh.py` 会逐键比对，任何缺失/多余键都会判定失败。
2. **只翻译字符串值**，不要翻译键名。
3. **占位符原样保留**：`{{title}}`、`{{count}}`、`{{error}}`、`{{editor}}`、`{{time}}`、`{{item}}` 等一律照抄，
   位置可按中文语序调整，但**一个都不能少、不能多加**。
4. **复数键（`_one` / `_other`）**：中文没有复数变化，两个键都保留，**翻译成完全相同的中文**。
   注意 `{{count}}` 之类的占位符两边都要保留。
5. **绝对不翻译**的内容：
   - 品牌与专有名词：`LeafWiki`、`Markdown`、`Git`、`API`、`JWT`、`TOTP`、`SMTP`、`URL`、`JSON`、`HTML`、`CSS`、`Node`、`Go`
   - 技术缩写与协议：`HTTPS`、`SSO`、`IdP`、`CSV`、`ZIP`、`PDF`、`PNG`、`SVG`
   - 快捷键：`Ctrl+K`、`Cmd+S`、`Esc`、`Enter`、`Shift+Enter`
   - 文件扩展名、路径、代码片段、`example.com` 类示例域名
6. **HTML/标签**：值里若含 `<br>`、`<strong>` 等标签，标签原样保留。
7. **JSON 合法性**：必须能被 `json.loads` 解析。中文字符**直接写 UTF-8 原文**（不要写成 `\uXXXX`）。
   字符串内的双引号用 `\"` 转义，换行用 `\n`。
8. **标点**：句子用中文全角标点（，。：？、）。**短标签（按钮、菜单项）不加句末标点**，与英文风格保持一致。
9. **长度**：这是 UI 文案，尽量简洁。按钮/菜单项优先用 2–4 个汉字。
10. 不要修改 `en/` 下任何文件，不要碰其他命名空间，不要改任何 `.go` / `.ts` / `.tsx` 源码。

## 三、术语表（必须统一使用）

| 英文 | 中文 | 说明 |
|---|---|---|
| page | 页面 | |
| pages | 页面 | |
| section | 章节 | 页面树中的分组 |
| subpage | 子页面 | |
| wiki | 维基 | 泛指这个 wiki 本身 |
| space | 空间 | |
| asset / assets | 附件 | 上传的图片/文件 |
| snapshot | 快照 | |
| backup | 备份 | |
| restore | 恢复 | |
| revision | 修订 | 页面历史里的版本 |
| history | 历史 | |
| branding | 品牌 | |
| broken link(s) | 失效链接 | |
| importer | 导入 | |
| viewer | 阅读器 | 阅读模式 UI |
| editor | 编辑器 | |
| role: admin | 管理员 | |
| role: editor | 编辑者 | |
| role: viewer | 访客 | 只读用户角色 |
| API key | API 密钥 | |
| public access | 公开访问 | |
| settings | 设置 | |
| account | 账户 | |
| preferences | 偏好设置 | |
| auto save | 自动保存 | |
| search | 搜索 | |
| login / sign in | 登录 | |
| logout / sign out | 退出登录 | |
| password | 密码 | |
| username | 用户名 | |
| email | 电子邮箱 | |
| invite / invitation | 邀请 | |
| TOTP / two-factor | 两步验证 | 保留 TOTP 时写 "TOTP 两步验证" |
| date format | 日期格式 | |
| time format | 时间格式 | |
| language | 语言 | |
| Save | 保存 | |
| Saved | 已保存 | |
| Cancel | 取消 | |
| Delete | 删除 | |
| Edit | 编辑 | |
| Create | 创建 | |
| Add | 添加 | |
| Remove | 移除 | |
| Upload | 上传 | |
| Download | 下载 | |
| Copy | 复制 | |
| Close | 关闭 | |
| Back | 返回 | |
| Next | 下一步 | |
| Confirm | 确认 | |
| Warning | 警告 | |
| Error | 错误 | |
| Success | 成功 | |
| Loading | 加载中 | |
| Filter | 筛选 | |
| Sort | 排序 | |
| Name | 名称 | |
| Size | 大小 | |
| Type | 类型 | |
| Actions | 操作 | |
| Title | 标题 | |
| Content | 内容 | |
| Tags | 标签 | |
| Overview | 概览 | |
| Untitled | 无标题 | |
| Draft | 草稿 | |
| Public | 公开 | |
| Private | 私有 | |
| Read-only | 只读 | |
| Permission | 权限 | |
| Owner | 所有者 | |
| Member | 成员 | |
| Last updated | 最近更新 | |
| Created | 创建于 | |
| Are you sure? | 确定要继续吗？ | 确认弹窗 |

## 四、风格示例

| 英文 | 推荐中文 |
|---|---|
| `Save changes` | 保存更改 |
| `Are you sure you want to delete this page?` | 确定要删除此页面吗？ |
| `{{count}} results` | `{{count}} 条结果` |
| `Updated by {{editor}} · {{time}}` | 由 {{editor}} 更新 · {{time}} |
| `Search pages…` | 搜索页面… |
| `No pages found` | 未找到页面 |
| `Failed to save` | 保存失败 |

## 五、自检（必须执行）

翻译完自己负责的文件后，运行：

```bash
python3 /tmp/leafwiki-src/validate_zh.py <你负责的命名空间...>
```

要求：**每个文件都是 `[OK]`**，即缺失 0、多余 0、占位符不符 0。
（"与英文相同" 一列不为 0 是允许的 —— 品牌名、缩写、代码片段本来就不该翻译；但若因漏译导致，必须修掉。）

## 六、交付报告（用中文，简洁）

1. 处理了哪些文件、各多少条文案
2. `validate_zh.py` 的原始输出
3. 你拿不准或做了特殊处理的术语（若有）
