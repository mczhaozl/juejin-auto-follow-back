#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日上传 databae 中「当天」的文档到掘金（以北京时间为准）。
- 目录规范：databae/{MMDD}/<slug>/config.json + index.md（MMDD = 北京时间的月日，如 0309 表示 3 月 9 日）
- 每天定时执行，上传当日目录下的全部文章，每篇间隔 1 分钟；若当日没有对应目录则不上传。
- Cookie：与其它定时脚本一致，使用 JUEJIN_COOKIES（大号）。
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    from zoneinfo import ZoneInfo
    BEIJING_TZ = ZoneInfo("Asia/Shanghai")
except ImportError:
    BEIJING_TZ = timezone(timedelta(hours=8))

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from scripts.juejin_article import publish_article
from scripts.juejin_themes import pick_theme_for_article

DATABAE_DIR = _repo_root / "databae"
UPLOAD_INTERVAL_SEC = 60


def get_today_mmdd() -> str:
    """北京时间的当日 MMDD（月日，如 0309 表示 3 月 9 日）。"""
    now = datetime.now(BEIJING_TZ)
    return now.strftime("%m%d")


def parse_index_md(content: str):
    """从 index.md 解析：标题（首行 # 后）、摘要（首段 > 引用，50–100 字）、正文。"""
    lines = content.strip().split("\n")
    title = ""
    brief_lines = []
    body_lines = []
    in_brief = False
    after_sep = False

    for line in lines:
        if not title and line.strip().startswith("# "):
            title = line.strip()[2:].strip()
            continue
        if line.strip() == "---":
            after_sep = True
            if in_brief:
                in_brief = False
            body_lines.append(line)
            continue
        if not after_sep and line.strip().startswith(">"):
            in_brief = True
            brief_lines.append(line.strip()[1:].strip())
            continue
        if in_brief and (not line.strip() or not line.strip().startswith(">")):
            in_brief = False
        body_lines.append(line)

    brief = " ".join(brief_lines).strip() if brief_lines else ""
    if not brief and title:
        brief = title
    if len(brief) < 50:
        brief = (brief + " " * 60)[:100].rstrip().ljust(50)
    elif len(brief) > 100:
        brief = brief[:100]

    body = "\n".join(body_lines).strip()
    if not title and body:
        m = re.match(r"^#\s+(.+)$", body.strip())
        if m:
            title = m.group(1).strip()
    return title or "未命名", brief, body or content


def collect_today_articles():
    """
    收集当日（北京 MMDD）下所有含 config.json + index.md 的子目录。
    :return: [(article_dir, config, title, brief, mark_content), ...]
    """
    mmdd = get_today_mmdd()
    day_dir = DATABAE_DIR / mmdd
    if not day_dir.is_dir():
        return []

    result = []
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
            print(f"⚠️ 跳过 {sub.name}: config.json 解析失败 {e}")
            continue
        try:
            raw = index_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"⚠️ 跳过 {sub.name}: index.md 读取失败 {e}")
            continue
        title, brief, mark_content = parse_index_md(raw)
        if not title or not mark_content:
            print(f"⚠️ 跳过 {sub.name}: 标题或正文为空")
            continue
        result.append((sub, config, title, brief, mark_content))
    return result


def run():
    cookies = os.getenv("JUEJIN_COOKIES")
    if not cookies:
        print("❌ 未找到 JUEJIN_COOKIES，请在 GitHub Secrets 中配置")
        return

    mmdd = get_today_mmdd()
    articles = collect_today_articles()
    if not articles:
        print(f"📭 当日（{mmdd}）无待上传文档，跳过")
        return

    print(f"📌 当日（{mmdd}）共 {len(articles)} 篇，每篇间隔 {UPLOAD_INTERVAL_SEC} 秒\n")
    for i, (art_dir, config, title, brief, mark_content) in enumerate(articles, 1):
        category_id = str(config.get("categoryId") or "")
        tag_ids_raw = config.get("tagIds") or ""
        tag_ids = [t.strip() for t in str(tag_ids_raw).split(",") if t.strip()]
        do_publish = bool(config.get("publish", True))

        if not category_id or not tag_ids:
            print(f"  [{i}/{len(articles)}] ⚠️ {art_dir.name} 缺少 categoryId 或 tagIds，跳过")
            continue

        theme_id = pick_theme_for_article(title, brief)
        theme_ids = [theme_id] if theme_id else []
        if theme_id:
            print(f"  [{i}/{len(articles)}] 📄 {title[:40]}… | 话题: 已选")
        else:
            print(f"  [{i}/{len(articles)}] 📄 {title[:40]}… | 话题: 未选")

        article_id, draft_id = publish_article(
            cookies,
            title=title,
            mark_content=mark_content,
            brief_content=brief,
            category_id=category_id,
            tag_ids=tag_ids,
            theme_ids=theme_ids,
            do_publish=do_publish,
        )
        if article_id:
            print(f"  [{i}/{len(articles)}] ✅ 已发布 article_id={article_id}")
        elif draft_id:
            print(f"  [{i}/{len(articles)}] 📝 已存草稿 draft_id={draft_id}")
        else:
            print(f"  [{i}/{len(articles)}] ❌ 发布失败")

        if i < len(articles):
            time.sleep(UPLOAD_INTERVAL_SEC)

    print("\n🎉 完成\n")


if __name__ == "__main__":
    run()
