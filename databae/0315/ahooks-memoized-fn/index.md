# ahooks useMemoizedFn：解决 useCallback 的依赖地狱

> 告别依赖数组，让函数引用永远稳定

---

## 一、useCallback 的痛点

在 React 中，我们经常用 useCallback 来缓存函数，避免子组件不必要的重渲染。

```javascript
function Parent() {
  const [count, setCount] = useState(0);
  const [text, setText] = useState('');

  const handleClick = useCallback(() => {
    console.log(count);
  }, [count]);  // 依赖 count

  return <Child onClick={handleClick} />;
}
```

问题：每次 count 变化，handleClick 都会重新创建，Child 还是会重渲染。

---

## 二、useMemoizedFn 的解决方案

useMemoizedFn 返回的函数引用永远不变，但内部总是能访问到最新的 state 和 props。

```javascript
import { useMemoizedFn } from 'ahooks';

function Parent() {
  const [count, setCount] = useState(0);

  const handleClick = useMemoizedFn(() => {
    console.log(count);  // 总是最新的 count
  });

  return <Child onClick={handleClick} />;
}
```

无论 count 如何变化，handleClick 的引用都不变，Child 不会重渲染。

---

## 三、与 useCallback 对比

```javascript
// useCallback：依赖变化时函数重新创建
const fn1 = useCallback(() => {
  doSomething(a, b, c);
}, [a, b, c]);  // 依赖地狱

// useMemoizedFn：引用永远不变
const fn2 = useMemoizedFn(() => {
  doSomething(a, b, c);  // 无需依赖数组
});
```

| 特性 | useCallback | useMemoizedFn |
|------|------------|---------------|
| 依赖数组 | 必须 | 不需要 |
| 引用稳定性 | 依赖变化时改变 | 永远不变 |
| 访问最新值 | 需要加入依赖 | 自动访问 |
| 使用复杂度 | 高 | 低 |

---

## 四、实战场景

### 场景 1：表单提交

```javascript
function Form() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);

  // ❌ useCallback：依赖太多
  const handleSubmit = useCallback(async () => {
    setLoading(true);
    await submitForm({ name, email });
    setLoading(false);
  }, [name, email]);  // 每次输入都会重新创建

  // ✅ useMemoizedFn：无需依赖
  const handleSubmit = useMemoizedFn(async () => {
    setLoading(true);
    await submitForm({ name, email });
    setLoading(false);
  });

  return (
    <form onSubmit={handleSubmit}>
      <input value={name} onChange={e => setName(e.target.value)} />
      <input value={email} onChange={e => setEmail(e.target.value)} />
      <button type="submit">提交</button>
    </form>
  );
}
```

### 场景 2：事件监听

```javascript
function ScrollTracker() {
  const [scrollTop, setScrollTop] = useState(0);

  // ❌ useCallback：每次 scrollTop 变化都重新绑定
  const handleScroll = useCallback(() => {
    console.log('当前位置:', scrollTop);
  }, [scrollTop]);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);  // handleScroll 变化导致重新绑定

  // ✅ useMemoizedFn：只绑定一次
  const handleScroll = useMemoizedFn(() => {
    console.log('当前位置:', scrollTop);
  });

  useEffect(() => {
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);  // 空依赖，只绑定一次
}
```

### 场景 3：传递给子组件

```javascript
function TodoList() {
  const [todos, setTodos] = useState([]);
  const [filter, setFilter] = useState('all');

  // ✅ 引用稳定，子组件不会重渲染
  const handleDelete = useMemoizedFn((id) => {
    setTodos(todos.filter(t => t.id !== id));
  });

  const handleToggle = useMemoizedFn((id) => {
    setTodos(todos.map(t => 
      t.id === id ? { ...t, done: !t.done } : t
    ));
  });

  return (
    <>
      <Filter value={filter} onChange={setFilter} />
      {todos.map(todo => (
        <TodoItem
          key={todo.id}
          {...todo}
          onDelete={handleDelete}  // 引用不变
          onToggle={handleToggle}  // 引用不变
        />
      ))}
    </>
  );
}

// 子组件用 memo 包裹，只在 props 变化时重渲染
const TodoItem = memo(({ id, text, done, onDelete, onToggle }) => {
  console.log('TodoItem render:', id);
  return (
    <div>
      <input
        type="checkbox"
        checked={done}
        onChange={() => onToggle(id)}
      />
      <span>{text}</span>
      <button onClick={() => onDelete(id)}>删除</button>
    </div>
  );
});
```

---

## 五、原理解析

useMemoizedFn 的核心思路：用 ref 存储最新的函数，返回一个永远不变的包装函数。

```javascript
function useMemoizedFn(fn) {
  const fnRef = useRef(fn);
  
  // 每次渲染都更新 ref
  fnRef.current = fn;
  
  // 返回的函数引用永远不变
  const memoizedFn = useRef((...args) => {
    return fnRef.current(...args);
  });
  
  return memoizedFn.current;
}
```

关键点：
1. fnRef 存储最新的函数
2. memoizedFn 是包装函数，引用不变
3. 调用时通过 fnRef.current 访问最新函数

---

## 六、注意事项

### 1. 不要在循环中使用

```javascript
// ❌ 错误：每次循环都创建新的 Hook
todos.map(todo => {
  const handleClick = useMemoizedFn(() => {
    deleteTodo(todo.id);
  });
  return <button onClick={handleClick}>删除</button>;
});

// ✅ 正确：在组件顶层创建
const handleDelete = useMemoizedFn((id) => {
  deleteTodo(id);
});

todos.map(todo => (
  <button onClick={() => handleDelete(todo.id)}>删除</button>
));
```

### 2. 异步函数也适用

```javascript
const fetchData = useMemoizedFn(async () => {
  const data = await api.getData();
  setData(data);
});

useEffect(() => {
  fetchData();
}, []);  // 空依赖，fetchData 引用不变
```

### 3. 配合 useEffect

```javascript
// ❌ useCallback：依赖变化导致 effect 重新执行
const fetchUser = useCallback(() => {
  return api.getUser(userId);
}, [userId]);

useEffect(() => {
  fetchUser().then(setUser);
}, [fetchUser]);  // fetchUser 变化导致重新请求

// ✅ useMemoizedFn：只在 userId 变化时请求
const fetchUser = useMemoizedFn(() => {
  return api.getUser(userId);
});

useEffect(() => {
  fetchUser().then(setUser);
}, [userId]);  // 只依赖 userId
```

---

## 七、性能测试

```javascript
function PerformanceTest() {
  const [count, setCount] = useState(0);
  const renderCount = useRef(0);

  // useCallback 版本
  const handleClick1 = useCallback(() => {
    console.log(count);
  }, [count]);

  // useMemoizedFn 版本
  const handleClick2 = useMemoizedFn(() => {
    console.log(count);
  });

  return (
    <>
      <button onClick={() => setCount(c => c + 1)}>
        Count: {count}
      </button>
      
      {/* 每次 count 变化，Child1 都会重渲染 */}
      <Child1 onClick={handleClick1} />
      
      {/* Child2 永远不会重渲染 */}
      <Child2 onClick={handleClick2} />
    </>
  );
}

const Child1 = memo(({ onClick }) => {
  console.log('Child1 render');
  return <button onClick={onClick}>Click</button>;
});

const Child2 = memo(({ onClick }) => {
  console.log('Child2 render');
  return <button onClick={onClick}>Click</button>;
});
```

结果：
- Child1：每次 count 变化都重渲染
- Child2：只渲染一次

---

## 八、何时使用

### 适合使用 useMemoizedFn

1. 函数需要传递给子组件
2. 函数作为 useEffect 的依赖
3. 函数需要绑定到 DOM 事件
4. 函数依赖很多 state/props

### 不需要使用

1. 函数不传递给子组件
2. 函数内部没有闭包变量
3. 性能不是瓶颈

```javascript
// 不需要：函数不传递给子组件
const handleClick = () => {
  console.log('clicked');
};

// 需要：传递给子组件
const handleClick = useMemoizedFn(() => {
  console.log('clicked');
});
return <Child onClick={handleClick} />;
```

---

## 九、与其他方案对比

### vs useCallback

```javascript
// useCallback：需要维护依赖
const fn = useCallback(() => {
  doSomething(a, b, c);
}, [a, b, c]);

// useMemoizedFn：无需依赖
const fn = useMemoizedFn(() => {
  doSomething(a, b, c);
});
```

### vs useEvent (React RFC)

React 团队提出的 useEvent 与 useMemoizedFn 思路类似，但还未正式发布。

```javascript
// React useEvent (未来)
const handleClick = useEvent(() => {
  console.log(count);
});

// ahooks useMemoizedFn (现在可用)
const handleClick = useMemoizedFn(() => {
  console.log(count);
});
```

---

## 十、最佳实践

1. **优先使用 useMemoizedFn**：在需要缓存函数时，优先考虑 useMemoizedFn

2. **配合 memo 使用**：子组件用 memo 包裹，才能体现性能优势

```javascript
const Child = memo(({ onClick }) => {
  return <button onClick={onClick}>Click</button>;
});
```

3. **不要过度优化**：如果组件渲染本身很快，不需要优化

4. **统一团队规范**：在团队中统一使用 useMemoizedFn 或 useCallback

---

## 总结

useMemoizedFn 是 useCallback 的更好替代方案，它：

- 无需维护依赖数组
- 函数引用永远稳定
- 总是访问最新的 state/props
- 减少心智负担

在需要缓存函数的场景下，推荐优先使用 useMemoizedFn。

如果这篇文章对你有帮助，欢迎点赞收藏！
