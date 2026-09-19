#!/usr/bin/env python3
"""校验简体中文语言包，并（可选）检查本衍生版的后端口径是否一致。

用法：
    python3 validate_zh.py                       # 校验全部命名空间（自动定位 locales）
    python3 validate_zh.py viewer editor         # 只校验指定命名空间
    python3 validate_zh.py --check-fork          # 只做衍生版口径检查
    python3 validate_zh.py --all                 # 语言包 + 衍生版口径，一次全查（CI 用）
    python3 validate_zh.py --locales DIR ...     # 显式指定 locales 父目录

locales 目录的自动定位顺序：
    1) --locales 参数
    2) 环境变量 LEAFWIKI_LOCALES
    3) <脚本所在目录>/locales                      （汉化包目录结构）
    4) <脚本所在目录>/ui/leafwiki-ui/src/locales   （完整源码目录结构）
    5) /tmp/leafwiki-src/ui/leafwiki-ui/src/locales

退出码：0 = 全部通过；1 = 有问题。
"""
import json
import os
import pathlib
import re
import sys

PLACEHOLDER = re.compile(r"\{\{[^}]+\}\}")
SELF_NAME = "简体中文"


def locate_locales(explicit=None):
    here = pathlib.Path(__file__).resolve().parent
    candidates = []
    if explicit:
        candidates.append(pathlib.Path(explicit))
    if os.environ.get("LEAFWIKI_LOCALES"):
        candidates.append(pathlib.Path(os.environ["LEAFWIKI_LOCALES"]))
    candidates += [
        here / "locales",
        here / "ui" / "leafwiki-ui" / "src" / "locales",
        pathlib.Path("/tmp/leafwiki-src/ui/leafwiki-ui/src/locales"),
    ]
    for c in candidates:
        if (c / "en").is_dir():
            return c
    sys.exit(f"找不到 locales 目录（含 en/ 的目录）。已尝试：{[str(c) for c in candidates]}")


def source_root(base):
    """从 locales 目录推出源码根目录（<root>/ui/leafwiki-ui/src/locales）。"""
    p = base.resolve()
    for _ in range(4):
        p = p.parent
    return p


def flatten(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from flatten(v, f"{prefix}.{k}" if prefix else k)
    else:
        yield prefix, obj


def check_locales(base, namespaces):
    problems = 0
    for ns in namespaces:
        en_path = base / "en" / f"{ns}.json"
        zh_path = base / "zh" / f"{ns}.json"
        if not zh_path.exists():
            print(f"[缺失] {ns}.json 不存在")
            problems += 1
            continue
        try:
            en = dict(flatten(json.loads(en_path.read_text(encoding="utf-8"))))
        except Exception as exc:  # noqa: BLE001
            print(f"[en 解析失败] {ns}: {exc}")
            problems += 1
            continue
        try:
            zh = dict(flatten(json.loads(zh_path.read_text(encoding="utf-8"))))
        except Exception as exc:  # noqa: BLE001
            print(f"[JSON 非法] {ns}: {exc}")
            problems += 1
            continue

        missing = sorted(set(en) - set(zh))
        extra = sorted(set(zh) - set(en))
        shared = set(en) & set(zh)
        ph_bad = [
            k
            for k in shared
            if sorted(PLACEHOLDER.findall(str(en[k]))) != sorted(PLACEHOLDER.findall(str(zh[k])))
        ]
        same = [k for k in shared if en[k] == zh[k]]
        ok = not (missing or extra or ph_bad)
        print(
            f"[{'OK' if ok else 'FAIL'}] {ns:16} 键 {len(en):4}  "
            f"缺失 {len(missing):2}  多余 {len(extra):2}  占位符不符 {len(ph_bad):2}  "
            f"与英文相同 {len(same):3}"
        )
        if missing:
            print("      缺失键:", missing[:8])
        if extra:
            print("      多余键:", extra[:8])
        if ph_bad:
            print("      占位符不符:", ph_bad[:8])
        if same:
            print("      与英文相同(需人工确认是否合理):", same[:8])
        if not ok:
            problems += 1
    return problems


def check_fork(base):
    """本衍生版后端口径：默认语言、白名单、语言自称。"""
    root = source_root(base)
    problems = 0

    common = base / "zh" / "common.json"
    try:
        name = json.loads(common.read_text(encoding="utf-8"))["language"]["selfName"]
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] 读取 zh/common.json 失败: {exc}")
        return 1
    if name != SELF_NAME:
        print(f"[FAIL] zh/common.json 的 language.selfName 应为「{SELF_NAME}」，实际是 {name!r}")
        problems += 1
    else:
        print(f"[OK]   语言自称 language.selfName = {SELF_NAME}")

    for rel, pattern, expect, hint in [
        (
            "internal/usersettings/models.go",
            r'const DefaultLanguage = "([^"]*)"',
            "zh",
            '默认语言必须是 zh，否则「未设置偏好」的用户会被前端覆盖回英文',
        ),
        (
            "internal/usersettings/language.go",
            r'(?m)^\s*"en"\s*:\s*true,',
            True,
            '白名单应显式保留 "en"，便于用户切回英文',
        ),
        (
            "internal/usersettings/language_test.go",
            r'"zh"',
            True,
            '语言白名单的用例需包含 "zh"（上游断言只有 de/en/es，会导致 CI 失败）',
        ),
    ]:
        p = root / rel
        if not p.is_file():
            print(f"[SKIP] 找不到 {rel}（只看语言包时可忽略）")
            continue
        text = p.read_text(encoding="utf-8")
        m = re.search(pattern, text)
        got = m.group(1) if (m and m.groups()) else bool(m)
        if got != expect:
            print(f"[FAIL] {rel}: 期望 {expect!r}，实际 {got!r} —— {hint}")
            problems += 1
        else:
            print(f"[OK]   {rel}")

    lang = root / "internal/usersettings/language.go"
    if lang.is_file() and re.search(r'(?m)^\s*"zh"\s*:\s*true,', lang.read_text(encoding="utf-8")):
        print('[FAIL] language.go 里显式写了 "zh"，会与 DefaultLanguage 重复导致编译失败 '
              '(duplicate key "zh" in map literal)')
        problems += 1

    return problems


def main(argv):
    explicit = None
    if "--locales" in argv:
        i = argv.index("--locales")
        explicit = argv[i + 1]
        del argv[i:i + 2]

    do_locales = True
    do_fork = False
    namespaces = []
    for a in argv:
        if a == "--check-fork":
            do_locales, do_fork = False, True
        elif a == "--all":
            do_locales, do_fork = True, True
        elif a in ("-h", "--help"):
            print(__doc__)
            return 0
        else:
            namespaces.append(a)

    base = locate_locales(explicit)
    print(f"locales 目录: {base}")
    print()

    problems = 0
    if do_locales:
        nss = namespaces or [p.stem for p in sorted((base / "en").glob("*.json"))]
        if not nss:
            sys.exit(f"{base}/en 下没有命名空间文件")
        problems += check_locales(base, nss)
        print()
    if do_fork:
        problems += check_fork(base)
        print()

    print("结果:", "全部通过 ✅" if problems == 0 else f"{problems} 项有问题 ❌")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
