# 从零实现一个 MCP Server：打造你的专属 AI 工具

> 手把手教你开发 MCP Server，让 Claude 调用你的 API

---

## 一、项目初始化

### 创建项目

```bash
mkdir my-mcp-server
cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk
npm install -D typescript @types/node
```

### TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "Node16",
    "moduleResolution": "Node16",
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true
  }
}
```

---

## 二、基础 Server

### 创建 Server

```typescript
// src/index.ts
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';

const server = new Server(
  {
    name: 'my-mcp-server',
    version: '1.0.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 列出工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'hello',
      description: '打招呼',
      inputSchema: {
        type: 'object',
        properties: {
          name: {
            type: 'string',
            description: '名字',
          },
        },
        required: ['name'],
      },
    },
  ],
}));

// 执行工具
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'hello') {
    const { name } = request.params.arguments as { name: string };
    return {
      content: [
        {
          type: 'text',
          text: `Hello, ${name}!`,
        },
      ],
    };
  }
  
  throw new Error(`Unknown tool: ${request.params.name}`);
});

// 启动 Server
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error('MCP Server running on stdio');
}

main().catch(console.error);
```

---

## 三、实战：天气查询 Server

### 安装依赖

```bash
npm install axios
```

### 实现天气查询

```typescript
import axios from 'axios';

interface WeatherTool {
  name: 'get_weather';
  arguments: {
    city: string;
  };
}

// 注册工具
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'get_weather',
      description: '获取城市天气信息',
      inputSchema: {
        type: 'object',
        properties: {
          city: {
            type: 'string',
            description: '城市名称，如：北京、上海',
          },
        },
        required: ['city'],
      },
    },
  ],
}));

// 执行工具
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'get_weather') {
    const { city } = request.params.arguments as WeatherTool['arguments'];
    
    try {
      // 调用天气 API
      const response = await axios.get(
        `https://api.weatherapi.com/v1/current.json`,
        {
          params: {
            key: process.env.WEATHER_API_KEY,
            q: city,
            lang: 'zh',
          },
        }
      );
      
      const { current, location } = response.data;
      
      return {
        content: [
          {
            type: 'text',
            text: `${location.name} 当前天气：
温度：${current.temp_c}°C
体感温度：${current.feelslike_c}°C
天气：${current.condition.text}
湿度：${current.humidity}%
风速：${current.wind_kph} km/h`,
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `获取天气失败：${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
  
  throw new Error(`Unknown tool: ${request.params.name}`);
});
```

---

## 四、添加 Resources

Resources 让 AI 能读取数据。

```typescript
import { 
  ListResourcesRequestSchema,
  ReadResourceRequestSchema,
} from '@modelcontextprotocol/sdk/types.js';
import fs from 'fs/promises';
import path from 'path';

// 列出资源
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  const files = await fs.readdir('./data');
  
  return {
    resources: files.map(file => ({
      uri: `file:///${path.join(process.cwd(), 'data', file)}`,
      name: file,
      mimeType: 'text/plain',
      description: `数据文件：${file}`,
    })),
  };
});

// 读取资源
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const url = new URL(request.params.uri);
  const filePath = url.pathname;
  
  try {
    const content = await fs.readFile(filePath, 'utf-8');
    
    return {
      contents: [
        {
          uri: request.params.uri,
          mimeType: 'text/plain',
          text: content,
        },
      ],
    };
  } catch (error) {
    throw new Error(`Failed to read file: ${error.message}`);
  }
});
```

---

## 五、配置 Claude Desktop

### 编译项目

```bash
npx tsc
```

### 配置文件

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["/path/to/my-mcp-server/dist/index.js"],
      "env": {
        "WEATHER_API_KEY": "your-api-key"
      }
    }
  }
}
```

### 重启 Claude Desktop

配置生效后，在 Claude 中测试：

```
请查询北京的天气
```

---

## 六、进阶：数据库查询 Server

```typescript
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'query_database',
      description: '执行 SQL 查询',
      inputSchema: {
        type: 'object',
        properties: {
          sql: {
            type: 'string',
            description: 'SQL 查询语句',
          },
        },
        required: ['sql'],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === 'query_database') {
    const { sql } = request.params.arguments as { sql: string };
    
    // 安全检查：只允许 SELECT
    if (!sql.trim().toLowerCase().startsWith('select')) {
      return {
        content: [
          {
            type: 'text',
            text: '只允许执行 SELECT 查询',
          },
        ],
        isError: true,
      };
    }
    
    try {
      const result = await pool.query(sql);
      
      return {
        content: [
          {
            type: 'text',
            text: JSON.stringify(result.rows, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: 'text',
            text: `查询失败：${error.message}`,
          },
        ],
        isError: true,
      };
    }
  }
});
```

---

## 七、错误处理

### 统一错误处理

```typescript
class MCPError extends Error {
  constructor(
    message: string,
    public code: string,
    public details?: any
  ) {
    super(message);
    this.name = 'MCPError';
  }
}

// 包装工具执行
async function executeTool(name: string, args: any) {
  try {
    // 执行工具逻辑
    return await toolHandlers[name](args);
  } catch (error) {
    if (error instanceof MCPError) {
      return {
        content: [
          {
            type: 'text',
            text: `错误 [${error.code}]: ${error.message}`,
          },
        ],
        isError: true,
      };
    }
    
    throw error;
  }
}
```

---

## 八、测试

### 单元测试

```typescript
import { describe, it, expect } from 'vitest';

describe('Weather Tool', () => {
  it('should return weather data', async () => {
    const result = await executeTool('get_weather', { city: '北京' });
    
    expect(result.content[0].text).toContain('温度');
    expect(result.content[0].text).toContain('°C');
  });
  
  it('should handle invalid city', async () => {
    const result = await executeTool('get_weather', { city: 'InvalidCity123' });
    
    expect(result.isError).toBe(true);
  });
});
```

---

## 九、发布

### 发布到 npm

```json
// package.json
{
  "name": "@yourname/mcp-weather",
  "version": "1.0.0",
  "bin": {
    "mcp-weather": "./dist/index.js"
  },
  "files": ["dist"]
}
```

```bash
npm publish
```

### 使用

```json
{
  "mcpServers": {
    "weather": {
      "command": "npx",
      "args": ["-y", "@yourname/mcp-weather"]
    }
  }
}
```

---

## 十、最佳实践

### 1. 安全性

- 验证输入参数
- 限制权限范围
- 使用环境变量存储密钥

### 2. 性能

- 缓存频繁请求
- 设置超时
- 限流

### 3. 可维护性

- 清晰的工具描述
- 完善的错误信息
- 详细的日志

### 4. 用户体验

- 友好的错误提示
- 合理的默认值
- 丰富的示例

---

## 总结

开发 MCP Server 的关键步骤：

1. 初始化项目和依赖
2. 实现工具和资源
3. 配置 Claude Desktop
4. 测试和调试
5. 发布和分享

现在你可以创建自己的 MCP Server，让 AI 连接任何数据和工具！

如果这篇文章对你有帮助，欢迎点赞收藏！
