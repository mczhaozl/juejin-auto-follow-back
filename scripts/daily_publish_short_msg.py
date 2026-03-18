#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日定时：用大号发一条沸点，内容为从固定诗句列表中随机选一句。
- 每天 8:15、9:20、10:30 由 GitHub Actions 触发（见 .github/workflows/daily-publish-short-msg.yml）
"""

import os
import random
import sys
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from scripts.juejin_short_msg import publish_short_msg
from scripts.short_msg_sentences import SENTENCES


def run_daily_publish_short_msg():
    """大号从诗句列表中随机选一句发布为沸点。"""
    cookies = os.getenv("JUEJIN_COOKIES")
    if not cookies:
        print("❌ 未找到 JUEJIN_COOKIES，请在 GitHub Secrets 中配置")
        return

    content = random.choice(SENTENCES)
    print("📌 大号发沸点（内容来源：随机诗句）")
    print(f"   内容: {content}")

    if publish_short_msg(cookies, content):
        print("✅ 发布成功\n")
    else:
        print("❌ 发布失败\n")


if __name__ == "__main__":
    run_daily_publish_short_msg()
