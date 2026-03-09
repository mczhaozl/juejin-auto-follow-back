# ahooks useDebounce 与 useThrottle：防抖节流的最佳实践

> 从原理到实战，掌握 ahooks 中防抖节流的正确用法与性能优化

---

## 一、为什么需要防抖和节流

在处理高频事件时（如搜索输入、窗口滚动、按钮点击），如果每次都触发处理函数，会导致性能问题。

```javascript
// ❌ 问题：每次输入都发请求
<input onChange={(e) => searchAPI(e.target.value)} />
// 输入 "react" 会发送 5 次请求：r, re, rea, reac, react
```

防抖和节流就是为了解决这个问题。

---

## 二、useDebounce：防抖

防抖的核心思想：**等用户停止操作后再执行**。

### 基础用法

```javascript
import { useDebounce } from 'ahooks';

function SearchInput() {
  const [value, setValue] = useState('');
  const debouncedValue = useDebounce(value, { wait: 500 });
  
  useEffect(() => {
    if (debouncedValue) {
      searchAPI(debouncedValue);
    }
  }, [debouncedValue]);
  
  return <input value={value} onChange={e => setValue(e.target.value)} />;
}
```

效果：用户停止输入 500ms 后才发送请求。

### 配置选项

```javascript
const debouncedValue = useDebounce(value, {
  wait: 500,  // 延迟时间
  leading: false,  // 是否在开始时立即执行
  trailing: true,  // 是否在结束时执行
  maxWait: 1000  // 最大等待时间
});
```

---

## 三、useDebounceFn：防抖函数

如果需要防抖一个函数而不是值，使用 `useDebounceFn`。

```javascript
import { useDebounceFn } from 'ahooks';

function SearchInput() {
  const { run, cancel, flush } = useDebounceFn(
    (value) => {
      searchAPI(value);
    },
    { wait: 500 }
  );
  
  return (
    <>
      <input onChange={e => run(e.target.value)} />
      <button onClick={cancel}>取消</button>
      <button onClick={flush}>立即执行</button>
    </>
  );
}
```

返回值：
- `run`: 触发防抖函数
- `cancel`: 取消等待中的执行
- `flush`: 立即执行并取消等待

---

## 四、useThrottle：节流

节流的核心思想：**固定时间内只执行一次**。

### 基础用法

```javascript
import { useThrottle } from 'ahooks';

function ScrollComponent() {
  const [scrollTop, setScrollTop] = useState(0);
  const throttledScrollTop = useThrottle(scrollTop, { wait: 200 });
  
  useEffect(() => {
    console.log('滚动位置:', throttledScrollTop);
  }, [throttledScrollTop]);
  
  return (
    <div onScroll={e => setScrollTop(e.target.scrollTop)}>
      {/* 内容 */}
    </div>
  );
}
```

效果：每 200ms 最多更新一次滚动位置。

---

## 五、useThrottleFn：节流函数

```javascript
import { useThrottleFn } from 'ahooks';

function InfiniteScroll() {
  const { run } = useThrottleFn(
    () => {
      loadMore();
    },
    { wait: 1000 }
  );
  
  return (
    <div onScroll={run}>
      {/* 列表内容 */}
    </div>
  );
}
```

---

## 六、防抖 vs 节流

| 特性 | 防抖 (Debounce) | 节流 (Throttle) |
|------|----------------|----------------|
| 执行时机 | 停止触发后延迟执行 | 固定间隔执行 |
| 适用场景 | 搜索输入、表单验证 | 滚动加载、窗口 resize |
| 高频触发 | 只执行最后一次 | 按间隔执行多次 |
| 响应速度 | 较慢（需等待） | 较快（立即响应） |

可视化对比：

```
原始事件: ||||||||||||||||||||||||
防抖:                            |  (只在最后执行)
节流:     |     |     |     |     |  (固定间隔执行)
```

---

## 七、实战场景

### 场景 1：搜索建议

```javascript
function SearchSuggestion() {
  const [keyword, setKeyword] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  
  const { run, cancel } = useDebounceFn(
    async (value) => {
      if (!value) {
        setSuggestions([]);
        return;
      }
      const data = await fetchSuggestions(value);
      setSuggestions(data);
    },
    { wait: 300 }
  );
  
  return (
    <div>
      <input
        value={keyword}
        onChange={e => {
          setKeyword(e.target.value);
          run(e.target.value);
        }}
        onBlur={cancel}  // 失焦时取消
      />
      <ul>
        {suggestions.map(item => (
          <li key={item.id}>{item.text}</li>
        ))}
      </ul>
    </div>
  );
}
```

### 场景 2：窗口 resize

```javascript
function ResponsiveLayout() {
  const [width, setWidth] = useState(window.innerWidth);
  
  const { run } = useThrottleFn(
    () => {
      setWidth(window.innerWidth);
    },
    { wait: 200 }
  );
  
  useEffect(() => {
    window.addEventListener('resize', run);
    return () => window.removeEventListener('resize', run);
  }, []);
  
  return <div>当前宽度: {width}px</div>;
}
```

### 场景 3：按钮防重复点击

```javascript
function SubmitButton() {
  const { run, cancel } = useDebounceFn(
    async () => {
      await submitForm();
      message.success('提交成功');
    },
    { wait: 1000, leading: true, trailing: false }
  );
  
  return <button onClick={run}>提交</button>;
}
```

配置说明：
- `leading: true`: 点击时立即执行
- `trailing: false`: 不在结束时执行
- 效果：1 秒内只能点击一次

### 场景 4：滚动加载

```javascript
function InfiniteList() {
  const [list, setList] = useState([]);
  const [page, setPage] = useState(1);
  
  const { run } = useThrottleFn(
    () => {
      const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
      
      // 距离底部 100px 时加载
      if (scrollTop + clientHeight >= scrollHeight - 100) {
        loadMore();
      }
    },
    { wait: 200 }
  );
  
  useEffect(() => {
    window.addEventListener('scroll', run);
    return () => window.removeEventListener('scroll', run);
  }, []);
  
  const loadMore = async () => {
    const data = await fetchList(page);
    setList([...list, ...data]);
    setPage(page + 1);
  };
  
  return (
    <div>
      {list.map(item => <Item key={item.id} {...item} />)}
    </div>
  );
}
```

---

## 八、源码解析（简化版）

### useDebounce 实现

```javascript
function useDebounce(value, options) {
  const [debounced, setDebounced] = useState(value);
  
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebounced(value);
    }, options.wait);
    
    return () => clearTimeout(timer);
  }, [value, options.wait]);
  
  return debounced;
}
```

### useThrottle 实现

```javascript
function useThrottle(value, options) {
  const [throttled, setThrottled] = useState(value);
  const lastRun = useRef(Date.now());
  
  useEffect(() => {
    const now = Date.now();
    
    if (now - lastRun.current >= options.wait) {
      setThrottled(value);
      lastRun.current = now;
    } else {
      const timer = setTimeout(() => {
        setThrottled(value);
        lastRun.current = Date.now();
      }, options.wait - (now - lastRun.current));
      
      return () => clearTimeout(timer);
    }
  }, [value, options.wait]);
  
  return throttled;
}
```

---

## 九、性能对比

测试场景：1 秒内触发 100 次事件

| 方案 | 执行次数 | 性能 |
|------|---------|------|
| 无优化 | 100 次 | ❌ 差 |
| 防抖 (500ms) | 1 次 | ✅ 最好 |
| 节流 (200ms) | 5 次 | ✅ 好 |

---

## 十、最佳实践

1. **搜索输入**：使用防抖，wait 300-500ms
2. **表单验证**：使用防抖，wait 500ms
3. **滚动加载**：使用节流，wait 200-300ms
4. **窗口 resize**：使用节流，wait 200ms
5. **按钮点击**：使用防抖 + leading，wait 1000ms

选择建议：
- 需要等用户"停下来"再执行 → 防抖
- 需要持续响应但控制频率 → 节流

---

## 总结

ahooks 的防抖节流 Hooks 提供了简洁易用的 API，帮助我们轻松处理高频事件。理解两者的区别和适用场景，能让你的应用性能更好、用户体验更流畅。

如果这篇文章对你有帮助，欢迎点赞收藏！
