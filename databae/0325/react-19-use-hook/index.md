# React 19 深度解析：全新的 use API 如何颠覆异步数据与 Context 的处理？

> React 19 引入了一个重量级的 API：`use`。它不是普通的 Hook，而是一个可以在循环和条件语句中调用的特殊函数。本文将带你深入理解 `use` 的核心机制，以及它如何配合 Suspense 简化我们的开发流程。

## 一、`use` 是什么？

在 React 19 之前，Hooks 有严格的使用限制：不能在循环、条件判断或嵌套函数中调用。但 `use` 打破了这一常规。

虽然它看起来像 Hook，但 React 官方将其定义为一种**在渲染时读取资源**的 API。目前，`use` 主要支持两种资源的读取：
1. **Promises**：异步获取数据。
2. **Context**：读取上下文的值。

### 为什么需要 `use`？

过去我们处理异步数据通常依赖 `useEffect` + `useState`，或者像 React Query 这样的第三方库。而 `use` 的出现，让「在渲染中等待异步结果」变得像读取普通变量一样自然。

---

## 二、场景一：异步读取 Promise

这是 `use` 最强大的功能。你可以直接在组件中 `use(promise)`。

### 1. 基础用法

```javascript
import { use } from 'react';

function Message({ messagePromise }) {
  // 直接读取 Promise 的值！
  const messageContent = use(messagePromise);
  return <p>来自服务端的消息: {messageContent}</p>;
}
```

### 2. 配合 Suspense 与 Error Boundary

`use` 并不是直接在组件里返回 `pending` 状态，而是会**挂起（Suspend）**当前组件的执行。这意味着你必须配合 `Suspense` 使用。

```javascript
import { Suspense, use } from 'react';
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  const messagePromise = fetchMessage(); // 获取 Promise（通常在父组件或外部发起）

  return (
    <ErrorBoundary fallback={<p>⚠️ 加载失败！</p>}>
      <Suspense fallback={<p>⌛ 正在拼命加载中...</p>}>
        <Message messagePromise={messagePromise} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### 3. 注意点：不要在组件内创建 Promise

这是新手最容易踩的坑。如果在组件内部每次渲染都重新 `fetch` 创建一个新的 Promise，会导致组件无限挂起并死循环。

**❌ 错误写法：**
```javascript
function Message() {
  const messagePromise = fetch('/api/msg'); // 每次渲染都重新 fetch，大错特错！
  const content = use(messagePromise);
  return <p>{content}</p>;
}
```

**✅ 正确做法：**
- 将 Promise 作为 props 传递。
- 或者使用 `cache`（React 19 提供的新 API）对 Promise 进行缓存。

---

## 三、场景二：条件化读取 Context

这是 `use` 另一个让人惊艳的特性：它可以在**条件判断**或**循环**中读取 Context！

### 1. 突破 Hook 限制

在 React 19 之前，如果你想根据某个条件读取 Context，你必须在组件顶部无条件调用 `useContext`。

**❌ 旧写法：**
```javascript
function Button({ showTheme }) {
  const theme = useContext(ThemeContext); // 无论用不用，都得调用
  if (!showTheme) return <button>Default Button</button>;
  return <button style={{ color: theme.color }}>Themed Button</button>;
}
```

**✅ React 19 `use` 写法：**
```javascript
function Button({ showTheme }) {
  if (!showTheme) return <button>Default Button</button>;

  // 只有在需要时才读取 Context！
  const theme = use(ThemeContext);
  return <button style={{ color: theme.color }}>Themed Button</button>;
}
```

### 2. 为什么这很重要？
这不仅让代码更简洁，还能优化性能。如果你的组件在某些分支下不需要 Context，那么当 Context 变化时，该组件可能不需要重新渲染。

---

## 四、总结

React 19 的 `use` API 标志着 React 向**声明式资源加载**迈出了巨大的一步。
- **异步数据**：让 Suspense 成为标配，彻底告别繁琐的 `useEffect` 数据请求。
- **Context**：打破 Hook 限制，让上下文读取更加灵活。

虽然 `use` 很强大，但也要注意它的心智负担（如 Promise 缓存问题）。建议在实际项目结合 React 19 的其他新特性（如 `cache` 和 `Server Components`）一起使用。

**如果你对 React 19 的其他新 API（如 useFormStatus）感兴趣，欢迎关注我的专栏！**
