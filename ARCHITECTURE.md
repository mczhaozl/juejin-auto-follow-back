# 🏗️ 五倍返回架构说明

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions                          │
│                  (每小时自动触发)                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  follow_back.py                             │
│                  (主控制脚本)                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              读取环境变量 (Cookies)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │ JUEJIN_COOKIES          (主账号)                     │  │
│  │ JUEJIN_COOKIES_ACCOUNT2 (小号1)                      │  │
│  │ JUEJIN_COOKIES_ACCOUNT3 (小号2)                      │  │
│  │ JUEJIN_COOKIES_ACCOUNT4 (小号3)                      │  │
│  │ JUEJIN_COOKIES_ACCOUNT5 (小号4)                      │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 1: 主账号获取粉丝列表                          │
│                                                             │
│  GET /interact_api/v1/message/get_message                  │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ 返回：                                               │  │
│  │ - 用户A (ID: 123456, 未关注)                        │  │
│  │ - 用户B (ID: 123457, 未关注)                        │  │
│  │ - 用户C (ID: 123458, 已关注) ← 跳过                 │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 2: 提取待回关用户列表                          │
│                                                             │
│  target_users = [                                           │
│    { id: "123456", name: "用户A" },                        │
│    { id: "123457", name: "用户B" }                         │
│  ]                                                          │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 3: 所有账号依次回关                            │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ [主账号] 关注 用户A → ✅ 成功                        │  │
│  │ [主账号] 关注 用户B → ✅ 成功                        │  │
│  │          (延时 2 秒)                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ [小号1] 关注 用户A → ✅ 成功                         │  │
│  │ [小号1] 关注 用户B → ✅ 成功                         │  │
│  │          (延时 2 秒)                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ [小号2] 关注 用户A → ✅ 成功                         │  │
│  │ [小号2] 关注 用户B → ✅ 成功                         │  │
│  │          (延时 2 秒)                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ... (小号3、小号4 同理)                                    │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 4: 记录执行日志                                │
│                                                             │
│  logs/2026-02.json                                          │
│  ┌─────────────────────────────────────────────────────┐  │
│  │ {                                                    │  │
│  │   "timestamp": "2026-02-10T14:00:00",               │  │
│  │   "account": "主账号",                               │  │
│  │   "follow_count": 2,                                │  │
│  │   "skip_count": 1,                                  │  │
│  │   "total": 3                                        │  │
│  │ },                                                   │  │
│  │ {                                                    │  │
│  │   "timestamp": "2026-02-10T14:00:15",               │  │
│  │   "account": "小号1",                                │  │
│  │   "follow_count": 2,                                │  │
│  │   "skip_count": 0,                                  │  │
│  │   "total": 2                                        │  │
│  │ },                                                   │  │
│  │ ...                                                  │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│          Step 5: 提交日志到 Git                              │
│                                                             │
│  git add logs/                                              │
│  git commit -m "📝 更新执行日志"                            │
│  git push                                                   │
└─────────────────────────────────────────────────────────────┘
```

## 核心类：JuejinFollowBot

```python
class JuejinFollowBot:
    def __init__(self, cookies_str, account_name):
        """
        初始化机器人
        - cookies_str: Cookie 字符串
        - account_name: 账号名称（用于日志标识）
        """
        
    def get_followers(self):
        """
        获取关注我的用户列表
        返回：粉丝列表数据
        """
        
    def follow_user(self, user_id):
        """
        关注指定用户
        返回：是否成功
        """
        
    def save_log(self, account_name, follow_count, skip_count, total):
        """
        保存执行日志到 logs/ 目录
        """
```

## 执行流程

### 1. 初始化阶段

```python
# 读取所有账号的 Cookies
accounts = [
    ("主账号", JUEJIN_COOKIES),
    ("小号1", JUEJIN_COOKIES_ACCOUNT2),
    ("小号2", JUEJIN_COOKIES_ACCOUNT3),
    ("小号3", JUEJIN_COOKIES_ACCOUNT4),
    ("小号4", JUEJIN_COOKIES_ACCOUNT5)
]
```

### 2. 获取粉丝列表

```python
# 用主账号获取粉丝列表
main_bot = JuejinFollowBot(JUEJIN_COOKIES, "主账号")
result = main_bot.get_followers()

# 提取未关注的用户
target_users = [
    user for user in result['data']
    if not user['src_info']['is_follow']
]
```

### 3. 多账号回关

```python
# 遍历所有账号
for account_name, cookies in accounts:
    bot = JuejinFollowBot(cookies, account_name)
    
    # 遍历所有目标用户
    for user in target_users:
        bot.follow_user(user['id'])
        time.sleep(2)  # 延时避免限流
    
    # 记录日志
    bot.save_log(...)
```

## API 接口

### 获取粉丝列表

```
POST https://api.juejin.cn/interact_api/v1/message/get_message
```

**请求参数**：
```json
{
  "message_type": 2,
  "cursor": "0",
  "limit": 20,
  "aid": 2608
}
```

**响应数据**：
```json
{
  "err_no": 0,
  "data": [
    {
      "src_info": {
        "item_id": "123456",
        "name": "用户A",
        "is_follow": false
      }
    }
  ]
}
```

### 关注用户

```
POST https://api.juejin.cn/interact_api/v1/follow/do
```

**请求参数**：
```json
{
  "id": "123456",
  "type": 1
}
```

**响应数据**：
```json
{
  "err_no": 0
}
```

## 安全机制

### 1. Cookie 安全
- 使用 GitHub Secrets 加密存储
- 不在代码中硬编码
- 不在日志中输出

### 2. 频率控制
- 每次操作间隔 2 秒
- 账号切换间隔 5 秒
- 每小时执行一次

### 3. 错误处理
- API 请求超时处理
- Cookie 失效检测
- 网络异常重试

## 日志系统

### 日志格式

```json
{
  "timestamp": "2026-02-10T14:00:00",
  "account": "主账号",
  "follow_count": 2,
  "skip_count": 1,
  "total": 3
}
```

### 日志文件

- 路径：`logs/YYYY-MM.json`
- 按月份分文件
- JSON 格式存储
- 自动提交到 Git

## 扩展性

### 支持更多账号

修改 `main()` 函数，添加更多环境变量：

```python
cookies_account6 = os.getenv('JUEJIN_COOKIES_ACCOUNT6')
cookies_account7 = os.getenv('JUEJIN_COOKIES_ACCOUNT7')
# ...

if cookies_account6:
    accounts.append(("小号5", cookies_account6))
if cookies_account7:
    accounts.append(("小号6", cookies_account7))
```

### 自定义延时

修改延时参数：

```python
time.sleep(2)  # 操作间隔
time.sleep(5)  # 账号切换间隔
```

### 调整执行频率

修改 `.github/workflows/auto-follow-back.yml`：

```yaml
schedule:
  - cron: '0 * * * *'      # 每小时
  # - cron: '0 */2 * * *'  # 每2小时
  # - cron: '0 9,18 * * *' # 每天9点和18点
```

## 性能优化

### 1. 并发处理
当前是串行处理，可以改为并发：

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(bot.follow_user, user['id'])
        for user in target_users
    ]
```

### 2. 缓存机制
缓存已处理的用户，避免重复操作：

```python
processed_users = set()
if user_id not in processed_users:
    bot.follow_user(user_id)
    processed_users.add(user_id)
```

### 3. 批量操作
如果 API 支持批量关注，可以减少请求次数

## 监控告警

### 添加通知功能

可以集成企业微信、钉钉等通知：

```python
def send_notification(message):
    # 发送通知到企业微信/钉钉
    pass

# 执行完成后通知
send_notification(f"五倍返回完成！成功关注 {total_success} 次")
```

### 错误告警

```python
if failed_count > 0:
    send_notification(f"⚠️ 有 {failed_count} 次关注失败")
```

## 总结

这个架构的优点：
- ✅ 简单易懂，易于维护
- ✅ 完全自动化，无需人工干预
- ✅ 灵活配置，支持任意数量账号
- ✅ 安全可靠，Cookie 加密存储
- ✅ 详细日志，便于追踪问题

可以改进的地方：
- 🔄 添加并发处理提升速度
- 🔄 添加缓存机制避免重复
- 🔄 集成通知功能实时告警
- 🔄 添加数据统计和可视化
