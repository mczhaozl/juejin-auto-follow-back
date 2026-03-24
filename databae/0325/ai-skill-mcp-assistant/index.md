# 每天一个 AI Skill：利用 MCP 快速搭建你的本地代码助手

> 想要让你的 AI 助手直接读取本地代码、运行终端命令甚至管理 GitHub Issue？本文带你从零开始利用 MCP（Model Context Protocol）协议，将你的 Claude 或 IDE 变身为全能的本地开发助手。

## 一、背景：为什么你需要 MCP？

在日常开发中，我们经常需要把代码复制粘贴给 AI，或者手动执行 AI 给出的命令。这种「人肉搬运」的方式效率极低。

**Model Context Protocol (MCP)** 是由 Anthropic 提出的一种开放标准，旨在让 AI 模型（如 Claude 3.5 Sonnet）能够安全、标准化地访问外部工具和数据源。

通过 MCP，你可以让你的 AI 助手：
- **读取本地文件**：直接分析你的整个项目目录。
- **执行终端命令**：让 AI 帮你跑测试、起服务。
- **调用第三方 API**：如 GitHub、Google Search、Notion 等。

## 二、从零开始：环境准备

在开始之前，请确保你已安装以下工具：
- **Claude Desktop** 或支持 MCP 的 IDE（如 Trae, Cursor, VS Code 等）。
- **Node.js** (推荐 v18+)：大部分 MCP Server 是基于 Node 编写的。

## 三、实战：安装你的第一个 MCP Server

### 1. 安装 Filesystem MCP
Filesystem MCP 是最基础的工具，允许 AI 安全地读写你指定的本地目录。

**步骤：**
1. 打开 Claude Desktop 的配置文件：
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`

2. 添加以下配置：
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "C:/path/to/your/projects"
      ]
    }
  }
}
```

### 2. 重启 Claude
重启后，你会发现对话框中多了一个「小锤子」图标。你可以尝试对 AI 说：
> "请分析我当前目录下的项目结构，并告诉我 main.js 实现了什么功能。"

## 四、进阶：组合多个 MCP 技能

你可以同时开启多个 MCP Server。例如，结合 **Brave Search** 和 **GitHub**：
- **Brave Search**: 让 AI 联网搜索最新的文档。
- **GitHub**: 让 AI 帮你提交 PR 或查看 Issue。

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": { "BRAVE_API_KEY": "YOUR_KEY_HERE" }
    }
  }
}
```

## 五、总结

MCP 协议的出现标志着 AI 助手从「对话框」走向了「工具箱」。通过简单的配置，你就能让 AI 拥有操作真实世界的能力。

**如果你觉得本文有用，欢迎点赞收藏！** 
下次我们将介绍如何编写你自己的自定义 MCP Server。
