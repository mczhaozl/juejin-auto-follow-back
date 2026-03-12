# 继续堆 Prompt 不如早点学 Skill

> Prompt 工程师的焦虑：每天写几百行 Prompt，效果还是不稳定。也许是时候换个思路了——用 Skill 代替 Prompt。

---

## 一、Prompt 工程师的日常

早上九点，打开 Cursor，开始今天的工作。

```
你是一个资深的 React 开发者，精通 TypeScript、Hooks、性能优化。
你的代码风格是：
1. 使用函数式组件
2. 优先使用 TypeScript
3. 遵循 Airbnb 代码规范
4. 注重性能优化
5. 添加详细注释
...（还有 50 行规则）

现在请帮我写一个用户列表组件，要求：
1. 支持分页
2. 支持搜索
3. 支持排序
4. 使用 React Query
5. 使用 Ant Design
...（还有 20 行需求）
```

写完这 70 行 Prompt，等了 30 秒，AI 给了我一个组件。

看起来不错，但有几个问题：
- 没有用 `useCallback`
- 没有用 `React.memo`
- 搜索没有防抖

于是我又加了 20 行 Prompt：

```
请注意：
1. 事件处理函数要用 useCallback
2. 组件要用 React.memo
3. 搜索要加防抖
...
```

又等了 30 秒，这次好了。

但下午写另一个组件时，又要重复这 90 行 Prompt。复制粘贴，改改需求，再等 30 秒。

**一天下来，我写了 500 行 Prompt，生成了 2000 行代码。**

累吗？累。效率高吗？不高。

## 二、Prompt 的问题

### 2.1 每次都要重复

```
# 今天写用户列表
你是一个资深的 React 开发者...（70 行）

# 明天写订单列表
你是一个资深的 React 开发者...（70 行，又来一遍）

# 后天写商品列表
你是一个资深的 React 开发者...（70 行，还是这些）
```

### 2.2 容易遗漏

```
# 第一次
请注意性能优化：useCallback、useMemo、React.memo

# 第二次
忘了写性能优化，AI 生成的代码没有优化

# 第三次
又忘了，又没优化
```

### 2.3 效果不稳定

```
# 同样的 Prompt，不同的结果

# 第一次
✅ 生成了完美的代码

# 第二次
❌ 忘了加 TypeScript 类型

# 第三次
❌ 没有错误处理
```

### 2.4 难以维护

```
# 一个月后
这个 Prompt 是什么意思来着？
为什么要加这条规则？
能删掉吗？
```

### 2.5 无法复用

```
# 团队协作
A: 我的 Prompt 效果很好
B: 发我看看
A: （复制粘贴 200 行）
B: 这么长？算了，我自己写
```

## 三、Skill 的优势

Skill 是什么？简单说，就是**把 Prompt 封装成可复用的模块**。

### 3.1 一次编写，到处使用

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

使用时：

```
/react-expert 帮我写一个用户列表组件
```

就这一行，AI 就知道所有规则了。

### 3.2 效果稳定

```
# 每次都是同样的规则
/react-expert 写用户列表  ✅
/react-expert 写订单列表  ✅
/react-expert 写商品列表  ✅
```

### 3.3 易于维护

```markdown
<!-- 更新 Skill -->
## 性能优化
1. 事件处理函数用 useCallback
2. 复杂计算用 useMemo
3. 纯展示组件用 React.memo
4. 长列表用虚拟滚动  ← 新增规则
```

所有使用这个 Skill 的地方都会自动应用新规则。

### 3.4 团队共享

```bash
# 团队共享 Skill
git clone https://github.com/company/cursor-skills.git
cp -r cursor-skills/.cursor/skills ~/.cursor/skills

# 所有人都能用
/react-expert
/vue-expert
/node-expert
```

## 四、Skill 实战

### 4.1 创建第一个 Skill

```bash
# 创建目录
mkdir -p .cursor/skills/react-expert

# 创建 Skill 文件
touch .cursor/skills/react-expert/SKILL.md
```

```markdown
<!-- .cursor/skills/react-expert/SKILL.md -->
# React Expert Skill

## 角色定位
你是一个资深的 React 开发者，有 5 年以上的实战经验。

## 技术栈
- React 18+
- TypeScript 5+
- React Query
- Ant Design
- Tailwind CSS

## 代码规范

### 组件编写
1. 使用函数式组件
2. 使用 TypeScript，所有 props 都要定义类型
3. 组件名使用 PascalCase
4. 文件名与组件名一致

### 性能优化
1. 传给子组件的函数用 `useCallback`
2. 复杂计算用 `useMemo`
3. 纯展示组件用 `React.memo`
4. 避免在渲染中创建对象/数组

### 状态管理
1. 本地状态用 `useState`
2. 复杂状态用 `useReducer`
3. 服务端状态用 React Query
4. 全局状态用 Zustand

### 错误处理
1. 使用 Error Boundary
2. 异步操作要有 loading 和 error 状态
3. 表单验证要有错误提示

### 代码风格
1. 使用 ESLint 和 Prettier
2. 遵循 Airbnb 代码规范
3. 添加必要的注释
4. 函数不超过 50 行

## 示例代码

### 组件模板
\`\`\`typescript
import React, { useState, useCallback, useMemo } from 'react';

interface Props {
  // props 类型定义
}

export const ComponentName: React.FC<Props> = ({ prop1, prop2 }) => {
  // 状态
  const [state, setState] = useState();

  // 计算值
  const computed = useMemo(() => {
    // 复杂计算
  }, [dependencies]);

  // 事件处理
  const handleEvent = useCallback(() => {
    // 处理逻辑
  }, [dependencies]);

  return (
    // JSX
  );
};
\`\`\`

## 注意事项
1. 先思考再编码
2. 考虑边界情况
3. 注重用户体验
4. 保持代码简洁
```

### 4.2 使用 Skill

```
/react-expert 帮我写一个用户列表组件，要求：
1. 支持分页
2. 支持搜索
3. 支持排序
```

AI 会根据 Skill 中的规则生成代码：
- ✅ 使用 TypeScript
- ✅ 函数用 useCallback
- ✅ 组件用 React.memo
- ✅ 搜索有防抖
- ✅ 有错误处理
- ✅ 有 loading 状态

### 4.3 组合多个 Skill

```markdown
<!-- .cursor/skills/testing-expert/SKILL.md -->
# Testing Expert Skill

## 测试原则
1. 测试用户行为，不测试实现细节
2. 使用 React Testing Library
3. 覆盖率 > 80%
...
```

使用时：

```
/react-expert /testing-expert 写一个用户列表组件，并写测试
```

AI 会同时应用两个 Skill 的规则。

## 五、Skill vs Prompt 对比

| 维度 | Prompt | Skill |
|------|--------|-------|
| 编写成本 | 每次都要写 | 一次编写 |
| 复用性 | 复制粘贴 | 直接调用 |
| 维护性 | 难以维护 | 集中维护 |
| 一致性 | 容易遗漏 | 始终一致 |
| 团队协作 | 难以共享 | 易于共享 |
| 学习曲线 | 低 | 中 |

## 六、进阶技巧

### 6.1 Skill 继承

```markdown
<!-- base-skill/SKILL.md -->
# Base Skill
通用规则...

<!-- react-expert/SKILL.md -->
# React Expert Skill
继承 base-skill
React 特定规则...
```

### 6.2 Skill 参数化

```markdown
# React Expert Skill

## 配置
- UI 库：${UI_LIBRARY}  # Ant Design / Material-UI
- 状态管理：${STATE_MANAGEMENT}  # Zustand / Redux
```

使用时：

```
/react-expert UI_LIBRARY=Material-UI STATE_MANAGEMENT=Redux
```

### 6.3 Skill 版本管理

```bash
.cursor/skills/
├── react-expert/
│   ├── v1/
│   │   └── SKILL.md
│   ├── v2/
│   │   └── SKILL.md
│   └── latest -> v2
```

## 七、实战案例

### 7.1 案例 1：前端团队的 Skill 库

```
.cursor/skills/
├── react-expert/
├── vue-expert/
├── typescript-expert/
├── testing-expert/
├── performance-expert/
├── accessibility-expert/
└── security-expert/
```

团队成员可以组合使用：

```
/react-expert /typescript-expert /testing-expert
写一个用户管理模块
```

### 7.2 案例 2：个人效率提升

**使用 Prompt 前**：
- 每天写 500 行 Prompt
- 生成 2000 行代码
- 效率：4 行代码/行 Prompt

**使用 Skill 后**：
- 每天写 50 行 Prompt（调用 Skill）
- 生成 3000 行代码
- 效率：60 行代码/行 Prompt

**效率提升 15 倍！**

## 八、总结

Prompt 的问题：
- 每次都要重复
- 容易遗漏
- 效果不稳定
- 难以维护
- 无法复用

Skill 的优势：
- 一次编写，到处使用
- 效果稳定
- 易于维护
- 团队共享
- 效率提升

什么时候用 Skill？
- ✅ 重复的规则
- ✅ 团队协作
- ✅ 长期维护
- ✅ 复杂场景

什么时候用 Prompt？
- ✅ 一次性任务
- ✅ 简单需求
- ✅ 快速验证

建议：
1. 把常用的 Prompt 整理成 Skill
2. 团队共享 Skill 库
3. 持续优化 Skill
4. Prompt + Skill 组合使用

继续堆 Prompt？不如早点学 Skill。

如果这篇文章对你有帮助，欢迎点赞收藏。有问题欢迎评论区讨论。
