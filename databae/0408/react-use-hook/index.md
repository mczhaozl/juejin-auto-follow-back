# React 19 use Hook 深度解析：颠覆异步数据与 Context 的全新 API

> 全面解析 React 19 全新的 use API，包括 use、useContext、useOptimistic 等，看 React 如何重新定义数据获取。

## 一、React 19 的新变革

React 19 带来了革命性的 `use` API，它重新定义了数据获取和状态管理的方式。

### 1.1 传统 vs React 19

```javascript
// 传统方式
function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetch(`/api/users/${userId}`)
      .then(res => res.json())
      .then(setUser);
  }, [userId]);
  
  if (!user) return <Skeleton />;
  return <div>{user.name}</div>;
}

// React 19 use 方式
async function getUser(userId) {
  const res = await fetch(`/api/users/${userId}`);
  return res.json();
}

function UserProfile({ userId }) {
  const user = use(getUser(userId));
  return <div>{user.name}</div>;
}
```

## 二、use() 基本用法

### 2.1 Promise 数据获取

```javascript
function TodoList() {
  const todos = use(fetch('/api/todos').then(r => r.json()));
  
  return (
    <ul>
      {todos.map(todo => (
        <li key={todo.id}>{todo.title}</li>
      ))}
    </ul>
  );
}
```

### 2.2 错误处理

```javascript
function UserData({ userId }) {
  const user = use(fetchUser(userId));
  
  return <div>{user.name}</div>;
}

// 父组件处理错误
function App() {
  return (
    <ErrorBoundary fallback={<ErrorPage />}>
      <UserData userId={1} />
    </ErrorBoundary>
  );
}
```

### 2.3 竞态处理

React 19 自动处理竞态条件：

```javascript
function SearchResults({ query }) {
  const results = use(searchAPI(query));
  // React 19 自动取消过时的请求
  // 无需手动处理 cleanup
  
  return <List items={results} />;
}
```

## 三、use Context

### 3.1 简化用法

```javascript
// 之前
function Toolbar() {
  const theme = useContext(ThemeContext);
  return <button className={theme}>Click</button>;
}

// React 19
function Toolbar() {
  const theme = use(ThemeContext);
  return <button className={theme}>Click</button>;
}
```

### 3.2 条件性 Context

```javascript
function ConditionalComponent() {
  if (!isLoggedIn) {
    return <LoginPrompt />;
  }
  
  // 只在登录后才读取 Context
  const user = use(UserContext);
  return <Welcome user={user} />;
}
```

### 3.3 动态 Context

```javascript
function ThemedButton({ theme }) {
  const value = use(ThemeContext);
  return <button style={value[theme]}>Click</button>;
}
```

## 四、useOptimistic

### 4.1 基础用法

```javascript
function LikeButton({ initialLikes }) {
  const [likes, setLikes] = useOptimistic(
    initialLikes,
    (state, newLike) => state + newLike
  );
  
  async function handleLike() {
    setLikes(1); // 立即更新 UI
    await likePost(); // 后台发送请求
  }
  
  return <button onClick={handleLike}>👍 {likes}</button>;
}
```

### 4.2 完整示例

```javascript
function TodoApp() {
  const [todos, setTodos] = useState([]);
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (state, newTodo) => [...state, { ...newTodo, pending: true }]
  );
  
  async function createTodo(title) {
    addOptimisticTodo({ id: Date.now(), title, completed: false });
    await saveTodo(title);
    refetch();
  }
  
  return (
    <ul>
      {optimisticTodos.map(todo => (
        <li key={todo.id} style={{ opacity: todo.pending ? 0.5 : 1 }}>
          {todo.title}
        </li>
      ))}
    </ul>
  );
}
```

## 五、useActionState

### 5.1 表单状态管理

```javascript
import { useActionState } from 'react';

async function submitForm(prevState, formData) {
  const email = formData.get('email');
  const error = await validateEmail(email);
  
  if (error) {
    return { error, success: false };
  }
  
  await saveEmail(email);
  return { error: null, success: true };
}

function SubscribeForm() {
  const [state, formAction, isPending] = useActionState(submitForm, null);
  
  return (
    <form action={formAction}>
      <input name="email" type="email" required />
      <button type="submit" disabled={isPending}>
        {isPending ? '提交中...' : '订阅'}
      </button>
      {state?.error && <p>{state.error}</p>}
      {state?.success && <p>订阅成功!</p>}
    </form>
  );
}
```

### 5.2 加载状态

```javascript
function LoginForm() {
  const [state, action, isPending] = useActionState(login, {
    error: null
  });
  
  return (
    <form action={action}>
      <button disabled={isPending}>
        {isPending ? '登录中...' : '登录'}
      </button>
    </form>
  );
}
```

## 六、useDeferredValue

### 6.1 优化渲染

```javascript
function SearchResults({ query }) {
  const deferredQuery = useDeferredValue(query);
  
  // 使用 deferredQuery 进行昂贵计算
  const results = useMemo(
    () => expensiveSearch(deferredQuery),
    [deferredQuery]
  );
  
  return <List items={results} />;
}
```

### 6.2 配合 Suspense

```javascript
function SearchPage({ query }) {
  const deferredQuery = useDeferredValue(query);
  
  return (
    <Suspense fallback={<Loading />}>
      <SearchResults query={deferredQuery} />
    </Suspense>
  );
}
```

## 七、useTransition

### 7.1 状态切换

```javascript
function TabContainer() {
  const [isPending, startTransition] = useTransition();
  const [activeTab, setActiveTab] = useState('posts');
  
  function handleTabChange(tab) {
    startTransition(() => {
      setActiveTab(tab);
    });
  }
  
  return (
    <div>
      {isPending && <Spinner />}
      <Tabs active={activeTab} onChange={handleTabChange} />
      <Content tab={activeTab} />
    </div>
  );
}
```

### 7.2 搜索示例

```javascript
function Search() {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();
  
  function handleChange(e) {
    startTransition(() => {
      setQuery(e.target.value);
    });
  }
  
  return (
    <div>
      <input onChange={handleChange} />
      {isPending ? <Loading /> : <Results query={query} />}
    </div>
  );
}
```

## 八、组合使用

### 8.1 完整数据流

```javascript
function UserTimeline({ userId }) {
  const user = use(fetchUser(userId));
  const posts = use(fetchPosts(userId));
  const [optimisticLike, addLike] = useOptimistic(
    posts,
    (state, postId) => state.map(p => 
      p.id === postId ? { ...p, likes: p.likes + 1 } : p
    )
  );
  
  return (
    <div>
      <Profile user={user} />
      <PostList 
        posts={optimisticLike} 
        onLike={addLike} 
      />
    </div>
  );
}
```

### 8.2 SSR 数据获取

```javascript
// 服务端
const userData = await fetchUser(1);
const initialState = userData;

// 客户端
function UserProfile({ initialData }) {
  const [data, setData] = useState(initialData);
  const freshData = use(fetchUser(1));
  
  return <Display data={freshData || data} />;
}
```

## 九、总结

React 19 use API 的核心改进：

1. **use()**：简化异步数据获取，自动处理竞态
2. **useOptimistic**：即时 UI 更新，后台同步
3. **useActionState**：简化表单状态管理
4. **useDeferredValue**：优化昂贵计算
5. **useTransition**：控制优先级

这些 API 让数据获取和状态管理变得更简单、更强大！

---

**推荐阅读**：
- [React 19 Beta 文档](https://react.dev/blog/2024/04/25/react-19)
- [use() API 详解](https://react.dev/reference/react/use)

**如果对你有帮助，欢迎点赞收藏！**
