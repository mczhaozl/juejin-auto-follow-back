# React useTransition：让 UI 更新更丝滑的并发特性

> 从原理到实战，掌握 React 18 并发渲染的核心 Hook

---

## 一、为什么需要 useTransition

在 React 中，所有状态更新默认都是紧急的，会立即阻塞 UI。

```javascript
function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);

  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);  // 紧急更新
    
    // 耗时的过滤操作
    const filtered = hugeList.filter(item => 
      item.name.includes(value)
    );
    setResults(filtered);  // 也是紧急更新，会卡顿
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      <Results data={results} />
    </>
  );
}
```

问题：输入时会卡顿，因为每次输入都要等待过滤完成。

---

## 二、useTransition 的解决方案

useTransition 可以将某些更新标记为"非紧急"，让 React 优先处理用户交互。

```javascript
import { useState, useTransition } from 'react';

function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    const value = e.target.value;
    setQuery(value);  // 紧急更新，立即响应
    
    startTransition(() => {
      // 非紧急更新，可以被打断
      const filtered = hugeList.filter(item => 
        item.name.includes(value)
      );
      setResults(filtered);
    });
  };

  return (
    <>
      <input value={query} onChange={handleChange} />
      {isPending && <Spinner />}
      <Results data={results} />
    </>
  );
}
```

效果：输入流畅，过滤操作在后台进行。

---

## 三、核心概念

### 返回值

```javascript
const [isPending, startTransition] = useTransition();
```

- `isPending`: 是否有待处理的 transition
- `startTransition`: 将更新标记为 transition

### 紧急 vs 非紧急更新

```javascript
// 紧急更新：立即执行，不可打断
setQuery(value);

// 非紧急更新：可以被打断，延迟执行
startTransition(() => {
  setResults(filtered);
});
```

---

## 四、实战场景

### 场景 1：搜索过滤

```javascript
function ProductList() {
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredProducts, setFilteredProducts] = useState(products);
  const [isPending, startTransition] = useTransition();

  const handleSearch = (value) => {
    setSearchTerm(value);
    
    startTransition(() => {
      const filtered = products.filter(p =>
        p.name.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredProducts(filtered);
    });
  };

  return (
    <>
      <input
        value={searchTerm}
        onChange={e => handleSearch(e.target.value)}
        placeholder="搜索商品..."
      />
      {isPending && <div className="loading">搜索中...</div>}
      <div className="products">
        {filteredProducts.map(p => (
          <ProductCard key={p.id} {...p} />
        ))}
      </div>
    </>
  );
}
```

### 场景 2：Tab 切换

```javascript
function TabContainer() {
  const [tab, setTab] = useState('home');
  const [isPending, startTransition] = useTransition();

  const handleTabChange = (newTab) => {
    startTransition(() => {
      setTab(newTab);  // 切换 tab 是非紧急的
    });
  };

  return (
    <>
      <div className="tabs">
        <button
          onClick={() => handleTabChange('home')}
          className={tab === 'home' ? 'active' : ''}
        >
          首页
        </button>
        <button
          onClick={() => handleTabChange('profile')}
          className={tab === 'profile' ? 'active' : ''}
        >
          个人中心
        </button>
      </div>
      
      {isPending && <LoadingBar />}
      
      <div className="tab-content">
        {tab === 'home' && <HomePage />}
        {tab === 'profile' && <ProfilePage />}
      </div>
    </>
  );
}
```

### 场景 3：路由切换

```javascript
function App() {
  const [page, setPage] = useState('home');
  const [isPending, startTransition] = useTransition();

  const navigate = (newPage) => {
    startTransition(() => {
      setPage(newPage);
    });
  };

  return (
    <>
      <nav>
        <button onClick={() => navigate('home')}>首页</button>
        <button onClick={() => navigate('about')}>关于</button>
        <button onClick={() => navigate('contact')}>联系</button>
      </nav>
      
      {isPending && <TopLoadingBar />}
      
      <main>
        {page === 'home' && <Home />}
        {page === 'about' && <About />}
        {page === 'contact' && <Contact />}
      </main>
    </>
  );
}
```

---

## 五、与 useDeferredValue 对比

```javascript
// useTransition：主动标记更新
const [isPending, startTransition] = useTransition();
startTransition(() => {
  setValue(newValue);
});

// useDeferredValue：被动延迟值
const deferredValue = useDeferredValue(value);
```

| 特性 | useTransition | useDeferredValue |
|------|--------------|------------------|
| 使用方式 | 包裹更新函数 | 包裹值 |
| 控制权 | 主动控制 | 被动延迟 |
| isPending | 有 | 无 |
| 适用场景 | 控制更新时机 | 延迟渲染 |

---

## 六、注意事项

### 1. 只能在 transition 中更新 state

```javascript
// ✅ 正确
startTransition(() => {
  setState(newValue);
});

// ❌ 错误：不能包含异步操作
startTransition(async () => {
  const data = await fetchData();
  setState(data);
});
```

### 2. 异步操作需要特殊处理

```javascript
const handleClick = async () => {
  const data = await fetchData();
  
  startTransition(() => {
    setState(data);  // 只有 setState 在 transition 中
  });
};
```

### 3. 不要过度使用

```javascript
// ❌ 不需要：简单的状态更新
startTransition(() => {
  setCount(count + 1);
});

// ✅ 需要：耗时的计算或渲染
startTransition(() => {
  setResults(expensiveFilter(data));
});
```

---

## 七、性能优化

### 配合 memo 使用

```javascript
const ExpensiveList = memo(({ items }) => {
  return items.map(item => <ExpensiveItem key={item.id} {...item} />);
});

function App() {
  const [query, setQuery] = useState('');
  const [items, setItems] = useState(allItems);
  const [isPending, startTransition] = useTransition();

  const handleSearch = (value) => {
    setQuery(value);
    startTransition(() => {
      setItems(allItems.filter(i => i.name.includes(value)));
    });
  };

  return (
    <>
      <input value={query} onChange={e => handleSearch(e.target.value)} />
      {isPending && <Spinner />}
      <ExpensiveList items={items} />
    </>
  );
}
```

---

## 八、与 Suspense 配合

```javascript
function App() {
  const [tab, setTab] = useState('home');
  const [isPending, startTransition] = useTransition();

  return (
    <>
      <Tabs value={tab} onChange={(t) => {
        startTransition(() => setTab(t));
      }} />
      
      <Suspense fallback={<Skeleton />}>
        {isPending && <InlineSpinner />}
        {tab === 'home' && <Home />}
        {tab === 'posts' && <Posts />}
      </Suspense>
    </>
  );
}
```

---

## 总结

useTransition 是 React 18 并发特性的核心，它让你能够：

- 区分紧急和非紧急更新
- 保持 UI 响应流畅
- 提供更好的用户体验
- 配合 Suspense 实现更复杂的加载状态

在处理耗时更新时，优先考虑使用 useTransition。

如果这篇文章对你有帮助，欢迎点赞收藏！
