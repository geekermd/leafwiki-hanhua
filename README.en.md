# 🌿 LeafWiki — Simplified Chinese Edition · leafwiki-zh

[简体中文](./README.md) | **English** ← you are reading the English version

[![zh-ci](https://github.com/geekermd/leafwiki-hanhua/actions/workflows/zh-ci.yml/badge.svg)](../../actions/workflows/zh-ci.yml)
[![Release](https://img.shields.io/github/v/release/geekermd/leafwiki-hanhua?style=flat-square&label=download)](../../releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE)
[![Upstream](https://img.shields.io/badge/upstream-v0.13.0-blue.svg)](https://github.com/perber/leafwiki/releases/tag/v0.13.0)
[![Go](https://img.shields.io/badge/Go-1.26-00ADD8.svg)](https://go.dev)

**Self-hosted wiki. A single Go binary. SQLite + Markdown on disk.**
No Node.js, no Redis, no Postgres — just a binary and a data directory.

> [!IMPORTANT]
> This repository (`leafwiki-hanhua`) is an **unofficial Simplified-Chinese fork** of
> [perber/leafwiki](https://github.com/perber/leafwiki), based on upstream **v0.13.0**.
> The upstream project is not responsible for this fork.
> There are only **3 code changes plus one test update**, all listed in **[NOTICE](./NOTICE)** and in the
> [differences table](#differences-from-upstream). The original upstream README is preserved verbatim in
> **[README.upstream.md](./README.upstream.md)**.
> The repository is named `leafwiki-hanhua` while the **package and binary are named `leafwiki-zh`**,
> which keeps them distinguishable from upstream.

---

## 🚀 30-second quick start

```bash
# 1) Download the deb from the Releases page and install it (use arm64 on ARM)
sudo apt install ./leafwiki-zh_0.13.0+zh2-1_amd64.deb

# 2) Read the generated admin password
sudo cat /etc/leafwiki/admin-password.txt

# 3) Open http://localhost:8080 in a browser
#    Username: admin — password from the previous step. The UI is already Chinese.
```

It listens on `127.0.0.1` only (a secure default). To serve it over HTTPS, see
[Reverse proxy & HTTPS](#reverse-proxy--https); other install methods (source, Docker) are in
[Install](#install).

---

## Table of Contents

- [Features](#features)
- [Differences from upstream](#differences-from-upstream)
- [Install](#install)
- [Quick start](#quick-start)
- [Reverse proxy & HTTPS](#reverse-proxy--https)
- [Configuration](#configuration)
- [Chinese UI & translation](#chinese-ui--translation)
- [Data, backups & restore](#data-backups--restore)
- [Directory structure](#directory-structure)
- [Development & build](#development--build)
- [Upgrading to a newer upstream](#upgrading-to-a-newer-upstream)
- [FAQ](#faq)
- [License & credits](#license--credits)

---

## Features

Based on upstream v0.13.0. Features marked ★ require an explicit flag (see [Configuration](#configuration)).

**Content**

- Tree-structured pages (pages / sections / subpages) with ordering
- Markdown editing, including relative links between pages
- Full-text search, tags, backlinks
- Broken-link checking
- Asset uploads, 50 MiB per file by default
- ★ Page revision history (`--enable-revision`): keeps the last 100 revisions per page,
  coalescing rapid successive saves within 5 minutes
- External edits: change the Markdown files on disk and the index is rebuilt

**Users & permissions**

- Roles: admin / editor / viewer
- Three access modes: login required (default), public read, fully open
- ★ Email invites and password reset (requires SMTP)
- ★ TOTP two-factor authentication (requires `--totp-encryption-key`)
- ★ API key management
- ★ Reverse-proxy authentication: trusts a `Remote-User` header, with optional
  auto-provisioning (works well behind corporate SSO)

**Backup & operations**

- Snapshot backups: a ZIP (including SQLite) every 24 h by default, latest 10 retained,
  with live restore and disaster recovery
- ★ Git backup: periodically pushes Markdown to a Git remote (SSH or HTTP(S))
- ★ Prometheus metrics on a separate listener
- Structured logging (text / json), per-request access log can be disabled

**Appearance & language**

- Branding: site name, logo, favicon
- Custom stylesheet, custom HTML/JS injected into `<head>`
- UI languages: **Simplified Chinese (added by this fork)**, English, German, Spanish

---

## Differences from upstream

**Three code changes plus one test update**, all required to make the Chinese UI actually work:

| Location | Change | What breaks without it |
|---|---|---|
| `ui/leafwiki-ui/src/locales/zh/` (new directory) | Simplified-Chinese locale: 19 namespace files, **1212 strings** | Chinese is not available in the UI at all |
| `internal/usersettings/language.go` | Language allow-list accepts `zh` (via the `DefaultLanguage` constant), and keeps `en` explicitly | Picking Chinese in the UI fails with `Language must be one of: ...` |
| `internal/usersettings/models.go` | `DefaultLanguage` changed from `"en"` to `"zh"` | **The login page is Chinese, but the UI flips back to English after signing in** |
| `internal/usersettings/language_test.go` | Test updated: the expected allow-list now includes `zh` | The upstream test hard-codes `de/en/es`, so the Go test suite would fail |

The third one is the easy one to miss, and it is worth explaining: the frontend
(`stores/userSettings.ts`) applies the user's stored language **on top of** the site-wide
`--default-language` once user settings load. Users who never saved a preference get the backend's
`DefaultLanguage`. So setting the default-language flag alone only changes the login page.

> ⚠️ Because `DefaultLanguage` is now `zh`, the allow-list must **not** contain an explicit
> `"zh": true` entry — that would fail to compile with `duplicate key "zh" in map literal`.

---

## Install

### Option 1: deb package (recommended, Debian / Ubuntu)

```bash
sudo apt install ./leafwiki-zh_0.13.0+zh2-1_amd64.deb     # use the arm64 file on ARM
```

What you get:

| Item | Location |
|---|---|
| Binary | `/usr/bin/leafwiki` |
| systemd service | `leafwiki.service` (enabled at boot, hardened) |
| Config incl. secrets (mode 600) | `/etc/leafwiki/leafwiki.env` |
| Initial admin password | `/etc/leafwiki/admin-password.txt` |
| Data directory | `/var/lib/leafwiki` |
| Default listener | `127.0.0.1:8080` |

The first install generates a random JWT secret and admin password and **prints them**.
Upgrades **never overwrite** an existing `/etc/leafwiki/leafwiki.env`, so your secret, sessions
and data survive. `apt remove` deletes the program but keeps config and data
(even `purge` only removes the system user).

### Option 2: build from source

```bash
packaging/build-from-source.sh          # binary only, defaults to ./leafwiki
packaging/build-deb.sh ./releases       # debs (amd64 + arm64 by default)
```

Requires Go **1.26.x**, Node **22+**, `dpkg-deb`. The scripts fall back to `~/.local/go`
when `go` is not on `PATH`.

### Option 3: Docker (build your own image)

The upstream `Dockerfile` / `docker-entrypoint.sh` are included, and it builds **from this
repository's source**, so a self-built image does contain the Chinese UI:

```bash
docker build -t leafwiki-zh --build-arg APP_VERSION=v0.13.0 .
docker run -d --name leafwiki -p 127.0.0.1:8080:8080 \
  -e LEAFWIKI_JWT_SECRET=your-secret \
  -e LEAFWIKI_ADMIN_PASSWORD=your-password \
  -e LEAFWIKI_ALLOW_INSECURE=true \
  -v leafwiki-data:/app/data leafwiki-zh
```

> This fork ships no prebuilt image and the Docker path has not been verified here.

### ⚠️ Do not use the upstream `install.sh`

The bundled `install.sh` downloads the **official binary from upstream GitHub releases**,
which does **not** include the Chinese UI. Use one of the three options above instead.

---

## Quick start

### After installing the deb

1. Open `http://localhost:8080`
2. Sign in as `admin` with the password in `/etc/leafwiki/admin-password.txt`
3. If the UI is English, go to **Settings → Account → Preferences → Language** and pick 简体中文

The service listens on loopback only — that is a deliberate secure default. See the next
section to expose it.

### Running the binary directly

```bash
# 1) Internal wiki: everything requires login (default)
./leafwiki --jwt-secret=your-secret --admin-password=your-password

# 2) Public read, login required to edit
./leafwiki --jwt-secret=your-secret --admin-password=your-password --public-access

# 3) No authentication at all (trusted networks only!)
./leafwiki --disable-auth
```

Common flags: `--host` (default `127.0.0.1`), `--port` (default `8080`),
`--data-dir` (default `./data`).

### Three things to do after the first login

1. Pin the language to Simplified Chinese under **Settings → Account → Preferences**
   (skip if it is already Chinese)
2. Change the initial admin password
3. Check that the data and snapshot directories are where you expect
   (see [Data, backups & restore](#data-backups--restore))

---

## Reverse proxy & HTTPS

LeafWiki itself serves plain HTTP; **TLS should be terminated by a reverse proxy**.
A ready-to-adapt config is in
[`packaging/nginx-leafwiki.conf`](./packaging/nginx-leafwiki.conf) (nginx listens on
`127.0.0.1:8443` and proxies to `127.0.0.1:8080`).

```nginx
location / {
    proxy_pass         http://127.0.0.1:8080;
    proxy_http_version 1.1;
    proxy_set_header   Host              $host;
    proxy_set_header   X-Real-IP         $remote_addr;
    proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
}
client_max_body_size 50M;   # keep in sync with --max-asset-upload-size
```

Also set `LEAFWIKI_TRUSTED_PROXY_IPS` to the proxy address (e.g. `127.0.0.1`), otherwise
LeafWiki will not trust the `X-Forwarded-*` headers. To serve under a subpath, use
`--base-path=/wiki` and adjust the proxy accordingly.

**Cloudflare Tunnel and similar:** point the origin at `https://localhost:8443` and bring
your own certificate (self-signed and registered in the system trust store, or a Cloudflare
Origin certificate plus the Origin CA root in the trust store). Pointing the tunnel at
`http://localhost:8080` means the origin leg is plaintext.

> ⚠️ **You cannot sign in over plain HTTP.** Without HTTPS, LeafWiki refuses to issue auth
> cookies (`auth_cookie_failed: HTTPS is required for auth cookies`). Only for trusted
> local setups you may set `LEAFWIKI_ALLOW_INSECURE=true` — cookies then travel in plain text.

---

## Configuration

Precedence: **CLI flag > environment variable > default**. Every flag has a matching
`LEAFWIKI_*` variable. Run `leafwiki --help` for the full list. The ones you will actually touch:

| Flag | Env var | Default | Notes |
|---|---|---|---|
| `--jwt-secret` | `LEAFWIKI_JWT_SECRET` | — | **Required** unless `--disable-auth`. Changing it invalidates all sessions |
| `--admin-password` | `LEAFWIKI_ADMIN_PASSWORD` | — | Initial admin password, **only used when no admin exists** |
| `--admin-username` | `LEAFWIKI_ADMIN_USERNAME` | `admin` | Initial admin username |
| `--host` / `--port` | `LEAFWIKI_HOST` / `LEAFWIKI_PORT` | `127.0.0.1` / `8080` | Listen address and port |
| `--data-dir` | `LEAFWIKI_DATA_DIR` | `./data` | Data directory |
| `--default-language` | `LEAFWIKI_DEFAULT_LANGUAGE` | — | Site-wide default language; `zh` in this fork |
| `--public-access` | `LEAFWIKI_PUBLIC_ACCESS` | off | Anonymous read access |
| `--disable-auth` | `LEAFWIKI_DISABLE_AUTH` | off | Disable authentication entirely (dangerous) |
| `--allow-insecure` | `LEAFWIKI_ALLOW_INSECURE` | off | Issue cookies over plain HTTP (local only) |
| `--trusted-proxy-ips` | `LEAFWIKI_TRUSTED_PROXY_IPS` | — | Which proxies' `X-Forwarded-*` to trust |
| `--base-path` | `LEAFWIKI_BASE_PATH` | — | Subpath behind a proxy, e.g. `/wiki` |
| `--enable-revision` | `LEAFWIKI_ENABLE_REVISION` | off | Page revision history |
| `--snapshot` | `LEAFWIKI_SNAPSHOT` | on | Snapshot backups |
| `--snapshot-interval` | `LEAFWIKI_SNAPSHOT_INTERVAL` | `24h` | `0` = manual only |
| `--snapshot-retention` | `LEAFWIKI_SNAPSHOT_RETENTION` | `10` | How many snapshots to keep |
| `--max-asset-upload-size` | `LEAFWIKI_MAX_ASSET_UPLOAD_SIZE` | `50MiB` | Per-file upload limit |
| `--enable-metrics` | `LEAFWIKI_ENABLE_METRICS` | off | Prometheus `/metrics` endpoint |
| `--log-format` | `LEAFWIKI_LOG_FORMAT` | `text` | `text` or `json` |

With the deb, put these in `/etc/leafwiki/leafwiki.env` (mode 600) and run
`sudo systemctl restart leafwiki`.

---

## Chinese UI & translation

**Switching language:** after signing in, go to **Settings → Account → Preferences → Language**
and pick 简体中文. The preference is stored per user; users who never saved one fall back to
`DefaultLanguage`, which this fork sets to `zh`.

**Where the locale lives:** `ui/leafwiki-ui/src/locales/zh/` (19 namespace files, 1212 strings).
The frontend globs that directory at build time, so **adding a language needs no frontend code
change** — the language switcher is generated from it too.

**Validating translations:**

```bash
python3 validate_zh.py                  # all namespaces
python3 validate_zh.py viewer editor    # only these namespaces
```

Sample output (every file must be `[OK]`):

```
[OK] common           键   23  缺失  0  多余  0  占位符不符  0  与英文相同   0
[OK] viewer           键  158  缺失  0  多余  0  占位符不符  0  与英文相同   0
结果: 全部通过 ✅
```

**Rules for editing strings** (full glossary in [`TRANSLATION-SPEC.md`](./TRANSLATION-SPEC.md)):

1. **Never change the keys** — do not add, remove, rename or re-nest any key.
2. **Keep every `{{...}}` placeholder** — same count, though they may move to fit Chinese word order.
3. Keep the plural keys `_one` / `_other`; Chinese has no plurals, so write the same text in both.
4. **Do not translate** `LeafWiki`, `Markdown`, `Git`, `API`, `JWT`, `TOTP`, `SMTP`, `URL`,
   keyboard shortcuts (`Ctrl+K`), file extensions, example domains and paths, or tags such as `<bold>`.
5. Use raw UTF-8 Chinese (not `\uXXXX`); full-width punctuation in sentences, no trailing
   punctuation on short labels.

Run `validate_zh.py` after editing, then rebuild. CI
([`.github/workflows/zh-ci.yml`](./.github/workflows/zh-ci.yml)) checks key parity, placeholders,
that `language.selfName` is 简体中文, and that the backend allow-list is consistent.

> A non-zero "与英文相同" (identical to English) count is **allowed** — `URL`, `Slug`, `2FA`,
> `application/octet-stream`, the sort arrows `A → Z`, date-format examples and Git example
> paths are meant to stay as they are.

---

## Data, backups & restore

The data directory (for the deb: `/var/lib/leafwiki`) looks like this:

```
├── users.db  sessions.db  favorites.db  links.db
├── properties.db  search.db  tags.db  usersettings.db     SQLite (WAL mode)
├── root/            page content (Markdown on disk)
├── assets/          uploaded attachments
├── avatars/  branding/
└── snapshots/       full backup ZIPs (including SQLite)
```

**Restoring a snapshot** (stop the service first):

```bash
sudo systemctl stop leafwiki
sudo -u leafwiki /usr/bin/leafwiki --data-dir /var/lib/leafwiki \
     restore-snapshot /var/lib/leafwiki/snapshots/<some>.zip
sudo systemctl start leafwiki
```

Live restore is also available from the admin UI (Settings → Full Backup).

**Forgot the admin password:**

```bash
sudo systemctl stop leafwiki
sudo -u leafwiki /usr/bin/leafwiki --data-dir /var/lib/leafwiki reset-admin-password
sudo systemctl start leafwiki
```

---

## Directory structure

★ = added or changed by this fork; everything else is upstream v0.13.0 untouched.

```
├── cmd/leafwiki/                entry point and CLI flags
├── internal/                    backend
│   ├── http/                    routing, middleware, embedded frontend
│   ├── wiki/                    page tree, search, revisions
│   └── usersettings/            ★ language.go / models.go are modified
├── ui/leafwiki-ui/              frontend (React + i18next + Vite)
│   └── src/locales/             locale catalogs
│       ├── en/ de/ es/          upstream
│       └── zh/                  ★ Simplified Chinese, 19 files
├── docs/  assets/  e2e/  e2e-proxy/  hacks/  loadtest/  scripts/     upstream
├── packaging/                   ★ build & packaging
│   ├── build-from-source.sh         build the binary
│   ├── build-deb.sh                 build and package debs (amd64 / arm64)
│   ├── leafwiki.service             hardened systemd unit
│   ├── leafwiki.env.example         config template
│   ├── nginx-leafwiki.conf          HTTPS termination example
│   ├── README-deb.md                readme shipped inside the deb
│   └── DEBIAN/                      control.in and preinst/postinst/prerm/postrm
├── .github/workflows/zh-ci.yml  ★ fork-specific CI
├── validate_zh.py               ★ locale validator
├── TRANSLATION-SPEC.md          ★ glossary and translation rules
├── CHANGELOG.md                 ★ fork changelog
├── NOTICE                       ★ attribution and full diff list
├── README.md                    Chinese main readme
├── README.en.md                 this file
├── README.upstream.md           upstream readme, preserved verbatim
├── LICENSE                      upstream MIT, unchanged
├── CONTRIBUTING.md / CODE_OF_CONDUCT.md / SECURITY.md / CODEOWNERS   upstream
├── Makefile / Dockerfile / docker-entrypoint.sh / install.sh / update.sh   upstream
└── go.mod / go.sum / package.json and friends                        upstream
```

---

## Development & build

**Requirements:** Go `1.26.x` (`go.mod` declares 1.26.0), Node `22+` (verified on 24).

```bash
# upstream Makefile targets
make ui          # build the frontend into internal/http/dist
make build       # build the binary with the embedded frontend
make test        # Go tests
make run         # run locally

# this fork
packaging/build-from-source.sh       # validate locales → build frontend → compile binary
packaging/build-deb.sh ./releases    # produce amd64/arm64 debs
python3 validate_zh.py               # validate the locale only
```

`CGO_ENABLED=0` is enough to build (SQLite is the pure-Go `modernc.org/sqlite`), so the
artifacts are fully static and arm64 cross-compiles directly.

---

## Upgrading to a newer upstream

1. Check out the new upstream tag (this fork is based on v0.13.0);
2. Copy `ui/leafwiki-ui/src/locales/zh/` across (a new directory, rarely conflicts);
3. Re-apply the two Go changes (`language.go` allow-list, `models.go` default language).
   If upstream restructured those files, note that with `DefaultLanguage = "zh"` the allow-list
   must **not** contain an explicit `"zh": true`;
4. Run `python3 validate_zh.py` and `packaging/build-deb.sh`, then release;
5. Update the version in `CHANGELOG.md` and the baseline in `NOTICE`.

The translations live in their own directory, so upstream updates are cheap.

---

## FAQ

**The UI has no Chinese option.**
You are not running this fork's build. The upstream binary ships only `en` / `de` / `es`.
Use the deb from this repository or [build from source](#option-2-build-from-source).
In particular, do not use the upstream `install.sh`.

**The login page is Chinese but the UI switches to English after signing in.**
Your account has a saved language preference, which overrides the default. Set it under
**Settings → Account → Preferences → Language → 简体中文**. New users get Chinese by default.

**The page loads, but login fails with `auth_cookie_failed`.**
You are on plain HTTP. LeafWiki refuses to issue auth cookies without HTTPS: put a
TLS-terminating reverse proxy in front, or set `LEAFWIKI_ALLOW_INSECURE=true` for local testing.

**Why does it only listen on `127.0.0.1`?**
That is the secure default. Expose it through a reverse proxy or a tunnel rather than
binding `--host 0.0.0.0`.

**I forgot the admin password.**
See `reset-admin-password` under [Data, backups & restore](#data-backups--restore).
With the deb, the generated password from the first install is in
`/etc/leafwiki/admin-password.txt`.

**How do I apply config changes?**
With the deb: edit `/etc/leafwiki/leafwiki.env`, then `sudo systemctl restart leafwiki`.

**Asset uploads fail.**
Check `--max-asset-upload-size` (50 MiB by default) **and** the reverse proxy's
`client_max_body_size` — both must allow the file size.

**Where do I report bugs?**
Upstream bugs go to the [upstream repository](https://github.com/perber/leafwiki/issues).
Fork-specific issues (translations, deb packaging) go to this repository.

---

## License & credits

- Upstream LeafWiki: **MIT**, Copyright (c) 2025 perber — [`LICENSE`](./LICENSE)
  is **kept verbatim and unmodified**.
- Translations and scripts added by this fork are released under the same **MIT** license.
- When redistributing, keep `LICENSE` and [`NOTICE`](./NOTICE), and make clear that this is
  an unofficial fork.
- Upstream trademarks and project names belong to the upstream authors; this fork uses the
  package/binary name `leafwiki-zh` to stay distinguishable.
- Thanks to the upstream author and all contributors 🌿
