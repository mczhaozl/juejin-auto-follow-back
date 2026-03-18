const axios = require('axios');

const MSG_IDS = [
    "7615460341234499622",
    "7615561502783258650",
    "7615156885722824740",
    "7614458063534882870",
    "7614458063534735414",
    "7614066405496193024",
    "7614030077067706414",
    "7614016570628522003",
    "7613702733937852422",
    "7613671319494508559",
    "7613258078369677318",
    "7612949440030703616",
    "7613156097801355327",
    "7612596935200260123",
    "7612467508634435638",
    "7611857790999379974",
    "7611857790998773766",
    "7611820139811274806"
];

const COOKIE = '__tea_cookie_tokens_2608=%257B%2522web_id%2522%253A%25227586574305263552043%2522%252C%2522user_unique_id%2522%253A%25227586574305263552043%2522%252C%2522timestamp%2522%253A1766386989417%257D; passport_csrf_token=7abc35ca23159a09cda3ab0c856e7dfe; passport_csrf_token_default=7abc35ca23159a09cda3ab0c856e7dfe; is_staff_user=false; _ga=GA1.2.424229928.1769653318; odin_tt=5c9e3665490e61ab3446a89259d23cce802d2ee0510682a4a98d1d8ffff89069d6da0b4eb6ce0468e694e528fa6ab404347f933fa0c2265e7147904fe4e904d4; n_mh=ykUY51NBxbyNPC_Ra6RxslXK8VADvKHUr1Yf-FwjIfM; sid_guard=116c2d1999eb35913fcdbcfa8fad2c1e%7C1770347973%7C31536000%7CSat%2C+06-Feb-2027+03%3A19%3A33+GMT; uid_tt=ee8fc3d7e08f3ce4a0ed7e271ad72449; uid_tt_ss=ee8fc3d7e08f3ce4a0ed7e271ad72449; sid_tt=116c2d1999eb35913fcdbcfa8fad2c1e; sessionid=116c2d1999eb35913fcdbcfa8fad2c1e; sessionid_ss=116c2d1999eb35913fcdbcfa8fad2c1e; sid_ucp_v1=1.0.0-KDUyMDA4NWY4MmNmZjI1ZDUyNjhhZGRkNjkzOTNlZTJlY2ViOWVhYTYKFgjezbCrt4ziARDFu5XMBhiwFDgIQAsaAmxmIiAxMTZjMmQxOTk5ZWIzNTkxM2ZjZGJjZmE4ZmFkMmMxZQ; ssid_ucp_v1=1.0.0-KDUyMDA4NWY4MmNmZjI1ZDUyNjhhZGRkNjkzOTNlZTJlY2ViOWVhYTYKFgjezbCrt4ziARDFu5XMBhiwFDgIQAsaAmxmIiAxMTZjMmQxOTk5ZWIzNTkxM2ZjZGJjZmE4ZmFkMmMxZQ; session_tlb_tag=sttt%7C9%7CEWwtGZnrNZE_zbz6j60sHv________-kDSi_SMSymz2axsQXOKWna4YsfV20LXjvGrGtHSVbHhc%3D; _tea_utm_cache_2608={%22utm_source%22:%22jj_nav%22}; _ga_S695FMNGPJ=GS2.2.s1773712026$o3$g0$t1773712026$j60$l0$h0; csrf_session_id=0ec970f24a3e53974e6bebd72aeb30cd; _tea_utm_cache_576092=undefined';
const CSRF_TOKEN = '0001000000013d0f6f4b8e6064e37a01b66a3947e7ea6c54e17cba1b1094709a70d41d3cab91189de10cf3877e37';
const UUID = '7586574305263552043';

const DELETE_URL = `https://api.juejin.cn/content_api/v1/short_msg/delete?aid=2608&uuid=${UUID}&spider=0`;

const headers = {
  'accept': '*/*',
  'content-type': 'application/json',
  'origin': 'https://juejin.cn',
  'referer': 'https://juejin.cn/',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
  'Cookie': COOKIE,
  'x-secsdk-csrf-token': CSRF_TOKEN,
};

async function deleteAll() {
  let ok = 0;
  let fail = 0;
  for (const msg_id of MSG_IDS) {
    try {
      const res = await axios.post(DELETE_URL, { msg_id }, { headers });
      if (res.data && res.data.err_no === 0) {
        console.log('删除成功:', msg_id);
        ok++;
      } else {
        console.log('删除失败:', msg_id, res.data);
        fail++;
      }
    } catch (e) {
      console.log('请求异常:', msg_id, e.message);
      fail++;
    }
  }
  console.log('完成: 成功 %d, 失败 %d', ok, fail);
}

deleteAll();
