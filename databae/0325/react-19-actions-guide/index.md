# React 生态：深入理解 React 19 中的 Actions 与 useActionState

> React 19 正式发布了！其中最受关注的变化莫过于 Actions 和新的 Hooks（如 useActionState）。本文将深入浅出地讲解这些新特性如何简化我们的表单处理和异步状态管理。

## 一、什么是 React 19 中的 Actions？

在 React 19 之前，我们处理异步表单提交通常需要手动管理多个状态：`isPending`、`error`、`data`。

```javascript
// 旧的写法
const [isPending, setIsPending] = useState(false);
const [error, setError] = useState(null);

async function handleSubmit(formData) {
  setIsPending(true);
  try {
    await updateName(formData.get('name'));
  } catch (e) {
    setError(e);
  } finally {
    setIsPending(false);
  }
}
```

在 React 19 中，**Actions** 让异步函数变得更加一等公民。React 会自动追踪异步操作的 `pending` 状态，并提供新的 Hook 来简化这一过程。

## 二、主角登场：useActionState

`useActionState` 是 React 19 中处理表单 Action 的核心 Hook。它取代了实验性的 `useFormState`。

### 基本用法

```javascript
import { useActionState } from 'react';

function ChangeName({ name, updateName }) {
  // state: Action 的返回值
  // action: 给 form 使用的提交函数
  // isPending: 是否正在提交
  const [state, action, isPending] = useActionState(async (previousState, formData) => {
    const error = await updateName(formData.get("name"));
    if (error) {
      return error;
    }
    return null;
  }, null);

  return (
    <form action={action}>
      <input type="text" name="name" disabled={isPending} />
      <button type="submit" disabled={isPending}>
        {isPending ? 'Updating...' : 'Update'}
      </button>
      {state && <p>{state}</p>}
    </form>
  );
}
```

### 核心优势
1. **自动 Pending 管理**：`isPending` 会根据异步函数的执行自动切换。
2. **状态共享**：`state` 可以存储后端返回的错误信息或成功结果。
3. **原生 Form 支持**：直接传递给 `<form action={action}>`，无缝集成。

## 三、配合 useFormStatus 使用

有时候，我们需要在表单深层的子组件中获取提交状态（例如：一个单独的 SubmitButton 组件）。这时可以使用 `useFormStatus`。

```javascript
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}
```

## 四、总结与建议

React 19 的 Actions 极大地减少了表单逻辑中的样板代码（Boilerplate）。
- **简单场景**：继续用 `useState`。
- **表单提交/异步数据更新**：强烈建议尝试 `useActionState`。

**如果你对 React 19 的其他特性（如 useOptimistic）感兴趣，欢迎在评论区留言！**
