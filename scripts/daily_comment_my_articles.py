#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日定时：大号给自己的前 10 篇文章评论区补发固定评论（若首次查询未出现则发布）。
- 每天 10:00 由 GitHub Actions 触发（见 .github/workflows/daily-comment-my-articles.yml）
- 每篇文章只查一次评论列表，无则发一条
"""

import os
import sys
import time
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from scripts.juejin_collect import (
    DEFAULT_MAIN_USER_ID,
    query_user_articles,
    get_article_comment_list,
    comment_article,
)

TARGET_COMMENT = "我已开启五倍返利系统,关注我 你将在两小时内收获五倍粉丝!"
TOP_ARTICLES = 10
COMMENT_LIST_LIMIT = 20
COMMENT_INTERVAL_SEC = 30


def article_has_target_comment(cookies_str: str, article_id: str) -> bool:
    """只查一次评论列表，判断是否已有目标评论。"""
    res = get_article_comment_list(
        cookies_str,
        article_id,
        cursor="0",
        limit=COMMENT_LIST_LIMIT,
    )
    if not res or res.get("err_no") != 0:
        return False
    for item in res.get("data") or []:
        info = item.get("comment_info") or {}
        if (info.get("comment_content") or "").strip() == TARGET_COMMENT:
            return True
    return False


def run_daily_comment_my_articles():
    """大号：前 10 篇文章，若无目标评论则发一条。"""
    cookies = os.getenv("JUEJIN_COOKIES")
    if not cookies:
        print("❌ 未找到 JUEJIN_COOKIES，请在 GitHub Secrets 中配置")
        return

    result = query_user_articles(DEFAULT_MAIN_USER_ID, cursor="0", limit=TOP_ARTICLES)
    if not result or result.get("err_no") != 0:
        print("❌ 未获取到大号文章列表")
        return

    article_ids = [
        item.get("article_id")
        for item in (result.get("data") or [])
        if item.get("article_id")
    ]
    if not article_ids:
        print("❌ 大号无文章")
        return

    print(f"📌 大号给自己的前 {TOP_ARTICLES} 篇文章补评论（目标文案已存在则跳过）")
    print(f"   目标评论: 「{TARGET_COMMENT}」")
    print(f"   每次发布评论间隔 {COMMENT_INTERVAL_SEC} 秒\n")

    published = 0
    skipped = 0
    failed = 0
    for i, article_id in enumerate(article_ids, 1):
        if article_has_target_comment(cookies, article_id):
            skipped += 1
            print(f"  [{i}/{len(article_ids)}] ⏭️  {article_id} 已有目标评论，跳过")
        else:
            if comment_article(cookies, article_id, TARGET_COMMENT):
                published += 1
                print(f"  [{i}/{len(article_ids)}] ✅ 已发布评论 {article_id}")
                if i < len(article_ids):
                    time.sleep(COMMENT_INTERVAL_SEC)
            else:
                failed += 1
                print(f"  [{i}/{len(article_ids)}] ❌ 发布失败 {article_id}")

    print(f"\n🎉 完成：新发布 {published}，已存在跳过 {skipped}，失败 {failed}\n")


if __name__ == "__main__":
    run_daily_comment_my_articles()
