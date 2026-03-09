# React 哲学之 Suspense

> 从「声明式加载状态」到「与数据请求解耦」：梳理 React Suspense 的设计哲学、适用场景与使用方式，帮助你在项目中正确选用 Suspense 与并发渲染。

---

## 一、Suspense 解决什么问题？

在传统写法里，我们往往在组件内部用 `useState` + `useEffect` 拉数据，再根据 `loading` 自己渲染骨架或占位。结果是：**数据与 UI 强耦合**，逻辑分散，且难以在树的上层统一处理「这一整块还没准备好」的状态。

**Suspense** 的思路是：子组件在「需要数据时」直接抛出一个 **Promise**（或使用支持 Suspense 的 data source），由 React 在父级用 `<Suspense fallback={...}>` 接住，在 Promise resolve 前只渲染 `fallback`。这样：

- **声明式**：父组件只声明「这里有一块是异步的，没准备好就显示 fallback」；
- **关注点分离**：子组件专注「我要什么数据」，不必写 loading 分支；
- **与并发模式配合**：React 可以优先保持已有 UI 稳定，再逐步展示新内容，减少布局跳动。

---

## 二、两种典型用法

### 1. 与 lazy 配合：代码分割

```jsx
const Other = React.lazy(() => import('./Other'));

function App() {
  return (
    <Suspense fallback={<div>加载中…</div>}>
      <Other />
    </Suspense>
  );
}
```

这里「异步」的是**模块加载**。子组件加载完成前，会显示 fallback。

### 2. 与「可挂起」的数据请求配合

当数据层支持 Suspense（例如在 render 里读「未就绪」的数据会 throw Promise）时，可以这样写：

```jsx
function Profile() {
  const user = use(getUser()); // 未就绪时内部 throw Promise
  return <div>{user.name}</div>;
}

<Suspense fallback={<Skeleton />}>
  <Profile />
</Suspense>
```

此时「异步」的是**数据**。React 会等 Promise resolve 后重新渲染该子树。

---

## 三、设计哲学小结

| 点 | 含义 |
|----|------|
| **声明式加载状态** | 父级用 Suspense 声明「这里有一块异步」，而不是在子组件里 if (loading) return ... |
| **与数据/代码解耦** | 子组件只表达「需要什么」，不负责写 loading/error UI，便于复用与组合 |
| **为并发渲染铺路** | 与 Transition、useDeferredValue 等配合，让 React 能调度优先级、减少卡顿感 |

---

## 四、使用注意

- **fallback 要有**：每个 Suspense 都应提供 fallback，否则会报错或行为异常。
- **边界放在哪**：边界越靠上，覆盖的异步范围越大，但 fallback 持续时间可能更长；通常按「路由」或「大区块」划分。
- **与 Error Boundary 搭配**：Suspense 只接「挂起」，不接错误；请求失败仍要由 Error Boundary 或上层 try/catch 处理。

---

## 总结

- Suspense 把「这里在等异步结果」从子组件里抽离出来，由父级用 fallback 统一表达，符合 React 的声明式哲学。
- 既可用于代码分割（lazy），也可用于数据请求（需数据层支持「挂起」协议）。
- 用好 Suspense，能让加载状态更清晰、更易与并发特性结合，为后续的 React 演进留足空间。

若对你有用，欢迎点赞、收藏；你有在项目里用 Suspense 做数据加载的实践，也欢迎在评论区分享。
