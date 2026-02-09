#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
掘金自动回关脚本
每小时检查新粉丝并自动回关
"""

import os
import json
import time
import requests
from datetime import datetime
from pathlib import Path


class JuejinFollowBot:
    def __init__(self, cookies_str):
        self.session = requests.Session()
        # 将 Cookie 字符串转换为字典
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
        
    def get_followers(self, cursor="0", limit=20):
        """获取关注我的用户列表"""
        url = f"{self.base_url}/interact_api/v1/message/get_message"
        params = {
            'aid': '2608',
            'uuid': '7586574305263552043',
            'spider': '0'
        }
        data = {
            "message_type": 2,
            "cursor": cursor,
            "limit": limit,
            "aid": 2608
        }
        
        try:
            response = self.session.post(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ 获取粉丝列表失败: {e}")
            return None
    
    def follow_user(self, user_id):
        """关注用户"""
        url = f"{self.base_url}/interact_api/v1/follow/do"
        params = {
            'aid': '2608',
            'uuid': '7586574305263552043',
            'spider': '0'
        }
        data = {
            "id": user_id,
            "type": 1
        }
        
        try:
            response = self.session.post(
                url,
                params=params,
                headers=self.headers,
                cookies=self.cookies,
                json=data,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get('err_no') == 0
        except Exception as e:
            print(f"❌ 关注用户 {user_id} 失败: {e}")
            return False
    
    def process_follow_back(self):
        """处理回关逻辑"""
        print(f"\n{'='*50}")
        print(f"🚀 开始执行回关任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        result = self.get_followers()
        if not result or result.get('err_no') != 0:
            print("❌ 获取粉丝列表失败")
            return
        
        data_list = result.get('data', [])
        if not data_list:
            print("✅ 暂无新粉丝")
            return
        
        follow_count = 0
        skip_count = 0
        
        for item in data_list:
            src_info = item.get('src_info', {})
            user_id = src_info.get('item_id')
            user_name = src_info.get('name', '未知用户')
            is_follow = src_info.get('is_follow', False)
            
            if is_follow:
                print(f"⏭️  跳过 {user_name} (已关注)")
                skip_count += 1
                continue
            
            print(f"🔄 正在回关: {user_name} (ID: {user_id})")
            
            if self.follow_user(user_id):
                print(f"✅ 成功回关: {user_name}")
                follow_count += 1
                # 避免操作过于频繁，添加延时
                time.sleep(2)
            else:
                print(f"❌ 回关失败: {user_name}")
        
        print(f"\n{'='*50}")
        print(f"📊 执行结果:")
        print(f"   - 新增回关: {follow_count} 人")
        print(f"   - 已关注: {skip_count} 人")
        print(f"   - 总计处理: {len(data_list)} 人")
        print(f"{'='*50}\n")
        
        # 记录日志
        self.save_log(follow_count, skip_count, len(data_list))
    
    def save_log(self, follow_count, skip_count, total):
        """保存执行日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "follow_count": follow_count,
            "skip_count": skip_count,
            "total": total
        }
        
        logs = []
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        
        logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, ensure_ascii=False, indent=2)


def main():
    # 从环境变量读取 Cookie 字符串
    cookies_str = os.getenv('JUEJIN_COOKIES')
    
    if not cookies_str:
        print("❌ 未找到 JUEJIN_COOKIES 环境变量")
        print("请在 GitHub Secrets 中配置 JUEJIN_COOKIES")
        return
    
    bot = JuejinFollowBot(cookies_str)
    bot.process_follow_back()


if __name__ == "__main__":
    main()
