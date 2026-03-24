# 每天一个 AI Skill：如何编写并部署你的第一个自定义 MCP Server

> 掌握了如何使用现成的 MCP Server 后，下一步就是根据自己的业务需求编写自定义工具。本文将带你使用 Node.js 从零实现一个简单的 MCP Server，并将其集成到 Claude 中。

## 一、背景：为什么需要自定义 MCP？

虽然社区已经提供了很多 MCP Server，但在实际工作中，你可能需要：
- **访问公司内部 API**：例如查询内部的排期系统或文档库。
- **操作特定的本地工具**：例如自动触发某个特定的脚本或编译流程。
- **集成私有数据源**：例如读取特定的日志文件格式。

## 二、核心概念：MCP 的工作方式

MCP (Model Context Protocol) 采用了典型的客户端-服务器架构：
- **Client**: 如 Claude Desktop 或 IDE，负责与用户交互并向 Server 发送指令。
- **Server**: 你的自定义程序，负责执行具体任务并返回数据。
- **Transport**: 通信协议，通常使用标准输入输出 (Stdio)。

## 三、快速上手：使用 Node.js 编写

我们将编写一个简单的「天气查询」工具。

### 1. 初始化项目
```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk
```

### 2. 编写核心代码 (index.js)
```javascript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new Server({
  name: "my-weather-server",
  version: "1.0.0"
}, {
  capabilities: { tools: {} }
});

// 定义工具
server.setRequestHandler("listTools", async () => ({
  tools: [{
    name: "get_weather",
    description: "获取指定城市的当前天气",
    inputSchema: {
      type: "object",
      properties: {
        city: { type: "string", description: "城市名称" }
      },
      required: ["city"]
    }
  }]
}));

// 执行逻辑
server.setRequestHandler("callTool", async (request) => {
  if (request.params.name === "get_weather") {
    const { city } = request.params.arguments;
    return {
      content: [{ type: "text", text: `${city} 的天气是：晴朗，25度。` }]
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

## 四、部署与集成

1. **打包项目**：确保 `package.json` 中设置了 `"type": "module"`。
2. **配置 Claude**：在 `claude_desktop_config.json` 中添加：
```json
{
  "mcpServers": {
    "my-weather": {
      "command": "node",
      "args": ["C:/path/to/my-mcp-server/index.js"]
    }
  }
}
```
3. **测试**：重启 Claude，询问「北京天气怎么样？」。

## 五、总结

编写自定义 MCP Server 并不复杂，关键在于定义好 `inputSchema`，让 AI 明白什么时候该调用你的工具。

**下期预告：如何让你的 MCP Server 拥有长久记忆？**
