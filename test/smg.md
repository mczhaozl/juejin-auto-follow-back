1.收集沸点
curl ^"https://api.juejin.cn/content_api/v1/short_msg/query_list?aid=2608^&uuid=7618017386033251874^&spider=0^" ^
  -H ^"accept: */*^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9^" ^
  -H ^"content-type: application/json^" ^
  -b ^"passport_csrf_token=850ca16195f8ba8dc2a175cf1294622d; passport_csrf_token_default=850ca16195f8ba8dc2a175cf1294622d; _tea_utm_cache_2608=undefined; __tea_cookie_tokens_2608=^%^257B^%^2522web_id^%^2522^%^253A^%^25227618017386033251874^%^2522^%^252C^%^2522user_unique_id^%^2522^%^253A^%^25227618017386033251874^%^2522^%^252C^%^2522timestamp^%^2522^%^253A1773707904629^%^257D; n_mh=ykUY51NBxbyNPC_Ra6RxslXK8VADvKHUr1Yf-FwjIfM; sid_guard=8c1bc902f27d7730b93ff005aa1dcd88^%^7C1774315055^%^7C31536000^%^7CWed^%^2C+24-Mar-2027+01^%^3A17^%^3A35+GMT; uid_tt=553f1b67a9a8d49c37add1e88840b1e5; uid_tt_ss=553f1b67a9a8d49c37add1e88840b1e5; sid_tt=8c1bc902f27d7730b93ff005aa1dcd88; sessionid=8c1bc902f27d7730b93ff005aa1dcd88; sessionid_ss=8c1bc902f27d7730b93ff005aa1dcd88; session_tlb_tag=sttt^%^7C2^%^7CjBvJAvJ9dzC5P_AFqh3NiP_________02yWnMa_6q83A2zAcSP6f78SPX8oC3Lq0JtU114rKY-o^%^3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGM5NGRiOWZkZWMwNDBmOTVmZGMxYWQ2ZGYxYTQxY2ZjYmYxOTY4MmEKFwjezbCrt4ziARCvzIfOBhiwFDgHQPQHGgJscSIgOGMxYmM5MDJmMjdkNzczMGI5M2ZmMDA1YWExZGNkODg; ssid_ucp_v1=1.0.0-KGM5NGRiOWZkZWMwNDBmOTVmZGMxYWQ2ZGYxYTQxY2ZjYmYxOTY4MmEKFwjezbCrt4ziARCvzIfOBhiwFDgHQPQHGgJscSIgOGMxYmM5MDJmMjdkNzczMGI5M2ZmMDA1YWExZGNkODg; _tea_utm_cache_576092=undefined; csrf_session_id=cd8ef66a0d80b0125ddd9ecbbdf6b5bc^" ^
  -H ^"origin: https://juejin.cn^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://juejin.cn/^" ^
  -H ^"sec-ch-ua: ^\^"Chromium^\^";v=^\^"146^\^", ^\^"Not-A.Brand^\^";v=^\^"24^\^", ^\^"Google Chrome^\^";v=^\^"146^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-site^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36^" ^
  -H ^"x-secsdk-csrf-token: 00010000000149a25146adb2b7b6b02d43ceb903cd83ff7913045c85863b082f48d66a265ff118a0e5a5b24a4c6f^" ^
  --data-raw ^"^{^\^"sort_type^\^":4,^\^"cursor^\^":^\^"0^\^",^\^"limit^\^":20,^\^"user_id^\^":^\^"994385683293918^\^"^}^"

{
    "err_no": 0,
    "err_msg": "success",
    "data": [
        {
            "msg_id": "7621830561019215881"
        }，
        ...
    ],
    "cursor": "20",
    "count": 57,
    "has_more": true
}
  
  1. 评论

  curl ^"https://api.juejin.cn/interact_api/v1/comment/publish?aid=2608^&uuid=7618017386033251874^&spider=0^&msToken=CvaNx4mOT98zX4fCw7MERpztWvs13QLZJboCmn5CFklRsvtY1MBWDhtTb_eWt6yW3WVGFnV29mbWXjYBSQaJB1WtEwjqsKUvIMbbuX9KGLfgOOKJdOMy05MEIWZyMrgxlw^%^3D^%^3D^&a_bogus=x7UxDO2OMsm1iR21jXDz99^%^2FSsjS0YW5FgZENCME590qi^" ^
  -H ^"accept: */*^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9^" ^
  -H ^"content-type: application/json^" ^
  -b ^"passport_csrf_token=850ca16195f8ba8dc2a175cf1294622d; passport_csrf_token_default=850ca16195f8ba8dc2a175cf1294622d; _tea_utm_cache_2608=undefined; __tea_cookie_tokens_2608=^%^257B^%^2522web_id^%^2522^%^253A^%^25227618017386033251874^%^2522^%^252C^%^2522user_unique_id^%^2522^%^253A^%^25227618017386033251874^%^2522^%^252C^%^2522timestamp^%^2522^%^253A1773707904629^%^257D; n_mh=ykUY51NBxbyNPC_Ra6RxslXK8VADvKHUr1Yf-FwjIfM; sid_guard=8c1bc902f27d7730b93ff005aa1dcd88^%^7C1774315055^%^7C31536000^%^7CWed^%^2C+24-Mar-2027+01^%^3A17^%^3A35+GMT; uid_tt=553f1b67a9a8d49c37add1e88840b1e5; uid_tt_ss=553f1b67a9a8d49c37add1e88840b1e5; sid_tt=8c1bc902f27d7730b93ff005aa1dcd88; sessionid=8c1bc902f27d7730b93ff005aa1dcd88; sessionid_ss=8c1bc902f27d7730b93ff005aa1dcd88; session_tlb_tag=sttt^%^7C2^%^7CjBvJAvJ9dzC5P_AFqh3NiP_________02yWnMa_6q83A2zAcSP6f78SPX8oC3Lq0JtU114rKY-o^%^3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGM5NGRiOWZkZWMwNDBmOTVmZGMxYWQ2ZGYxYTQxY2ZjYmYxOTY4MmEKFwjezbCrt4ziARCvzIfOBhiwFDgHQPQHGgJscSIgOGMxYmM5MDJmMjdkNzczMGI5M2ZmMDA1YWExZGNkODg; ssid_ucp_v1=1.0.0-KGM5NGRiOWZkZWMwNDBmOTVmZGMxYWQ2ZGYxYTQxY2ZjYmYxOTY4MmEKFwjezbCrt4ziARCvzIfOBhiwFDgHQPQHGgJscSIgOGMxYmM5MDJmMjdkNzczMGI5M2ZmMDA1YWExZGNkODg; _tea_utm_cache_576092=undefined; csrf_session_id=cd8ef66a0d80b0125ddd9ecbbdf6b5bc^" ^
  -H ^"origin: https://juejin.cn^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://juejin.cn/^" ^
  -H ^"sec-ch-ua: ^\^"Chromium^\^";v=^\^"146^\^", ^\^"Not-A.Brand^\^";v=^\^"24^\^", ^\^"Google Chrome^\^";v=^\^"146^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-site^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36^" ^
  -H ^"x-secsdk-csrf-token: 00010000000149a25146adb2b7b6b02d43ceb903cd83ff7913045c85863b082f48d66a265ff118a0e5a5b24a4c6f^" ^
  --data-raw ^"^{^\^"client_type^\^":2608,^\^"item_id^\^":^\^"7621830561019215881^\^",^\^"item_type^\^":4,^\^"comment_content^\^":^\^"12^\^",^\^"comment_pics^\^":^[^]^}^"


  2. 删除
  curl ^"https://api.juejin.cn/content_api/v1/short_msg/delete?aid=2608^&uuid=7618017386033251874^&spider=0^" ^
  -H ^"accept: */*^" ^
  -H ^"accept-language: zh-CN,zh;q=0.9^" ^
  -H ^"content-type: application/json^" ^
  -b ^"passport_csrf_token=850ca16195f8ba8dc2a175cf1294622d; passport_csrf_token_default=850ca16195f8ba8dc2a175cf1294622d; _tea_utm_cache_2608=undefined; __tea_cookie_tokens_2608=^%^257B^%^2522web_id^%^2522^%^253A^%^25227618017386033251874^%^2522^%^252C^%^2522user_unique_id^%^2522^%^253A^%^25227618017386033251874^%^2522^%^252C^%^2522timestamp^%^2522^%^253A1773707904629^%^257D; n_mh=ykUY51NBxbyNPC_Ra6RxslXK8VADvKHUr1Yf-FwjIfM; sid_guard=8c1bc902f27d7730b93ff005aa1dcd88^%^7C1774315055^%^7C31536000^%^7CWed^%^2C+24-Mar-2027+01^%^3A17^%^3A35+GMT; uid_tt=553f1b67a9a8d49c37add1e88840b1e5; uid_tt_ss=553f1b67a9a8d49c37add1e88840b1e5; sid_tt=8c1bc902f27d7730b93ff005aa1dcd88; sessionid=8c1bc902f27d7730b93ff005aa1dcd88; sessionid_ss=8c1bc902f27d7730b93ff005aa1dcd88; session_tlb_tag=sttt^%^7C2^%^7CjBvJAvJ9dzC5P_AFqh3NiP_________02yWnMa_6q83A2zAcSP6f78SPX8oC3Lq0JtU114rKY-o^%^3D; is_staff_user=false; sid_ucp_v1=1.0.0-KGM5NGRiOWZkZWMwNDBmOTVmZGMxYWQ2ZGYxYTQxY2ZjYmYxOTY4MmEKFwjezbCrt4ziARCvzIfOBhiwFDgHQPQHGgJscSIgOGMxYmM5MDJmMjdkNzczMGI5M2ZmMDA1YWExZGNkODg; ssid_ucp_v1=1.0.0-KGM5NGRiOWZkZWMwNDBmOTVmZGMxYWQ2ZGYxYTQxY2ZjYmYxOTY4MmEKFwjezbCrt4ziARCvzIfOBhiwFDgHQPQHGgJscSIgOGMxYmM5MDJmMjdkNzczMGI5M2ZmMDA1YWExZGNkODg; _tea_utm_cache_576092=undefined; csrf_session_id=cd8ef66a0d80b0125ddd9ecbbdf6b5bc^" ^
  -H ^"origin: https://juejin.cn^" ^
  -H ^"priority: u=1, i^" ^
  -H ^"referer: https://juejin.cn/^" ^
  -H ^"sec-ch-ua: ^\^"Chromium^\^";v=^\^"146^\^", ^\^"Not-A.Brand^\^";v=^\^"24^\^", ^\^"Google Chrome^\^";v=^\^"146^\^"^" ^
  -H ^"sec-ch-ua-mobile: ?0^" ^
  -H ^"sec-ch-ua-platform: ^\^"Windows^\^"^" ^
  -H ^"sec-fetch-dest: empty^" ^
  -H ^"sec-fetch-mode: cors^" ^
  -H ^"sec-fetch-site: same-site^" ^
  -H ^"user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36^" ^
  -H ^"x-secsdk-csrf-token: 00010000000149a25146adb2b7b6b02d43ceb903cd83ff7913045c85863b082f48d66a265ff118a0e5a5b24a4c6f^" ^
  --data-raw ^"^{^\^"msg_id^\^":^\^"7621830561019215881^\^"^}^"