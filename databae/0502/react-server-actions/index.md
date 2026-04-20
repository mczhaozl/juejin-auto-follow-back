# React Server Actions 深度实战指南

## 一、Server Actions 概述

### 1.1 什么是 Server Actions

在服务器端执行的函数，用于处理表单提交、数据变更等。

### 1.2 优势

- 直接操作数据库
- 隐藏敏感逻辑
- 自动 CSRF 防护
- 渐进增强

---

## 二、基本用法

### 2.1 简单表单

```tsx
// app/actions.ts
'use server';

export async function createUser(formData: FormData) {
  const name = formData.get('name') as string;
  const email = formData.get('email') as string;
  
  await db.users.create({ data: { name, email } });
  
  revalidatePath('/users');
}

// app/page.tsx
import { createUser } from './actions';

export default function CreateUserPage() {
  return (
    <form action={createUser}>
      <input type="text" name="name" required />
      <input type="email" name="email" required />
      <button type="submit">创建用户</button>
    </form>
  );
}
```

### 2.2 返回值

```tsx
'use server';

import { revalidatePath } from 'next/cache';

export async function createPost(formData: FormData) {
  try {
    const title = formData.get('title') as string;
    const content = formData.get('content') as string;
    
    const post = await db.posts.create({ data: { title, content } });
    
    revalidatePath('/posts');
    
    return { success: true, postId: post.id };
  } catch (error) {
    return { success: false, error: '创建失败' };
  }
}
```

---

## 三、useActionState

### 3.1 处理状态

```tsx
'use client';

import { useActionState } from 'react';
import { createPost } from './actions';

export default function CreatePostForm() {
  const [state, formAction] = useActionState(createPost, null);
  
  return (
    <form action={formAction}>
      <input type="text" name="title" required />
      <textarea name="content" required />
      <button type="submit">发布</button>
      
      {state?.error && <p className="text-red-500">{state.error}</p>}
      {state?.success && <p className="text-green-500">发布成功！</p>}
    </form>
  );
}
```

---

## 四、useFormStatus

### 4.1 加载状态

```tsx
'use client';

import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending } = useFormStatus();
  
  return (
    <button type="submit" disabled={pending}>
      {pending ? '提交中...' : '提交'}
    </button>
  );
}

export default function MyForm() {
  return (
    <form action={myAction}>
      <input type="text" name="data" />
      <SubmitButton />
    </form>
  );
}
```

---

## 五、useOptimistic

### 5.1 乐观更新

```tsx
'use client';

import { useOptimistic } from 'react';

function TodoList({ initialTodos, addTodo }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    initialTodos,
    (state, newTodo) => [...state, newTodo]
  );
  
  async function handleSubmit(formData: FormData) {
    const text = formData.get('text') as string;
    addOptimisticTodo({ id: Date.now(), text, completed: false });
    await addTodo(text);
  }
  
  return (
    <div>
      <form action={handleSubmit}>
        <input type="text" name="text" />
        <button type="submit">添加</button>
      </form>
      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id}>{todo.text}</li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 六、高级用法

### 6.1 嵌套对象

```tsx
'use server';

export async function updateUser(data: {
  id: string;
  name: string;
  email: string;
}) {
  await db.users.update({
    where: { id: data.id },
    data: { name: data.name, email: data.email }
  });
}

// 使用
'use client';

import { updateUser } from './actions';

export default function EditUser({ user }) {
  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    await updateUser({
      id: user.id,
      name: formData.get('name') as string,
      email: formData.get('email') as string
    });
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input type="text" name="name" defaultValue={user.name} />
      <input type="email" name="email" defaultValue={user.email} />
      <button type="submit">保存</button>
    </form>
  );
}
```

### 6.2 错误处理

```tsx
'use server';

export async function deletePost(id: string) {
  const post = await db.posts.findUnique({ where: { id } });
  
  if (!post) {
    throw new Error('文章不存在');
  }
  
  await db.posts.delete({ where: { id } });
  revalidatePath('/posts');
}

// 使用
'use client';

import { useActionState } from 'react';
import { deletePost } from './actions';

function DeleteButton({ postId }) {
  const [state, deleteAction] = useActionState(
    async (_, id) => {
      try {
        await deletePost(id);
        return { success: true };
      } catch (err) {
        return { error: err.message };
      }
    },
    null
  );
  
  return (
    <form action={() => deleteAction(postId)}>
      <button type="submit">删除</button>
      {state?.error && <p>{state.error}</p>}
    </form>
  );
}
```

---

## 七、实战示例

### 7.1 待办事项

```tsx
// app/actions.ts
'use server';

import { revalidatePath } from 'next/cache';

export async function addTodo(text: string) {
  const todo = await db.todo.create({ data: { text, completed: false } });
  revalidatePath('/todos');
  return todo;
}

export async function toggleTodo(id: string) {
  const todo = await db.todo.findUnique({ where: { id } });
  await db.todo.update({
    where: { id },
    data: { completed: !todo.completed }
  });
  revalidatePath('/todos');
}

export async function deleteTodo(id: string) {
  await db.todo.delete({ where: { id } });
  revalidatePath('/todos');
}

// app/todos/page.tsx
import { addTodo, toggleTodo, deleteTodo } from '../actions';
import TodoList from './todo-list';

export default async function TodosPage() {
  const todos = await db.todo.findMany();
  return <TodoList todos={todos} />;
}

// app/todos/todo-list.tsx
'use client';

import { useOptimistic } from 'react';
import { addTodo, toggleTodo, deleteTodo } from '../actions';

export default function TodoList({ initialTodos }) {
  const [optimisticTodos, setOptimisticTodos] = useOptimistic(
    initialTodos,
    (state, update) => {
      if (update.type === 'add') {
        return [...state, update.todo];
      }
      if (update.type === 'toggle') {
        return state.map(t =>
          t.id === update.id ? { ...t, completed: !t.completed } : t
        );
      }
      if (update.type === 'delete') {
        return state.filter(t => t.id !== update.id);
      }
      return state;
    }
  );
  
  async function handleAddTodo(formData: FormData) {
    const text = formData.get('text') as string;
    setOptimisticTodos({
      type: 'add',
      todo: { id: Date.now().toString(), text, completed: false }
    });
    await addTodo(text);
  }
  
  async function handleToggle(id: string) {
    setOptimisticTodos({ type: 'toggle', id });
    await toggleTodo(id);
  }
  
  async function handleDelete(id: string) {
    setOptimisticTodos({ type: 'delete', id });
    await deleteTodo(id);
  }
  
  return (
    <div>
      <form action={handleAddTodo}>
        <input type="text" name="text" required />
        <button type="submit">添加</button>
      </form>
      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id}>
            <span
              style={{ textDecoration: todo.completed ? 'line-through' : 'none' }}
              onClick={() => handleToggle(todo.id)}
            >
              {todo.text}
            </span>
            <button onClick={() => handleDelete(todo.id)}>删除</button>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

---

## 八、最佳实践

### 8.1 验证输入

```tsx
'use server';

import { z } from 'zod';

const PostSchema = z.object({
  title: z.string().min(5),
  content: z.string().min(10)
});

export async function createPost(formData: FormData) {
  const parsed = PostSchema.safeParse({
    title: formData.get('title'),
    content: formData.get('content')
  });
  
  if (!parsed.success) {
    return { error: parsed.error.flatten() };
  }
  
  await db.posts.create({ data: parsed.data });
  revalidatePath('/posts');
  return { success: true };
}
```

### 8.2 权限检查

```tsx
'use server';

export async function deletePost(id: string) {
  const session = await getSession();
  
  if (!session?.user) {
    throw new Error('未登录');
  }
  
  const post = await db.posts.findUnique({ where: { id } });
  
  if (post?.authorId !== session.user.id) {
    throw new Error('无权删除');
  }
  
  await db.posts.delete({ where: { id } });
  revalidatePath('/posts');
}
```

---

## 总结

Server Actions 简化了服务器端数据操作，配合 useOptimistic、useFormStatus 可以实现流畅的用户体验。
