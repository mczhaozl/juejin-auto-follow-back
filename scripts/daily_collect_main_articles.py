#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日定时：所有账号（大号+小号）收藏大号新发布的 10 篇文章中未收藏的。
- 每天 7:50 由 GitHub Actions 触发（见 .github/workflows/daily-collect-main-articles.yml）
- 每两次收藏 API 之间间隔 15 秒
- 顺序：先按文章（同一篇文章被各账号收藏完），再处理下一篇
"""

import os
import sys
import time
from pathlib import Path

# 保证从仓库根或 scripts 目录运行都能正确导入
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from scripts.juejin_collect import (
    DEFAULT_MAIN_USER_ID,
    query_user_articles,
    get_collections,
    collect_article_if_not_in,
)

COLLECT_INTERVAL_SEC = 15


def gather_accounts():
    """从环境变量收集所有账号（主账号 + 小号），与 daily_checkin 一致。"""
    cookies_main = os.getenv("JUEJIN_COOKIES")
    if not cookies_main:
        return []
    accounts = [("主账号", cookies_main)]
    for i, env_key in enumerate(
        [
            "JUEJIN_COOKIES_ACCOUNT2",
            "JUEJIN_COOKIES_ACCOUNT3",
            "JUEJIN_COOKIES_ACCOUNT4",
            "JUEJIN_COOKIES_ACCOUNT5",
            "JUEJIN_COOKIES_ACCOUNT6",
            "JUEJIN_COOKIES_ACCOUNT7",
            "JUEJIN_COOKIES_ACCOUNT8",
            "JUEJIN_COOKIES_ACCOUNT9",
        ],
        start=1,
    ):
        cookies = os.getenv(env_key)
        if cookies:
            accounts.append((f"小号{i}", cookies))
    return accounts


def get_main_article_ids(limit: int = 10):
    """获取大号最近 limit 篇文章的 article_id 列表。"""
    result = query_user_articles(DEFAULT_MAIN_USER_ID, cursor="0", limit=limit)
    if not result or result.get("err_no") != 0:
        return []
    data = result.get("data") or []
    return [item.get("article_id") for item in data if item.get("article_id")]


def run_daily_collect():
    """先按文章再按账号：同一篇文章被各账号收藏完再处理下一篇，每次收藏后间隔 15 秒。"""
    accounts = gather_accounts()
    if not accounts:
        print("❌ 未找到 JUEJIN_COOKIES，请在 GitHub Secrets 中配置")
        return

    article_ids = get_main_article_ids(limit=10)
    if not article_ids:
        print("❌ 未获取到大号文章列表")
        return

    # 预取各账号第一个收藏夹 ID
    accounts_with_coll = []
    for account_name, cookies in accounts:
        coll_res = get_collections(cookies, "")
        if not coll_res or coll_res.get("err_no") != 0:
            print(f"  ❌ [{account_name}] 获取收藏夹列表失败，跳过该账号")
            continue
        coll_data = coll_res.get("data") or []
        if not coll_data:
            print(f"  ❌ [{account_name}] 无收藏夹，跳过该账号")
            continue
        first_collection_id = coll_data[0].get("collection_id") or None
        accounts_with_coll.append((account_name, cookies, first_collection_id))

    if not accounts_with_coll:
        print("❌ 无可用账号（收藏夹获取均失败）")
        return

    print(f"📄 大号近 10 篇文章: {article_ids}")
    print(f"👤 共 {len(accounts_with_coll)} 个账号，顺序：先同一文章各账号收藏，再下一篇；间隔 {COLLECT_INTERVAL_SEC} 秒\n")

    total_collected = 0
    total_skipped = 0
    total_failed = 0

    for art_idx, article_id in enumerate(article_ids, 1):
        print(f"{'='*50}")
        print(f"📌 文章 [{art_idx}/{len(article_ids)}] {article_id}")
        print(f"{'='*50}")
        for account_name, cookies, first_collection_id in accounts_with_coll:
            status = collect_article_if_not_in(
                cookies,
                article_id,
                [first_collection_id] if first_collection_id else None,
            )
            if status == "collected":
                total_collected += 1
                print(f"  [{account_name}] ✅ 已收藏")
                time.sleep(COLLECT_INTERVAL_SEC)
            elif status == "skipped":
                total_skipped += 1
                print(f"  [{account_name}] ⏭️  已在收藏夹，跳过")
            else:
                total_failed += 1
                print(f"  [{account_name}] ❌ 收藏失败")
        print()

    print(f"{'='*50}")
    print("🎉 每日收藏任务结束")
    print(f"  新收藏: {total_collected} 次 | 已存在跳过: {total_skipped} 次 | 失败: {total_failed} 次")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_daily_collect()
