#!/bin/bash
# 从源码构建汉化版 LeafWiki（只出二进制，不出 deb）
#
# 用法:  packaging/build-from-source.sh [输出文件]     默认 ./leafwiki
# 依赖:  Go 1.26.x、Node 22+（含 npm）
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$SRC/leafwiki}"

# 允许把 Go 装在 ~/.local/go（无需 root）
if ! command -v go >/dev/null && [ -x "$HOME/.local/go/bin/go" ]; then
    export GOROOT="$HOME/.local/go"
    export PATH="$GOROOT/bin:$PATH"
fi
command -v go >/dev/null || { echo "❌ 找不到 go（需要 1.26.x）"; exit 1; }
command -v npm >/dev/null || { echo "❌ 找不到 npm（需要 Node 22+）"; exit 1; }

export CGO_ENABLED=0   # modernc.org/sqlite 是纯 Go 实现，可静态编译

cd "$SRC"
VERSION=$(./scripts/resolve-version.sh)
echo "=== 版本 $VERSION  (go $(go version | awk '{print $3}'), node $(node -v)) ==="

echo "=== 1/3 校验语言包 ==="
python3 validate_zh.py | tail -2

echo "=== 2/3 构建前端 ==="
cd ui/leafwiki-ui
[ -d node_modules ] || npm ci --ignore-scripts
VITE_API_URL=/ APP_VERSION="$VERSION" npm run build 2>&1 | tail -3

echo "=== 3/3 编译后端 ==="
cd "$SRC"
rm -rf internal/http/dist
mkdir -p internal/http/dist
cp -R ui/leafwiki-ui/dist/. internal/http/dist/
touch internal/http/dist/.gitkeep
test -f internal/http/dist/index.html || { echo "❌ 前端产物缺少 index.html"; exit 1; }

go build -ldflags "-s -w \
  -X main.Version=$VERSION \
  -X github.com/perber/wiki/internal/http.EmbedFrontend=true \
  -X github.com/perber/wiki/internal/http.Environment=production" \
  -o "$OUT" ./cmd/leafwiki

ls -lh "$OUT"
"$OUT" --version
echo "构建完成 ✅  →  $OUT"
