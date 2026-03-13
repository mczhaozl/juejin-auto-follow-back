# 从零理解 React 18 并发渲染：Suspense、useTransition 与可中断更新

> 讲清 React 18 并发模型、Suspense 数据获取、useTransition 使用场景与原理，能自己判断何时上并发、如何避免坑。

---

## 一、背景：为什么需要「并发」

在 React 17 及之前，一旦开始渲染一棵组件树，就会**一口气算到底**再提交到 DOM。中间不能暂停、不能插队。带来的问题很直观：

- **长列表或重计算**：主线程被占满，输入框打字、滚动都会卡顿。
- **多数据源**：先到的数据要等最慢的接口，首屏被拖慢。
- **高优先级更新被阻塞**：用户点击「展开详情」要等一个不紧急的渲染跑完。

React 18 的**并发模式（Concurrent Mode）**把「渲染」拆成可中断、可插队、可复用中间结果的工作单元，让高优先级更新（如用户输入）能打断低优先级更新（如列表渲染），从而在保持声明式写法的前提下提升体感流畅度。

**核心概念**：**可中断更新**、**并发渲染**、**Suspense**、**useTransition**。下文按「是什么 → 怎么用 → 原理与注意点」展开。

## 二、Suspense：把「等数据」变成声明式

Suspense 在 React 18 里不再只是「等 lazy 组件」，而是**任何异步依赖**都可以用 `<Suspense fallback={...}>` 包一层，子组件在 Promise resolve 前会挂起，显示 fallback。

### 2.1 基本用法

```jsx
import { Suspense } from 'react';

function App() {
  return (
    <Suspense fallback={<div>加载中...</div>}>
      <ProfilePage />  {/* 内部可能 throw promise */}
    </Suspense>
  );
}
```

子组件或它调用的**数据层**在数据未就绪时 `throw promise`，React 会捕获并订阅该 promise，resolve 后重新渲染该子树。这样「加载中」的 UI 完全由 Suspense 统一管，业务组件只关心「有数据时怎么画」。

### 2.2 与数据请求结合（不依赖具体库）

概念上，任何「返回 Promise 的读」都可以和 Suspense 配合：在请求未完成时 throw 该 promise，完成后再渲染。例如：

```javascript
// 概念示例：缓存 + throw promise
const cache = new Map();
function read(key) {
  if (cache.has(key)) return cache.get(key);
  const p = fetch(key).then(r => r.json()).then(data => { cache.set(key, data); return data; });
  throw p;
}
```

组件里调用 `read('user')`，第一次会 throw，React 挂起；请求回来后重新渲染，第二次 `read('user')` 命中缓存直接返回，即可渲染。实际项目里通常用 **React Query、SWR、Relay** 等支持 Suspense 的封装。

### 2.3 多层 Suspense 与 loading 层级

可以嵌套多个 Suspense，每一层有自己的 fallback，这样表格、侧边栏、详情区可以各自 loading，而不是整个页面一个大转圈。

## 三、useTransition：区分「紧急」与「不紧急」更新

`useTransition` 用来标记**非紧急更新**：这类更新可以被更紧急的（如输入、点击）打断，从而不阻塞交互。

### 3.1 API

```javascript
const [isPending, startTransition] = useTransition();

// 把「不紧急」的 setState 包在 startTransition 里
startTransition(() => {
  setSearchQuery(input);  // 例如驱动一个很重的列表过滤
});
```

- **isPending**：当前是否有由 startTransition 触发的更新仍在进行（可能被中断后重算）。
- **startTransition(fn)**：在 fn 里触发的 setState 会被标记为**过渡更新**，优先级低于用户输入等。

### 3.2 典型场景

- **搜索/筛选**：输入框用受控 state，列表过滤用另一个 state；把「设置过滤条件」放进 startTransition，输入不卡。
- **Tab 切换**：新 Tab 内容渲染很重时，用 startTransition 包住「切换 Tab 的 setState」，旧 Tab 可先保持响应。
- **路由/大列表**：下一页或下一屏的渲染用 startTransition，当前页的点击、滚动保持优先。

### 3.3 和防抖/节流的区别

防抖是「少触发」；startTransition 是「触发但允许被打断、延后」。两者可以叠加：先防抖减少触发次数，再对单次更新用 startTransition 降级优先级。

## 四、useDeferredValue：把「慢数据」延后

`useDeferredValue(value)` 会给你一个「可能滞后一两个渲染周期」的版本，用于驱动重渲染，从而不阻塞当前帧对高优先级更新的响应。

```javascript
const [text, setText] = useState('');
const deferredText = useDeferredValue(text);

return (
  <>
    <input value={text} onChange={e => setText(e.target.value)} />
    <HeavyList query={deferredText} />  {/* 用延后的值，不阻塞输入 */}
  </>
);
```

和 useTransition 的差异：Transition 是「包住更新从哪来」；DeferredValue 是「包住要消费的值」，适合「同一数据源，一部分 UI 要快、一部分可以慢一拍」的场景。

## 五、并发下的「可中断」与双缓冲

React 18 的 Fiber 架构在并发模式下会：

1. **时间切片**：把渲染工作拆成小段，每段执行一段时间后让出主线程，高优先级更新可以插队。
2. **双缓冲**：为同一棵子树准备两套 Fiber 树（current / workInProgress），正在算的是 workInProgress，算完再一次性 commit 替换 current，避免半成品 UI。
3. **可复用/可丢弃**：若在算 workInProgress 时来了更高优先级更新，当前 workInProgress 可能被丢弃，用新 state 重新算，从而保证界面先响应「更紧急」的事。

所以你会看到：**同一次交互触发的更新可能被拆成多次 commit**（例如先 commit 输入框，再 commit 列表），或者**某次过渡更新被中断后重算**，这是预期行为。

## 六、实践注意点与常见坑

- **Suspense 必须和「throw promise」的数据层配合**：自己写的请求要封装成「未就绪就 throw」，或直接用支持 Suspense 的库。
- **useTransition 只对「由 React 调度的 setState」生效**：原生 DOM、非 React 的动画库不会自动被降级，需要自己控制。
- **不要滥用**：只有真正「重」或「可延后」的更新才包在 startTransition 里，否则反而增加调度开销。
- **SSR/流式**：React 18 的流式 SSR 和 Selective Hydration 也依赖类似的「可中断」与优先级，和并发渲染是一套思路。

## 七、总结

- **并发**：渲染可中断、可插队，高优更新先反馈，提升体感流畅度。
- **Suspense**：用「throw promise + fallback」把异步依赖变成声明式，统一 loading 与错误边界。
- **useTransition / useDeferredValue**：区分紧急与非紧急更新，把重计算、重列表、Tab/路由切换等做成「可打断、可延后」，避免阻塞输入与点击。

用好这三块，就能在 React 18 里既保留声明式写法，又拿到接近手写调度级别的交互体验。建议在真实项目里对「最卡」的一两个场景先上 useTransition 或 DeferredValue，再根据效果决定是否全面上 Suspense 数据层。

## 八、延伸：与 React 19、Compiler 的关系

React 19 在并发这一块延续并强化了 18 的设计：**Actions**、**useOptimistic** 等 API 仍然建立在「过渡更新」和「可中断」之上。理解 18 的 useTransition/Suspense，再学 19 会顺很多。

**React Compiler**（原 React Forget）做的是「自动记忆化」：自动插入类似 useMemo/useCallback 的优化，减少不必要的重渲染。它和并发不冲突：Compiler 管的是「少算」，并发管的是「算的时候别堵住交互」。两者叠加，重组件在 18+ 下的体验会更好。

## 九、自测：你是否真的搞懂了

- 能说清「可中断更新」和「双缓冲」分别解决什么问题吗？
- 在现有项目里，能否指出 1～2 个适合用 useTransition 或 useDeferredValue 的场景？
- 若要从零接一个「支持 Suspense 的数据层」，你会怎么设计缓存与 throw promise 的时机？

如果你能答上来，说明这篇长文没白看；答不上来就回头翻一翻对应小节，再写两行 demo 跑一跑，印象会深很多。
