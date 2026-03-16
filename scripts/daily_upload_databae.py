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
from scripts.juejin_collect import get_main_account_published_titles

DATABAE_DIR = _repo_root / "databae"
UPLOAD_INTERVAL_SEC = 60

# 上传前是否根据「大号前 10 篇标题」判重：已发布过则跳过。设为 False 或环境变量 SKIP_IF_ALREADY_PUBLISHED=0 可关闭
SKIP_IF_ALREADY_PUBLISHED = os.getenv("SKIP_IF_ALREADY_PUBLISHED", "1").strip().lower() in ("1", "true", "yes")
PUBLISHED_TITLES_LIMIT = 10


def get_today_mmdd() -> str:
    """北京时间的当日 MMDD（月日，如 0309 表示 3 月 9 日）。"""
    now = datetime.now(BEIJING_TZ)
    return now.strftime("%m%d")


def parse_index_md(content: str):
    """
    从 index.md 解析：标题（首行 # 后）、摘要（首段 > 引用，50–100 字）、正文。
    正文规则：若有至少 2 个独立行 '---'，正文 = 第一个与最后一个 '---' 之间的内容（不含这两行，中间的 --- 保留为正文分隔线）；
    若只有 1 个 '---' 则取该行之后的全部；若无则取除标题和 > 摘要块外的全部。
    """
    raw = content.strip()
    lines = raw.split("\n")
    title = ""
    brief_lines = []
    sep_indices = [i for i, line in enumerate(lines) if line.strip() == "---"]
    if len(sep_indices) >= 2:
        first, last = sep_indices[0], sep_indices[-1]
        body = "\n".join(lines[first + 1 : last]).strip()
        sep_idx = first
    elif len(sep_indices) == 1:
        sep_idx = sep_indices[0]
        body = "\n".join(lines[sep_idx + 1 :]).strip()
    else:
        sep_idx = -1
        body = ""
    if sep_idx < 0:
        body_lines = []
        in_brief = False
        for line in lines:
            if not title and line.strip().startswith("# "):
                title = line.strip()[2:].strip()
                continue
            if line.strip().startswith(">"):
                in_brief = True
                brief_lines.append(line.strip()[1:].strip())
                continue
            if in_brief and (not line.strip() or not line.strip().startswith(">")):
                in_brief = False
            body_lines.append(line)
        body = "\n".join(body_lines).strip()

    # 标题：若尚未从首行解析到，尝试从正文首行 # 取
    if not title and body:
        m = re.match(r"^#\s+(.+)$", body.strip())
        if m:
            title = m.group(1).strip()
    if not title:
        for line in lines:
            if line.strip().startswith("# "):
                title = line.strip()[2:].strip()
                break
    title = title or "未命名"

    # 摘要：仅从 "---" 之前的行里取 > 引用
    if sep_idx > 0:
        brief_lines = []
        for line in lines[:sep_idx]:
            if line.strip().startswith(">"):
                brief_lines.append(line.strip()[1:].strip())
    brief = " ".join(brief_lines).strip() if brief_lines else ""
    if not brief and title:
        brief = title
    if len(brief) < 50:
        brief = (brief + " " * 60)[:100].rstrip().ljust(50)
    elif len(brief) > 100:
        brief = brief[:100]

    # 正文为空时用全文，避免上传无内容
    if not body or len(body) < 20:
        body = raw
    return title, brief, body


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
        parsed_title, parsed_brief, mark_content = parse_index_md(raw)
        # 优先使用 config 中的 title、brief，不解析文档
        title = (config.get("title") or "").strip() or parsed_title
        brief = (config.get("brief") or "").strip() or parsed_brief
        if not title or not mark_content:
            print(f"⚠️ 跳过 {sub.name}: 标题或正文为空")
            continue
        if not brief or len(brief) < 50:
            brief = (brief or title or "") + " " * 60
            brief = brief[:100].rstrip().ljust(50)
        elif len(brief) > 100:
            brief = brief[:100]
        result.append((sub, config, title, brief, mark_content))
    return result


def get_published_titles_for_skip_check(limit: int = 10) -> set:
    """获取大号已发布文章标题集合，用于上传前判重。失败时返回空集合。"""
    return get_main_account_published_titles(limit=limit)


def should_skip_upload_by_title(title: str, published_titles: set) -> bool:
    """若 title 已出现在大号已发布标题集合中，则应跳过本次上传。"""
    if not title or not published_titles:
        return False
    return title.strip() in published_titles


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

    published_titles = set()
    if SKIP_IF_ALREADY_PUBLISHED:
        published_titles = get_published_titles_for_skip_check(limit=PUBLISHED_TITLES_LIMIT)
        print(f"📌 已开启「上传前判重」：大号近 {PUBLISHED_TITLES_LIMIT} 篇标题共 {len(published_titles)} 个，与待上传标题重复则跳过")
    print(f"📌 当日（{mmdd}）共 {len(articles)} 篇，每篇间隔 {UPLOAD_INTERVAL_SEC} 秒\n")

    for i, (art_dir, config, title, brief, mark_content) in enumerate(articles, 1):
        if SKIP_IF_ALREADY_PUBLISHED and should_skip_upload_by_title(title, published_titles):
            print(f"  [{i}/{len(articles)}] ⏭️  {title[:40]}… 已发布过（标题在大号前 {PUBLISHED_TITLES_LIMIT} 篇中），跳过")
            if i < len(articles):
                time.sleep(UPLOAD_INTERVAL_SEC)
            continue

        category_id = str(config.get("categoryId") or "")
        tag_ids_raw = config.get("tagIds") or ""
        tag_ids = [t.strip() for t in str(tag_ids_raw).split(",") if t.strip()]
        do_publish = bool(config.get("publish", True))

        if not category_id or not tag_ids:
            print(f"  [{i}/{len(articles)}] ⚠️ {art_dir.name} 缺少 categoryId 或 tagIds，跳过")
            continue

        # 优先使用 config 中的 themeIds；否则由话题专家根据标题/摘要匹配
        config_theme = config.get("themeIds")
        if config_theme is not None:
            if isinstance(config_theme, list):
                theme_ids = [str(t) for t in config_theme if t]
            else:
                theme_ids = [str(config_theme).strip()] if str(config_theme).strip() else []
        else:
            theme_id = pick_theme_for_article(title, brief)
            theme_ids = [theme_id] if theme_id else []
        # 专栏：config 中 columnIds（字符串或数组），发布时传入
        config_column = config.get("columnIds")
        if config_column is not None:
            if isinstance(config_column, list):
                column_ids = [str(c) for c in config_column if c]
            else:
                column_ids = [s.strip() for s in str(config_column).split(",") if s.strip()]
        else:
            column_ids = []

        body_len = len(mark_content)
        if theme_ids:
            print(f"  [{i}/{len(articles)}] 📄 {title[:40]}… | 正文 {body_len} 字 | 话题: 已选")
        else:
            print(f"  [{i}/{len(articles)}] 📄 {title[:40]}… | 正文 {body_len} 字 | 话题: 未选")
        if column_ids:
            print(f"  [{i}/{len(articles)}]    专栏: 已选 {len(column_ids)} 个")
        if body_len < 100:
            print(f"  [{i}/{len(articles)}] ⚠️ 正文过短({body_len}字)，请检查 index.md 是否有 --- 及正文")

        cover_image = (config.get("cover_image") or config.get("coverImage") or "").strip() or None

        article_id, draft_id = publish_article(
            cookies,
            title=title,
            mark_content=mark_content,
            brief_content=brief,
            category_id=category_id,
            tag_ids=tag_ids,
            theme_ids=theme_ids,
            column_ids=column_ids,
            do_publish=do_publish,
            cover_image=cover_image,
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
