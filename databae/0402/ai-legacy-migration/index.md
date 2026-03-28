# AI 辅助重构实战：利用 LLM 迁移遗留系统到 React 19

> 重构遗留系统（Legacy System）是每个资深开发者的必经之路。随着 React 19 的发布，其带来的 Actions、Server Components 和新的 Hooks 为性能优化提供了巨大的空间。但面对数万行的陈旧代码，手动迁移不仅低效且极易引入 Bug。本文将带你实战：如何利用 LLM（大语言模型）作为「重构助手」，平滑地将老旧项目升级到 React 19。

---

## 目录 (Outline)
- [一、 迁移的挑战：为什么 React 19 的重构与众不同？](#一-迁移的挑战为什么-react-19-的重构与众不同)
- [二、 LLM 辅助重构的核心流程：Prompt 链的设计](#二-llm-辅助重构的核心流程prompt-链的设计)
- [三、 实战 1：利用 AI 自动将 useEffect 异步逻辑重构为 Actions](#三-实战-1利用-ai-自动将-useeffect-异步逻辑重构为-actions)
- [四、 实战 2：语义化分析并提取 Server Components](#四-实战-2语义化分析并提取-server-components)
- [五、 质量保障：如何通过 AI 生成迁移后的单元测试？](#五-质量保障如何通过-ai-生成迁移后的单元测试)
- [六、 总结与最佳实践](#六-总结与最佳实践)

---

## 一、 迁移的挑战：为什么 React 19 的重构与众不同？

### 1. 范式转移
React 19 不仅仅是 API 的增删，它代表了从「纯客户端调度」向「全栈流式渲染」的范式转移。
- **痛点**：老代码中充斥着大量的 `useState` 驱动的表单加载状态，这在 React 19 中应当被 `useActionState` 替代。

---

## 二、 LLM 辅助重构的核心流程：Prompt 链的设计

我们不能简单地把 1000 行代码丢给 AI 说「请重构」。一个稳健的 AI 重构链应该是：
1. **语义理解层**：AI 解释这段代码在干什么，识别出数据获取、交互、副作用。
2. **坏味道识别层**：识别出哪些地方可以利用 React 19 新特性优化。
3. **分片转换层**：按功能模块，逐步输出重构后的代码。
4. **一致性检查层**：对比重构前后的 API 签名和 Props 结构。

---

## 三、 实战 1：利用 AI 自动将 useEffect 异步逻辑重构为 Actions

### 老代码（典型的 useEffect 灾难）
```javascript
function OldProfile() {
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/user').then(r => r.json()).then(u => {
      setUser(u);
      setLoading(false);
    });
  }, []);
  // ...
}
```

### AI 重构 Prompt
> "你是一个 React 专家。请将以下代码中的数据获取逻辑重构为 React 19 的 `useActionState`。保持业务逻辑不变，移除手动的 loading 状态管理。"

### AI 输出（React 19 风格）
```javascript
import { useActionState } from 'react';

function NewProfile() {
  const [state, submitAction, isPending] = useActionState(async () => {
    const res = await fetch('/api/user');
    return await res.json();
  }, null);
  // ...
}
```

---

## 四、 实战 2：语义化分析并提取 Server Components

AI 擅长识别哪些逻辑不依赖浏览器 API。

### 重构策略
我们将组件代码喂给 AI，问它：*"这段代码中，哪些部分可以直接在服务器端执行（不包含 useState, useEffect, window）？请将它们拆分为单独的 .server.js 文件。"**

---

## 五、 质量保障：如何通过 AI 生成迁移后的单元测试？

重构完成后，最担心的是破坏原有功能。
利用 AI 针对重构后的 `Actions` 自动生成 Vitest 测试用例：
```javascript
// AI 生成的测试示例
test('action should update state correctly', async () => {
  const [state, action] = renderHook(() => useActionState(myAction, null));
  await act(() => action());
  expect(state.data).toBeDefined();
});
```

---

## 六、 总结与最佳实践

- **小步快跑**：每次只让 AI 重构一个组件，人工审核后再合并。
- **Context 注入**：重构前，先给 AI 喂入 React 19 的官方升级文档作为背景知识。
- **混合模式**：AI 负责写代码，人类负责架构决策和边界划分。

AI 辅助重构不是为了逃避工作，而是为了让我们有更多时间去思考业务价值，而不是在繁琐的 API 替换中消磨生命。

---

> **参考资料：**
> - *React 19 Upgrade Guide*
> - *Using LLMs for Large-scale Code Refactoring - arXiv*
> - *AI-Powered Frontend Engineering - Modern Patterns*
