# 一次需求引发的效率革命：用 GitHub MCP 实现自动化代码审查与 Issue 管理

> 一句话摘要：本文讲述我们如何利用 GitHub MCP 自动化完成代码审查、Issue 整理、PR 汇总等重复性工作，将原本需要人工跟踪的 GitHub 协作流程交给 AI 管理。

## 一、背景与问题

### 1.1 业务场景

有一次，团队需要**对代码仓库进行规范化管理**，具体包括：

1. 每天检查新提交的 PR（Pull Request）
2. 对 PR 进行初步代码审查，找出明显问题
3. 整理当天的 Issue（问题反馈）
4. 汇总每周的代码贡献情况
5. 定期清理已关闭的 Issue 和 PR

如果放在以前，我们可能需要：

1. 每天打开 GitHub 仓库页面
2. 逐个查看新提交的 PR
3. 手动检查代码规范
4. 逐个标签 Issue
5. 手动统计贡献数据

**这工作量，想想都头皮发麻。**

### 1.2 痛点分析

- **重复性高**：每天都要做同样的检查和整理
- **容易遗漏**：人工审查可能漏掉某些问题
- **效率低下**：即使只是初步审查，每个 PR 也需要 10-15 分钟

### 1.3 我们的需求

- **自动审查**：AI 自动检查 PR 中的代码规范问题
- **智能分类**：自动为 Issue 添加标签和分类
- **定时汇总**：每天/每周自动生成报告
- **流程自动化**：自动处理一些简单的协作流程

---

## 二、方案选型

### 2.1 什么是 GitHub MCP？

GitHub MCP 是一个 Model Context Protocol（MCP）服务器，它允许 AI 助手通过 GitHub API 操作仓库。换句话说，**你可以用自然语言指挥 AI 管理 GitHub 仓库**。

### 2.2 为什么选择它？

| 方案 | 优点 | 缺点 |
|------|------|------|
| 手动操作 | 无需技术准备 | 效率低、易遗漏 |
| GitHub Actions | 自动化程度高 | 需要编写 YAML 配置 |
| GitHub API + 脚本 | 灵活性高 | 需要编写代码 |
| **GitHub MCP** | **AI 直接控制、无需编写脚本** | **需要 MCP 环境** |

---

## 三、实现步骤

### 3.1 环境准备

首先，你需要安装 GitHub MCP。以下是安装命令：

```bash
# 使用 uvx 安装
uvx mcp-server-github
```

### 3.2 配置 MCP

在项目的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "github": {
      "command": "uvx",
      "args": ["mcp-server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token"
      }
    }
  }
}
```

### 3.3 配置 GitHub Token

1. 登录 GitHub：https://github.com/
2. 进入 Settings → Developer settings → Personal access tokens
3. 生成 Classic Token，需要以下权限：
   - `repo` - 完整仓库操作
   - `read:user` - 读取用户信息
   - `read:org` - 读取组织信息

### 3.4 自动化代码审查

配置完成后，你可以直接用自然语言指挥 AI。以下是我们当时使用的提示词：

```
请帮我完成以下任务：
1. 查看仓库的所有打开的 PR
2. 对每个 PR 进行初步审查，检查：
   - 代码是否符合项目规范
   - 是否有明显的安全问题
   - 是否有未解决的 TODO
   - 单元测试是否完整
3. 对每个 PR 给出审查意见，以评论形式提交
4. 汇总所有 PR 的审查结果
```

AI 会自动：

- 获取所有打开的 PR
- 读取 PR 中的代码变更
- 分析代码问题
- 提交审查评论
- 生成汇总报告

### 3.5 Issue 智能管理

```
请帮我完成以下任务：
1. 查看仓库的所有未处理 Issue
2. 对每个 Issue 进行分类：
   - Bug（bug 报告）
   - Feature（功能请求）
   - Question（问题咨询）
   - Documentation（文档相关）
3. 根据 Issue 内容自动添加合适的标签
4. 对于重复的 Issue，标记为 duplicate 并关联原 Issue
5. 汇总需要优先处理的问题
```

---

## 四、核心代码示例

虽然 MCP 可以用自然语言操作，但有些场景我们还是需要编写脚本。以下是一个使用 GitHub API 的示例：

```javascript
const axios = require('axios');

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const REPO_OWNER = 'your-owner';
const REPO_NAME = 'your-repo';

const api = axios.create({
  baseURL: 'https://api.github.com',
  headers: {
    Authorization: `token ${GITHUB_TOKEN}`,
    Accept: 'application/vnd.github.v3+json'
  }
});

// 获取所有打开的 PR
async function getOpenPRs() {
  const response = await api.get(`/repos/${REPO_OWNER}/${REPO_NAME}/pulls?state=open`);
  return response.data;
}

// 获取 PR 的文件变更
async function getPRFiles(prNumber) {
  const response = await api.get(
    `/repos/${REPO_OWNER}/${REPO_NAME}/pulls/${prNumber}/files`
  );
  return response.data;
}

// 添加审查评论
async function addReviewComment(prNumber, body) {
  const response = await api.post(
    `/repos/${REPO_OWNER}/${REPO_NAME}/issues/${prNumber}/comments`,
    { body }
  );
  return response.data;
}

// 自动化代码审查
async function autoReviewPR(pr) {
  const files = await getPRFiles(pr.number);
  
  const issues = [];
  
  for (const file of files) {
    // 检查文件大小
    if (file.additions > 500) {
      issues.push(`文件 ${file.filename} 变更过大（${file.additions} 行），建议拆分`);
    }
    
    // 检查是否包含敏感信息
    if (file.patch && file.patch.includes('password') || file.patch.includes('secret')) {
      issues.push(`文件 ${file.filename} 可能包含敏感信息，请检查`);
    }
    
    // 检查测试文件
    if (!file.filename.includes('.test.') && !file.filename.includes('.spec.')) {
      issues.push(`文件 ${file.filename} 缺少对应的测试文件`);
    }
  }
  
  // 提交审查意见
  if (issues.length > 0) {
    const comment = `## 🤖 AI 初步审查结果\n\n${issues.map(i => `- ${i}`).join('\n')}\n\n---\n*此评论由 AI 自动生成，仅供参考*`;
    await addReviewComment(pr.number, comment);
  }
  
  return issues;
}

// 批量审查所有 PR
async function batchReviewPRs() {
  const prs = await getOpenPRs();
  const results = [];
  
  for (const pr of prs) {
    console.log(`正在审查 PR #${pr.number}: ${pr.title}`);
    const issues = await autoReviewPR(pr);
    results.push({ pr: pr.number, issues });
  }
  
  return results;
}
```

---

## 五、效果对比

| 指标 | 手动操作 | MCP 自动化 |
|------|----------|------------|
| 10 个 PR 审查 | 2-3 小时 | 约 10 分钟 |
| Issue 分类 | 手动逐个标签 | 自动分类 |
| 报告生成 | 手动统计 | 自动生成 |
| 遗漏率 | 约 15% | 接近 0% |

---

## 六、更多应用场景

### 6.1 自动化周报生成

- 每周自动统计代码贡献
- 汇总 PR 合并情况
- 生成团队周报

### 6.2 Issue 自动回复

- 对新 Issue 进行初步回复
- 自动关联相关文档
- 引导用户补充信息

### 6.3 仓库健康度监控

- 监控仓库的活跃度
- 检测长期未处理的 Issue 和 PR
- 提醒维护者及时处理

---

## 七、注意事项与最佳实践

### 7.1 常见坑

1. **Token 权限**：确保 Token 有足够的权限操作仓库
2. **API 频率限制**：GitHub API 有调用次数限制，批量操作时注意控制
3. **审查质量**：AI 审查只是初步检查，不能替代人工审查

### 7.2 安全建议

- **敏感信息**：不要在代码中硬编码 Token，使用环境变量
- **权限最小化**：只给 MCP 必要的最小权限
- **审查日志**：记录 AI 的审查行为，便于审计

---

## 总结

通过 GitHub MCP，我们成功将 **每��的代码审查时间从 2 小时缩短到 10 分钟**，效率提升了 **12+ 倍**。

更重要的是，**AI 可以 24 小时不间断工作**，随时帮你监控仓库状态，让你不再错过任何重要的 PR 和 Issue。

如果你也有类似的 GitHub 协作管理需求，不妨试试 GitHub MCP。

---

**相关资源**：

- GitHub API 官方文档：https://docs.github.com/en/rest
- MCP 官方文档：https://modelcontextprotocol.io/
- GitHub MCP 仓库：https://github.com/anthropics/mcp-servers

**标签**：#AI #MCP #GitHub #自动化 #代码审查