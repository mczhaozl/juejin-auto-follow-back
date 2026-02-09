# 告别手动回关！用 GitHub Actions 打造掘金自动回关机器人

## 前言：一个程序员的日常烦恼

作为一名程序员，我每天都要处理各种定时任务。公司的项目有定时任务，自己的个人项目也有定时任务。数据爬取、报表生成、自动备份……这些任务就像一个个小闹钟，时不时就要响一下。

最让我头疼的是，很多平台都有风控机制。你不能一口气批量操作，必须加延时；操作太频繁会被限制，必须控制频率。于是代码里到处都是 `time.sleep()`，看着就心累。

更要命的是执行环境的问题：

- **自己电脑**：领导总说要熄屏省电，下班了还得关机。第二天来了，发现昨晚的任务根本没跑……
- **公司服务器**：资源紧张，申请个定时任务还要走流程。而且跑个人项目总感觉不太合适
- **云服务器**：最稳定，但要花钱啊！一个月几十块，跑个小任务有点浪费

就在我为这些琐事烦恼的时候，我突然想到：**GitHub Actions 不就是现成的免费定时任务平台吗？**

## 灵感来源：掘金的回关需求

作为一个在掘金写文章的技术博主，我经常收到粉丝的关注。按照社交礼仪，别人关注了你，你也应该回关一下表示感谢。

但问题来了：

1. 每次都要手动打开掘金，点进消息页面
2. 一个个查看谁关注了我
3. 点进他们的主页，点击关注按钮
4. 如果粉丝多了，这个过程能重复几十次

这不就是典型的重复劳动吗？作为程序员，怎么能容忍这种低效操作！

于是我决定：**用 GitHub Actions 做一个自动回关机器人，每小时自动检查一次，发现新粉丝就自动回关。**

## 技术方案：GitHub Actions + Python

### 为什么选择 GitHub Actions？

1. **完全免费**：公共仓库不限时长，私有仓库每月 2000 分钟（足够用了）
2. **稳定可靠**：GitHub 的基础设施，比自己的电脑靠谱多了
3. **配置简单**：一个 YAML 文件搞定，不需要额外的服务器
4. **自动执行**：设置好 cron 表达式，到点自动跑，不用操心

### 技术栈

- **GitHub Actions**：定时任务调度
- **Python**：脚本语言，简单高效
- **Requests**：HTTP 请求库
- **GitHub Secrets**：安全存储 Cookie

## 实现步骤

### 第一步：分析掘金 API

打开掘金网站，按 F12 打开开发者工具，观察网络请求。我发现了两个关键接口：

**1. 获取粉丝列表**

```
POST https://api.juejin.cn/interact_api/v1/message/get_message
```

返回数据中有个关键字段：`src_info.is_follow`，表示我是否已经关注了对方。

**2. 关注用户**

```
POST https://api.juejin.cn/interact_api/v1/follow/do
```

传入用户 ID 即可完成关注。

### 第二步：编写 Python 脚本

核心逻辑很简单：

```python
class JuejinFollowBot:
    def process_follow_back(self):
        # 1. 获取粉丝列表
        result = self.get_followers()
        
        # 2. 遍历每个粉丝
        for item in result.get('data', []):
            src_info = item.get('src_info', {})
            user_id = src_info.get('item_id')
            is_follow = src_info.get('is_follow', False)
            
            # 3. 如果还没关注，就回关
            if not is_follow:
                self.follow_user(user_id)
                time.sleep(2)  # 避免操作过快
```

关键点：
- 每次关注后 `sleep(2)` 秒，避免触发风控
- 记录执行日志，方便查看运行情况
- 异常处理，保证脚本稳定性

### 第三步：配置 GitHub Actions

创建 `.github/workflows/auto-follow-back.yml`：

```yaml
name: 自动回关掘金粉丝

on:
  schedule:
    - cron: '0 * * * *'  # 每小时执行一次
  workflow_dispatch:  # 允许手动触发

jobs:
  follow-back:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout 代码
        uses: actions/checkout@v4

      - name: 设置 Python 环境
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: 安装依赖
        run: pip install requests

      - name: 执行回关脚本
        run: python scripts/follow_back.py
        env:
          JUEJIN_COOKIES: ${{ secrets.JUEJIN_COOKIES }}
```

### 第四步：配置 Cookie

Cookie 是敏感信息，不能直接写在代码里。GitHub Secrets 完美解决了这个问题：

1. 从浏览器复制掘金的 Cookie
2. 转换成 JSON 格式
3. 在仓库的 Settings → Secrets 中添加 `JUEJIN_COOKIES`

格式示例：

```json
{
  "sessionid": "your_sessionid_here",
  "sid_guard": "your_sid_guard_here",
  "uid_tt": "your_uid_tt_here"
}
```

## 实际效果

配置完成后，每小时 GitHub Actions 会自动执行一次：

```
==================================================
🚀 开始执行回关任务 - 2026-02-09 10:00:00
==================================================

🔄 正在回关: 张三 (ID: 123456789)
✅ 成功回关: 张三
🔄 正在回关: 李四 (ID: 987654321)
✅ 成功回关: 李四
⏭️  跳过 王五 (已关注)

==================================================
📊 执行结果:
   - 新增回关: 2 人
   - 已关注: 1 人
   - 总计处理: 3 人
==================================================
```

从此以后，我再也不用手动回关了。每天打开掘金，发现粉丝都已经自动回关好了，省心又省力！

## 进阶优化

### 1. 调整执行频率

如果觉得每小时太频繁，可以修改 cron 表达式：

```yaml
# 每2小时执行一次
- cron: '0 */2 * * *'

# 每天早上9点和晚上6点执行
- cron: '0 9,18 * * *'
```

### 2. 添加通知功能

可以集成企业微信、钉钉等通知，执行完成后发送消息提醒：

```python
def send_notification(follow_count):
    webhook_url = os.getenv('WEBHOOK_URL')
    requests.post(webhook_url, json={
        'msgtype': 'text',
        'text': {'content': f'今日回关 {follow_count} 位新粉丝'}
    })
```

### 3. 数据统计

每月生成一份统计报告，看看涨了多少粉：

```python
def generate_monthly_report(self):
    log_file = Path(f"logs/{datetime.now().strftime('%Y-%m')}.json")
    with open(log_file) as f:
        logs = json.load(f)
    
    total_follows = sum(log['follow_count'] for log in logs)
    print(f"本月共回关 {total_follows} 位粉丝")
```

## 成本分析

让我们算一笔账：

- **执行频率**：每小时 1 次，每天 24 次
- **单次耗时**：约 30 秒
- **每月耗时**：24 × 30 × 30 = 21,600 秒 = 360 分钟

GitHub 免费账户每月 2000 分钟，这个项目只用了 360 分钟，还剩 1640 分钟可以跑其他任务。**完全免费，零成本！**

## 举一反三：更多应用场景

掌握了这个技巧，你可以用 GitHub Actions 做很多事情：

1. **自动签到**：每天自动签到各种平台，领积分、领金币
2. **数据监控**：定时爬取数据，价格变动、库存变化自动通知
3. **定时备份**：自动备份数据库、文件到云盘
4. **RSS 订阅**：定时抓取博客更新，生成 RSS 源
5. **健康检查**：定时 ping 你的网站，挂了立即通知

只要是定时任务，都可以用 GitHub Actions 来做！

## 总结

从一个简单的回关需求出发，我们用 GitHub Actions 打造了一个自动化机器人。这个方案的优势在于：

- ✅ **零成本**：完全免费
- ✅ **零维护**：设置好就不用管了
- ✅ **高可用**：GitHub 的基础设施，稳定可靠
- ✅ **易扩展**：可以轻松添加更多功能

作为程序员，我们的目标就是：**能自动化的绝不手动，能偷懒的绝不勤快！**

希望这篇文章能给你带来启发。如果你也有类似的定时任务需求，不妨试试 GitHub Actions，说不定会打开新世界的大门！

---

**项目地址**：[GitHub - juejin-auto-follow-back](https://github.com/yourusername/juejin-auto-follow-back)

**觉得有用的话，给个 Star ⭐️ 吧！顺便关注一下我，我会自动回关的 😄**
