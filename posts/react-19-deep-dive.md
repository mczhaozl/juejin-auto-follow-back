# 【React】19 深度解析：掌握新一代 React 特性

> 从 Actions、use()、ref 作 prop 到表单与 Server Components，一文梳理 React 19 稳定版核心特性与落地方式。

---

## 一、React 19 是什么

**React 19** 是 React 团队在 **2024 年 12 月 5 日** 发布的稳定版本，在 npm 上可直接安装使用。它在保留 React 18 并发与 Suspense 能力的基础上，重点增强了**异步数据与表单**（Actions）、**在渲染中消费资源**（`use()`）、**ref 与 Context 用法**，并正式纳入 **Server Components / Server Actions** 的稳定能力，方便与支持全栈架构的框架（如 Next.js）配合使用。

与 18 相比，19 更强调「用声明式方式处理异步与表单」，减少手写 pending/error、减少 `forwardRef` 与 Context 的样板代码，同时改进水合报错、文档元数据等开发体验。

---

## 二、核心新特性概览

| 方向       | 内容 |
|------------|------|
| **Actions** | 异步函数放进 `useTransition`，自动管理 pending、错误、表单重置；配合 `useActionState`、`useOptimistic`、`<form action={fn}>` |
| **use()**  | 在渲染中读取 Promise 或 Context，可条件调用，需配合 Suspense |
| **ref**    | 函数组件可直接用 `ref` 作 prop，不再强制 `forwardRef` |
| **表单**   | `<form>` 支持 `action`/`formAction` 为函数；`useFormStatus` 读父级表单状态；`requestFormReset` 手动重置 |
| **Context**| 可用 `<Context value={...}>` 作 Provider，替代 `<Context.Provider>` |
| **Server** | Server Components、Server Actions 在 React 19 中稳定，需框架/打包器支持 |

下面按块说明用法与注意点。

---

## 三、Actions：异步与表单一体化

**Actions** 指在 **transition** 里跑的异步函数：React 自动提供 pending 状态、错误边界内的错误处理、表单提交后重置（非受控）、以及乐观更新的回滚。

### 用 useTransition 跑异步

以前要自己用 `useState` 管 `isPending`、`error`；现在把异步逻辑放进 `startTransition` 即可，pending 由 React 管理：

```javascript
function UpdateName() {
  const [name, setName] = useState("");
  const [error, setError] = useState(null);
  const [isPending, startTransition] = useTransition();

  const handleSubmit = () => {
    startTransition(async () => {
      const err = await updateName(name);
      if (err) {
        setError(err);
        return;
      }
      redirect("/path");
    });
  };

  return (
    <>
      <input value={name} onChange={(e) => setName(e.target.value)} />
      <button onClick={handleSubmit} disabled={isPending}>Update</button>
      {error && <p>{error}</p>}
    </>
  );
}
```

### useActionState：封装 Action + 状态

把「服务端/异步操作 + 上一次结果 + pending」打包成一个 Hook，适合表单提交：

```javascript
function ChangeName({ name, setName }) {
  const [error, submitAction, isPending] = useActionState(
    async (previousState, formData) => {
      const err = await updateName(formData.get("name"));
      if (err) return err;
      redirect("/path");
      return null;
    },
    null
  );

  return (
    <form action={submitAction}>
      <input type="text" name="name" defaultValue={name} />
      <button type="submit" disabled={isPending}>Update</button>
      {error && <p>{error}</p>}
    </form>
  );
}
```

**要点**：`useActionState` 第一个参数是 Action（可接收 `previousState` 与表单等入参），返回的 `submitAction` 可直接作为 `<form action={submitAction}>`，提交成功后 React 会重置非受控表单。

### useOptimistic：乐观更新

在请求尚未返回前先更新 UI，失败时 React 会回滚到真实状态。需在 Action 内调用 `setOptimisticXxx`：

```javascript
function ChangeName({ currentName, onUpdateName }) {
  const [optimisticName, setOptimisticName] = useOptimistic(currentName);

  const submitAction = async (formData) => {
    const newName = formData.get("name");
    setOptimisticName(newName);
    const updated = await updateName(newName);
    onUpdateName(updated);
  };

  return (
    <form action={submitAction}>
      <p>Your name is: {optimisticName}</p>
      <input type="text" name="name" disabled={currentName !== optimisticName} />
    </form>
  );
}
```

### useFormStatus（react-dom）

在**父级 `<form>`** 内的子组件里，用 `useFormStatus()` 拿到该表单的 pending 等状态，无需层层传 props：

```javascript
import { useFormStatus } from "react-dom";

function SubmitButton() {
  const { pending } = useFormStatus();
  return <button type="submit" disabled={pending}>Submit</button>;
}

function MyForm() {
  return (
    <form action={someAction}>
      <input name="field" />
      <SubmitButton />
    </form>
  );
}
```

---

## 四、use()：在渲染中读 Promise / Context

**`use(resource)`** 可在组件渲染时消费两种资源：

1. **Promise**：未 resolve 时组件挂起，由上层 `<Suspense>` 显示 fallback；resolve 后得到数据再渲染。
2. **Context**：等价于「可条件调用的 `useContext`」，可在 early return 之后调用，这是和 Hooks 规则的重要区别。

### 读 Promise（配 Suspense）

```javascript
import { use } from "react";

function Comments({ commentsPromise }) {
  const comments = use(commentsPromise);
  return comments.map((c) => <p key={c.id}>{c.text}</p>);
}

function Page({ commentsPromise }) {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <Comments commentsPromise={commentsPromise} />
    </Suspense>
  );
}
```

注意：**不要在渲染里现场 new Promise 再传给 use()**，React 会警告「uncached promise」。应使用支持缓存的数据源（如框架或 Suspense 兼容库提供的 promise）。

### 读 Context（可条件调用）

```javascript
import { use } from "react";

function Heading({ children }) {
  if (children == null) return null;
  const theme = use(ThemeContext);  // 在 return 之后调用，useContext 做不到
  return <h1 style={{ color: theme.color }}>{children}</h1>;
}
```

---

## 五、ref 作为 prop、Context 作为 Provider

### ref 直接当 prop

函数组件不再必须用 `forwardRef`，可直接声明 `ref` 并转发给 DOM 或子组件：

```javascript
function MyInput({ placeholder, ref }) {
  return <input placeholder={placeholder} ref={ref} />;
}
// 使用：<MyInput ref={ref} />
```

未来版本中 `forwardRef` 将被弃用，官方会提供 codemod 协助迁移。

### Context 直接当 Provider

可以用 `<Context value={...}>` 替代 `<Context.Provider value={...}>`：

```javascript
const ThemeContext = createContext("");

function App({ children }) {
  return (
    <ThemeContext value="dark">
      {children}
    </ThemeContext>
  );
}
```

---

## 六、文档元数据、ref 清理与其它

- **文档元数据**：在组件里直接渲染 `<title>`、`<meta>` 等，React 会提升到 `<head>`（需在支持该能力的框架/环境中使用）。
- **ref 回调清理**：ref 回调可返回一个清理函数，在节点从 DOM 移除时执行。
- **水合错误**：`react-dom` 对水合不匹配的报错做了改进，会给出更清晰的 diff 与说明链接。
- **React DOM 静态 API**：`react-dom/static` 提供 `prerender`、`prerenderToNodeStream` 等，用于在等待数据加载后输出静态 HTML 流。
- **Server Components / Server Actions**：在 React 19 中稳定，需由支持全栈架构的框架（如 Next.js）或自定义打包器实现；`"use server"` 仅用于标记 Server Action，不用于标记 Server Component。

---

## 七、如何升级与参考

- **升级步骤**：见官方 [React 19 Upgrade Guide](https://react.dev/blog/2024/04/25/react-19-upgrade-guide)，含破坏性变更与迁移建议。
- **安装**：`npm install react@19 react-dom@19`（或 yarn/pnpm），以官方文档为准。
- **官方链接**（可溯源）：
  - [React 19 发布博客](https://react.dev/blog/2024/12/05/react-19)
  - [useActionState](https://react.dev/reference/react/useActionState)
  - [useOptimistic](https://react.dev/reference/react/useOptimistic)
  - [use](https://react.dev/reference/react/use)
  - [Server Components](https://react.dev/reference/rsc/server-components)、[Server Actions](https://react.dev/reference/rsc/server-actions)

---

## 总结

- **Actions**：用 `useTransition` 跑异步、`useActionState` 包表单、`useOptimistic` 做乐观更新，`<form action={fn}>` 与 `useFormStatus` 简化表单状态。
- **use()**：在渲染中读 Promise（配 Suspense）或 Context，且 `use()` 可条件调用。
- **ref / Context**：函数组件可直接用 `ref` 作 prop；可用 `<Context value={...}>` 作 Provider。
- **Server**：Server Components 与 Server Actions 在 React 19 稳定，需框架支持；文档元数据、静态预渲染等需在对应环境中使用。

若对你有用，欢迎点赞、收藏；你若有 React 19 落地或迁移经验，也欢迎在评论区分享。
