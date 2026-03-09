# Chrome DevTools MCP Server 介绍

> 介绍 Chrome DevTools MCP Server，让 AI 助手能够直接操作浏览器进行调试、测试和自动化。

---

## 一、什么是 Chrome DevTools MCP Server

Chrome DevTools MCP Server 是一个 MCP（Model Context Protocol）服务器，它将 Chrome DevTools Protocol（CDP）的能力暴露给 AI 助手。

### 核心能力

- 控制浏览器：打开页面、点击、输入
- 调试网页：查看 DOM、Console、Network
- 截图录屏：捕获页面状态
- 性能分析：监控加载时间、资源使用
- 自动化测试：执行测试脚本

### 适用场景

- AI 辅助调试前端问题
- 自动化测试与验证
- 页面性能分析
- 网页内容抓取
- UI 自动化操作

## 二、快速开始

### 安装

```bash
# 使用 uvx（推荐）
uvx install chrome-devtools-mcp-server

# 或使用 npm
npm install -g chrome-devtools-mcp-server
```

### 配置 MCP

在 `.kiro/settings/mcp.json` 或 `~/.kiro/settings/mcp.json` 中添加：

```json
{
  "mcpServers": {
    "chrome-devtools": {
      "command": "uvx",
      "args": ["chrome-devtools-mcp-server"],
      "env": {
        "CHROME_PATH": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
      }
    }
  }
}
```

### 启动浏览器

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222

# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" \
  --remote-debugging-port=9222

# Linux
google-chrome --remote-debugging-port=9222
```

## 三、主要工具（Tools）

### 1. navigate - 导航到页面

```javascript
// AI 助手调用示例
{
  "tool": "navigate",
  "arguments": {
    "url": "https://example.com"
  }
}
```

### 2. screenshot - 截图

```javascript
{
  "tool": "screenshot",
  "arguments": {
    "selector": ".main-content", // 可选，截取特定元素
    "fullPage": true // 全页截图
  }
}
```

### 3. click - 点击元素

```javascript
{
  "tool": "click",
  "arguments": {
    "selector": "button.submit"
  }
}
```

### 4. fill - 填充表单

```javascript
{
  "tool": "fill",
  "arguments": {
    "selector": "input[name='email']",
    "value": "test@example.com"
  }
}
```

### 5. evaluate - 执行 JavaScript

```javascript
{
  "tool": "evaluate",
  "arguments": {
    "expression": "document.title"
  }
}
```

### 6. console_logs - 获取控制台日志

```javascript
{
  "tool": "console_logs",
  "arguments": {
    "level": "error" // 可选：log, warn, error
  }
}
```

### 7. network_logs - 获取网络请求

```javascript
{
  "tool": "network_logs",
  "arguments": {
    "filter": "xhr" // 可选：xhr, fetch, all
  }
}
```

### 8. get_dom - 获取 DOM 结构

```javascript
{
  "tool": "get_dom",
  "arguments": {
    "selector": ".container" // 可选，获取特定元素
  }
}
```

## 四、实战场景

### 场景 1：调试页面错误

```
用户：帮我看看这个页面有什么 JavaScript 错误

AI 助手：
1. navigate 到页面
2. console_logs 获取错误日志
3. 分析错误原因
4. 给出修复建议
```

### 场景 2：测试表单提交

```
用户：测试登录表单是否正常工作

AI 助手：
1. navigate 到登录页
2. fill 填充用户名和密码
3. click 提交按钮
4. 等待跳转
5. screenshot 截图验证
6. 返回测试结果
```

### 场景 3：性能分析

```
用户：分析首页加载性能

AI 助手：
1. navigate 到首页
2. network_logs 获取所有请求
3. 分析：
   - 总请求数
   - 最慢的请求
   - 资源大小
4. 给出优化建议
```

### 场景 4：UI 自动化

```
用户：帮我填写这个复杂表单

AI 助手：
1. navigate 到表单页
2. 依次 fill 各个字段
3. click 下拉选择
4. click 提交
5. screenshot 确认结果
```

## 五、与 Puppeteer/Playwright 对比

| 特性 | Chrome DevTools MCP | Puppeteer/Playwright |
|------|---------------------|----------------------|
| 使用方式 | AI 助手调用 | 编写代码 |
| 学习成本 | 低（自然语言） | 高（需要学 API） |
| 灵活性 | 中 | 高 |
| 适用场景 | 临时调试、快速验证 | 自动化测试、CI/CD |
| 维护成本 | 低 | 高 |

## 六、高级用法

### 1. 等待元素出现

```javascript
{
  "tool": "wait_for_selector",
  "arguments": {
    "selector": ".loading-complete",
    "timeout": 5000
  }
}
```

### 2. 模拟移动设备

```javascript
{
  "tool": "emulate_device",
  "arguments": {
    "device": "iPhone 12"
  }
}
```

### 3. 拦截网络请求

```javascript
{
  "tool": "intercept_request",
  "arguments": {
    "pattern": "*/api/*",
    "response": {
      "status": 200,
      "body": "{\"mock\": true}"
    }
  }
}
```

### 4. 执行复杂脚本

```javascript
{
  "tool": "evaluate",
  "arguments": {
    "expression": `
      const buttons = document.querySelectorAll('button');
      return Array.from(buttons).map(b => ({
        text: b.textContent,
        disabled: b.disabled
      }));
    `
  }
}
```

## 七、最佳实践

### 1. 明确描述需求

```
❌ 不好：测试一下这个页面
✅ 好：测试登录表单，用户名 test@example.com，密码 123456，验证是否跳转到首页
```

### 2. 分步骤操作

```
用户：帮我完成以下操作：
1. 打开 https://example.com
2. 点击"登录"按钮
3. 填写表单
4. 提交并截图
```

### 3. 处理异步操作

```
用户：点击按钮后等待 3 秒再截图（等待动画完成）
```

### 4. 错误处理

```
用户：如果找不到元素，尝试等待 5 秒后再试
```

## 八、常见问题

### 1. 连接不上浏览器

检查：

- 浏览器是否用 `--remote-debugging-port=9222` 启动
- 端口是否被占用
- 防火墙是否阻止

### 2. 元素选择器不准确

建议：

- 用唯一的 ID 或 class
- 用 data 属性：`[data-testid="submit"]`
- 避免用复杂的 CSS 选择器

### 3. 操作太快导致失败

解决：

- 加 wait_for_selector
- 用 setTimeout 延迟
- 等待网络请求完成

### 4. 截图不完整

解决：

- 用 `fullPage: true`
- 等待页面加载完成
- 滚动到目标元素

## 九、安全注意事项

### 1. 不要在生产环境使用

远程调试端口会暴露浏览器控制权，仅在开发/测试环境使用。

### 2. 保护敏感信息

```javascript
// ❌ 不要在日志中暴露密码
fill("input[type='password']", "mypassword")

// ✅ 用占位符
fill("input[type='password']", "[REDACTED]")
```

### 3. 限制访问权限

```json
{
  "env": {
    "ALLOWED_ORIGINS": "http://localhost:*"
  }
}
```

## 十、与其他 MCP Server 配合

### 与 Filesystem MCP 配合

```
用户：截图保存到项目的 screenshots 目录

AI 助手：
1. chrome-devtools: screenshot
2. filesystem: write_file("screenshots/page.png", imageData)
```

### 与 GitHub MCP 配合

```
用户：测试 PR 的改动是否正常

AI 助手：
1. github: 获取 PR 改动的页面
2. chrome-devtools: 打开页面测试
3. github: 在 PR 中评论测试结果
```

## 总结

Chrome DevTools MCP Server 的价值：

- 让 AI 助手能直接操作浏览器
- 降低自动化测试门槛（自然语言描述即可）
- 快速验证前端问题
- 适合临时调试和快速测试

适用场景：

- 开发时快速验证功能
- 调试难以复现的问题
- 演示和教学
- 简单的自动化任务

不适用场景：

- 复杂的 E2E 测试（用 Playwright）
- CI/CD 流程（用专业测试框架）
- 生产环境监控

配合 AI 助手使用，能大幅提升前端开发和调试效率。
