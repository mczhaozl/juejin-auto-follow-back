# 深入理解React 19中的Actions与useActionState

> 全面解析React 19的Actions新特性，详解useActionState、useFormStatus等API的用法与最佳实践，助你快速上手React 19。

## 一、引言

React 19 带来了革命性的表单处理方式——**Actions**。这一新特性让表单提交和状态管理变得更加简单和直观。本文将深入解析 Actions 的工作机制。

## 二、什么是Actions

### 2.1 Actions的基本概念

Actions 是一种在 React 中处理表单提交和数据更新的新方式：

```javascript
// 传统的表单提交
function TraditionalForm() {
  const [loading, setLoading] = useState(false);
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    await submitData(new FormData(e.target));
    setLoading(false);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input name="title" />
      <button disabled={loading}>
        {loading ? '提交中...' : '提交'}
      </button>
    </form>
  );
}

// 使用 Actions（React 19）
async function action(formData) {
  'use server';
  await submitData(formData);
}

function ActionForm() {
  return (
    <form action={action}>
      <input name="title" />
      <button type="submit">提交</button>
    </form>
  );
}
```

## 三、useActionState 详解

### 3.1 基本用法

```javascript
'use client';
import { useActionState } from 'react';

async function createItem(prevState, formData) {
  const title = formData.get('title');
  
  try {
    await db.items.create({ title });
    return { success: true, message: '创建成功' };
  } catch (error) {
    return { success: false, message: error.message };
  }
}

function CreateForm() {
  const [state, dispatch, isPending] = useActionState(createItem, null);
  
  return (
    <form action={dispatch}>
      <input name="title" />
      <button disabled={isPending}>
        {isPending ? '提交中...' : '提交'}
      </button>
      {state?.message && <p>{state.message}</p>}
    </form>
  );
}
```

### 3.2 useActionState 返回值

```javascript
const [state, dispatch, isPending] = useActionState(action, initialState);
```

- **state**：Actions 的当前状态
- **dispatch**：用于触Actions 的函数
- **isPending**：表示 Actions 是否正在执行

### 3.3 状态持久化

```javascript
function Counter() {
  const [count, setCount] = useState(0);
  
  const [state, dispatch, isPending] = useActionState(
    async (prev, delta) => {
      const newCount = prev + delta;
      await saveToDatabase(newCount);
      return newCount;
    },
    count
  );
  
  return (
    <div>
      <p>当前计数: {state}</p>
      <button onClick={() => dispatch(1)} disabled={isPending}>
        +1
      </button>
    </div>
  );
}
```

## 四、useFormStatus 详解

### 4.1 基本用法

```javascript
import { useFormStatus } from 'react';

function SubmitButton() {
  const { pending, data, method, action } = useFormStatus();
  
  return (
    <button disabled={pending}>
      {pending ? '提交中...' : '提交'}
    </button>
  );
}

function MyForm() {
  return (
    <form action={asyncAction}>
      <input name="name" />
      <SubmitButton />
    </form>
  );
}
```

### 4.2 useFormStatus 返回值

| 属性 | 说明 |
|------|------|
| pending | 是否有提交正在进行 |
| data | 表单数据 FormData |
| method | 表单提交方法 GET/POST |
| action | 表单提交的 action |

## 五、useFormAction

### 5.1 自动继承表单action

```javascript
import { useFormAction } from 'react';

function MyInput() {
  const defaultAction = useFormAction();
  
  return (
    <input 
      name="title" 
      formAction={defaultAction}
    />
  );
}
```

## 六、实战：构建完整的表单系统

### 6.1 用户注册表单

```javascript
'use client';

async function register(prevState, formData) {
  const email = formData.get('email');
  const password = formData.get('password');
  
  // 验证
  if (!email.includes('@')) {
    return { error: '邮箱格式不正确' };
  }
  
  if (password.length < 6) {
    return { error: '密码至少6位' };
  }
  
  try {
    await auth.register({ email, password });
    return { success: true, message: '注册成功！' };
  } catch (error) {
    return { error: error.message };
  }
}

function RegisterForm() {
  const [state, dispatch, pending] = useActionState(register, null);
  
  return (
    <form action={dispatch}>
      <div>
        <label>邮箱</label>
        <input name="email" type="email" required />
      </div>
      <div>
        <label>密码</label>
        <input name="password" type="password" required />
      </div>
      {state?.error && <p className="error">{state.error}</p>}
      {state?.success && <p className="success">{state.message}</p>}
      <SubmitButton />
    </form>
  );
}
```

### 6.2 删除确认对话框

```javascript
async function deleteItem(prevState, formData) {
  const id = formData.get('id');
  
  try {
    await db.items.delete(id);
    return { success: true };
  } catch (error) {
    return { error: error.message };
  }
}

function DeleteButton({ itemId }) {
  return (
    <form action={useActionState(deleteItem, null)}>
      <input type="hidden" name="id" value={itemId} />
      <button type="submit">删除</button>
    </form>
  );
}
```

## 七、Server Actions 进阶

### 7.1 调用Server Actions

```javascript
'use client';

import { callServer } from 'react';

async function serverAction(data) {
  'use server';
  console.log('Server:', data);
  return 'Server Response';
}

function ClientComponent() {
  const handleClick = async () => {
    const result = await callServer(serverAction, 'Hello');
    console.log(result);
  };
  
  return <button onClick={handleClick}>调用</button>;
}
```

### 7.2 乐观更新

```javascript
'use client';

function TodoItem({ todo, onUpdate }) {
  const [optimistic, setOptimistic] = useOptimistic(
    todo,
    (state, newStatus) => ({ ...state, status: newStatus })
  );
  
  const handleToggle = async () => {
    const newStatus = todo.status === 'active' ? 'completed' : 'active';
    setOptimistic(newStatus);
    await updateTodoStatus(todo.id, newStatus);
  };
  
  return (
    <div className={optimistic.status}>
      {todo.title}
      <button onClick={handleToggle}>切换状态</button>
    </div>
  );
}
```

## 八、最佳实践

### 8.1 表单验证

```javascript
async function validateForm(prevState, formData) {
  const errors = {};
  
  const email = formData.get('email');
  if (!email || !email.includes('@')) {
    errors.email = '请输入有效的邮箱地址';
  }
  
  const password = formData.get('password');
  if (!password || password.length < 8) {
    errors.password = '密码至少8位';
  }
  
  if (Object.keys(errors).length > 0) {
    return { errors, values: { email, password } };
  }
  
  // 提交数据
  try {
    await submitData(formData);
    return { success: true };
  } catch (error) {
    return { error: error.message };
  }
}
```

### 8.2 错误处理

```javascript
function Form() {
  const [state, dispatch] = useActionState(submitAction, null);
  
  return (
    <form action={dispatch}>
      {/* 表单内容 */}
      {state?.errors?.field && (
        <span className="error">{state.errors.field}</span>
      )}
    </form>
  );
}
```

## 九、总结

React 19 的 Actions 为表单处理带来了革命性的变化：

1. **useActionState**：简化状态管理，让表单状态和业务逻辑分离
2. **useFormStatus**：轻松获取表单提交状态
3. **Server Actions**：前后端代码更清晰

这些新特性让 React 应用的开发变得更加高效和优雅。

---

**推荐阅读**：
- [React 19 Beta 文档](https://react.dev/blog/2024/04/25/react-19)
- [React Server Actions 指南](https://react.dev/reference/rsc/server-actions)

**如果对你有帮助，欢迎点赞收藏！**
