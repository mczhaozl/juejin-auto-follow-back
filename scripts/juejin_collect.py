#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金文章查询与收藏（原子化接口）
- 查询指定用户最近 N 篇文章（无需登录）
- 获取当前账号收藏夹列表
- 将文章加入收藏夹（默认使用第一个收藏夹）
"""

import json
import os
import urllib.parse
from typing import List, Optional

import requests

BASE_URL = "https://api.juejin.cn"
AID = "2608"
SPIDER = "0"

# 默认使用第一个收藏夹「我的收藏」的 ID（与当前账号一致时可写死）
DEFAULT_FIRST_COLLECTION_ID = "7289368836561010744"

# 大号 user_id（查询近 10 篇文章示例）
DEFAULT_MAIN_USER_ID = "994385683293918"


def _default_headers():
    return {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "origin": "https://juejin.cn",
        "referer": "https://juejin.cn/",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
    }


def _sanitize_cookie_header(cookies_str: str) -> str:
    """去掉 Cookie 中的换行/首尾空白，避免 Invalid header value（如 GitHub Secrets 粘贴带换行）。"""
    if not cookies_str:
        return cookies_str or ""
    return cookies_str.strip().replace("\n", "").replace("\r", "")


def _extract_uuid(cookies_str: str) -> str:
    """从 Cookie 字符串中解析 web_id 作为 uuid。"""
    try:
        for item in cookies_str.split(";"):
            item = item.strip()
            if "__tea_cookie_tokens_2608" not in item:
                continue
            value = item.split("=", 1)[1]
            decoded = urllib.parse.unquote(urllib.parse.unquote(value))
            tokens = json.loads(decoded)
            web_id = tokens.get("web_id")
            if web_id:
                return web_id
    except Exception:
        pass
    return "7586574305263552043"


def query_user_articles(user_id: str, cursor: str = "0", limit: int = 10):
    """
    查询指定用户最近的文章列表（无需登录）。
    :param user_id: 掘金用户 ID
    :param cursor: 分页游标，首次传 "0"
    :param limit: 每页条数
    :return: {"data": [{"article_id": "..."}], "cursor", "count", "has_more"} 或 None
    """
    url = f"{BASE_URL}/content_api/v1/article/query_list"
    params = {"aid": AID, "uuid": "0", "spider": SPIDER}
    payload = {"user_id": user_id, "sort_type": 2, "cursor": cursor}
    try:
        resp = requests.post(
            url,
            params=params,
            headers=_default_headers(),
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"❌ 查询文章列表失败: {e}")
        return None


def get_collections(cookies_str: str, article_id: str = ""):
    """
    获取当前账号的收藏夹列表（需要登录）。
    :param cookies_str: 完整 Cookie 字符串
    :param article_id: 可选，用于判断文章是否已在某收藏夹
    :return: {"data": [{"collection_id", "collection_name", ...}], ...} 或 None
    """
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/interact_api/v2/collectionset/list"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    payload = {"limit": 10, "cursor": "0", "article_id": article_id or "0"}
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
        return resp.json()
    except Exception as e:
        print(f"❌ 获取收藏夹列表失败: {e}")
        return None


def add_article_to_collection(
    cookies_str: str,
    article_id: str,
    collection_ids: Optional[List[str]] = None,
):
    """
    将文章加入收藏夹（需要登录）。未传 collection_ids 时使用默认第一个收藏夹。
    :param cookies_str: 完整 Cookie 字符串
    :param article_id: 文章 ID
    :param collection_ids: 要加入的收藏夹 ID 列表，默认 [DEFAULT_FIRST_COLLECTION_ID]
    :return: API 原始 JSON 或 None
    """
    if not collection_ids:
        collection_ids = [DEFAULT_FIRST_COLLECTION_ID]
    cookies_str = _sanitize_cookie_header(cookies_str)
    uuid = _extract_uuid(cookies_str)
    url = f"{BASE_URL}/interact_api/v2/collectionset/add_article"
    params = {"aid": AID, "uuid": uuid, "spider": SPIDER}
    payload = {
        "article_id": article_id,
        "select_collection_ids": collection_ids,
        "unselect_collection_ids": [],
        "is_collect_fast": False,
    }
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
        return resp.json()
    except Exception as e:
        print(f"❌ 收藏文章失败: {e}")
        return None


def is_article_in_first_collection(cookies_str: str, article_id: str) -> bool:
    """
    判断文章是否已在当前账号的第一个收藏夹中。
    :param cookies_str: 完整 Cookie 字符串
    :param article_id: 文章 ID
    :return: True 表示已在第一个收藏夹，False 表示未收藏或接口异常
    """
    res = get_collections(cookies_str, article_id)
    if not res or res.get("err_no") != 0:
        return False
    data = res.get("data") or []
    if not data:
        return False
    return bool(data[0].get("is_article_in", False))


def collect_article_if_not_in(
    cookies_str: str,
    article_id: str,
    collection_ids: Optional[List[str]] = None,
) -> str:
    """
    仅当文章未在第一个收藏夹中时才收藏，避免多余请求。
    :param cookies_str: 完整 Cookie 字符串
    :param article_id: 文章 ID
    :param collection_ids: 要加入的收藏夹 ID 列表，不传则用 get_collections 取第一个
    :return: "collected" | "skipped" | "failed"
    """
    if collection_ids:
        first_id = collection_ids[0]
    else:
        res = get_collections(cookies_str, article_id)
        if not res or res.get("err_no") != 0:
            first_id = DEFAULT_FIRST_COLLECTION_ID
        else:
            data = res.get("data") or []
            first_id = data[0]["collection_id"] if data else DEFAULT_FIRST_COLLECTION_ID
        collection_ids = [first_id]

    if is_article_in_first_collection(cookies_str, article_id):
        return "skipped"
    ret = add_article_to_collection(cookies_str, article_id, collection_ids)
    if not ret:
        return "failed"
    if ret.get("err_no") == 0:
        return "collected"
    return "failed"


def get_main_account_published_titles(limit: int = 10) -> set:
    """
    获取大号最近 limit 篇文章的标题集合（用于上传前判重：若待上传标题已在此集合中则跳过）。
    兼容返回结构中 title 在顶层或在 article_info 下的情况。
    """
    result = query_user_articles(DEFAULT_MAIN_USER_ID, cursor="0", limit=limit)
    if not result or result.get("err_no") != 0:
        return set()
    data = result.get("data") or []
    titles = set()
    for item in data:
        title = (item.get("article_info") or {}).get("title") or item.get("title") or ""
        if isinstance(title, str) and title.strip():
            titles.add(title.strip())
    return titles


def run_query_main_articles(limit: int = 10):
    """查询大号近 N 篇文章并打印。"""
    result = query_user_articles(DEFAULT_MAIN_USER_ID, cursor="0", limit=limit)
    if not result or result.get("err_no") != 0:
        print("❌ 查询失败")
        return []
    data = result.get("data") or []
    for i, item in enumerate(data, 1):
        print(f"  {i}. article_id: {item.get('article_id')}")
    return data


def run_collect_article(article_id: str, cookies_str: Optional[str] = None):
    """用当前账号收藏一篇文章（默认第一个收藏夹）；已在收藏夹则跳过。"""
    cookies_str = cookies_str or os.getenv("JUEJIN_COOKIES")
    if not cookies_str:
        print("❌ 需要 JUEJIN_COOKIES 环境变量或传入 cookies_str")
        return False
    status = collect_article_if_not_in(cookies_str, article_id)
    if status == "collected":
        print(f"✅ 已收藏文章: {article_id}")
        return True
    if status == "skipped":
        print(f"⏭️  文章 {article_id} 已在收藏夹，跳过")
        return True
    print(f"❌ 收藏失败: {article_id}")
    return False


def main():
    import sys
    # 查询大号近 10 篇文章
    print("📄 大号近 10 篇文章:")
    run_query_main_articles(limit=10)
    # 若传入文章 ID 则执行收藏
    if len(sys.argv) > 1:
        article_id = sys.argv[1]
        print(f"\n📌 收藏文章: {article_id}")
        run_collect_article(article_id)


if __name__ == "__main__":
    main()
