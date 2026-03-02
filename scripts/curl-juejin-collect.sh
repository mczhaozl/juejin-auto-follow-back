#!/usr/bin/env bash
# 掘金：查询大号近 10 篇文章 + 用 curl 收藏指定文章
# 用法：
#   1. 把下面的 COOKIE 换成你的 Cookie（或从环境变量 JUEJIN_COOKIES 读取）
#   2. 收藏接口若返回 403/401，请从浏览器请求头复制 x-secsdk-csrf-token 填到 CSRF_TOKEN
# 收藏夹默认使用第一个：7289368836561010744（我的收藏）

set -e

COOKIE="${JUEJIN_COOKIES:-__tea_cookie_tokens_2608=%257B%2522web_id%2522%253A%25227586574305263552043%2522%252C%2522user_unique_id%2522%253A%25227586574305263552043%2522%252C%2522timestamp%2522%253A1766386989417%257D; passport_csrf_token=7abc35ca23159a09cda3ab0c856e7dfe; passport_csrf_token_default=7abc35ca23159a09cda3ab0c856e7dfe; is_staff_user=false; _ga=GA1.2.424229928.1769653318; odin_tt=5c9e3665490e61ab3446a89259d23cce802d2ee0510682a4a98d1d8ffff89069d6da0b4eb6ce0468e694e528fa6ab404347f933fa0c2265e7147904fe4e904d4; n_mh=ykUY51NBxbyNPC_Ra6RxslXK8VADvKHUr1Yf-FwjIfM; sid_guard=116c2d1999eb35913fcdbcfa8fad2c1e%7C1770347973%7C31536000%7CSat%2C+06-Feb-2027+03%3A19%3A33+GMT; uid_tt=ee8fc3d7e08f3ce4a0ed7e271ad72449; uid_tt_ss=ee8fc3d7e08f3ce4a0ed7e271ad72449; sid_tt=116c2d1999eb35913fcdbcfa8fad2c1e; sessionid=116c2d1999eb35913fcdbcfa8fad2c1e; sessionid_ss=116c2d1999eb35913fcdbcfa8fad2c1e; sid_ucp_v1=1.0.0-KDUyMDA4NWY4MmNmZjI1ZDUyNjhhZGRkNjkzOTNlZTJlY2ViOWVhYTYKFgjezbCrt4ziARDFu5XMBhiwFDgIQAsaAmxmIiAxMTZjMmQxOTk5ZWIzNTkxM2ZjZGJjZmE4ZmFkMmMxZQ; ssid_ucp_v1=1.0.0-KDUyMDA4NWY4MmNmZjI1ZDUyNjhhZGRkNjkzOTNlZTJlY2ViOWVhYTYKFgjezbCrt4ziARDFu5XMBhiwFDgIQAsaAmxmIiAxMTZjMmQxOTk5ZWIzNTkxM2ZjZGJjZmE4ZmFkMmMxZQ; session_tlb_tag=sttt%7C9%7CEWwtGZnrNZE_zbz6j60sHv________-kDSi_SMSymz2axsQXOKWna4YsfV20LXjvGrGtHSVbHhc%3D; _ga_S695FMNGPJ=GS2.2.s1770347939\$o2\$g1\$t1770347974\$j25\$l0\$h0; _tea_utm_cache_2608={%22utm_source%22:%22jj_nav%22}; _tea_utm_cache_576092=undefined; csrf_session_id=90a2c045efe817984cb9f364dbbbcd7f}"

# 可选：从浏览器请求头复制，若收藏接口报 403/401 再填
CSRF_TOKEN="${JUEJIN_CSRF_TOKEN:-}"

# 大号 user_id（查询近 10 篇）
MAIN_USER_ID="994385683293918"
# 默认第一个收藏夹 ID（我的收藏）
COLLECTION_ID="7289368836561010744"
# 要收藏的文章 ID
ARTICLE_ID="${1:-7611432097544175643}"

echo "========== 1. 查询大号近 10 篇文章（无需登录） =========="
curl -s 'https://api.juejin.cn/content_api/v1/article/query_list?aid=2608&uuid=0&spider=0' \
  -H 'accept: */*' \
  -H 'content-type: application/json' \
  -H 'origin: https://juejin.cn' \
  -H 'referer: https://juejin.cn/' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
  --data-raw "{\"user_id\":\"${MAIN_USER_ID}\",\"sort_type\":2,\"cursor\":\"0\"}" | python3 -m json.tool

echo ""
echo "========== 2. 收藏文章 ${ARTICLE_ID} 到收藏夹 ${COLLECTION_ID} =========="
if [ -n "$CSRF_TOKEN" ]; then
  curl -s 'https://api.juejin.cn/interact_api/v2/collectionset/add_article?aid=2608&uuid=7586574305263552043&spider=0' \
    -H 'accept: */*' \
    -H 'content-type: application/json' \
    -H 'origin: https://juejin.cn' \
    -H 'referer: https://juejin.cn/' \
    -H "x-secsdk-csrf-token: ${CSRF_TOKEN}" \
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
    -b "$COOKIE" \
    --data-raw "{\"article_id\":\"${ARTICLE_ID}\",\"select_collection_ids\":[\"${COLLECTION_ID}\"],\"unselect_collection_ids\":[],\"is_collect_fast\":false}" | python3 -m json.tool
else
  curl -s 'https://api.juejin.cn/interact_api/v2/collectionset/add_article?aid=2608&uuid=7586574305263552043&spider=0' \
    -H 'accept: */*' \
    -H 'content-type: application/json' \
    -H 'origin: https://juejin.cn' \
    -H 'referer: https://juejin.cn/' \
    -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36' \
    -b "$COOKIE" \
    --data-raw "{\"article_id\":\"${ARTICLE_ID}\",\"select_collection_ids\":[\"${COLLECTION_ID}\"],\"unselect_collection_ids\":[],\"is_collect_fast\":false}" | python3 -m json.tool
fi
