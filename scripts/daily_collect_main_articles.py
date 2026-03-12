#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日定时：所有账号（大号+小号）收藏大号新发布的 10 篇文章中未收藏的。
- 每天 7:50 由 GitHub Actions 触发（见 .github/workflows/daily-collect-main-articles.yml）
- 每两次收藏 API 之间间隔 30 秒
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

COLLECT_INTERVAL_SEC = 30


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
    """对所有账号执行：收藏大号近 10 篇中未收藏的，每次收藏后间隔 30 秒。"""
    accounts = gather_accounts()
    if not accounts:
        print("❌ 未找到 JUEJIN_COOKIES，请在 GitHub Secrets 中配置")
        return

    article_ids = get_main_article_ids(limit=10)
    if not article_ids:
        print("❌ 未获取到大号文章列表")
        return

    print(f"📄 大号近 10 篇文章: {article_ids}")
    print(f"👤 共 {len(accounts)} 个账号，每两次收藏 API 间隔 {COLLECT_INTERVAL_SEC} 秒\n")

    total_collected = 0
    total_skipped = 0
    total_failed = 0

    for account_name, cookies in accounts:
        print(f"{'='*50}")
        print(f"🎯 [{account_name}] 开始处理")
        print(f"{'='*50}")

        # 获取该账号第一个收藏夹 ID（不同账号可能不同）
        coll_res = get_collections(cookies, "")
        if not coll_res or coll_res.get("err_no") != 0:
            print(f"  ❌ 获取收藏夹列表失败，跳过该账号\n")
            total_failed += len(article_ids)
            continue
        coll_data = coll_res.get("data") or []
        if not coll_data:
            print(f"  ❌ 无收藏夹，跳过该账号\n")
            continue
        first_collection_id = coll_data[0].get("collection_id")
        if not first_collection_id:
            first_collection_id = None  # 让 collect_article_if_not_in 内部用默认

        collected_this_account = 0
        for i, article_id in enumerate(article_ids, 1):
            status = collect_article_if_not_in(
                cookies,
                article_id,
                [first_collection_id] if first_collection_id else None,
            )
            if status == "collected":
                total_collected += 1
                collected_this_account += 1
                print(f"  [{i}/10] ✅ 已收藏 {article_id}")
                time.sleep(COLLECT_INTERVAL_SEC)
            elif status == "skipped":
                total_skipped += 1
                print(f"  [{i}/10] ⏭️  {article_id} 已在收藏夹，跳过")
            else:
                total_failed += 1
                print(f"  [{i}/10] ❌ 收藏失败 {article_id}")

        print(f"  [{account_name}] 本账号本次新收藏: {collected_this_account} 篇\n")

    print(f"{'='*50}")
    print("🎉 每日收藏任务结束")
    print(f"  新收藏: {total_collected} 次 | 已存在跳过: {total_skipped} 次 | 失败: {total_failed} 次")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    run_daily_collect()
