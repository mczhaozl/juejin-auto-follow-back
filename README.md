# 🤖 掘金自动化工具集

> 基于 GitHub Actions 的掘金自动化工具，包含自动回关和每日签到功能

## ✨ 功能特性

### 🔄 自动回关
- 每小时自动检查新粉丝
- 智能识别未回关的用户
- 自动回关并记录日志

### 📅 每日签到
- 每天早上 8 点自动签到
- 自动领取矿石奖励
- 显示当前矿石总数

### 🔒 安全可靠
- Cookie 加密存储在 GitHub Secrets
- 完全免费，利用 GitHub Actions 免费额度
- 自动记录执行日志

## 🚀 快速开始

### 1. Fork 本仓库

点击右上角 Fork 按钮，将仓库复制到你的账号下

### 2. 获取掘金 Cookie

1. 打开浏览器，登录 [掘金](https://juejin.cn)
2. 按 F12 打开开发者工具
3. 切换到 Network（网络）标签
4. 刷新页面，找到任意请求
5. 在请求头中找到 Cookie，**直接复制完整内容**（一长串字符串）

### 3. 配置 GitHub Secrets

1. 进入你 Fork 的仓库
2. 点击 Settings → Secrets and variables → Actions
3. 点击 New repository secret
4. Name 填写：`JUEJIN_COOKIES`
5. Value 填写：**直接粘贴你复制的 Cookie 字符串**
6. 点击 Add secret

### 4. 启用 GitHub Actions

1. 进入 Actions 标签页
2. 点击 "I understand my workflows, go ahead and enable them"
3. 你会看到两个工作流：
   - **自动回关掘金粉丝**：每小时执行一次
   - **掘金每日签到**：每天早上 8 点执行
4. 等待自动执行，或点击 "Run workflow" 手动触发

## 📋 Cookie 格式示例

直接粘贴浏览器复制的 Cookie 字符串即可，格式如下：

```
__tea_cookie_tokens_2608=xxx; passport_csrf_token=xxx; sessionid=xxx; sid_guard=xxx; uid_tt=xxx; ...
```

**无需转换格式，直接复制粘贴！**

## 📊 执行日志

### 自动回关日志
每次执行后会在 `logs/` 目录下生成月度日志文件，记录：
- 执行时间
- 新增回关数量
- 已关注数量
- 总处理数量

### 签到日志
在 Actions 执行日志中查看：
- 签到状态
- 今日获得矿石
- 当前矿石总数

## ⚙️ 自定义配置

### 修改回关执行频率

编辑 `.github/workflows/auto-follow-back.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 * * * *'  # 每小时执行
  # - cron: '0 */2 * * *'  # 每2小时执行
  # - cron: '0 9,18 * * *'  # 每天9点和18点执行
```

### 修改签到执行时间

编辑 `.github/workflows/daily-checkin.yml` 文件中的 cron 表达式：

```yaml
schedule:
  - cron: '0 0 * * *'  # 每天早上 8 点（北京时间）
  # - cron: '0 12 * * *'  # 每天晚上 8 点（北京时间）
```

### 修改延时时间

编辑 `scripts/follow_back.py` 文件中的延时设置：

```python
time.sleep(2)  # 每次关注后延时2秒，可根据需要调整
```

## 🔧 本地测试

```bash
# 安装依赖
pip install requests

# 设置环境变量（直接粘贴你的 Cookie 字符串）
export JUEJIN_COOKIES='sessionid=xxx; sid_guard=xxx; uid_tt=xxx; ...'

# 测试回关功能
python scripts/follow_back.py

# 测试签到功能
python scripts/daily_checkin.py
```

## ⚠️ 注意事项

1. **Cookie 安全**：不要将 Cookie 直接写在代码中，务必使用 GitHub Secrets
2. **Cookie 有效期**：Cookie 会过期，建议定期（每周）更新一次
3. **频率控制**：不建议设置过高的执行频率，避免触发平台风控
4. **Actions 额度**：GitHub 免费账户每月有 2000 分钟额度，本项目每月约消耗 400 分钟

## 📖 相关文章

- [告别手动回关！用 GitHub Actions 打造掘金自动回关机器人](./about/article.md)
- [🎉 几行代码实现掘金自动签到+微信推送 再也不怕漏签了](https://juejin.cn/post/7021027165294559245) - 感谢原作者的启发

## 🙏 致谢

感谢 [@Bi8bo](https://juejin.cn/user/3369350189299688) 的掘金签到文章给我的启发，让我发现了 GitHub Actions 的强大之处！

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
