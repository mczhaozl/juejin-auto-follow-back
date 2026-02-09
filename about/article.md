# GitHub Actions 真香！我用它解决了所有定时任务烦恼

## 前言：一篇文章引发的思考

前段时间刷掘金，看到一篇文章[《🎉 几行代码实现掘金自动签到+微信推送 再也不怕漏签了》](https://juejin.cn/post/7021027165294559245)，作者用 GitHub Actions 实现了自动签到，每天早上还能收到微信推送。

看完之后我突然意识到：**GitHub Actions 不就是现成的免费定时任务平台吗？**

作为一名程序员，我每天都要处理各种定时任务：

- **公司项目**：数据爬取、报表生成、自动备份
- **个人项目**：各种平台签到、数据监控、定时提醒
- **日常琐事**：健康检查、价格监控、内容聚合

这些任务就像一个个小闹钟，时不时就要响一下。

最让我头疼的是执行环境的问题：

- **自己电脑**：领导总说要熄屏省电，下班了还得关机。第二天来了，发现昨晚的任务根本没跑……
- **公司服务器**：资源紧张，申请个定时任务还要走流程。而且跑个人项目总感觉不太合适
- **云服务器**：最稳定，但要花钱啊！一个月几十块，跑个小任务有点浪费

看完那篇签到文章后，我开始尝试用 GitHub Actions 做各种自动化任务。结果发现，这玩意儿真香！

## 我的 GitHub Actions 实践之路

### 第一步：自动签到

受那篇文章启发，我先实现了掘金自动签到。每天早上 8 点自动签到领矿石，再也不用担心漏签了。

### 第二步：数据监控

有了第一次成功经验，我开始尝试更多场景：
- 监控商品价格，降价自动通知
- 检查服务器健康状态
- 定时备份重要数据

### 第三步：社交自动化

在掘金写文章后，经常有朋友关注我。按照社交礼仪，应该回关表示感谢。但每次都要手动操作，有时候忙起来就忘了……

作为程序员，怎么能容忍这种重复劳动？于是我想：**能不能也用 GitHub Actions 来处理这个问题？**

经过一番研究，我发现完全可行！而且实现起来并不复杂。

## GitHub Actions 是什么？

GitHub Actions 是 GitHub 官方提供的 CI/CD（持续集成/持续部署）服务，但它的能力远不止于此。简单来说，它就是一个**云端的自动化执行平台**。

### 核心概念

**1. Workflow（工作流）**
- 一个自动化流程，由一个 YAML 文件定义
- 存放在仓库的 `.github/workflows/` 目录下
- 可以有多个 workflow，互不干扰

**2. Event（事件）**
- 触发 workflow 的条件
- 常见事件：
  - `push`：代码推送时触发
  - `pull_request`：PR 创建时触发
  - `schedule`：定时触发（cron 表达式）
  - `workflow_dispatch`：手动触发

**3. Job（任务）**
- workflow 中的一个执行单元
- 可以并行或串行执行多个 job
- 每个 job 运行在独立的虚拟机中

**4. Step（步骤）**
- job 中的具体操作
- 可以是运行命令，也可以是使用 Action

**5. Action（动作）**
- 可复用的代码片段
- GitHub 官方和社区提供了大量现成的 Action
- 比如：`actions/checkout`（拉取代码）、`actions/setup-python`（安装 Python）

### 为什么选择 GitHub Actions？

#### 1. 完全免费
- **公共仓库**：不限时长，随便用
- **私有仓库**：每月 2000 分钟（足够用了）
- **计费规则**：
  - Linux 虚拟机：1 分钟 = 1 分钟
  - Windows 虚拟机：1 分钟 = 2 分钟
  - macOS 虚拟机：1 分钟 = 10 分钟
- 我现在跑了好几个定时任务，每月才用 400 分钟

#### 2. 稳定可靠
- GitHub 的基础设施，比自己的电脑靠谱多了
- 不用担心断电、断网、重启
- 24/7 运行，从不掉线
- 全球多个数据中心，速度快

#### 3. 配置简单
- 一个 YAML 文件搞定
- 不需要额外的服务器
- 不需要复杂的运维知识
- 丰富的官方文档和社区资源

#### 4. 安全性高
- GitHub Secrets 加密存储敏感信息
- 日志自动屏蔽密钥（显示为 `***`）
- 即使仓库公开，密钥也不会泄露
- 支持环境隔离和权限控制

#### 5. 生态丰富
- 超过 10,000+ 个现成的 Action 可用
- 支持 Docker 容器
- 可以调用任何 API 和服务
- 社区活跃，问题容易解决

### GitHub Actions 的运行环境

每次执行时，GitHub 会分配一个全新的虚拟机：

**可用的操作系统**：
- `ubuntu-latest`（推荐，最快）
- `windows-latest`
- `macos-latest`

**预装软件**：
- 常见编程语言：Python、Node.js、Java、Go、Ruby 等
- 开发工具：Git、Docker、curl、wget 等
- 数据库：MySQL、PostgreSQL、MongoDB 等

**硬件配置**：
- CPU：2 核
- 内存：7 GB
- 磁盘：14 GB SSD

对于定时任务来说，这个配置完全够用了！

## Cron 表达式详解

定时任务的核心是 cron 表达式，它决定了任务的执行时间。

### 基本格式

```
* * * * *
│ │ │ │ │
│ │ │ │ └─── 星期几 (0-6, 0 = 周日)
│ │ │ └───── 月份 (1-12)
│ │ └─────── 日期 (1-31)
│ └───────── 小时 (0-23)
└─────────── 分钟 (0-59)
```

### 常用示例

```yaml
# 每小时执行一次（整点）
- cron: '0 * * * *'

# 每天早上 8 点（北京时间需要 -8 小时，即 UTC 0 点）
- cron: '0 0 * * *'

# 每天早上 9 点和晚上 6 点
- cron: '0 1,10 * * *'  # UTC 时间

# 每 2 小时执行一次
- cron: '0 */2 * * *'

# 每周一早上 9 点
- cron: '0 1 * * 1'

# 每月 1 号早上 9 点
- cron: '0 1 1 * *'

# 工作日（周一到周五）早上 9 点
- cron: '0 1 * * 1-5'
```

**注意**：GitHub Actions 使用 UTC 时间，北京时间需要 -8 小时！

### 在线工具

推荐使用 [crontab.guru](https://crontab.guru/) 来生成和验证 cron 表达式。

## 通用实现思路

不管是签到、回关还是其他自动化任务，实现思路都是类似的：

### 第一步：分析需求

以社交平台的自动化为例，我们需要：
1. 获取需要处理的数据（比如新粉丝列表）
2. 判断是否需要操作（比如是否已经关注）
3. 执行相应操作（比如回关）
4. 记录执行日志

### 第二步：编写脚本

核心逻辑框架：

```python
class AutomationBot:
    def __init__(self, credentials):
        # 初始化：设置认证信息、请求头等
        pass
    
    def get_data(self):
        # 获取需要处理的数据
        pass
    
    def process_item(self, item):
        # 处理单个数据项
        pass
    
    def run(self):
        # 主流程：获取数据 → 遍历处理 → 记录日志
        data = self.get_data()
        for item in data:
            self.process_item(item)
            time.sleep(2)  # 避免操作过快
```

关键点：
- 添加延时，避免触发风控
- 异常处理，保证脚本稳定性
- 记录日志，方便查看运行情况

### 第三步：配置 GitHub Actions

创建 `.github/workflows/automation.yml`：

```yaml
name: 自动化任务

on:
  schedule:
    - cron: '0 * * * *'  # 定时执行
  workflow_dispatch:  # 允许手动触发

jobs:
  automation:
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

      - name: 执行脚本
        run: python scripts/automation.py
        env:
          CREDENTIALS: ${{ secrets.CREDENTIALS }}
```

### 第四步：配置密钥

敏感信息（如 Cookie、Token）存储在 GitHub Secrets：

**添加 Secret**：
1. 打开仓库页面
2. 点击 Settings（设置）
3. 左侧菜单选择 Secrets and variables → Actions
4. 点击 New repository secret
5. 输入 Name（名称）和 Secret（值）
6. 点击 Add secret

**在代码中使用**：
```yaml
env:
  MY_SECRET: ${{ secrets.MY_SECRET }}
```

**安全特性**：
- Secret 添加后无法查看，只能更新或删除
- 日志中自动屏蔽 Secret 内容
- Fork 的仓库不会复制 Secret
- 可以设置环境级别的 Secret

## 我的实践成果

用 GitHub Actions 几个月下来，我已经实现了：

### 1. 每日签到系列
- 掘金签到：每天早上 8 点，自动领矿石
- 其他平台签到：再也不用担心漏签

### 2. 社交自动化
- 自动回关：有人关注我，一小时内自动回关
- 消息提醒：重要互动及时通知

### 3. 数据监控
- 价格监控：商品降价自动通知
- 服务监控：网站挂了立即提醒

### 4. 定时备份
- 数据库备份：每天自动备份到云盘
- 文件同步：重要文件定时同步

所有这些任务，都在 GitHub 上稳定运行，完全不用操心！

## 进阶技巧

### 1. 调整执行频率

根据实际需求调整 cron 表达式：

```yaml
# 每2小时执行一次
- cron: '0 */2 * * *'

# 每天早上9点和晚上6点执行
- cron: '0 9,18 * * *'

# 每周一早上9点执行
- cron: '0 1 * * 1'
```

### 2. 添加通知功能

可以集成企业微信、钉钉、PushPlus 等通知服务：

```python
def send_notification(message):
    webhook_url = os.getenv('WEBHOOK_URL')
    requests.post(webhook_url, json={
        'msgtype': 'text',
        'text': {'content': message}
    })
```

### 3. 错误重试机制

添加重试逻辑，提高脚本稳定性：

```python
def retry_on_failure(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise e
            time.sleep(5)
```

### 4. 数据统计

记录执行历史，生成统计报告：

```python
def save_log(data):
    log_file = Path(f"logs/{datetime.now().strftime('%Y-%m')}.json")
    logs = []
    if log_file.exists():
        with open(log_file) as f:
            logs = json.load(f)
    logs.append(data)
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=2)
```

## 成本分析

让我们算一笔账，看看 GitHub Actions 到底有多划算：

**我的使用情况**：
- 签到任务：每天 1 次，每次 20 秒
- 社交自动化：每小时 1 次，每次 30 秒
- 数据监控：每 2 小时 1 次，每次 15 秒

**每月总耗时**：
- 签到：30 天 × 20 秒 = 10 分钟
- 社交：30 天 × 24 次 × 30 秒 = 360 分钟
- 监控：30 天 × 12 次 × 15 秒 = 90 分钟
- **合计：约 460 分钟**

GitHub 免费账户每月 2000 分钟，我只用了 460 分钟，还剩 1540 分钟可以跑其他任务。

**如果用云服务器**：
- 最便宜的云服务器：约 50 元/月
- GitHub Actions：0 元/月

**完全免费，零成本！**

## 举一反三：更多应用场景

掌握了这个技巧，你可以用 GitHub Actions 做很多事情。我现在已经用它实现了：

### 1. 自动签到系列
- **掘金签到**：每天早上 8 点自动签到，领矿石
- **CSDN 签到**：自动签到领积分
- **GitHub 打卡**：保持 Contributions 绿色

### 2. 数据监控系列
- **价格监控**：定时爬取商品价格，降价自动通知
- **库存监控**：抢购商品有货立即提醒
- **网站监控**：定时检查网站是否正常

### 3. 自动化运维
- **定时备份**：自动备份数据库、文件到云盘
- **健康检查**：定时 ping 服务器，挂了立即通知
- **日志清理**：定期清理过期日志文件

### 4. 内容聚合
- **RSS 订阅**：定时抓取博客更新，生成 RSS 源
- **热榜聚合**：每天汇总各大平台热榜，发送到邮箱
- **文章推送**：关注的作者发新文章，自动推送

只要是定时任务，都可以用 GitHub Actions 来做！而且完全免费，稳定可靠。

## 总结与思考

从最初看到别人的签到脚本受到启发，到现在用 GitHub Actions 实现了各种自动化任务，我深刻体会到：

**作为程序员，我们的目标就是：能自动化的绝不手动，能偷懒的绝不勤快！**

GitHub Actions 的优势：
- ✅ **零成本**：完全免费
- ✅ **零维护**：设置好就不用管了
- ✅ **高可用**：GitHub 的基础设施，稳定可靠
- ✅ **易扩展**：可以轻松添加更多功能

现在我的各种定时任务都跑在 GitHub 上：
- 电脑关机也不怕
- 服务器也不用买
- 省心又省钱

希望这篇文章能给你带来启发。如果你也有类似的定时任务需求，不妨试试 GitHub Actions，说不定会打开新世界的大门！

## 常见问题与解决方案

### 1. 为什么我的定时任务没有执行？

**可能原因**：
- 仓库长期没有活动，GitHub 会自动禁用 workflow
- cron 表达式写错了
- workflow 文件语法错误

**解决方法**：
- 定期（每 60 天）手动触发一次 workflow
- 使用 [crontab.guru](https://crontab.guru/) 验证表达式
- 在 Actions 页面查看错误日志

### 2. 如何查看执行日志？

1. 进入仓库的 Actions 标签页
2. 点击对应的 workflow
3. 点击具体的运行记录
4. 展开每个 step 查看详细日志

### 3. 如何手动触发 workflow？

在 workflow 中添加：
```yaml
on:
  workflow_dispatch:  # 允许手动触发
```

然后在 Actions 页面点击 "Run workflow" 按钮。

### 4. 如何调试脚本？

**方法一**：在脚本中添加 print 语句
```python
print(f"Debug: {variable}")
```

**方法二**：使用 `act` 在本地运行 GitHub Actions
```bash
# 安装 act
brew install act  # macOS
# 运行 workflow
act -j job_name
```

### 5. 如何避免超出免费额度？

- 优先使用 Linux 虚拟机（最省）
- 减少执行频率
- 优化脚本执行时间
- 使用缓存减少重复安装

### 6. 定时任务不准时怎么办？

GitHub Actions 的定时任务可能会延迟 3-10 分钟，这是正常现象。如果需要精确定时，建议：
- 提前几分钟执行
- 或者使用其他定时任务服务

## 最佳实践建议

### 1. 代码组织
```
your-repo/
├── .github/
│   └── workflows/
│       ├── checkin.yml      # 签到任务
│       ├── follow-back.yml  # 回关任务
│       └── monitor.yml      # 监控任务
├── scripts/
│   ├── checkin.py
│   ├── follow_back.py
│   └── utils.py             # 公共工具函数
├── logs/                    # 日志目录
├── config/
│   └── example.json         # 配置示例
└── README.md
```

### 2. 错误处理
```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    # 执行任务
    result = do_something()
    logging.info(f"Success: {result}")
except Exception as e:
    logging.error(f"Error: {e}")
    # 可以发送通知
    send_notification(f"Task failed: {e}")
```

### 3. 性能优化
- 使用缓存减少重复安装
```yaml
- name: Cache dependencies
  uses: actions/cache@v3
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
```

### 4. 安全建议
- 永远不要在代码中硬编码密钥
- 定期更新 Secret（如 Cookie）
- 使用最小权限原则
- 审查第三方 Action 的代码

### 5. 从简单开始
1. **第一步**：实现一个简单的签到脚本
2. **第二步**：添加日志和错误处理
3. **第三步**：集成通知功能
4. **第四步**：扩展更多自动化任务

### 6. 注意事项
- 不要设置过高的执行频率，避免给平台造成压力
- 尊重平台规则，自动化是为了提高效率
- 保护好个人隐私信息
- 定期检查任务执行情况

## 写在最后

最近我在掘金上写文章，经常收到朋友们的关注。为了表示感谢，我都会回关。

不过从现在开始,如果你关注了我，最多一小时就能收到回关。不信的话，可以试试看 �

---

**参考文章**：
- [🎉 几行代码实现掘金自动签到+微信推送 再也不怕漏签了](https://juejin.cn/post/7021027165294559245) - 感谢 @Bi8bo 的文章给我的启发！

**相关资源**：
- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [Cron 表达式生成器](https://crontab.guru/)

如果这篇文章对你有帮助，欢迎点赞、收藏、关注三连！有任何问题也欢迎在评论区交流 🎉
