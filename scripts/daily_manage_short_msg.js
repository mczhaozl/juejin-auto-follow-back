const axios = require('axios');

/**
 * 每日 12 点评论并删除自己最近 5 条沸点。
 * 逻辑：
 * 1. 获取大号最近 5 条沸点。
 * 2. 对每条沸点进行评论。
 * 3. 评论成功后删除该沸点。
 */

const AID = '2608';
const SPIDER = '0';
const API_BASE = 'https://api.juejin.cn';
const MSSDK_URL = 'https://mssdk.bytedance.com/web/common';
const DEFAULT_MAIN_USER_ID = '994385683293918';
const DELAY_MS = 5000; // 间隔 5 秒

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

/**
 * 原子化：临时获取 msToken
 */
async function refreshMsTokenFromMssdk(cookie) {
    const bodyObj = {
        "is_ps": 0, "is_p_m": 0, "is_w_m": 0, "is_s_m": 0,
        "p_m_c": 0, "w_m_c": 0, "s_m_c": 0,
        "tspFromClient": Date.now()
    };
    try {
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
    } catch (e) {
        console.error("  ⚠️  获取 msToken 异常:", e.message);
    }
    return '';
}

/**
 * 原子化：查询自己的最近沸点列表
 */
async function queryMyShortMsgs(cookie, userId, limit = 5) {
    const url = `${API_BASE}/content_api/v1/short_msg/query_list`;
    const payload = {
        sort_type: 4, // 4 通常表示自己的沸点列表
        cursor: "0",
        limit: limit,
        user_id: userId
    };
    try {
        const { data } = await axios.post(url, payload, {
            params: { aid: AID, uuid: extractUuid(cookie), spider: SPIDER },
            headers: {
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://juejin.cn',
                'referer': 'https://juejin.cn/',
                'Cookie': cookie
            },
            timeout: 15000
        });
        if (data && data.err_no === 0) {
            return (data.data || []).map(item => item.msg_id).filter(Boolean);
        } else {
            console.error("  ❌ 查询沸点列表失败:", data.err_msg);
        }
    } catch (e) {
        console.error("  ❌ 查询沸点列表异常:", e.message);
    }
    return [];
}

/**
 * 原子化：对指定沸点发表评论
 */
async function publishComment(msgId, content, cookie, msToken, aBogus, csrfToken) {
    const url = `${API_BASE}/interact_api/v1/comment/publish`;
    const payload = {
        client_type: Number(AID),
        item_id: msgId,
        item_type: 4, // 4 表示沸点
        comment_content: content,
        comment_pics: []
    };
    const params = { 
        aid: AID, 
        uuid: extractUuid(cookie), 
        spider: SPIDER
    };
    if (msToken) {
        params.msToken = decodeURIComponent(msToken);
    }
    if (aBogus) {
        params.a_bogus = aBogus;
    }
    const headers = {
        'accept': '*/*',
        'accept-language': 'zh-CN,zh;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://juejin.cn',
        'referer': 'https://juejin.cn/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Cookie': cookie
    };
    if (csrfToken) {
        headers['x-secsdk-csrf-token'] = csrfToken;
    }
    try {
        const { data } = await axios.post(url, payload, {
            params,
            headers,
            timeout: 15000,
            validateStatus: () => true
        });
        return { success: data && data.err_no === 0, data };
    } catch (e) {
        return { success: false, error: e.message };
    }
}

/**
 * 原子化：删除指定沸点
 */
async function deleteShortMsg(msgId, cookie) {
    const url = `${API_BASE}/content_api/v1/short_msg/delete`;
    const payload = {
        msg_id: msgId
    };
    try {
        const { data } = await axios.post(url, payload, {
            params: { aid: AID, uuid: extractUuid(cookie), spider: SPIDER },
            headers: {
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://juejin.cn',
                'referer': 'https://juejin.cn/',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
                'Cookie': cookie
            },
            timeout: 15000,
            validateStatus: () => true
        });
        return { success: data && data.err_no === 0, data };
    } catch (e) {
        return { success: false, error: e.message };
    }
}

/**
 * 整合逻辑
 */
async function processShortMsgs(cookie, userId, csrfToken, aBogus) {
    console.log(`🚀 [${userId}] 开始处理沸点...`);
    const sanitizedCookie = sanitizeCookieHeader(cookie);
    
    // 1. 获取沸点列表
    const msgIds = await queryMyShortMsgs(sanitizedCookie, userId, 5);
    if (!msgIds || msgIds.length === 0) {
        console.log("  ℹ️  未找到待处理的沸点。");
        return;
    }
    console.log(`  📄 找到 ${msgIds.length} 条待处理沸点: ${msgIds.join(', ')}`);

    for (let i = 0; i < msgIds.length; i++) {
        const msgId = msgIds[i];
        
        // 2. 临时获取 msToken
        const msToken = await refreshMsTokenFromMssdk(sanitizedCookie);
        if (!msToken) {
            console.log(`  ⚠️  获取 msToken 失败，尝试直接评论`);
        }
        
        // 3. 评论
        console.log(`  [${i + 1}/${msgIds.length}] 正在评论 ${msgId}...`);
        const commentRes = await publishComment(msgId, "打卡下班", sanitizedCookie, msToken, aBogus, csrfToken);
        
        if (commentRes.success) {
            console.log(`    ✅ 评论成功`);
        } else {
            console.log(`    ❌ 评论失败:`, JSON.stringify(commentRes.data || commentRes.error));
        }

        // 4. 删除
        console.log(`    正在删除 ${msgId}...`);
        const deleteRes = await deleteShortMsg(msgId, sanitizedCookie);
        if (deleteRes.success) {
            console.log(`    ✅ 删除成功`);
        } else {
            console.log(`    ❌ 删除失败:`, JSON.stringify(deleteRes.data || deleteRes.error));
        }

        if (i < msgIds.length - 1) await sleep(DELAY_MS);
    }
}

async function main() {
    const cookie = process.env.JUEJIN_COOKIES||'passport_csrf_token=850ca16195f8ba8dc2a175cf1294622d; passport_csrf_token_default=850ca16195f8ba8dc2a175cf1294622d; _tea_utm_cache_2608=undefined; __tea_cookie_tokens_2608=%257B%2522web_id%2522%253A%25227618017386033251874%2522%252C%2522user_unique_id%2522%253A%25227618017386033251874%2522%252C%2522timestamp%2522%253A1773707904629%257D; n_mh=ykUY51NBxbyNPC_Ra6RxslXK8VADvKHUr1Yf-FwjIfM; sid_guard=8c1bc902f27d7730b93ff005aa1dcd88%7C1774315055%7C31536000%7CWed%2C+24-Mar-2027+01%3A17%3A35+GMT; uid_tt=553f1b67a9a8d49c37add1e88840b1e5; uid_tt_ss=553f1b67a9a8d49c37add1e88840b1e5; sid_tt=8c1bc902f27d7730b93ff005aa1dcd88; sessionid=8c1bc902f27d7730b93ff005aa1dcd88; sessionid_ss=8c1bc902f27d7730b93ff005aa1dcd88; session_tlb_tag=sttt%7C2%7CjBvJAvJ9dzC5P_AFqh3NiP_________02yWnMa_6q83A2zAcSP6f78SPX8oC3Lq0JtU114rKY-o%3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGM5NGRiOWZkZWMwNDBmOTVmZGMxYWQ2ZGYxYTQxY2ZjYmYxOTY4MmEKFwjezbCrt4ziARCvzIfOBhiwFDgHQPQHGgJscSIgOGMxYmM5MDJmMjdkNzczMGI5M2ZmMDA1YWExZGNkODg; ssid_ucp_v1=1.0.0-KGM5NGRiOWZkZWMwNDBmOTVmZGMxYWQ2ZGYxYTQxY2ZjYmYxOTY4MmEKFwjezbCrt4ziARCvzIfOBhiwFDgHQPQHGgJscSIgOGMxYmM5MDJmMjdkNzczMGI5M2ZmMDA1YWExZGNkODg; _tea_utm_cache_576092=undefined; csrf_session_id=cd8ef66a0d80b0125ddd9ecbbdf6b5bc';
    if (!cookie) {
        console.error("❌ 环境变量 JUEJIN_COOKIES 未定义。本地测试请手动设置环境或在 main 中传入临时 cookie。");
        process.exit(1);
    }
    
    const userId = process.env.JUEJIN_USER_ID || DEFAULT_MAIN_USER_ID;
    const csrfToken = process.env.JUEJIN_CSRF_TOKEN || '';
    const aBogus = process.env.JUEJIN_A_BOGUS || '';
    
    await processShortMsgs(cookie, userId, csrfToken, aBogus);
    console.log("\n🏁 沸点处理任务结束。");
}

// 导出函数方便本地测试
module.exports = {
    refreshMsTokenFromMssdk,
    queryMyShortMsgs,
    publishComment,
    deleteShortMsg,
    processShortMsgs
};

// 如果是直接运行脚本则执行 main
if (require.main === module) {
    main().catch(e => {
        console.error("❌ 程序异常:", e);
        process.exit(1);
    });
}
