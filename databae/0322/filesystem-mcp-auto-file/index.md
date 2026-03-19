# 一次需求引发的效率革命：用 Filesystem MCP 实现自动化文件处理与文档生成

> 一句话摘要：本文讲述我们如何利用 Filesystem MCP 自动化完成文件整理、代码文档生成、项目结构分析等重复性工作，将原本需要手动操作的文件管理交给 AI 完成。

## 一、背景与问题

### 1.1 业务场景

有一次，团队需要**对项目代码进行全面的文档整理**，具体包括：

1. 分析项目目录结构，生成架构文档
2. 为所有 API 接口生成 Markdown 文档
3. 提取代码中的注释，生成注释文档
4. 检查项目中未完成的 TODO 和 FIXME
5. 统一项目中的代码规范

如果放在以前，我们可能需要：

1. 手动遍历每个目录
2. 逐个文件读取和分析
3. 手动编写文档
4. 逐个检查 TODO 注释
5. 手动整理代码规范

**这工作量，想想都头皮发麻。**

### 1.2 痛点分析

- **重复性高**：每个项目都要做同样的整理工作
- **容易遗漏**：人工检查可能漏掉某些文件或 TODO
- **效率低下**：一个中型项目的文档整理可能需要 1-2 天

### 1.3 我们的需求

- **自动分析**：AI 自动分析项目结构和代码
- **智能文档生成**：自动生成 API 文档、注释文档
- **TODO 追踪**：自动收集所有 TODO 和 FIXME
- **规范检查**：自动检查代码规范问题

---

## 二、方案选型

### 2.1 什么是 Filesystem MCP？

Filesystem MCP 是一个 Model Context Protocol（MCP）服务器，它允许 AI 助手直接操作本地文件系统。换句话说，**你可以用自然语言指挥 AI 读写、搜索、分析本地文件**。

### 2.2 为什么选择它？

| 方案 | 优点 | 缺点 |
|------|------|------|
| 手动操作 | 无需技术准备 | 效率低、易遗漏 |
| 脚本工具 | 可定制 | 需要编写代码 |
| IDE 插件 | 集成方便 | 功能有限 |
| **Filesystem MCP** | **AI 直接控制、无需编写脚本** | **需要 MCP 环境** |

---

## 三、实现步骤

### 3.1 环境准备

首先，你需要安装 Filesystem MCP。以下是安装命令：

```bash
# 使用 uvx 安装
uvx mcp-server-filesystem
```

### 3.2 配置 MCP

在项目的 MCP 配置文件中添加：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "uvx",
      "args": ["mcp-server-filesystem", "/path/to/allowed/directory"]
    }
  }
}
```

### 3.3 配置可访问目录

出于安全考虑，Filesystem MCP 需要配置允许访问的目录。建议只配置项目根目录：

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "uvx",
      "args": [
        "mcp-server-filesystem",
        "./"
      ]
    }
  }
}
```

### 3.4 自动化项目分析

配置完成后，你可以直接用自然语言指挥 AI。以下是我们当时使用的提示词：

```
请帮我完成以下任务：
1. 分析当前项目的目录结构
2. 列出所有源代码文件（.js, .ts, .py, .go 等）
3. 统计每个目录的代码行数
4. 生成项目结构文档
```

AI 会自动：

- 遍历项目目录
- 统计文件和代码行数
- 生成结构化文档

### 3.5 自动化文档生成

```
请帮我完成以下任务：
1. 读取所有 API 相关文件（routes, controllers, api 目录）
2. 提取接口路径、请求方法、参数说明
3. 生成 API 文档（Markdown 格式）
4. 保存到 docs/api.md
```

---

## 四、核心代码示例

虽然 MCP 可以用自然语言操作，但有些场景我们还是需要编写脚本。以下是一个使用 Node.js 的示例：

```javascript
const fs = require('fs');
const path = require('path');

// 递归获取目录下的所有文件
function getAllFiles(dir, extensions = []) {
  const files = [];
  
  function traverse(currentPath) {
    const items = fs.readdirSync(currentPath);
    
    for (const item of items) {
      const fullPath = path.join(currentPath, item);
      const stat = fs.statSync(fullPath);
      
      if (stat.isDirectory()) {
        // 跳过 node_modules 等目录
        if (!['node_modules', '.git', 'dist', 'build'].includes(item)) {
          traverse(fullPath);
        }
      } else if (stat.isFile()) {
        // 根据扩展名过滤
        if (extensions.length === 0 || 
            extensions.some(ext => item.endsWith(ext))) {
          files.push(fullPath);
        }
      }
    }
  }
  
  traverse(dir);
  return files;
}

// 统计代码行数
function countLines(filePath) {
  const content = fs.readFileSync(filePath, 'utf-8');
  return content.split('\n').length;
}

// 生成项目结构文档
function generateProjectDoc(projectRoot) {
  const structure = {
    totalFiles: 0,
    totalLines: 0,
    byExtension: {},
    directories: []
  };
  
  const files = getAllFiles(projectRoot, ['.js', '.ts', '.py', '.go', '.java']);
  
  for (const file of files) {
    structure.totalFiles++;
    const lines = countLines(file);
    structure.totalLines += lines;
    
    const ext = path.extname(file);
    structure.byExtension[ext] = (structure.byExtension[ext] || 0) + 1;
  }
  
  return structure;
}

// 提取 TODO 和 FIXME
function extractTodos(projectRoot) {
  const files = getAllFiles(projectRoot, ['.js', '.ts', '.py', '.go', '.java']);
  const todos = [];
  
  for (const file of files) {
    const content = fs.readFileSync(file, 'utf-8');
    const lines = content.split('\n');
    
    lines.forEach((line, index) => {
      if (line.includes('TODO') || line.includes('FIXME')) {
        todos.push({
          file: path.relative(projectRoot, file),
          line: index + 1,
          content: line.trim()
        });
      }
    });
  }
  
  return todos;
}

// 生成 API 文档
function generateAPIDoc(apiDir) {
  if (!fs.existsSync(apiDir)) {
    return null;
  }
  
  const files = getAllFiles(apiDir, ['.js', '.ts']);
  let doc = '# API 文档\n\n';
  
  for (const file of files) {
    const content = fs.readFileSync(file, 'utf-8');
    const relativePath = path.relative(process.cwd(), file);
    
    doc += `## ${relativePath}\n\n`;
    
    // 简单的路由提取（实际使用中需要更复杂的解析）
    const routes = content.match(/@(Get|Post|Put|Delete|Patch)\s+(\/[^\s]+)/g);
    if (routes) {
      routes.forEach(route => {
        doc += `- ${route}\n`;
      });
    }
    
    doc += '\n';
  }
  
  return doc;
}
```

---

## 五、效果对比

| 指标 | 手动操作 | MCP 自动化 |
|------|----------|------------|
| 项目结构分析 | 1-2 小时 | 约 1 分钟 |
| API 文档生成 | 2-3 小时 | 约 5 分钟 |
| TODO 收集 | 30 分钟 | 约 30 秒 |
| 代码规范检查 | 1-2 小时 | 约 5 分钟 |

---

## 六、更多应用场景

### 6.1 自动化代码注释

- 扫描项目中的代码
- 识别函数和类
- 生成 JSDoc 风格的注释

### 6.2 项目健康度检查

- 检查依赖是否过期
- 检查是否有安全漏洞
- 检查代码复杂度

### 6.3 批量重命名和移动

- 根据规则批量重命名文件
- 自动整理项目结构
- 批量移动文件到对应目录

---

## 七、注意事项与最佳实践

### 7.1 常见坑

1. **目录权限**：确保 MCP 有权限访问项目目录
2. **大文件处理**：对于超大文件，可能需要分批处理
3. **编码问题**：注意文件的字符编码，建议统一使用 UTF-8

### 7.2 安全建议

- **敏感目录**：不要将 MCP 配置为可以访问��统敏感目录
- **只读操作**：大部分场景使用只读模式即可
- **操作日志**：记录文件操作日志，便于审计

---

## 总结

通过 Filesystem MCP，我们成功将 **项目文档整理从 2 天缩短到 30 分钟**，效率提升了 **60+ 倍**。

更重要的是，**AI 可以理解代码语义**，不仅能生成文档，还能帮你发现代码中的问题。

如果你也有类似的文件管理需求，不妨试试 Filesystem MCP。

---

**相关资源**：

- Filesystem MCP 官方文档：https://github.com/anthropics/mcp-servers
- MCP 官方文档：https://modelcontextprotocol.io/

**标签**：#AI #MCP #文件系统 #自动化 #文档生成