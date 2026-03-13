#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
一次性迁移：为 databae/0314～0331 下每篇文章的 config.json 写入 title、brief（从 index.md 解析）。
运行后请检查 git diff，确认无误再提交。
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DATABAE = REPO_ROOT / "databae"


def parse_title_brief(content: str) -> tuple[str, str]:
    """从 index.md 解析主标题（首行 #）和摘要（第一个 --- 之前的 > 引用块）。"""
    raw = content.strip()
    lines = raw.split("\n")
    title = ""
    brief_lines = []
    sep_idx = -1
    for i, line in enumerate(lines):
        if line.strip() == "---":
            sep_idx = i
            break
    for i, line in enumerate(lines):
        if sep_idx >= 0 and i >= sep_idx:
            break
        if not title and line.strip().startswith("# "):
            title = line.strip()[2:].strip()
            continue
        if line.strip().startswith(">"):
            brief_lines.append(line.strip()[1:].strip())
    brief = " ".join(brief_lines).strip() if brief_lines else ""
    if not title and brief:
        title = brief[:50]
    if not title:
        m = re.match(r"^#\s+(.+)$", raw.strip())
        title = m.group(1).strip() if m else "未命名"
    if not brief:
        brief = title
    if len(brief) < 50:
        brief = (brief + " " * 60)[:100].rstrip().ljust(50)
    elif len(brief) > 100:
        brief = brief[:100]
    return title, brief


def main():
    mmdd_list = [f"03{d:02d}" for d in range(14, 32)]  # 0314..0331
    done = 0
    for mmdd in mmdd_list:
        day_dir = DATABAE / mmdd
        if not day_dir.is_dir():
            continue
        for sub in sorted(day_dir.iterdir()):
            if not sub.is_dir():
                continue
            config_path = sub / "config.json"
            index_path = sub / "index.md"
            if not config_path.is_file() or not index_path.is_file():
                continue
            try:
                config = json.loads(config_path.read_text(encoding="utf-8"))
            except Exception as e:
                print(f"⚠️ 跳过 {sub}: config 解析失败 {e}")
                continue
            try:
                raw = index_path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"⚠️ 跳过 {sub}: index.md 读取失败 {e}")
                continue
            title, brief = parse_title_brief(raw)
            config["title"] = title
            config["brief"] = brief
            config_path.write_text(json.dumps(config, ensure_ascii=False, indent=4) + "\n", encoding="utf-8")
            print(f"✅ {mmdd}/{sub.name}: title={title[:40]}…")
            done += 1
    print(f"\n🎉 共写入 {done} 个 config.json（0314～0331）")


if __name__ == "__main__":
    main()
