#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金自动签到脚本
每天自动签到领矿石
"""

import os
import json
import requests
from datetime import datetime


class JuejinCheckIn:
    def __init__(self, cookies_str):
        self.session = requests.Session()
        self.cookies = self._parse_cookies(cookies_str)
        self.base_url = "https://api.juejin.cn"
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://juejin.cn',
            'referer': 'https://juejin.cn/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def _parse_cookies(self, cookies_str):
        """将 Cookie 字符串解析为字典"""
        cookies_dict = {}
        for item in cookies_str.split(';'):
            item = item.strip()
            if '=' in item:
                key, value = item.split('=', 1)
                cookies_dict[key.strip()] = value.strip()
        return cookies_dict
    
    def check_in(self):
        """执行签到"""
        url = f"{self.base_url}/growth_api/v1/check_in"
        params = {
            'aid': '2608',
            'uuid': '7586574305263552043',
            'spider': '0'
        }
        
        try:
            response = self.session.post(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result
        except Exception as e:
            print(f"❌ 签到失败: {e}")
            return None
    
    def get_current_point(self):
        """获取当前矿石数"""
        url = f"{self.base_url}/growth_api/v1/get_cur_point"
        params = {
            'aid': '2608',
            'uuid': '7586574305263552043',
            'spider': '0'
        }
        
        try:
            response = self.session.get(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('data', 0)
        except Exception as e:
            print(f"❌ 获取矿石数失败: {e}")
            return 0
    
    def run(self):
        """执行签到任务"""
        print(f"\n{'='*50}")
        print(f"🎯 开始执行签到任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # 执行签到
        result = self.check_in()
        
        if not result:
            print("❌ 签到失败")
            return
        
        err_no = result.get('err_no')
        err_msg = result.get('err_msg', '')
        
        if err_no == 0:
            print("✅ 签到成功！")
            incr_point = result.get('data', {}).get('incr_point', 0)
            sum_point = result.get('data', {}).get('sum_point', 0)
            print(f"📈 今日获得: {incr_point} 矿石")
            print(f"💎 当前总计: {sum_point} 矿石")
        elif err_no == 15001:
            print("⏭️  今日已签到")
            # 获取当前矿石数
            current_point = self.get_current_point()
            print(f"💎 当前总计: {current_point} 矿石")
        else:
            print(f"❌ 签到失败: {err_msg}")
        
        print(f"\n{'='*50}\n")


def main():
    # 从环境变量读取 Cookie 字符串
    cookies_str = os.getenv('JUEJIN_COOKIES')
    
    if not cookies_str:
        print("❌ 未找到 JUEJIN_COOKIES 环境变量")
        print("请在 GitHub Secrets 中配置 JUEJIN_COOKIES")
        return
    
    checkin = JuejinCheckIn(cookies_str)
    checkin.run()


if __name__ == "__main__":
    main()
