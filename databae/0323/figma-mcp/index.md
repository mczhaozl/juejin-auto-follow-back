# Figma MCP：用 AI 自动生成设计稿的黑科技

> 介绍 Figma MCP Server，让 Claude 直接操作 Figma

---

## 一、Figma MCP 是什么

Figma MCP Server 让 AI 能够：
- 读取 Figma 设计稿
- 提取设计元素
- 生成设计规范
- 自动创建组件

---

## 二、安装配置

```bash
npm install -g @figma/mcp-server
```

```json
{
  "mcpServers": {
    "figma": {
      "command": "figma-mcp",
      "env": {
        "FIGMA_TOKEN": "your-token"
      }
    }
  }
}
```

---

## 三、使用场景

### 1. 提取设计规范

```
请分析这个 Figma 文件的颜色规范
```

Claude 会自动读取并整理所有颜色。

### 2. 生成代码

```
请根据这个设计稿生成 React 组件
```

### 3. 设计审查

```
请检查这个设计是否符合无障碍标准
```

---

## 四、实战案例

### ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ?## ": {
    "primary": "#1890ff",
    "success": "#52c41a"
  },
  "fonts": {
    "base": "14px",
    "large": "16px"
  }
}
```

### 案例 2：组件文档生成

```
请为所有组件生成使用文档
```

---

## 总结

Figma MCP 让设计到开发的流程更加自动化，大幅提升效率。

如果这篇文章对你有帮助，欢迎点赞收藏！
