# 一次需求引发的效率革命：用 Sentry MCP 实现智能化错误监控与告警

> 一句话摘要：本文讲述我们如何利用 Sentry MCP 自动化完成错误监控、问题分析、告警处理等重复性工作，将原本需要人工排查的错误问题交给 AI 处理。

## 一、背景与问题

### 1.1 业务场景

有一次，团队需要**建立一套完善的错误监控体系**，具体包括：

1. 实时监控线上环境的错误和异常
2. 自动分析错误原因和影响范围
3. 及时通知相关开发人员
4. 跟踪错误处理进度和结果

如果放在以前，我们可能需要：

1. 每天登录 Sentry 手动查看错误列表
2. 逐个分析错误堆栈和上下文
3. 手动复制错误信息创建 Issue
4. 逐个通知相关开发人员

**这工作量，想想都头皮发麻。**

### 1.2 痛点分析

- **错误量大**：线上环境每天产生大量错误，难以逐个处理
- **分析困难**：错误堆栈复杂，难以快速定位问题
- **响应慢**：从发现错误到处理完成周期长
- **遗漏风险**：可能遗漏重要错误

### 1.3 我们的需求

- **自动监控**：AI 自动监控错误趋势
- **智能分析**：自动分析错误原因和影响范围
- **自动告警**：根据错误级别自动通知相关人员
- **自动跟踪**：自动跟踪错误处理进度

---

## 二、方案选型

### 2.1 什么是 Sentry MCP？

Sentry MCP 是一个 Model Context Protocol（MCP）服务器，它允许 AI 助手通过 Sentry API 操作错误监控数据。换句话说，**你可以用自然语言指挥 AI 管理错误监控和告警**。

### 2.2 为什么选择它？

| 方案 | 优点 | 缺点 |
|------|------|------|
| 手动查看 | 无需技术准备 | 效率低、易遗漏 |
| Sentry Webhook | 简单易用 | 功能有限 |
| Sentry API + 脚本 | 功能强大 | 需要编写代码 |
| **Sentry MCP** | **AI 直接控制、无需编写脚本** | **需要 MCP 环境** |

---

## 三、实现步骤

### 3.1 环境准备

首先，你需要安装 Sentry MCP。以下是安装命令：

```bash
# 使用 uvx 安装
uvx mcp-server-sentry
```

### 3.2 配置 MCP

在项目的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "sentry": {
      "command": "uvx",
      "args": ["mcp-server-sentry"],
      "env": {
        "SENTRY_ORG": "your-org",
        "SENTRY_AUTH_TOKEN": "your-token"
      }
    }
  }
}
```

### 3.3 配置 Sentry Token

1. 登录 Sentry：https://sentry.io/
2. 进入 Settings → API → Auth Tokens
3. 创建新的 Token，需要以下权限：
   - `event:read` - 读取事件
   - `project:read` - 读取项目
   - `issue:read` - 读取问题

### 3.4 自动化错误分析

配置完成后，你可以直接用自然语言指挥 AI。以下是我们当时使用的提示词：

```
请帮我完成以下任务：
1. 查看过去 24 小时的所有错误
2. 按错误类型分组统计数量
3. 对每个错误类型分析可能的原因
4. 找出影响最大的 5 个错误
5. 生成错误分析报告
```

AI 会自动：

- 获取错误列表
- 分析错误模式
- 评估影响范围
- 生成分析报告

### 3.5 自动化告警处理

```
请帮我完成以下任务：
1. 监控新的严重错误
2. 自动分析错误堆栈，找出根本原因
3. 根据错误类型自动创建 JIRA Issue
4. 通知相关开发人员
5. 跟踪 Issue 处理进度
```

---

## 四、核心代码示例

```javascript
const axios = require('axios');

const SENTRY_ORG = process.env.SENTRY_ORG;
const SENTRY_TOKEN = process.env.SENT

RY_TOKEN;

const api = axios.create({
  baseURL: 'https://sentry.io/api/0',
  headers: {
    Authorization: `Bearer ${SENTRY_TOKEN}`
  }
});

// 获取项目列表
async function getProjects() {
  const response = await api.get(`/organizations/${SENTRY_ORG}/projects/`);
  return response.data;
}

// 获取错误列表
async function getIssues(projectSlug) {
  const response = await api.get(
    `/projects/${SENTRY_ORG}/${projectSlug}/issues/`
  );
  return response.data;
}

// 获取错误详情
async function getIssueDetail(issueId) {
  const response = await api.get(`/issues/${issueId}/`);
  return response.data;
}

// 获取错误事件
async function getIssueEvents(issueId) {
  const response = await api.get(`/issues/${issueId}/events/`);
  return response.data;
}

// 自动化错误分析
async function analyzeErrors(projectSlug) {
  const issues = await getIssues(projectSlug);
  
  const analysis = {
    total: issues.length,
    byLevel: {},
    byType: {},
    critical: []
  };
  
  for (const issue of issues) {
    // 按级别统计
    const level = issue.level;
    analysis.byLevel[level] = (analysis.byLevel[level] || 0) + 1;
    
    // 统计关键错误
    if (level === 'error' || level === 'fatal') {
      const detail = await getIssueDetail(issue.id);
      const events = await getIssueEvents(issue.id);
      
      analysis.critical.push({
        id: issue.id,
        title: issue.title,
        count: issue.count,
        userCount: issue.userCount,
        firstSeen: issue.firstSeen,
        lastSeen: issue.lastSeen,
        sampleEvent: events[0]
      });
    }
  }
  
  return analysis;
}

// 自动创建 Issue
async function createJiraIssue(issue) {
  // 调用 JIRA API 创建 Issue
  console.log(`创建 JIRA Issue: ${issue.title}`);
}
```

---

## 五、效果对比

| 指标 | 手动操作 | MCP 自动化 |
|------|----------|------------|
| 错误分析 | 1-2 小时/天 | 约 5 分钟/天 |
| 告警响应 | 30 分钟+ | 实时 |
| 问题定位 | 手动分析 | AI 自动分析 |
| 跟踪管理 | 手动更新 | 自动跟踪 |

---

## 六、注意事项

1. **权限配置**：确保 Token 有足够的权限
2. **频率限制**：注意 API 调用频率限制
3. **敏感数据**：注意保护敏感错误信息

---

## 总结

通过 Sentry MCP，我们成功将 **错误监控和处理效率提升了 10+ 倍**，实现了从被动发现到主动预防的转变。

---

**相关资源**：

- Sentry 官方文档：https://docs.sentry.io/
- MCP 官方文档：https://modelcontextprotocol.io/

**标签**：#AI #MCP #Sentry #错误监控