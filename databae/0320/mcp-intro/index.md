# MCP 协议入门：让 AI 连接你的数据和工具

> Model Context Protocol 完全指南，从概念到实战

---

## 一、MCP 是什么

MCP（Model Context Protocol）是 Anthropic 推出的开放协议，让 AI 助手能够安全地连接外部数据源和工具。

### 解决的问题

传统 AI 助手的局限：
- 无法访问本地文件
- 无法连接数据库
- 无法调用 API
- 上下文有限

MCP 让 AI 能够：
- 读取本地文件系统
- 查询数据库
- 调用第三方 API
- 访问企业内部系统

---

## 二、核心概念

### 1. MCP Server

提供资源和工具的服务端。

```typescript
// 一个简单的 MCP Server
import { Server } from '@modelcontextprotocol/sdk/server/index.js';

const server = new Server({
  name: 'my-server',
  version: '1.0.0',
});

// 注册工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'get_weather',
      description: '获取天气信息',
      inputSchema: {
        type: 'object',
        properties: {
          city: { type: 'string' }
        }
      }
    }
  ]
}));
```

### 2. MCP Client

使用 MCP Server 的客户端（如 Claude Desktop）。

### 3. Resources

MCP Server 提供的数据资源。

```typescript
// 提供文件资源
server.setRequestHandler(ListResourcesRequestSchema, async () => ({
  resources: [
    {
      uri: 'file:///path/to/file.txt',
      name: 'My File',
      mimeType: 'text/plain'
    }
  ]
}));
```

### 4. Tools

MCP Server 提供的可执行工具。

```typescript
// 执行工具
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'get_weather') {
    const { city } = request.params.arguments;
    const weather = await fetchWeather(city);
    return {
      content: [
        {
          type: 'text',
          text: `${city} 的天气：${weather}`
        }
      ]
    };
  }
});
```

---

## 三、快速开始

### 安装 Claude Desktop

1. 下载 Claude Desktop
2. 配置 MCP Server

### 配置文件

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/username/Documents"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

### 使用

在 Claude Desktop 中：
```
请帮我读取 Documents 目录下的 README.md 文件
```

Claude 会自动调用 filesystem MCP Server 读取文件。

---

## 四、官方 MCP Servers

### 1. Filesystem

访问本地文件系统。

```bash
npx -y @modelcontextprotocol/server-filesystem /path/to/directory
```

功能：
- 读取文件
- 列出目录
- 搜索文件

### 2. GitHub

访问 GitHub 仓库。

```bash
npx -y @modelcontextprotocol/server-github
```

功能：
- 读取仓库文件
- 创建 Issue
- 提交 PR
- 搜索代码

### 3. PostgreSQL

连接 PostgreSQL 数据库。

```bash
npx -y @modelcontextprotocol/server-postgres postgresql://user:pass@localhost/db
```

功能：
- 执行 SQL 查询
- 列出表结构
- 查看数据

### 4. Puppeteer

浏览器自动化。

```bash
npx -y @modelcontextprotocol/server-puppeteer
```

功能：
- 截图
- 抓取网页
- 填写表单

---

## 五、实战案例

### 案例 1：本地文档助手

```json
{
  "mcpServers": {
    "docs": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/docs"]
    }
  }
}
```

使用：
```
请总结 docs/project-plan.md 的内容
```

### 案例 2：GitHub 代码审查

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "ghp_xxx"
      }
    }
  }
}
```

使用：
```
请审查 myrepo 最新的 PR
```

### 案例 3：数据库查询助手

```json
{
  "mcpServers": {
    "db": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost/mydb"]
    }
  }
}
```

使用：
```
查询用户表中注册时间最近的 10 个用户
```

---

## 六、MCP 的优势

### 1. 安全性

- 明确的权限控制
- 沙箱隔离
- 用户授权

### 2. 标准化

- 统一的协议
- 跨平台支持
- 易于集成

### 3. 可扩展

- 自定义 Server
- 插件生态
- 社区贡献

---

## 七、与其他方案对比

| 特性 | MCP | Function Calling | Plugins |
|------|-----|------------------|---------|
| 标准化 | ✅ 开放协议 | ⚠️ 各家不同 | ⚠️ 平台绑定 |
| 安全性 | ✅ 沙箱隔离 | ⚠️ 依赖实现 | ⚠️ 依赖平台 |
| 本地数据 | ✅ 支持 | ❌ 不支持 | ❌ 不支持 |
| 自定义 | ✅ 容易 | ⚠️ 复杂 | ❌ 受限 |

---

## 八、社区 MCP Servers

### 热门 Servers

1. **Notion MCP**：访问 Notion 数据库
2. **Slack MCP**：发送消息、查询历史
3. **Jira MCP**：管理任务和 Issue
4. **Google Drive MCP**：访问云端文件
5. **Figma MCP**：读取设计稿

### 查找更多

- GitHub: `awesome-mcp-servers`
- MCP 官方目录
- 社区论坛

---

## 九、开发建议

### 1. 从简单开始

先使用官方 Servers，熟悉 MCP 工作流程。

### 2. 明确需求

确定需要连接什么数据源或工具。

### 3. 安全第一

- 不要暴露敏感信息
- 使用环境变量存储密钥
- 限制访问权限

### 4. 测试充分

在 Claude Desktop 中充分测试。

---

## 十、未来展望

MCP 正在快速发展：

- 更多官方 Servers
- 更好的开发工具
- 更广泛的应用支持
- 企业级功能

---

## 总结

MCP 是 AI 助手连接外部世界的标准协议，它：

- 让 AI 能访问本地数据
- 提供统一的工具调用接口
- 安全可控
- 易于扩展

现在就开始使用 MCP，让你的 AI 助手更强大！

如果这篇文章对你有帮助，欢迎点赞收藏！
