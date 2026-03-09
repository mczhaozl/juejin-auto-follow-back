#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金文章发布（草稿创建 + 发布）
- 先创建草稿获得 draft_id，再调用发布接口
- 支持 theme_ids（话题），可选
- Cookie：与其它定时脚本一致，使用环境变量 JUEJIN_COOKIES（大号）
"""

import os
from typing import List, Optional, Tuple

import requests

from scripts.juejin_collect import (
    _default_headers,
    _extract_uuid,
    _sanitize_cookie_header,
)

BASE_URL = "https://api.juejin.cn"
AID = "2608"
SPIDER = "0"


def create_draft(
    cookies_str: str,
    title: str,
    mark_content: str,
    brief_content: str,
    category_id: str,
    tag_ids: List[str],
    theme_ids: Optional[List[str]] = None,
) -> Optional[str]:
    """
    创建文章草稿。brief_content 需 50–100 字。
    :return: draft_id（即 data.id），失败返回 None
    """
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/content_api/v1/article_draft/create"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    brief = (brief_content or "").strip()
    if len(brief) < 50:
        brief = (brief + " " * 60)[:100].rstrip().ljust(50)
    elif len(brief) > 100:
        brief = brief[:100]
    payload = {
        "category_id": category_id,
        "tag_ids": tag_ids,
        "title": title,
        "brief_content": brief,
        "edit_type": 10,
        "html_content": "deprecated",
        "mark_content": mark_content,
        "theme_ids": theme_ids or [],
        "link_url": "",
        "cover_image": "",
        "pics": [],
    }
    headers = {**_default_headers(), "Cookie": cookies_str}
    try:
        resp = requests.post(url, params=params, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_no") != 0:
            print(f"❌ 创建草稿失败: {data.get('err_msg', '')}")
            return None
        d = data.get("data") or {}
        draft_id = d.get("id") or d.get("article_id")
        return str(draft_id) if draft_id else None
    except Exception as e:
        print(f"❌ 创建草稿失败: {e}")
        return None


def publish_draft(
    cookies_str: str,
    draft_id: str,
    theme_ids: Optional[List[str]] = None,
) -> Optional[str]:
    """
    发布已创建的草稿。
    :return: article_id，失败返回 None
    """
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/content_api/v1/article/publish"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    payload = {
        "draft_id": draft_id,
        "sync_to_org": False,
        "column_ids": [],
        "theme_ids": theme_ids or [],
        "encrypted_word_count": 0,
        "origin_word_count": 0,
    }
    headers = {**_default_headers(), "Cookie": cookies_str}
    try:
        resp = requests.post(url, params=params, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_no") != 0:
            print(f"❌ 发布失败: {data.get('err_msg', '')}")
            return None
        d = data.get("data") or {}
        return str(d.get("article_id") or "")
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        return None


def publish_article(
    cookies_str: str,
    title: str,
    mark_content: str,
    brief_content: str,
    category_id: str,
    tag_ids: List[str],
    theme_ids: Optional[List[str]] = None,
    do_publish: bool = True,
) -> Tuple[Optional[str], Optional[str]]:
    """
    创建草稿并可选发布。
    :return: (article_id, None) 成功；(None, draft_id) 仅草稿；(None, None) 失败
    """
    draft_id = create_draft(
        cookies_str, title, mark_content, brief_content, category_id, tag_ids, theme_ids
    )
    if not draft_id:
        return None, None
    if not do_publish:
        return None, draft_id
    article_id = publish_draft(cookies_str, draft_id, theme_ids)
    if article_id:
        return article_id, None
    return None, draft_id
