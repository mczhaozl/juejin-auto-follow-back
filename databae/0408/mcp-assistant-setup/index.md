# MCP 本地代码助手搭建指南：利用 Model Context Protocol 快速构建AI开发环境

> 手把手教你搭建基于 MCP 的本地代码助手，连接 Cursor、Claude Desktop 等工具，大幅提升开发效率。

## 一、什么是 MCP

**MCP (Model Context Protocol)** 是一个开放协议，允许 AI 助手安全地与本地资源交互。

### 1.1 MCP 核心概念

```
┌─────────────┐     MCP      ┌─────────────┐
│   AI 助手   │◄────────────►│  MCP Server │
│ (Cursor/    │              │ (本地服务)   │
│  Claude)    │              │             │
└─────────────┘              └─────────────┘
        │                            │
        │                            ▼
        │                    ┌─────────────┐
        │                    │ 本地资源    │
        └───────────────────►│ 文件/API/   │
                            │ 数据库/终端  │
                            └─────────────┘
```

### 1.2 MCP 能做什么

- 读写本地文件
- 执行终端命令
- 访问 GitHub API
- 查询数据库
- 浏览网页
- 发送通知

## 二、环境准备

### 2.1 安装 Node.js

```bash
# 检查版本
node --version  # >= 18
npm --version
```

### 2.2 安装 Cursor 或 Claude Desktop

- **Cursor**: https://cursor.sh
- **Claude Desktop**: https://claude.ai/desktop

## 三、快速开始

### 3.1 创建项目

```bash
mkdir my-mcp-assistant
cd my-mcp-assistant
npm init -y
```

### 3.2 安装 MCP SDK

```bash
npm install @modelcontextprotocol/sdk
```

### 3.3 创建第一个 MCP Server

```javascript
// server.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  CallToolRequestSchema, 
  ListResourcesRequestSchema, 
  ListToolsRequestSchema 
} from '@modelcontextprotocol/sdk/types.js';

const server = new Server({
  name: 'my-first-mcp',
  version: '1.0.0'
}, {
  capabilities: {
    tools: {},
    resources: {}
  }
});

// 定义工具
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'echo',
        description: 'Echo back the input text',
        inputSchema: {
          type: 'object',
          properties: {
            text: { type: 'string', description: 'Text to echo' }
          },
          required: ['text']
        }
      },
      {
        name: 'get_date',
        description: 'Get current date and time',
        inputSchema: {
          type: 'object',
          properties: {}
        }
      }
    ]
  };
});

// 处理工具调用
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === 'echo') {
    return {
      content: [
        { type: 'text', text: args.text }
      ]
    };
  }
  
  if (name === 'get_date') {
    return {
      content: [
        { type: 'text', text: new Date().toISOString() }
      ]
    };
  }
  
  throw new Error(`Unknown tool: ${name}`);
});

// 启动服务器
const transport = new StdioServerTransport();
await server.connect(transport);
```

### 3.4 运行测试

```bash
node server.js
```

## 四、连接 AI 助手

### 4.1 配置 Cursor

1. 打开 Cursor 设置
2. 找到 `mcp.json` 配置文件
3. 添加配置：

```json
{
  "mcpServers": {
    "my-first-mcp": {
      "command": "node",
      "args": ["/path/to/your/server.js"]
    }
  }
}
```

### 4.2 配置 Claude Desktop

1. 找到配置文件：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%/Claude/claude_desktop_config.json`

2. 添加相同配置

### 4.3 使用

在 AI 助手的对话中：

```
请调用 echo 工具，传入文本 "Hello MCP!"
```

## 五、实战：文件系统 MCP

### 5.1 创建文件操作 Server

```javascript
// file-server.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import fs from 'fs/promises';
import path from 'path';

const server = new Server({
  name: 'file-operations',
  version: '1.0.0'
}, {
  capabilities: { tools: {} }
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'read_file',
      description: 'Read contents of a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'File path to read' }
        },
        required: ['path']
      }
    },
    {
      name: 'write_file',
      description: 'Write content to a file',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'File path to write' },
          content: { type: 'string', description: 'Content to write' }
        },
        required: ['path', 'content']
      }
    },
    {
      name: 'list_directory',
      description: 'List files in a directory',
      inputSchema: {
        type: 'object',
        properties: {
          path: { type: 'string', description: 'Directory path' }
        },
        required: ['path']
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  try {
    if (name === 'read_file') {
      const content = await fs.readFile(args.path, 'utf-8');
      return { content: [{ type: 'text', text: content }] };
    }
    
    if (name === 'write_file') {
      await fs.writeFile(args.path, args.content, 'utf-8');
      return { content: [{ type: 'text', text: 'File written successfully' }] };
    }
    
    if (name === 'list_directory') {
      const files = await fs.readdir(args.path);
      return { content: [{ type: 'text', text: files.join('\n') }] };
    }
  } catch (error) {
    return { content: [{ type: 'text', text: `Error: ${error.message}` }] };
  }
  
  throw new Error(`Unknown tool: ${name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## 六、实战：GitHub MCP

### 6.1 安装 GitHub MCP

```bash
npx @modelcontextprotocol/server-github
```

### 6.2 配置

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_TOKEN": "your-token-here"
      }
    }
  }
}
```

### 6.3 可用工具

- 搜索仓库
- 获取 Issue
- 创建/更新文件
- 提交代码

## 七、实战：终端 MCP

### 7.1 创建终端 Server

```javascript
// terminal-server.js
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const server = new Server({
  name: 'terminal',
  version: '1.0.0'
}, {
  capabilities: { tools: {} }
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'run_command',
      description: 'Run a terminal command',
      inputSchema: {
        type: 'object',
        properties: {
          command: { type: 'string', description: 'Command to run' },
          cwd: { type: 'string', description: 'Working directory' }
        },
        required: ['command']
      }
    }
  ]
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === 'run_command') {
    try {
      const { stdout, stderr } = await execAsync(args.command, {
        cwd: args.cwd || process.cwd()
      });
      return { 
        content: [{ 
          type: 'text', 
          text: stdout || stderr 
        }] 
      };
    } catch (error) {
      return { 
        content: [{ 
          type: 'text', 
          text: `Error: ${error.message}` 
        }] 
      };
    }
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## 八、MCP 最佳实践

### 8.1 安全建议

1. **不要暴露敏感信息**
2. **使用环境变量存储密钥**
3. **限制文件访问范围**

### 8.2 性能优化

```javascript
// 添加缓存
const cache = new Map();

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const cacheKey = JSON.stringify(request.params);
  
  if (cache.has(cacheKey)) {
    return cache.get(cacheKey);
  }
  
  const result = await processRequest(request);
  cache.set(cacheKey, result);
  return result;
});
```

### 8.3 错误处理

```javascript
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  try {
    return await processRequest(request);
  } catch (error) {
    return {
      content: [{ type: 'text', text: `Error: ${error.message}` }],
      isError: true
    };
  }
});
```

## 九、总结

MCP 让 AI 助手真正具备了「动手能力」：

1. **标准化协议**：跨工具、跨平台
2. **本地运行**：数据不外泄
3. **可扩展**：自定义 Server 简单
4. **生态丰富**：已有大量现成 Server

现在就开始搭建你的本地 AI 开发助手吧！

---

**推荐阅读**：
- [MCP 官方文档](https://modelcontextprotocol.io)
- [MCP Server 示例](https://github.com/modelcontextprotocol/servers)

**如果对你有帮助，欢迎点赞收藏！**
