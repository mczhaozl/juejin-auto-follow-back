#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金话题列表与话题专家：根据文章标题/摘要匹配合适话题，没有合适则不选。
"""

from typing import Optional

# 话题专家：关键词 -> theme_id（按优先级）
THEME_KEYWORDS = [
    (["MCP", "mcp"], "7487778802563547174"),
    (["AI 编程", "AI编程", "人工智能", "大模型", "机器学习", "深度学习", "NLP", "计算机视觉"], "7509033842892603419"),
    (["2025 AI", "Vibe Coding", "年终", "围炉"], "7586482726807535666"),
    (["技术写作", "写作成长"], "7215101716402798596"),
    (["青训营", "笔记创作", "伴学"], "7172374200018010142"),
    (["新人", "自我介绍"], "7073670907851440160"),
    (["日新", "每日", "每天一个知识点"], "7243698841848348730"),
    (["精选", "掘金一周"], "7476000490959044659"),
    (["精选文章"], "7275231252674773028"),
]


def pick_theme_for_article(title: str, brief_content: str) -> Optional[str]:
    """
    根据标题与摘要选择合适的话题 theme_id，没有合适则返回 None。
    """
    text = f"{title}\n{brief_content}".lower()
    for keywords, theme_id in THEME_KEYWORDS:
        for kw in keywords:
            if kw.lower() in text or kw in title or kw in brief_content:
                return theme_id
    return None
