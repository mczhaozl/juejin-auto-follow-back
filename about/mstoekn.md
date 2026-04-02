首先 需要
拿到用户 cookie 

然后调用 
curl 'https://mssdk.bytedance.com/web/common?msToken=GSNa1czss0QZFC9zGz5CATlH_wfHZsLceLAlmp-KwvyZdOojuVb8HuC-dHNeO1bgy1KTczMzUoB3fMSeTDy3SaErTG5ZWlr0TWPMvCegDs9U6WBkNSDMO9xzpxwcPy8_' \
  -H 'accept: */*' \
  -H 'accept-language: zh-CN,zh;q=0.9,en;q=0.8' \
  -H 'cache-control: no-cache' \
  -H 'content-type: text/plain;charset=UTF-8' \
  -b 'ttwid=1%7CqEMbHH_wybrAUfrgToBG0F7POvwnRJCDexG_yfOZDBY%7C1772448569%7C144f7ae1724396478fab659e0cf44eef6085a41f9ce63e198bf6b0d8ead5bdac; ttcid=1653b39e13ca4fe59ba83a9d2caa16a542; tt_scid=WaAOxTg.Q07OX5HBcN4UtGU0O2mAtGgmqRXos0C1axnE-eW-AlFcTS.TS3LLbrjac6cc' \
  -H 'ingress-traffic-env: test-gtbg-dev-8' \
  -H 'origin: https://juejin.cn' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://juejin.cn/' \
  -H 'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "macOS"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: cross-site' \
  -H 'sec-fetch-storage-access: active' \
  -H 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' \
  --data-raw '{"magic":538969122,"version":1,"dataType":8,"strData":"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","tspFromClient":1774233725008}'

  获取到 响应头的
  set-cookie
  msToken=CTrLyhJQ7hsOBZyl8nlZKx4QUJFe5L6LxQw2uRsNkFTjKCYzW7kpgF26P2rSsq5L7fztvsKr4FOXFucg2Wrsno-WRF6F2bO46N7OvZViQcHskZ5vHsun4cpxEUhezLVkVA==; expires=Mon, 30 Mar 2026 02:42:05 GMT; domain=bytedance.com; path=/;

  提取里面的  msToken
  CTrLyhJQ7hsOBZyl8nlZKx4QUJFe5L6LxQw2uRsNkFTjKCYzW7kpgF26P2rSsq5L7fztvsKr4FOXFucg2Wrsno-WRF6F2bO46N7OvZViQcHskZ5vHsun4cpxEUhezLVkVA==


  curl --location 'https://api.juejin.cn/interact_api/v1/digg/save?aid=2608&uuid=7586574305263552043&spider=0&msToken=8A4HQoFFc8B3moI6EJuMtsn7LuCHNaBlWA4Z06Z9SeifVD-RzJK9gUM7uSU3kO_dck2LNFXwAYzmS1yhq2Ya8-pQIamR4JiJPuwwnjAomlZ_1ySW53x6eEsu_DjeGZ4rdQ%3D%3D' \
--header 'accept: */*' \
--header 'accept-language: zh-CN,zh;q=0.9,en;q=0.8' \
--header 'cache-control: no-cache' \
--header 'content-type: application/json' \
--header 'ingress-traffic-env: test-gtbg-dev-8' \
--header 'origin: https://juejin.cn' \
--header 'pragma: no-cache' \
--header 'priority: u=1, i' \
--header 'referer: https://juejin.cn/' \
--header 'sec-ch-ua: "Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"' \
--header 'sec-ch-ua-mobile: ?0' \
--header 'sec-ch-ua-platform: "macOS"' \
--header 'sec-fetch-dest: empty' \
--header 'sec-fetch-mode: cors' \
--header 'sec-fetch-site: same-site' \
--header 'user-agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36' \
--header 'Cookie: __tea_cookie_tokens_2608=%257B%2522web_id%2522%253A%25227586574305263552043%2522%252C%2522user_unique_id%2522%253A%25227586574305263552043%2522%252C%2522timestamp%2522%253A1766386989417%257D; passport_csrf_token=7abc35ca23159a09cda3ab0c856e7dfe; passport_csrf_token_default=7abc35ca23159a09cda3ab0c856e7dfe; is_staff_user=false; _ga=GA1.2.424229928.1769653318; odin_tt=5c9e3665490e61ab3446a89259d23cce802d2ee0510682a4a98d1d8ffff89069d6da0b4eb6ce0468e694e528fa6ab404347f933fa0c2265e7147904fe4e904d4; n_mh=ykUY51NBxbyNPC_Ra6RxslXK8VADvKHUr1Yf-FwjIfM; sid_guard=116c2d1999eb35913fcdbcfa8fad2c1e%7C1770347973%7C31536000%7CSat%2C+06-Feb-2027+03%3A19%3A33+GMT; uid_tt=ee8fc3d7e08f3ce4a0ed7e271ad72449; uid_tt_ss=ee8fc3d7e08f3ce4a0ed7e271ad72449; sid_tt=116c2d1999eb35913fcdbcfa8fad2c1e; sessionid=116c2d1999eb35913fcdbcfa8fad2c1e; sessionid_ss=116c2d1999eb35913fcdbcfa8fad2c1e; sid_ucp_v1=1.0.0-KDUyMDA4NWY4MmNmZjI1ZDUyNjhhZGRkNjkzOTNlZTJlY2ViOWVhYTYKFgjezbCrt4ziARDFu5XMBhiwFDgIQAsaAmxmIiAxMTZjMmQxOTk5ZWIzNTkxM2ZjZGJjZmE4ZmFkMmMxZQ; ssid_ucp_v1=1.0.0-KDUyMDA4NWY4MmNmZjI1ZDUyNjhhZGRkNjkzOTNlZTJlY2ViOWVhYTYKFgjezbCrt4ziARDFu5XMBhiwFDgIQAsaAmxmIiAxMTZjMmQxOTk5ZWIzNTkxM2ZjZGJjZmE4ZmFkMmMxZQ; session_tlb_tag=sttt%7C9%7CEWwtGZnrNZE_zbz6j60sHv________-kDSi_SMSymz2axsQXOKWna4YsfV20LXjvGrGtHSVbHhc%3D; _tea_utm_cache_2608={%22utm_source%22:%22jj_nav%22}; _ga_S695FMNGPJ=GS2.2.s1773712026$o3$g0$t1773712026$j60$l0$h0; _tea_utm_cache_576092=undefined; csrf_session_id=0ec970f24a3e53974e6bebd72aeb30cd' \
--data '{"item_id":"7619649661303029770","item_type":2,"client_type":2608}'

其中  aid,spider 是固定写死的 uuid通过cookie 解析

/**
 * @param {string} cookiesStr - 完整 Cookie 头字符串
 * @returns {string} uuid（web_id），解析失败返回 ''
 */
function extractJuejinUuidFromCookie(cookiesStr) {
    const sanitized = sanitizeCookieHeader(cookiesStr);
    if (!sanitized) return '';

    for (const item of sanitized.split(';')) {
        const part = item.trim();
        if (!part.includes(TEA_KEY)) continue;

        const eq = part.indexOf('=');
        if (eq < 0) continue;
        const val = part.slice(eq + 1).trim();

        try {
            let decoded = decodeURIComponent(val);
            try {
                decoded = decodeURIComponent(decoded);
            } catch {
                /* 单层编码：第二次无效，保留第一次 */
            }
            const obj = JSON.parse(decoded);
            const id = obj.web_id || obj.user_unique_id;
            return id != null ? String(id) : '';
        } catch {
            // 本条解析失败，继续下一段
        }
    }
    return '';
}