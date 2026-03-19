# 一次需求引发的效率革命：用飞书文档 MCP 实现自动化文档管理

> 一句话摘要：本文讲述我们如何利用飞书文档 MCP 自动化完成周报汇总、文档同步、团队知识库维护等重复性工作，将原本需要手动复制粘贴的文档操作交给 AI 完成。

## 一、背景与问题

### 1.1 业务场景

有一次，团队需要**每周汇总各成员的周报**，并统一整理到公司的知识库中。具体流程是：

1. 每周五下午，团队成员在飞书文档中填写周报
2. 管理员需要逐个打开每个成员的周报文档
3. 复制内容到一个汇总文档中
4. 格式调整、排版美化
5. 发布到团队知识库

**每个周五，我们都要花 1-2 小时做这件事。**

### 1.2 痛点分析

- **重复性高**：每周同样的流程，只是内容不同
- **容易出错**：手动复制粘贴可能出现遗漏或格式错乱
- **时效性差**：手动汇总需要时间，周报往往要等到下周一才能发布

### 1.3 我们的需求

- **自动汇总**：AI 自动读取各成员的周报文档
- **格式统一**：自动按照预设模板格式化
- **定时执行**：每周五自动执行，无需人工触发
- **通知提醒**：汇总完成后自动通知相关人员

---

## 二、方案选型

### 2.1 什么是飞书文档 MCP？

飞书文档 MCP 是一个 Model Context Protocol（MCP）服务器，它允许 AI 助手通过飞书开放 API 操作飞书文档。换句话说，**你可以用自然语言指挥 AI 管理飞书文档**。

### 2.2 为什么选择它？

| 方案 | 优点 | 缺点 |
|------|------|------|
| 手动复制粘贴 | 无需技术准备 | 效率低、易出错 |
| 飞书开放 API | 功能强大 | 需要编写代码、配置复杂 |
| 飞书机器人 | 可实现部分自动化 | 功能有限 |
| **飞书文档 MCP** | **AI 直接控制文档、无需编写脚本** | **需要 MCP 环境** |

---

## 三、实现步骤

### 3.1 环境准备

首先，你需要安装飞书文档 MCP。以下是安装命令：

```bash
# 使用 uvx 安装
uvx mcp-server-feishu
```

### 3.2 配置 MCP

在项目的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "feishu": {
      "command": "uvx",
      "args": ["mcp-server-feishu"],
      "env": {
        "FEISHU_APP_ID": "your_app_id",
        "FEISHU_APP_SECRET": "your_app_secret"
      }
    }
  }
}
```

### 3.3 配置飞书开放平台

1. 登录飞书开放平台：https://open.feishu.cn/
2. 创建企业自建应用
3. 获取 App ID 和 App Secret
4. 添加权限：
   - `doc:readonly` - 读取文档
   - `doc:write` - 写入文档
   - `drive:readonly` - 读取云盘文件

### 3.4 自动化周报汇总

配置完成后，你可以直接用自然语言指挥 AI。以下是我们当时使用的提示词：

```
请帮我完成以下任务：
1. 读取「周报文件夹」中所有本周更新的周报文档
2. 提取每个成员的周报内容（格式：姓名 + 本周工作 + 下周计划）
3. 按照模板格式汇总到一个新文档中
4. 文档标题格式：2024年XX月第XX周周报汇总
5. 汇总完成后，在团队群里发送通知
```

AI 会自动：

- 扫描周报文件夹
- 读取每个文档内容
- 按模板格式化
- 创建汇总文档
- 发送通知

### 3.5 定时执行配置

可以使用 cron 定时任务或 GitHub Actions 定时触发：

```yaml
# .github/workflows/weekly-report.yml
name: Weekly Report Automation
on:
  schedule:
    - cron: '0 9 * * 5'  # 每周五上午 9 点执行
```

---

## 四、核心代码示例

虽然 MCP 可以用自然语言操作，但有些场景我们还是需要编写脚本。以下是一个使用飞书 API 的示例：

```javascript
const axios = require('axios');

const APP_ID = process.env.FEISHU_APP_ID;
const APP_SECRET = process.env.FEISHU_APP_SECRET;

// 获取 access_token
async function getAccessToken() {
  const response = await axios.post(
    'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal',
    { app_id: APP_ID, app_secret: APP_SECRET }
  );
  return response.data.tenant_access_token;
}

// 读取文档内容
async function getDocumentContent(token, documentId) {
  const response = await axios.get(
    `https://open.feishu.cn/open-apis/doc/v1/documents/${documentId}`,
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return response.data.data.content;
}

// 创建新文档
async function createDocument(token, title, content) {
  const response = await axios.post(
    'https://open.feishu.cn/open-apis/doc/v1/documents',
    {
      document: {
        title,
        content: [
          {
            tag: 'text',
            text: content
          }
        ]
      }
    },
    { headers: { Authorization: `Bearer ${token}` } }
  );
  return response.data.data.document_id;
}

// 批量读取周报并汇总
async function weeklyReportSummary(folderId) {
  const token = await getAccessToken();
  
  // 1. 获取文件夹中的文档列表
  const docs = await getFolderDocuments(token, folderId);
  
  // 2. 读取每个文档内容
  const reports = [];
  for (const doc of docs) {
    const content = await getDocumentContent(token, doc.id);
    reports.push({ name: doc.name, content });
  }
  
  // 3. 汇总成新文档
  const summary = reports.map(r => `## ${r.name}\n\n${r.content}`).join('\n\n---\n\n');
  const summaryDocId = await createDocument(token, `周报汇总-${Date.now()}`, summary);
  
  return summaryDocId;
}
```

---

## 五、效果对比

| 指标 | 手动操作 | MCP 自动化 |
|------|----------|------------|
| 10 人周报汇总 | 1-2 小时 | 约 2 分钟 |
| 格式一致性 | 依赖人工 | 模板统一 |
| 及时性 | 下周一发布 | 当天完成 |
| 错误率 | 约 10% | 接近 0% |

---

## 六、更多应用场景

### 6.1 知识库自动同步

- 当 GitHub 有新文档更新时，自动同步到飞书知识库
- 当飞书文档更新时，自动提交到代码仓库

### 6.2 会议纪要自动整理

- AI 自动读取会议录音转文字
- 自动提取关键结论和待办事项
- 生成结构化会议纪要

### 6.3 团队规范文档维护

- 当团队规范更新时，自动通知所有成员
- 自动检查文档格式是否符合规范

---

## 七、注意事项与最佳实践

### 7.1 常见坑

1. **权限配置**：一定要确保 MCP 应用有足够的权限访问文档
2. **频率限制**：飞书 API 有调用频率限制，批量操作时注意控制并发
3. **文档格式**：飞书文档格式比较复杂，建议先用 API 读取简单文本内容

### 7.2 安全建议

- **敏感信息**：不要在 MCP 配置中直接写明文密钥，使用环境变量
- **权限最小化**：只给 MCP 应用必要的最小权限
- **日志审计**：记录 MCP 的操作日志，便于问题排查

---

## 总结

通过飞书文档 MCP，我们成功将 **每周的周报汇总从 2 小时缩短到 2 分钟**，效率提升了 **60+ 倍**。

更重要的是，**AI 不会疲劳，不会遗漏，永远按照模板执行**。这让我们可以专注于更有价值的工作。

如果你也有类似的飞书文档管理需求，不妨试试飞书文档 MCP。

---

**相关资源**：

- 飞书开放平台：https://open.feishu.cn/
- 飞书文档 API：https://open.feishu.cn/document/ukTMukTMukTM/uADOwUjLwgDM14CM4ATN
- MCP 官方文档：https://modelcontextprotocol.io/

**标签**：#AI #MCP #飞书 #自动化 #效率提升