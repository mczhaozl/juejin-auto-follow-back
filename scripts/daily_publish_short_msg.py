#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日定时：用大号发一条沸点，内容为按当前日期时间选一句诗句（确定性 index，短期内不重复）。
- 每天 8:15、9:20、10:30 等由 GitHub Actions 触发（见 .github/workflows/daily-publish-short-msg.yml）
"""

import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

from scripts.juejin_short_msg import publish_short_msg
from scripts.short_msg_sentences import SENTENCES


def _sentence_index_for_now():
    """按当前 UTC 日期时间生成 [0, len(SENTENCES)) 的确定性下标，同一分钟相同，不同时间不重复。"""
    t = datetime.now(timezone.utc)
    # 年月日 + 时分，同一分钟内相同
    seed = (t.year * 10000 + t.month * 100 + t.day) * 24 * 60 + t.hour * 60 + t.minute
    return seed % len(SENTENCES)


def run_daily_publish_short_msg():
    """大号按当前日期时间选一句诗句发布为沸点。"""
    cookies = os.getenv("JUEJIN_COOKIES")
    if not cookies:
        print("❌ 未找到 JUEJIN_COOKIES，请在 GitHub Secrets 中配置")
        return

    idx = _sentence_index_for_now()
    content = SENTENCES[idx]
    print("📌 大号发沸点（内容来源：按日期时间选诗句）")
    print(f"   内容: {content}")

    if publish_short_msg(cookies, content):
        print("✅ 发布成功\n")
    else:
        print("❌ 发布失败\n")


if __name__ == "__main__":
    run_daily_publish_short_msg()
