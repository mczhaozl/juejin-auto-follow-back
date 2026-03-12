# AI 世界的新黑话：Skills、MCP、Projects、Prompts 一文看懂

> 2026 年的 AI 开发，不懂这些术语你就out了。从 Prompt 到 Skill，从 MCP 到 Projects，这篇文章带你搞懂 AI 工具链的新概念。

---

## 一、AI 开发的「黑话」越来越多

上周参加技术分享会，听到这样的对话：

> A: "你用 MCP 了吗？"  
> B: "用了，配合 Skill 效果很好。"  
> A: "Projects 呢？"  
> B: "也在用，比 Prompt 方便多了。"

我一脸懵：MCP 是什么？Skill 又是什么？Projects 和 Prompt 有什么区别？

作为一个用了两年 AI 编程工具的老用户，我发现自己跟不上时代了。

于是花了一周时间研究，终于搞懂了这些新概念。今天就来聊聊 AI 开发的「新黑话」。

## 二、Prompt：AI 的「说明书」

### 2.1 什么是 Prompt？

Prompt 就是你给 AI 的指令，告诉它你想要什么。

```
# 简单 Prompt
帮我写一个 React 组件

# 复杂 Prompt
你是一个资深的 React 开发者，精通 TypeScript 和性能优化。
请帮我写一个用户列表组件，要求：
1. 使用 TypeScript
2. 支持分页
3. 支持搜索
4. 使用 React Query
5. 注重性能优化
...
```

### 2.2 Prompt 的问题

**问题 1：每次都要重复**

```
# 今天
你是一个资深的 React 开发者...（100 行）

# 明天
你是一个资深的 React 开发者...（100 行，又来一遍）
```

**问题 2：容易遗漏**

```
# 第一次
记得加 TypeScript 类型、错误处理、loading 状态

# 第二次
忘了写，AI 生成的代码没有错误处理
```

**问题 3：难以维护**

```
# 一个月后
这个 Prompt 为什么要这样写？
能删掉这条规则吗？
不知道，不敢动
```

### 2.3 Prompt 的适用场景

✅ **适合**：
- 一次性任务
- 简单需求
- 快速验证

❌ **不适合**：
- 重复任务
- 复杂规则
- 团队协作

## 三、Skill：可复用的「专家」

### 3.1 什么是 Skill？

Skill 是把 Prompt 封装成可复用的模块，就像给 AI 安装一个「专家插件」。

```markdown
<!-- .cursor/skills/react-expert/SKILL.md -->
# React Expert Skill

你是一个资深的 React 开发者，精通：
- TypeScript
- React Hooks
- 性能优化
- 测试

## 代码规范
1. 使用函数式组件
2. 优先使用 TypeScript
3. 遵循 Airbnb 代码规范
...

## 性能优化
1. 事件处理函数用 useCallback
2. 复杂计算用 useMemo
3. 纯展示组件用 React.memo
...
```

### 3.2 Skill 的优势

**优势 1：一次编写，到处使用**

```
# 使用 Skill
/react-expert 写一个用户列表组件
/react-expert 写一个订单列表组件
/react-expert 写一个商品列表组件
```

**优势 2：效果稳定**

```
# 每次都应用相同的规则
✅ TypeScript
✅ 性能优化
✅ 错误处理
✅ 代码规范
```

**优势 3：易于维护**

```markdown
<!-- 更新 Skill -->
## 性能优化
1. 事件处理函数用 useCallback
2. 复杂计算用 useMemo
3. 纯展示组件用 React.memo
4. 长列表用虚拟滚动  ← 新增规则
```

所有使用这个 Skill 的地方都会自动应用新规则。

**优势 4：团队共享**

```bash
# 团队共享 Skill 库
git clone https://github.com/company/cursor-skills.git
cp -r cursor-skills/.cursor/skills ~/.cursor/skills

# 所有人都能用
/react-expert
/vue-expert
/node-expert
```

### 3.3 Skill vs Prompt

| 维度 | Prompt | Skill |
|------|--------|-------|
| 复用性 | 复制粘贴 | 直接调用 |
| 维护性 | 难以维护 | 集中维护 |
| 一致性 | 容易遗漏 | 始终一致 |
| 团队协作 | 难以共享 | 易于共享 |
| 学习曲线 | 低 | 中 |

## 四、MCP：AI 的「工具箱」

### 4.1 什么是 MCP？

MCP（Model Context Protocol）是 Anthropic 推出的协议，让 AI 能够调用外部工具。

**类比**：
- Prompt/Skill：告诉 AI「怎么做」
- MCP：给 AI「工具」，让它自己做

### 4.2 MCP 的工作原理

```
用户：帮我查一下今天的天气

AI：好的，我需要调用天气 API
    ↓
MCP Server：调用 weather API
    ↓
返回：北京，晴，25°C
    ↓
AI：今天北京天气晴朗，温度 25°C
```

### 4.3 MCP 的应用场景

**场景 1：文件操作**

```
用户：帮我创建一个 React 项目

AI：
1. 调用 MCP 的 filesystem 工具
2. 创建目录结构
3. 生成配置文件
4. 安装依赖
```

**场景 2：数据库查询**

```
用户：查询最近 7 天的订单数据

AI：
1. 调用 MCP 的 database 工具
2. 执行 SQL 查询
3. 返回结果
4. 生成报表
```

**场景 3：API 调用**

```
用户：帮我发一条推特

AI：
1. 调用 MCP 的 twitter 工具
2. 发送推文
3. 返回推文链接
```

### 4.4 MCP 的配置

```json
// .cursor/mcp.json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/workspace"]
    },
    "database": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": {
        "DATABASE_URL": "postgresql://user:pass@localhost:5432/db"
      }
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

### 4.5 MCP vs API

| 维度 | 传统 API | MCP |
|------|----------|-----|
| 调用方式 | 手动编码 | AI 自动调用 |
| 错误处理 | 手动处理 | AI 自动重试 |
| 参数构造 | 手动构造 | AI 自动推断 |
| 结果解析 | 手动解析 | AI 自动理解 |

## 五、Projects：AI 的「记忆」

### 5.1 什么是 Projects？

Projects 是 Cursor 的新功能，让 AI 记住项目的上下文。

**类比**：
- Prompt：一次性对话
- Skill：可复用的规则
- MCP：可调用的工具
- Projects：持久化的记忆

### 5.2 Projects 的作用

**作用 1：记住项目结构**

```
# 第一次对话
用户：这个项目的目录结构是什么？
AI：（扫描项目）
    src/
    ├── components/
    ├── pages/
    ├── utils/
    └── types/

# 第二次对话（几天后）
用户：帮我在 components 目录下创建一个新组件
AI：好的，我记得 components 目录在 src 下
```

**作用 2：记住代码风格**

```
# AI 分析项目后
- 使用 TypeScript
- 使用函数式组件
- 使用 Tailwind CSS
- 使用 React Query

# 之后生成的代码都会遵循这些风格
```

**作用 3：记住业务逻辑**

```
# AI 分析项目后
- 用户认证使用 JWT
- API 基础 URL 是 /api/v1
- 错误处理使用 toast 提示
- 表单验证使用 Zod

# 之后生成的代码都会遵循这些逻辑
```

### 5.3 Projects 的配置

```markdown
<!-- .cursor/projects/my-project.md -->
# My Project

## 项目信息
- 名称：电商管理系统
- 技术栈：React + TypeScript + Tailwind CSS
- 状态管理：Zustand
- 数据请求：React Query

## 目录结构
src/
├── components/  # 通用组件
├── pages/       # 页面组件
├── hooks/       # 自定义 Hooks
├── utils/       # 工具函数
├── types/       # TypeScript 类型
└── api/         # API 接口

## 代码规范
1. 组件使用函数式组件
2. 所有 props 都要定义类型
3. 使用 Tailwind CSS，不写内联样式
4. API 调用使用 React Query

## 业务规则
1. 用户认证使用 JWT
2. Token 存储在 localStorage
3. 未登录跳转到 /login
4. 错误提示使用 toast
```

### 5.4 Projects vs Skill

| 维度 | Skill | Projects |
|------|-------|----------|
| 作用域 | 通用规则 | 项目特定 |
| 内容 | 编码规范 | 项目上下文 |
| 复用性 | 跨项目 | 单项目 |
| 维护 | 手动更新 | AI 自动学习 |

## 六、四者的关系

```
Prompt（基础）
  ↓
Skill（可复用的 Prompt）
  ↓
MCP（可调用的工具）
  ↓
Projects（持久化的上下文）
```

**组合使用**：

```
用户：/react-expert 帮我在这个项目中创建一个用户管理模块

AI 的工作流程：
1. 读取 Projects：了解项目结构和规范
2. 应用 Skill：使用 React Expert 的规则
3. 调用 MCP：创建文件、安装依赖
4. 生成代码：符合项目规范的代码
```

## 七、实战案例

### 7.1 案例 1：从零搭建项目

```
# 1. 创建 Project
用户：创建一个电商管理系统项目

AI：
- 调用 MCP filesystem 创建目录
- 生成 package.json
- 安装依赖
- 创建 Projects 配置

# 2. 使用 Skill 生成代码
用户：/react-expert 创建用户管理模块

AI：
- 读取 Projects 了解项目结构
- 应用 Skill 的规则
- 生成符合规范的代码

# 3. 持续开发
用户：添加订单管理模块

AI：
- 参考用户管理模块的风格
- 保持一致性
- 自动应用相同的规范
```

### 7.2 案例 2：团队协作

```
# 团队 Skill 库
.cursor/skills/
├── react-expert/
├── vue-expert/
├── node-expert/
├── testing-expert/
└── security-expert/

# 项目 Projects 配置
.cursor/projects/
├── frontend.md
├── backend.md
└── mobile.md

# MCP 工具
.cursor/mcp.json
- filesystem
- database
- github
- slack
```

团队成员可以：
1. 共享 Skill 库（统一规范）
2. 共享 Projects 配置（统一上下文）
3. 共享 MCP 工具（统一工具链）

## 八、总结

AI 开发的四大概念：

**Prompt**：
- 基础的指令
- 适合一次性任务
- 难以复用和维护

**Skill**：
- 可复用的专家
- 适合重复任务
- 易于维护和共享

**MCP**：
- 可调用的工具
- 让 AI 能操作外部系统
- 扩展 AI 的能力

**Projects**：
- 持久化的上下文
- 让 AI 记住项目信息
- 保持代码一致性

**使用建议**：
1. 基础任务：Prompt
2. 重复任务：Skill
3. 外部操作：MCP
4. 项目开发：Projects

**组合使用**：
```
Projects（项目上下文）
  + Skill（编码规范）
  + MCP（工具调用）
  = 高效的 AI 开发
```

2026 年的 AI 开发，不再是简单的「问答」，而是「协作」。掌握这些新概念，让 AI 成为你的得力助手。

如果这篇文章对你有帮助，欢迎点赞收藏。有问题欢迎评论区讨论。
