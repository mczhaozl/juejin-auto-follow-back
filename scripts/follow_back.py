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
    def __init__(self, cookies_str, account_name="主账号"):
        self.session = requests.Session()
        self.account_name = account_name
        # 将 Cookie 字符串转换为字典
        self.cookies = self._parse_cookies(cookies_str)
        self.base_url = "https://api.juejin.cn"
        
        # 从 cookies 中提取 uuid
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
        
    def get_followers(self, cursor="0", limit=20):
        """获取关注我的用户列表"""
        url = f"{self.base_url}/interact_api/v1/message/get_message"
        params = {
            'aid': '2608',
            'uuid': self.uuid,
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
            'uuid': self.uuid,
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
        print(f"🚀 [{self.account_name}] 开始执行回关任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*50}\n")
        
        result = self.get_followers()
        if not result or result.get('err_no') != 0:
            print(f"❌ [{self.account_name}] 获取粉丝列表失败")
            return 0, 0, 0
        
        data_list = result.get('data', [])
        if not data_list:
            print(f"✅ [{self.account_name}] 暂无新粉丝")
            return 0, 0, 0
        
        follow_count = 0
        skip_count = 0
        
        for item in data_list:
            src_info = item.get('src_info', {})
            user_id = src_info.get('item_id')
            user_name = src_info.get('name', '未知用户')
            is_follow = src_info.get('is_follow', False)
            
            if is_follow:
                print(f"⏭️  [{self.account_name}] 跳过 {user_name} (已关注)")
                skip_count += 1
                continue
            
            print(f"🔄 [{self.account_name}] 正在回关: {user_name} (ID: {user_id})")
            
            if self.follow_user(user_id):
                print(f"✅ [{self.account_name}] 成功回关: {user_name}")
                follow_count += 1
                # 避免操作过于频繁，添加延时
                time.sleep(2)
            else:
                print(f"❌ [{self.account_name}] 回关失败: {user_name}")
        
        print(f"\n{'='*50}")
        print(f"📊 [{self.account_name}] 执行结果:")
        print(f"   - 新增回关: {follow_count} 人")
        print(f"   - 已关注: {skip_count} 人")
        print(f"   - 总计处理: {len(data_list)} 人")
        print(f"{'='*50}\n")
        
        return follow_count, skip_count, len(data_list)
    
    def save_log(self, account_name, follow_count, skip_count, total):
        """保存执行日志"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"{datetime.now().strftime('%Y-%m')}.json"
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "account": account_name,
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
    cookies_account2 = os.getenv('JUEJIN_COOKIES_ACCOUNT2')
    cookies_account3 = os.getenv('JUEJIN_COOKIES_ACCOUNT3')
    cookies_account4 = os.getenv('JUEJIN_COOKIES_ACCOUNT4')
    cookies_account5 = os.getenv('JUEJIN_COOKIES_ACCOUNT5')
    cookies_account6 = os.getenv('JUEJIN_COOKIES_ACCOUNT6')
    cookies_account7 = os.getenv('JUEJIN_COOKIES_ACCOUNT7')
    cookies_account8 = os.getenv('JUEJIN_COOKIES_ACCOUNT8')
    
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
    if cookies_account6:
        accounts.append(("小号5", cookies_account6))
    if cookies_account7:
        accounts.append(("小号6", cookies_account7))
    if cookies_account8:
        accounts.append(("小号7", cookies_account8))
    
    print(f"\n🎯 五倍返回模式启动！共 {len(accounts)} 个账号")
    print(f"{'='*60}\n")
    
    # 首先用主账号获取粉丝列表
    main_bot = JuejinFollowBot(cookies_str, "主账号")
    main_result = main_bot.get_followers()
    
    if not main_result or main_result.get('err_no') != 0:
        print("❌ 主账号获取粉丝列表失败")
        return
    
    data_list = main_result.get('data', [])
    if not data_list:
        print("✅ 暂无新粉丝需要回关")
        return
    
    # 提取所有需要回关的用户ID
    target_users = []
    for item in data_list:
        src_info = item.get('src_info', {})
        user_id = src_info.get('item_id')
        user_name = src_info.get('name', '未知用户')
        is_follow = src_info.get('is_follow', False)
        
        if not is_follow and user_id:
            target_users.append({
                'id': user_id,
                'name': user_name
            })
    
    if not target_users:
        print("✅ 所有粉丝都已回关")
        return
    
    print(f"📋 发现 {len(target_users)} 位新粉丝待回关\n")
    
    # 用所有账号依次回关
    total_stats = {
        'success': 0,
        'failed': 0
    }
    
    for account_name, cookies in accounts:
        bot = JuejinFollowBot(cookies, account_name)
        
        print(f"\n{'='*60}")
        print(f"🤖 [{account_name}] 开始执行回关")
        print(f"{'='*60}\n")
        
        account_success = 0
        account_failed = 0
        
        for user in target_users:
            user_id = user['id']
            user_name = user['name']
            
            print(f"🔄 [{account_name}] 正在关注: {user_name} (ID: {user_id})")
            
            if bot.follow_user(user_id):
                print(f"✅ [{account_name}] 成功关注: {user_name}")
                account_success += 1
                total_stats['success'] += 1
            else:
                print(f"❌ [{account_name}] 关注失败: {user_name}")
                account_failed += 1
                total_stats['failed'] += 1
            
            # 避免操作过于频繁
            time.sleep(2)
        
        print(f"\n📊 [{account_name}] 执行结果: 成功 {account_success} 人, 失败 {account_failed} 人")
        
        # 记录日志
        bot.save_log(account_name, account_success, account_failed, len(target_users))
        
        # 账号之间间隔稍长一些
        if account_name != accounts[-1][0]:
            time.sleep(5)
    
    print(f"\n{'='*60}")
    print(f"🎉 五倍返回任务完成！")
    print(f"{'='*60}")
    print(f"📊 总体统计:")
    print(f"   - 目标用户: {len(target_users)} 人")
    print(f"   - 使用账号: {len(accounts)} 个")
    print(f"   - 成功关注: {total_stats['success']} 次")
    print(f"   - 失败次数: {total_stats['failed']} 次")
    print(f"   - 理论倍数: {len(accounts)}x")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
