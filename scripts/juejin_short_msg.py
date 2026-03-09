#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金沸点（short_msg）原子接口
- 获取推荐沸点列表（含内容）
- 点赞沸点（digg）
- 发布沸点（publish）
- 评论沸点（comment）
"""

from typing import Any, List, Optional

import os
import urllib.parse
import requests

from scripts.juejin_collect import (
    _default_headers,
    _extract_uuid,
    _sanitize_cookie_header,
)

BASE_URL = "https://api.juejin.cn"
AID = "2608"
SPIDER = "0"
ITEM_TYPE_SHORT_MSG = 4


def get_recommend_short_msgs(
    cookies_str: str,
    limit: int = 6,
    cursor: str = "0",
) -> List[Any]:
    """
    获取推荐沸点列表（含 content），用于取某条内容再发沸点等。
    :param cookies_str: 完整 Cookie 字符串
    :param limit: 条数
    :param cursor: 分页游标
    :return: data 列表，每项含 msg_id、msg_Info.content 等，失败返回 []
    """
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/recommend_api/v1/short_msg/recommend"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    payload = {"id_type": 4, "sort_type": 300, "cursor": cursor, "limit": limit}
    headers = {**_default_headers(), "Cookie": cookies_str}
    try:
        resp = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_no") != 0:
            return []
        return data.get("data") or []
    except Exception as e:
        print(f"❌ 获取推荐沸点失败: {e}")
        return []


def get_recommend_short_msg_ids(
    cookies_str: str,
    limit: int = 3,
    cursor: str = "0",
) -> List[str]:
    """
    获取推荐沸点列表的前 limit 条的 msg_id（需要登录）。
    :param cookies_str: 完整 Cookie 字符串
    :param limit: 条数
    :param cursor: 分页游标
    :return: msg_id 列表，失败返回 []
    """
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/recommend_api/v1/short_msg/recommend"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    payload = {"id_type": 4, "sort_type": 300, "cursor": cursor, "limit": limit}
    headers = {**_default_headers(), "Cookie": cookies_str}
    try:
        resp = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if data.get("err_no") != 0:
            return []
        items = data.get("data") or []
        return [str(x.get("msg_id", "")) for x in items[:limit] if x.get("msg_id")]
    except Exception as e:
        print(f"❌ 获取推荐沸点失败: {e}")
        return []


def publish_short_msg(cookies_str: str, content: str) -> bool:
    """
    发布一条沸点（需要登录）。
    :param cookies_str: 完整 Cookie 字符串
    :param content: 沸点正文
    :return: 是否成功
    """
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/content_api/v1/short_msg/publish"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    payload = {"content": content, "mentions": [], "sync_to_org": False}
    headers = {**_default_headers(), "Cookie": cookies_str}
    try:
        resp = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("err_no") == 0
    except Exception as e:
        print(f"❌ 发布沸点失败: {e}")
        return False


def digg_short_msg(cookies_str: str, msg_id: str) -> bool:
    """
    点赞一条沸点（需要登录）。
    :param cookies_str: 完整 Cookie 字符串
    :param msg_id: 沸点 msg_id
    :return: 是否成功
    """
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/interact_api/v1/digg/save"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    payload = {"item_id": msg_id, "item_type": ITEM_TYPE_SHORT_MSG, "client_type": 2608}
    headers = {**_default_headers(), "Cookie": cookies_str}
    try:
        resp = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("err_no") == 0
    except Exception as e:
        print(f"❌ 点赞沸点失败 {msg_id}: {e}")
        return False


def comment_short_msg(
    cookies_str: str,
    msg_id: str,
    comment_content: str,
) -> bool:
    """
    评论一条沸点（需要登录）。
    若接口返回空，需同时提供 JUEJIN_CSRF_TOKEN、JUEJIN_MS_TOKEN、JUEJIN_A_BOGUS（从浏览器评论请求的 URL 与请求头复制）。
    """
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/interact_api/v1/comment/publish"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    ms_token = (os.getenv("JUEJIN_MS_TOKEN") or "").strip()
    a_bogus = (os.getenv("JUEJIN_A_BOGUS") or "").strip()
    if ms_token:
        try:
            params["msToken"] = urllib.parse.unquote(ms_token)
        except Exception:
            params["msToken"] = ms_token
    if a_bogus:
        try:
            params["a_bogus"] = urllib.parse.unquote(a_bogus)
        except Exception:
            params["a_bogus"] = a_bogus
    payload = {
        "client_type": 2608,
        "item_id": msg_id,
        "item_type": ITEM_TYPE_SHORT_MSG,
        "comment_content": comment_content,
        "comment_pics": [],
    }
    headers = {**_default_headers(), "Cookie": cookies_str}
    csrf = (os.getenv("JUEJIN_CSRF_TOKEN") or "").strip()
    if csrf:
        headers["x-secsdk-csrf-token"] = csrf
    try:
        resp = requests.post(
            url,
            params=params,
            headers=headers,
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        text = (resp.text or "").strip()
        if not text:
            has_csrf = "是" if csrf else "否"
            has_ms = "是" if ms_token else "否"
            has_ab = "是" if a_bogus else "否"
            print(f"❌ 评论沸点失败 {msg_id}: 接口返回空 | 已带 CSRF: {has_csrf}, msToken: {has_ms}, a_bogus: {has_ab}（若均为是仍失败，多半为 msToken/a_bogus 已过期，请从浏览器评论请求 URL 重新复制）")
            return False
        try:
            data = resp.json()
        except ValueError:
            print(f"❌ 评论沸点失败 {msg_id}: 接口返回非 JSON，status={resp.status_code} body={text[:100]!r}")
            return False
        return data.get("err_no") == 0
    except requests.exceptions.HTTPError as e:
        print(f"❌ 评论沸点失败 {msg_id}: HTTP {e.response.status_code if e.response else ''} {e}")
        return False
    except Exception as e:
        print(f"❌ 评论沸点失败 {msg_id}: {e}")
        return False
