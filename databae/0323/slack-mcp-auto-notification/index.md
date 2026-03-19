# 一次需求引发的效率革命：用 Slack MCP 实现团队协作与自动化通知

> 一句话摘要：本文讲述我们如何利用 Slack MCP 自动化完成团队通知、任务提醒、工作流触发等重复性工作，将原本需要手动发送的消息和提醒交给 AI 管理。

## 一、背景与问题

### 1.1 业务场景

有一次，团队需要**建立一套完善的自动化通知体系**，具体包括：

1. 代码合并到主分支时，自动通知相关人员
2. CI/CD 流水线执行完成后，发送构建结果通知
3. 定时提醒待办任务和会议
4. 当监控系统检测到异常时，自动发送告警到 Slack
5. 每周五自动发送周报汇总到团队频道

如果放在以前，我们可能需要：

1. 手动在各个平台配置 Webhook
2. 编写各种脚本和定时任务
3. 逐个发送通知消息
4. 手动整理和汇总信息

**这工作量，想想都头皮发麻。**

### 1.2 痛点分析

- **重复性高**：每次都是类似的通知，只是内容不同
- **分散管理**：各种通知分散在不同的平台和脚本中
- **容易遗漏**：手动发送可能忘记某些通知
- **维护困难**：多个脚本难以统一管理和维护

### 1.3 我们的需求

- **统一入口**：所有通知通过 Slack MCP 统一发送
- **智能触发**：根据事件自动触发通知
- **定时任务**：支持定时发送通知
- **交互能力**：支持 Slack 消息的交互操作

---

## 二、方案选型

### 2.1 什么是 Slack MCP？

Slack MCP 是一个 Model Context Protocol（MCP）服务器，它允许 AI 助手通过 Slack API 操作 Slack 频道、发送消息、管理成员等。换句话说，**你可以用自然语言指挥 AI 管理 Slack 消息和频道**。

### 2.2 为什么选择它？

| 方案 | 优点 | 缺点 |
|------|------|------|
| 手动发送 | 无需技术准备 | 效率低、易遗漏 |
| Slack Webhook | 简单易用 | 功能有限 |
| Slack Bot | 功能强大 | 需要编写代码 |
| **Slack MCP** | **AI 直接控制、无需编写脚本** | **需要 MCP 环境** |

---

## 三、实现步骤

### 3.1 环境准备

首先，你需要安装 Slack MCP。以下是安装命令：

```bash
# 使用 uvx 安装
uvx mcp-server-slack
```

### 3.2 配置 MCP

在项目的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "slack": {
      "command": "uvx",
      "args": ["mcp-server-slack"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-your-token",
        "SLACK_TEAM_ID": "your-team-id"
      }
    }
  }
}
```

### 3.3 配置 Slack App

1. 登录 Slack API：https://api.slack.com/
2. 创建一个新的 App
3. 添加以下权限（OAuth Scopes）：
   - `chat:write` - 发送消息
   - `channels:read` - 读取频道列表
   - `channels:history` - 读取频道历史
   - `users:read` - 读取用户信息
   - `reactions:write` - 添加反应
4. 安装应用到工作区
5. 获取 Bot User OAuth Token

### 3.4 自动化通知配置

配置完成后，你可以直接用自然语言指挥 AI。以下是我们当时使用的提示词：

```
请帮我完成以下任务：
1. 在 #devops 频道发送一条消息：CI/CD 流水线 #123 已完成构建
2. 消息格式：标题 + 状态（成功/失败）+ 详情链接
3. 如果构建失败，@相关开发人员
```

AI 会自动：

- 连接到 Slack API
- 发送消息到指定频道
- 处理消息格式和提及

### 3.5 定时通知配置

```
请帮我设置以下定时通知：
1. 每天上午 9 点，在 #general 频道发送「早上好」问候
2. 每周五下午 5 点，在 #team 频道发送周报汇总
3. 每天下午 6 点，提醒未完成的 Code Review
```

---

## 四、核心代码示例

虽然 MCP 可以用自然语言操作，但有些场景我们还是需要编写脚本。以下是一个使用 Slack API 的示例：

```javascript
const { WebClient } = require('@slack/web-api');

const SLACK_TOKEN = process.env.SLACK_BOT_TOKEN;
const slack = new WebClient(SLACK_TOKEN);

// 发送消息到频道
async function sendMessage(channel, text, blocks = null) {
  const result = await slack.chat.postMessage({
    channel,
    text,
    blocks
  });
  return result;
}

// 发送富文本消息
async function sendRichMessage(channel, title, fields, color = 'good') {
  const blocks = [
    {
      type: 'header',
      text: { type: 'plain_text', text: title }
    },
    {
      type: 'section',
      fields: fields.map(f => ({
        type: 'mrkdwn',
        text: `*${f.title}:*\n${f.value}`
      }))
    }
  ];
  
  return sendMessage(channel, title, blocks);
}

// CI/CD 构建通知
async function notifyBuildResult(channel, buildId, status, duration, commit) {
  const statusEmoji = status === 'success' ? '✅' : '❌';
  const statusText = status === 'success' ? '成功' : '失败';
  
  return sendRichMessage(channel, `${statusEmoji} 构建 #${buildId} ${statusText}`, [
    { title: '构建 ID', value: buildId },
    { title: '状态', value: statusText },
    { title: '耗时', value: `${duration}s` },
    { title: '提交', value: commit }
  ]);
}

// 代码审查提醒
async function remindCodeReview(channel, prList) {
  const prTexts = prList.map(pr => 
    `• <${pr.url}|#${pr.number} {pr.title}> - @${pr.author}`
  ).join('\n');
  
  const blocks = [
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: `📝 *待 Code Review 的 PR:*\n${prTexts}`
      }
    },
    {
      type: 'actions',
      elements: [
        {
          type: 'button',
          text: { type: 'plain_text', text: '查看全部' },
          url: 'https://github.com/pulls/review-requested'
        }
      ]
    }
  ];
  
  return sendMessage(channel, '待 Code Review 提醒', blocks);
}

// 周报汇总通知
async function weeklyReportNotify(channel, report) {
  const blocks = [
    {
      type: 'header',
      text: { type: 'plain_text', text: '📊 本周周报汇总' }
    },
    {
      type: 'section',
      fields: [
        { type: 'mrkdwn', text: `*PR 合并:*\n${report.prMerged}` },
        { type: 'mrkdwn', text: `*Issue 关闭:*\n${report.issueClosed}` },
        { type: 'mrkdwn', text: `*代码提交:*\n${report.commits}` },
        { type: 'mrkdwn', text: `*本周亮点:*\n${report.highlights}` }
      ]
    }
  ];
  
  return sendMessage(channel, '本周周报汇总', blocks);
}

// 定时任务示例（使用 node-cron）
const cron = require('node-cron');

// 每天早上 9 点发送问候
cron.schedule('0 9 * * 1-5', async () => {
  await sendMessage('#general', '☀️ 早上好！新的一天开始了，加油！');
});

// 每天下午 6 点提醒 Code Review
cron.schedule('0 18 * * 1-5', async () => {
  const prs = await getPendingPRs();
  if (prs.length > 0) {
    await remindCodeReview('#dev', prs);
  }
});
```

---

## 五、效果对比

| 指标 | 手动操作 | MCP 自动化 |
|------|----------|------------|
| 构建通知 | 每次手动发送 | 自动发送 |
| 定时提醒 | 需要定时任务脚本 | 自然语言配置 |
| 告警处理 | 分散在各个平台 | 统一入口 |
| 维护成本 | 多个脚本难维护 | 统一管理 |

---

## 六、更多应用场景

### 6.1 监控系统集成

- 当监控系统检测到异常时，自动发送告警到 Slack
- 根据告警级别选择不同的频道和通知方式
- 支持告警聚合，避免信息过载

### 6.2 自动化工作流

- 当 GitHub 有新 Issue 时，自动在 Slack 创建任务
- 当 JIRA 状态变更时，自动通知相关人员
- 当审批流程完成时，自动发送通知

### 6.3 团队互动

- 定时发送「每日一句」或技术小贴士
- 团队成员生日时自动发送祝福
- 里程碑达成时发送庆祝消息

---

## 七、注意事项与最佳实践

### 7.1 常见坑

1. **Token 权限**：确保 Bot Token 有足够的权限
2. **频率限制**：Slack API 有调用频率限制，注意控制
3. **频道 ID**：使用频道 ID 而不是频道名称

### 7.2 安全建议

- **敏感信息**：不要在代码中硬编码 Token，使用环境变量
- **权限最小化**：只给 Bot 必要的最小权限
- **消息审核**：重要通知添加人工审核环节

### 7.3 最佳实践

- **消息模板**：建立统一的消息模板，保持风格一致
- **分级通知**：根据重要程度选择不同的通知方式
- **日志记录**：记录所有通知发送日志，便于排查问题

---

## 总结

通过 Slack MCP，我们成功将 **团队通知从手动操作转变为自动化流程**，效率提升了 **10+ 倍**。

更重要的是，**AI 可以根据上下文智能处理通知**，不仅能发送消息，还能处理交互、汇总信息等。

如果你也有类似的团队协作和通知需求，不妨试试 Slack MCP。

---

**相关资源**：

- Slack API 官方文档：https://api.slack.com/
- MCP 官方文档：https://modelcontextprotocol.io/
- Slack MCP 仓库：https://github.com/anthropics/mcp-servers

**标签**：#AI #MCP #Slack #自动化 #团队协作