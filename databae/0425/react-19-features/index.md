# React 19 新特性完全指南：从基础到实战

React 19 带来了许多令人兴奋的新特性。本文将带你全面掌握这些新特性。

## 一、React 19 新特性概览

```
React 19 核心改进：
- Actions: 处理表单提交和数据变更
- useOptimistic: 乐观更新
- use: 新的 Hook 用于读取 Promise 和 Context
- Document Metadata: 内置 SEO 支持
- Server Components: 改进的服务端组件
- 性能优化: 自动批处理、编译器改进
- 开发者体验: 更好的错误提示
```

## 二、Actions

### 1. 基础使用

```jsx
import { useActionState } from 'react';

async function submitForm(prevState, formData) {
  const name = formData.get('name');
  const email = formData.get('email');
  
  try {
    const response = await fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify({ name, email })
    });
    
    if (!response.ok) {
      return { error: 'Failed to create user' };
    }
    
    return { success: true };
  } catch (error) {
    return { error: error.message };
  }
}

function Form() {
  const [state, formAction] = useActionState(submitForm, { error: null, success: false });
  
  return (
    <form action={formAction}>
      <input name="name" placeholder="Name" required />
      <input name="email" type="email" placeholder="Email" required />
      <button type="submit">Submit</button>
      
      {state.error && <p className="error">{state.error}</p>}
      {state.success && <p className="success">User created!</p>}
    </form>
  );
}
```

### 2. useFormStatus

```jsx
import { useFormStatus, useActionState } from 'react';

function SubmitButton() {
  const { pending } = useFormStatus();
  
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Submitting...' : 'Submit'}
    </button>
  );
}

function Form() {
  const [state, formAction] = useActionState(submitForm, initialState);
  
  return (
    <form action={formAction}>
      <input name="name" />
      <SubmitButton />
    </form>
  );
}
```

### 3. useOptimistic

```jsx
import { useOptimistic, useState } from 'react';

function TodoList() {
  const [todos, setTodos] = useState([]);
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, { ...newTodo, id: Date.now(), optimistic: true }]
  );
  
  const addTodo = async (text) => {
    const tempTodo = { text, completed: false };
    
    addOptimisticTodo(tempTodo);
    
    try {
      const response = await fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify(tempTodo)
      });
      const savedTodo = await response.json();
      setTodos(prev => [...prev, savedTodo]);
    } catch (error) {
      // 乐观更新失败，显示错误
    }
  };
  
  return (
    <div>
      {optimisticTodos.map(todo => (
        <div key={todo.id}>
          {todo.text}
          {todo.optimistic && <span>(Saving...)</span>}
        </div>
      ))}
      <button onClick={() => addTodo('New Todo')}>Add Todo</button>
    </div>
  );
}
```

## 三、use Hook

### 1. 读取 Promise

```jsx
import { use, Suspense } from 'react';

async function fetchData() {
  const res = await fetch('/api/data');
  return res.json();
}

function DataComponent() {
  const data = use(fetchData());
  return <div>{data.message}</div>;
}

function App() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <DataComponent />
    </Suspense>
  );
}
```

### 2. 读取 Context

```jsx
import { createContext, use } from 'react';

const ThemeContext = createContext('light');

function ThemeButton() {
  const theme = use(ThemeContext);
  return (
    <button style={{ background: theme === 'dark' ? '#333' : '#fff' }}>
      Click me
    </button>
  );
}

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <ThemeButton />
    </ThemeContext.Provider>
  );
}
```

## 四、Document Metadata

```jsx
import { Title, Meta, Link } from 'react';

function Page() {
  return (
    <div>
      <Title>My Page Title</Title>
      <Meta name="description" content="This is my page description" />
      <Meta property="og:title" content="Open Graph Title" />
      <Link rel="canonical" href="https://example.com/page" />
      
      <h1>Hello World</h1>
    </div>
  );
}

// 服务端组件中使用
export default function BlogPost({ post }) {
  return (
    <article>
      <Title>{post.title}</Title>
      <Meta name="description" content={post.excerpt} />
      
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  );
}
```

## 五、Server Components 改进

### 1. 数据获取

```jsx
// 服务端组件
async function BlogPosts() {
  const posts = await fetch('https://api.example.com/posts', {
    cache: 'force-cache'
  }).then(res => res.json());
  
  return (
    <ul>
      {posts.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}

// 增量静态再生成
export default async function Page({ params }) {
  const post = await fetch(`https://api.example.com/posts/${params.id}`, {
    next: { revalidate: 60 }
  }).then(res => res.json());
  
  return <Post post={post} />;
}

export async function generateStaticParams() {
  const posts = await fetch('https://api.example.com/posts').then(res => res.json());
  
  return posts.map(post => ({
    id: post.id.toString()
  }));
}
```

### 2. 客户端组件

```jsx
'use client';

import { useState, useEffect } from 'react';

export default function InteractiveComponent() {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    console.log('Component mounted');
  }, []);
  
  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

## 六、useActionState 进阶

```jsx
import { useActionState, useOptimistic } from 'react';

async function updateTodo(prevState, formData) {
  const id = formData.get('id');
  const text = formData.get('text');
  
  try {
    const response = await fetch(`/api/todos/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ text })
    });
    
    if (!response.ok) {
      return { ...prevState, error: 'Update failed' };
    }
    
    return { ...prevState, error: null, success: true };
  } catch (error) {
    return { ...prevState, error: error.message };
  }
}

function TodoItem({ todo }) {
  const [state, formAction] = useActionState(updateTodo, { error: null, success: false });
  const [optimisticTodo, setOptimisticTodo] = useOptimistic(todo);
  
  const handleSubmit = (formData) => {
    const newText = formData.get('text');
    setOptimisticTodo({ ...optimisticTodo, text: newText });
    return formAction(formData);
  };
  
  return (
    <form action={handleSubmit}>
      <input type="hidden" name="id" value={todo.id} />
      <input name="text" defaultValue={optimisticTodo.text} />
      <button type="submit">Update</button>
      
      {state.error && <p className="error">{state.error}</p>}
    </form>
  );
}
```

## 七、性能优化

### 1. 自动批处理

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');
  
  function handleClick() {
    // React 19 自动批处理这些更新
    setCount(c => c + 1);
    setText('Hello');
  }
  
  return (
    <div>
      <p>Count: {count}</p>
      <p>Text: {text}</p>
      <button onClick={handleClick}>Click</button>
    </div>
  );
}
```

### 2. React Compiler

```jsx
// React Compiler 自动优化
function ExpensiveComponent({ items, filter }) {
  const filteredItems = items.filter(item => item.includes(filter));
  
  return (
    <div>
      {filteredItems.map(item => (
        <div key={item}>{item}</div>
      ))}
    </div>
  );
}

// 不需要 useMemo，React Compiler 自动处理
```

## 八、错误处理改进

```jsx
import { ErrorBoundary } from 'react-error-boundary';

function Fallback({ error, resetErrorBoundary }) {
  return (
    <div>
      <h2>Something went wrong:</h2>
      <p>{error.message}</p>
      <button onClick={resetErrorBoundary}>Try again</button>
    </div>
  );
}

function App() {
  return (
    <ErrorBoundary FallbackComponent={Fallback}>
      <MyComponent />
    </ErrorBoundary>
  );
}

// use 中的错误处理
function DataComponent() {
  try {
    const data = use(fetchData());
    return <div>{data.message}</div>;
  } catch (error) {
    return <div>Error: {error.message}</div>;
  }
}
```

## 九、完整示例：Todo 应用

```jsx
import { 
  useState, 
  useActionState, 
  useOptimistic, 
  useFormStatus,
  Suspense 
} from 'react';

async function addTodo(prevState, formData) {
  const text = formData.get('text');
  
  try {
    const response = await fetch('/api/todos', {
      method: 'POST',
      body: JSON.stringify({ text, completed: false })
    });
    
    if (!response.ok) {
      return { ...prevState, error: 'Failed to add todo' };
    }
    
    const newTodo = await response.json();
    return { ...prevState, error: null, todos: [...prevState.todos, newTodo] };
  } catch (error) {
    return { ...prevState, error: error.message };
  }
}

function SubmitButton() {
  const { pending } = useFormStatus();
  return (
    <button type="submit" disabled={pending}>
      {pending ? 'Adding...' : 'Add Todo'}
    </button>
  );
}

function TodoForm({ initialTodos }) {
  const [state, formAction] = useActionState(addTodo, { 
    todos: initialTodos, 
    error: null 
  });
  const [optimisticTodos, addOptimistic] = useOptimistic(
    state.todos,
    (todos, text) => [...todos, { id: Date.now(), text, completed: false, optimistic: true }]
  );
  
  const handleSubmit = async (formData) => {
    const text = formData.get('text');
    addOptimistic(text);
    return formAction(formData);
  };
  
  return (
    <div>
      <form action={handleSubmit}>
        <input name="text" placeholder="New todo" required />
        <SubmitButton />
      </form>
      
      {state.error && <p className="error">{state.error}</p>}
      
      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id} style={{ opacity: todo.optimistic ? 0.5 : 1 }}>
            {todo.text}
            {todo.optimistic && ' (Saving...)'}
          </li>
        ))}
      </ul>
    </div>
  );
}

async function fetchTodos() {
  const res = await fetch('/api/todos');
  return res.json();
}

function App() {
  return (
    <div className="app">
      <h1>Todo App</h1>
      <Suspense fallback={<div>Loading todos...</div>}>
        <TodoList />
      </Suspense>
    </div>
  );
}

async function TodoList() {
  const todos = await fetchTodos();
  return <TodoForm initialTodos={todos} />;
}

export default App;
```

## 十、最佳实践

1. 使用 Actions 处理表单和数据变更
2. 结合 useOptimistic 实现乐观更新
3. 用 use Hook 读取 Promise 和 Context
4. 利用 Document Metadata 提升 SEO
5. 合理使用 Server Components 和 Client Components
6. 错误边界处理错误
7. 利用 React Compiler 优化性能
8. 使用 Suspense 处理加载状态
9. useFormStatus 显示加载状态
10. 遵循服务端渲染最佳实践

## 十一、总结

React 19 核心新特性：
- Actions（useActionState）
- useOptimistic 乐观更新
- use Hook（Promise/Context）
- Document Metadata
- Server Components 改进
- 性能优化（自动批处理、React Compiler）
- 更好的错误处理

开始使用 React 19 新特性吧！
