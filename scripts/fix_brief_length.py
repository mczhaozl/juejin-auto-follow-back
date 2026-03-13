#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""将 databae 下所有 config.json 的 brief 修正为 50–100 字（不足则尾部补空格，超过则截断）。"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATABAE = REPO / "databae"


def normalize_brief(brief: str) -> str:
    """保证摘要有效内容 50–100 字：不足 50 字则补一句短句，超过 100 字则截断。"""
    s = (brief or "").strip()
    if len(s) > 100:
        return s[:100]
    if len(s) < 50:
        # 补足到至少 50 字有效内容（一句约 22 字，可重复至满 50）
        suffix = " 本文从原理到实战带你搞懂，阅读即可掌握。"
        while len(s) < 50:
            s = (s + suffix)[:100].rstrip()
        s = s[:100]
    return s


def main():
    updated = []
    for f in sorted(DATABAE.glob("**/config.json")):
        try:
            config = json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            continue
        if "brief" not in config:
            continue
        old = config["brief"]
        new = normalize_brief(old)
        if new != old:
            config["brief"] = new
            f.write_text(json.dumps(config, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
            updated.append((str(f.relative_to(REPO)), len(old.strip()), len(new)))
    for path, old_len, new_len in updated:
        print(f"✅ {path}: {old_len} -> {new_len} 字")
    print(f"\n共修正 {len(updated)} 个 config.json")


if __name__ == "__main__":
    main()
