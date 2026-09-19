#!/bin/bash
# 从源码构建汉化版 LeafWiki 并打包为 .deb（默认 amd64 + arm64）
#
# 用法:  packaging/build-deb.sh [输出目录]     默认 <源码>/releases
# 依赖:  Go 1.26.x、Node 22+、dpkg-deb、可选 fakeroot
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
OUTDIR="${1:-$SRC/releases}"

if ! command -v go >/dev/null && [ -x "$HOME/.local/go/bin/go" ]; then
    export GOROOT="$HOME/.local/go"
    export PATH="$GOROOT/bin:$PATH"
fi
command -v go >/dev/null || { echo "❌ 找不到 go（需要 1.26.x）"; exit 1; }
command -v dpkg-deb >/dev/null || { echo "❌ 找不到 dpkg-deb"; exit 1; }

export CGO_ENABLED=0

PKG=leafwiki-zh
UPVER=$(cd "$SRC" && ./scripts/resolve-version.sh | sed 's/^v//')
PKGVER="${PKGVER:-${UPVER}+zh2-1}"
ARCHES="${ARCHES:-amd64 arm64}"
LDFLAGS="-s -w -X main.Version=v${UPVER} -X github.com/perber/wiki/internal/http.EmbedFrontend=true -X github.com/perber/wiki/internal/http.Environment=production"

BUILD=/tmp/leafwiki-zh-build
rm -rf "$BUILD"; mkdir -p "$BUILD" "$OUTDIR"

cd "$SRC"
echo "=== $PKG $PKGVER  ($ARCHES) ==="

echo "=== 1/4 校验语言包 ==="
python3 validate_zh.py | tail -2

echo "=== 2/4 构建前端 ==="
cd ui/leafwiki-ui
[ -d node_modules ] || npm ci --ignore-scripts
VITE_API_URL=/ APP_VERSION="v$UPVER" npm run build 2>&1 | tail -2
cd "$SRC"
rm -rf internal/http/dist
mkdir -p internal/http/dist
cp -R ui/leafwiki-ui/dist/. internal/http/dist/
touch internal/http/dist/.gitkeep

echo "=== 3/4 交叉编译 ==="
for ARCH in $ARCHES; do
    GOOS=linux GOARCH="$ARCH" go build -ldflags "$LDFLAGS" -o "$BUILD/leafwiki-$ARCH" ./cmd/leafwiki
    echo "    $ARCH: $(du -h "$BUILD/leafwiki-$ARCH" | cut -f1)  $(file -b "$BUILD/leafwiki-$ARCH" | cut -d, -f1-3)"
done

echo "=== 4/4 组装 deb ==="
for ARCH in $ARCHES; do
    ROOT="$BUILD/${PKG}_${PKGVER}_${ARCH}"
    mkdir -p "$ROOT/DEBIAN" "$ROOT/usr/bin" "$ROOT/usr/lib/systemd/system" "$ROOT/usr/share/doc/$PKG"
    install -m 755 "$BUILD/leafwiki-$ARCH" "$ROOT/usr/bin/leafwiki"
    install -m 644 "$SRC/packaging/leafwiki.service" "$ROOT/usr/lib/systemd/system/leafwiki.service"
    install -m 644 "$SRC/packaging/leafwiki.env.example" "$ROOT/usr/share/doc/$PKG/leafwiki.env.example"
    install -m 644 "$SRC/packaging/nginx-leafwiki.conf" "$ROOT/usr/share/doc/$PKG/nginx-leafwiki.conf"
    install -m 644 "$SRC/packaging/README-deb.md" "$ROOT/usr/share/doc/$PKG/README.md"
    install -m 644 "$SRC/packaging/copyright" "$ROOT/usr/share/doc/$PKG/copyright"
    for s in preinst postinst prerm postrm; do
        install -m 755 "$SRC/packaging/DEBIAN/$s" "$ROOT/DEBIAN/$s"
    done
    SIZE=$(du -sk --exclude=DEBIAN "$ROOT" | cut -f1)
    sed -e "s/@ARCH@/$ARCH/" -e "s/@PKGVER@/$PKGVER/" -e "s/@SIZE@/$SIZE/" \
        -e "s/@UPVER@/$UPVER/" "$SRC/packaging/DEBIAN/control.in" > "$ROOT/DEBIAN/control"
    dpkg-deb --root-owner-group --build "$ROOT" "$OUTDIR/${PKG}_${PKGVER}_${ARCH}.deb" >/dev/null
    echo "    $OUTDIR/${PKG}_${PKGVER}_${ARCH}.deb"
done

cd "$OUTDIR"
sha256sum ${PKG}_${PKGVER}_*.deb | tee "${PKG}_${PKGVER}_SHA256.txt"
echo "打包完成 ✅"
