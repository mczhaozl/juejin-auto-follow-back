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
    def __init__(self, cookies_str, account_name="主账号"):
        self.session = requests.Session()
        self.account_name = account_name
        self.cookies = self._parse_cookies(cookies_str)
        self.base_url = "https://api.juejin.cn"
        
        # Extract UUID from cookies
        self.uuid = self._extract_uuid(cookies_str)
        
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'origin': 'https://juejin.cn',
            'referer': 'https://juejin.cn/',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
    
    def _extract_uuid(self, cookies_str):
        """从 cookies 中提取 web_id 作为 uuid"""
        try:
            import urllib.parse
            for item in cookies_str.split(';'):
                item = item.strip()
                if '__tea_cookie_tokens_2608' in item:
                    value = item.split('=', 1)[1]
                    # 需要解码两次（双重 URL 编码）
                    decoded = urllib.parse.unquote(value)
                    decoded = urllib.parse.unquote(decoded)
                    tokens = json.loads(decoded)
                    web_id = tokens.get('web_id')
                    if web_id:
                        print(f"[{self.account_name}] 成功提取 UUID: {web_id}")
                        return web_id
        except Exception as e:
            print(f"[{self.account_name}] UUID 提取失败，使用默认值: {e}")
        return '7586574305263552043'
    
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
            'uuid': self.uuid,
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
        except json.JSONDecodeError as e:
            print(f"❌ [{self.account_name}] JSON 解析失败: {e}")
            print(f"Response text: {response.text[:500]}")
            return None
        except Exception as e:
            print(f"❌ [{self.account_name}] 签到失败: {e}")
            return None
    
    def get_current_point(self):
        """获取当前矿石数"""
        url = f"{self.base_url}/growth_api/v1/get_cur_point"
        params = {
            'aid': '2608',
            'uuid': self.uuid,
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
            print(f"❌ [{self.account_name}] 获取矿石数失败: {e}")
            return 0
    
    def run(self):
        """执行签到任务"""
        print(f"\n{'='*50}")
        print(f"🎯 [{self.account_name}] 开始执行签到任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        # 执行签到
        result = self.check_in()
        
        if not result:
            print(f"❌ [{self.account_name}] 签到失败")
            return False, 0, 0
        
        err_no = result.get('err_no')
        err_msg = result.get('err_msg', '')
        
        if err_no == 0:
            print(f"✅ [{self.account_name}] 签到成功！")
            incr_point = result.get('data', {}).get('incr_point', 0)
            sum_point = result.get('data', {}).get('sum_point', 0)
            print(f"📈 今日获得: {incr_point} 矿石")
            print(f"💎 当前总计: {sum_point} 矿石")
            print(f"\n{'='*50}\n")
            return True, incr_point, sum_point
        elif err_no == 15001:
            print(f"⏭️  [{self.account_name}] 今日已签到")
            # 获取当前矿石数
            current_point = self.get_current_point()
            print(f"💎 当前总计: {current_point} 矿石")
            print(f"\n{'='*50}\n")
            return True, 0, current_point
        else:
            print(f"❌ [{self.account_name}] 签到失败: {err_msg}")
            print(f"\n{'='*50}\n")
            return False, 0, 0


def main():
    # 从环境变量读取 Cookie 字符串
    cookies_str = os.getenv('JUEJIN_COOKIES')
    cookies_account2 = os.getenv('JUEJIN_COOKIES_ACCOUNT2')
    cookies_account3 = os.getenv('JUEJIN_COOKIES_ACCOUNT3')
    cookies_account4 = os.getenv('JUEJIN_COOKIES_ACCOUNT4')
    cookies_account5 = os.getenv('JUEJIN_COOKIES_ACCOUNT5')
    
    if not cookies_str:
        print("❌ 未找到 JUEJIN_COOKIES 环境变量")
        print("请在 GitHub Secrets 中配置 JUEJIN_COOKIES")
        return
    
    # 收集所有账号
    accounts = [
        ("主账号", cookies_str)
    ]
    
    if cookies_account2:
        accounts.append(("小号1", cookies_account2))
    if cookies_account3:
        accounts.append(("小号2", cookies_account3))
    if cookies_account4:
        accounts.append(("小号3", cookies_account4))
    if cookies_account5:
        accounts.append(("小号4", cookies_account5))
    
    print(f"\n🎯 多账号签到模式启动！共 {len(accounts)} 个账号")
    print(f"{'='*60}\n")
    
    # 统计信息
    total_stats = {
        'success': 0,
        'failed': 0,
        'total_points': 0,
        'today_points': 0
    }
    
    # 依次为每个账号签到
    for account_name, cookies in accounts:
        checkin = JuejinCheckIn(cookies, account_name)
        success, incr_point, sum_point = checkin.run()
        
        if success:
            total_stats['success'] += 1
            total_stats['today_points'] += incr_point
            total_stats['total_points'] += sum_point
        else:
            total_stats['failed'] += 1
        
        # 账号之间间隔一下
        if account_name != accounts[-1][0]:
            import time
            time.sleep(3)
    
    # 打印总体统计
    print(f"\n{'='*60}")
    print(f"🎉 多账号签到任务完成！")
    print(f"{'='*60}")
    print(f"📊 总体统计:")
    print(f"   - 账号总数: {len(accounts)} 个")
    print(f"   - 签到成功: {total_stats['success']} 个")
    print(f"   - 签到失败: {total_stats['failed']} 个")
    print(f"   - 今日获得: {total_stats['today_points']} 矿石")
    print(f"   - 总计矿石: {total_stats['total_points']} 矿石")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
