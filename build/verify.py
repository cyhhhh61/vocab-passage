#!/usr/bin/env python3
"""校验单文件单词故事页：词库、正文、译文三者是否对齐。

用法: python3 verify.py /workspace/vocab-passage.html
退出码 0 表示通过。
"""
import re
import sys
from collections import Counter


def main(path: str) -> int:
    html = open(path, encoding="utf-8").read()

    nodes = re.findall(r'<w\b([^>]*)>(.*?)</w>', html, re.S)
    keys = []
    for attrs, _ in nodes:
        m = re.search(r'data-k="([^"]*)"', attrs)
        if m and m.group(1):
            keys.append(m.group(1))

    if "const D = {" not in html:
        print("FAIL: 找不到 const D 词库")
        return 1
    block = html.split("const D = {", 1)[1].split("\n};", 1)[0]
    dict_keys = re.findall(r'^\s*([A-Za-z][A-Za-z\-]*)\s*:\s*\{p:', block, re.M)

    dup = [k for k, c in Counter(keys).items() if c > 1]
    missing = sorted(set(dict_keys) - set(keys))
    unknown = sorted(set(keys) - set(dict_keys))
    dup_dict = [k for k, c in Counter(dict_keys).items() if c > 1]

    paras = len(re.findall(r'<p>', html))
    zh = len(re.findall(r'<p class="zh"', html))
    words = len(nodes)

    print(f"file          {path}")
    print(f"dict keys     {len(dict_keys)}")
    print(f"unique used   {len(set(keys))}")
    print(f"<w> nodes     {words}  (targets: {len(keys)})")
    print(f"paragraphs    {paras}  (translations: {zh})")
    print(f"repeated keys {dup if dup else '—'}")

    ok = True
    if missing:
        print(f"MISSING in passage : {missing}")
        ok = False
    if unknown:
        print(f"UNKNOWN (not in D) : {unknown}")
        ok = False
    if dup_dict:
        print(f"DUPLICATE dict key : {dup_dict}")
        ok = False
    if paras != zh:
        print("WARN: 英文段数与译文段数不一致")
        ok = False
    if zh == 0:
        print("FAIL: 缺少中文全文译文（p.zh）")
        ok = False

    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
