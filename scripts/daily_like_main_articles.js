const axios = require('axios');

/**
 * 每日点赞大号文章。
 * 逻辑：从环境变量加载所有账号，获取大号最近 10 篇文章进行点赞。
 * 如果某账号点赞失败（非重复点赞），则该账号停止后续点赞。
 */

const AID = '2608';
const SPIDER = '0';
const API_BASE = 'https://api.juejin.cn';
const MSSDK_URL = 'https://mssdk.bytedance.com/web/common';
const DEFAULT_MAIN_USER_ID = '994385683293918';
const DELAY_MS = 15000; // 间隔 15 秒

function sleep(ms) {
    return new Promise((r) => setTimeout(r, ms));
}

function sanitizeCookieHeader(cookiesStr) {
    if (!cookiesStr) return '';
    return String(cookiesStr).trim().replace(/\n/g, '').replace(/\r/g, '');
}

function extractUuid(cookiesStr) {
    const sanitized = sanitizeCookieHeader(cookiesStr);
    if (!sanitized) return '';
    const TEA_KEY = '__tea_cookie_tokens_2608';
    for (const item of sanitized.split(';')) {
        const part = item.trim();
        if (!part.includes(TEA_KEY)) continue;
        const eq = part.indexOf('=');
        if (eq < 0) continue;
        const val = part.slice(eq + 1).trim();
        try {
            let decoded = decodeURIComponent(val);
            try { decoded = decodeURIComponent(decoded); } catch (e) {}
            const obj = JSON.parse(decoded);
            return String(obj.web_id || obj.user_unique_id || '');
        } catch (e) {}
    }
    return '';
}

async function refreshMsTokenFromMssdk(cookie) {
    const bodyObj = {
        "is_ps": 0,
        "is_p_m": 0,
        "is_w_m": 0,
        "is_s_m": 0,
        "p_m_c": 0,
        "w_m_c": 0,
        "s_m_c": 0,
        "tspFromClient": Date.now()
    };
    const res = await axios.post(MSSDK_URL, JSON.stringify(bodyObj), {
        headers: {
            'Accept': '*/*',
            'Content-Type': 'text/plain;charset=UTF-8',
            'Origin': 'https://juejin.cn',
            'Referer': 'https://juejin.cn/',
            'Cookie': cookie
        },
        timeout: 15000,
        validateStatus: () => true
    });
    const sc = res.headers['set-cookie'] || res.headers['Set-Cookie'];
    if (sc) {
        const arr = Array.isArray(sc) ? sc : [sc];
        for (const line of arr) {
            const m = /msToken=([^;]+)/i.exec(String(line));
            if (m) return m[1].trim();
        }
    }
    return '';
}

async function queryUserArticles(userId) {
    const url = `${API_BASE}/content_api/v1/article/query_list`;
    const payload = { user_id: userId, sort_type: 2, cursor: "0" };
    try {
        const { data } = await axios.post(url, payload, {
            params: { aid: AID, uuid: "0", spider: SPIDER },
            headers: {
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://juejin.cn',
                'referer': 'https://juejin.cn/'
            },
            timeout: 10000
        });
        if (data && data.err_no === 0) {
            return (data.data || []).map(item => item.article_id).filter(Boolean);
        }
    } catch (e) {
        console.error("❌ 查询文章列表失败:", e.message);
    }
    return [];
}

async function likeArticle(itemId, cookie, msToken) {
    const uuid = extractUuid(cookie);
    const url = `${API_BASE}/interact_api/v1/digg/save`;
    try {
        const { data } = await axios.post(url, {
            item_id: itemId,
            item_type: 2,
            client_type: Number(AID)
        }, {
            params: { aid: AID, uuid, spider: SPIDER, msToken },
            headers: {
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://juejin.cn',
                'referer': 'https://juejin.cn/',
                'Cookie': cookie
            },
            timeout: 15000
        });
        return { success: data && data.err_no === 0, data };
    } catch (e) {
        return { success: false, error: e.message };
    }
}

async function runAccount(name, cookie, articleIds) {
    console.log(`👤 [${name}] 开始点赞...`);
    const sanitizedCookie = sanitizeCookieHeader(cookie);
    let msToken = '';
    try {
        msToken = await refreshMsTokenFromMssdk(sanitizedCookie);
        if (!msToken) console.log(`  ⚠️  [${name}] 未获取到 msToken，尝试直接点赞`);
    } catch (e) {
        console.log(`  ⚠️  [${name}] mssdk 获取失败: ${e.message}`);
    }

    let okCount = 0;
    let skipCount = 0;

    for (let i = 0; i < articleIds.length; i++) {
        const id = articleIds[i];
        const res = await likeArticle(id, sanitizedCookie, msToken);
        if (res.success) {
            okCount++;
            console.log(`  [${i + 1}/${articleIds.length}] ✅ ${id}`);
        } else {
            const data = res.data || {};
            const msg = data.err_msg || data.message || res.error || "未知错误";
            const already = /已赞|重复|digg|like|already/i.test(msg) || (data.err_no === 6001); // 6001 通常是已赞
            if (already) {
                skipCount++;
                console.log(`  [${i + 1}/${articleIds.length}] ⏭️  ${id} (已赞或重复)`);
            } else {
                console.log(`  [${i + 1}/${articleIds.length}] ❌ ${id} 操作失败:`, data);
                if (data.err_no === 4032) {
                    console.log(`  🛑 [${name}] 触发 4032 (未绑定手机号)，停止该账号后续点赞操作。`);
                    return { okCount, skipCount, failed: true };
                }
                console.log(`  ⚠️  [${name}] 非 4032 错误，继续尝试后续文章。`);
            }
        }
        if (i < articleIds.length - 1) await sleep(DELAY_MS);
    }
    return { okCount, skipCount, failed: false };
}

async function main() {
    const articleIds = await queryUserArticles(DEFAULT_MAIN_USER_ID);
    if (!articleIds || articleIds.length === 0) {
        console.error("❌ 未获取到大号文章列表");
        process.exit(1);
    }
    console.log(`📄 大号最近 ${articleIds.length} 篇文章: ${articleIds.join(', ')}\n`);

    const accounts = [
        { name: "主账号", env: "JUEJIN_COOKIES" },
        { name: "小号1", env: "JUEJIN_COOKIES_ACCOUNT2" },
        { name: "小号2", env: "JUEJIN_COOKIES_ACCOUNT3" },
        { name: "小号3", env: "JUEJIN_COOKIES_ACCOUNT4" },
        { name: "小号4", env: "JUEJIN_COOKIES_ACCOUNT5" },
        { name: "小号5", env: "JUEJIN_COOKIES_ACCOUNT6" },
        { name: "小号6", env: "JUEJIN_COOKIES_ACCOUNT7" },
        { name: "小号7", env: "JUEJIN_COOKIES_ACCOUNT8" },
        { name: "小号8", env: "JUEJIN_COOKIES_ACCOUNT9" }
    ];

    for (const acc of accounts) {
        const cookie = process.env[acc.env];
        if (!cookie) continue;
        const res = await runAccount(acc.name, cookie, articleIds);
        console.log(`汇总 [${acc.name}]: 成功 ${res.okCount} | 跳过 ${res.skipCount} | ${res.failed ? "❌ 已中断" : "✅ 已完成"}\n`);
    }
}

main().catch(e => {
    console.error("❌ 程序异常:", e);
    process.exit(1);
});
