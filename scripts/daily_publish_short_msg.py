#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日定时：用大号发一条沸点，内容为推荐列表第 6 条的内容 + 固定后缀（方便后续删除）。
- 每天 8:15、9:20、10:30 由 GitHub Actions 触发（见 .github/workflows/daily-publish-short-msg.yml）
"""

import os
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from scripts.juejin_short_msg import get_recommend_short_msgs, publish_short_msg

RECOMMEND_INDEX_FOR_CONTENT = 5  # 第 6 条（0-based）
CONTENT_SUFFIX = ",另外有人互关注或者点赞文章吗,我已经开启了五倍返利系统,一起活跃一下呗..."


def run_daily_publish_short_msg():
    """大号取推荐第 6 条沸点内容 + '...' 后发布。"""
    cookies = os.getenv("JUEJIN_COOKIES")
    if not cookies:
        print("❌ 未找到 JUEJIN_COOKIES，请在 GitHub Secrets 中配置")
        return

    items = get_recommend_short_msgs(cookies, limit=6)
    if len(items) <= RECOMMEND_INDEX_FOR_CONTENT:
        print(f"❌ 推荐沸点不足 {RECOMMEND_INDEX_FOR_CONTENT + 1} 条，当前 {len(items)} 条")
        return

    item = items[RECOMMEND_INDEX_FOR_CONTENT]
    msg_info = item.get("msg_Info") or {}
    raw_content = (msg_info.get("content") or "").strip()
    if not raw_content:
        print("❌ 第 6 条沸点无 content，跳过发布")
        return

    content = raw_content + CONTENT_SUFFIX
    print(f"📌 大号发沸点（内容来源：推荐第 6 条 + 固定后缀）")
    print(f"   内容预览: {content[:60]}...")

    if publish_short_msg(cookies, content):
        print("✅ 发布成功\n")
    else:
        print("❌ 发布失败\n")


if __name__ == "__main__":
    run_daily_publish_short_msg()
