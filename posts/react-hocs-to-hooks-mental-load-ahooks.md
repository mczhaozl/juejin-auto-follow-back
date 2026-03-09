# 从高阶函数到 Hooks：React 如何减轻开发者的心智负担（含 Demo + ahooks 推荐）

> 对比 HOC/render props 与 Hooks，用具体 demo 展示「按功能组织、无 this、复用逻辑」的减负效果，并推荐 ahooks 库。

---

## 一、高阶函数时代的心智负担

在 Hooks 之前，React 里复用「带状态的逻辑」主要靠两类手段：**高阶组件（HOC）** 和 **render props**。二者本质都是「高阶函数」——接收组件或函数，返回增强后的组件或新的渲染方式。它们能解决问题，但会带来明显的心智负担。

### 1. 嵌套地狱，难以追踪

多个 HOC 叠加时，组件树会变成一层套一层：`withAuth(withTheme(withWindowSize(MyPage)))`。DevTools 里看到的是一串 `WithAuth(WithTheme(WithWindowSize(...)))`，**数据从哪一层来、props 叫什么**，都要一层层往上找，调试和阅读成本都很高。

### 2. this 与生命周期分散逻辑

Class 组件里，**this** 的绑定（`bind` 或类字段）是常见坑；同一块逻辑还经常被拆到 `componentDidMount` 和 `componentDidUpdate` 两处，**「根据 A 同步 B」** 的代码散落在不同生命周期里，难以按「功能」理解。

### 3. 命名与透传的样板代码

HOC 要透传 props（`{...this.props}`），还要小心 **ref** 和 **displayName**；render props 则要多写一层函数和命名（如 `render={({ x, y }) => ...}`）。这些都是在解决「逻辑复用」时多出来的心智开销。

下面先用一个**具体 demo** 对比「HOC 写法」和「自定义 Hook 写法」，直观感受 Hooks 如何减负。

---

## 二、Demo 1：窗口尺寸 —— HOC 与 Hook 对比

**需求**：多个组件需要用到「当前窗口宽高」，并在 resize 时更新。

### 用 HOC 实现（心智负担大）

```javascript
// 高阶组件：包装一层 Class，把 width/height 通过 props 注入
function withWindowSize(WrappedComponent) {
    return class WithWindowSize extends React.Component {
        state = { width: window.innerWidth, height: window.innerHeight };
        componentDidMount() {
            this.handler = () => this.setState({
                width: window.innerWidth,
                height: window.innerHeight,
            });
            window.addEventListener('resize', this.handler);
        }
        componentWillUnmount() {
            window.removeEventListener('resize', this.handler);
        }
        render() {
            return (
                <WrappedComponent
                    width={this.state.width}
                    height={this.state.height}
                    {...this.props}
                />
            );
        }
    };
}

// 使用：组件被包一层，DevTools 里多一个 WithWindowSize
const MyPanel = withWindowSize(function MyPanel({ width, height }) {
    return <div>当前宽度：{width}px，高度：{height}px</div>;
});
```

你要关心：HOC 的 **displayName**、**ref 透传**（若需要）、以及「数据从哪个 HOC 来」。多个 HOC 叠加时，问题成倍增加。

### 用自定义 Hook 实现（减负）

```javascript
// 自定义 Hook：按「一块逻辑」组织，无 Class、无 this
function useWindowSize() {
    const [size, setSize] = useState({
        width: window.innerWidth,
        height: window.innerHeight,
    });
    useEffect(() => {
        const handler = () => setSize({
            width: window.innerWidth,
            height: window.innerHeight,
        });
        window.addEventListener('resize', handler);
        return () => window.removeEventListener('resize', handler);
    }, []);
    return size;
}

// 使用：直接调用，无包装、无嵌套
function MyPanel() {
    const { width, height } = useWindowSize();
    return <div>当前宽度：{width}px，高度：{height}px</div>;
}
```

**减负体现**：逻辑集中在 `useWindowSize` 里，按「功能」一块块组织；组件树扁平，没有多余的包装组件；没有 this，没有生命周期命名，读代码时「用到什么就调什么 Hook」。

---

## 三、Demo 2：请求数据 + loading —— 手写 vs ahooks useRequest

**需求**：请求用户列表，展示 loading、错误和重试。

### 手写 useEffect（容易漏依赖、重复逻辑）

```javascript
function UserList() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        let cancelled = false;
        setLoading(true);
        setError(null);
        fetch('/api/users')
            .then((res) => res.json())
            .then((json) => {
                if (!cancelled) setData(json);
            })
            .catch((e) => {
                if (!cancelled) setError(e);
            })
            .finally(() => {
                if (!cancelled) setLoading(false);
            });
        return () => { cancelled = true; };
    }, []);

    if (loading) return <div>加载中...</div>;
    if (error) return <div>错误：{error.message}</div>;
    return <ul>{data?.map((u) => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

你要自己处理：**竞态取消**、loading/error 状态、重试逻辑若再加一层，代码更长、心智负担更大。

### 用 ahooks 的 useRequest（减负）

```javascript
import { useRequest } from 'ahooks';

function UserList() {
    const { data, loading, error, refresh } = useRequest(() =>
        fetch('/api/users').then((res) => res.json())
    );

    if (loading) return <div>加载中...</div>;
    if (error) return <div>错误：{error.message} <button onClick={refresh}>重试</button></div>;
    return (
        <ul>
            {data?.map((u) => <li key={u.id}>{u.name}</li>)}
            <button onClick={refresh}>刷新</button>
        </ul>
    );
}
```

**减负体现**：**竞态、loading、error、重试** 都由 `useRequest` 管，你只关心「发什么请求」和「怎么渲染」；代码更短，逻辑更清晰，心智负担明显下降。

---

## 四、Demo 3：防抖输入 —— 手写 vs ahooks useDebounce

**需求**：搜索框输入防抖，仅在实际停顿后再请求。

### 手写（要管定时器、清理、依赖）

```javascript
function SearchBox() {
    const [keyword, setKeyword] = useState('');
    const [debouncedKeyword, setDebouncedKeyword] = useState('');

    useEffect(() => {
        const timer = setTimeout(() => setDebouncedKeyword(keyword), 300);
        return () => clearTimeout(timer);
    }, [keyword]);

    useEffect(() => {
        if (!debouncedKeyword) return;
        fetch(`/api/search?q=${debouncedKeyword}`).then(/* ... */);
    }, [debouncedKeyword]);

    return <input value={keyword} onChange={(e) => setKeyword(e.target.value)} />;
}
```

你要自己保证：防抖时间、清理、以及「防抖后的值」和「请求」的依赖关系正确。

### 用 ahooks 的 useDebounce（减负）

```javascript
import { useDebounce } from 'ahooks';

function SearchBox() {
    const [keyword, setKeyword] = useState('');
    const debouncedKeyword = useDebounce(keyword, { wait: 300 });

    useEffect(() => {
        if (!debouncedKeyword) return;
        fetch(`/api/search?q=${debouncedKeyword}`).then(/* ... */);
    }, [debouncedKeyword]);

    return <input value={keyword} onChange={(e) => setKeyword(e.target.value)} />;
}
```

**减负体现**：防抖逻辑交给 `useDebounce`，你只关心「用防抖后的值做什么」；少写定时器、少操心清理，心智负担更小。

---

## 五、React 如何用 Hooks 减轻心智负担（小结三点）

1. **按功能组织，而非按生命周期**  
   同一块逻辑（如「窗口尺寸」「请求用户」）收拢在一个 Hook 里，相关代码在一起，读起来是「这个组件用了哪些能力」，而不是「mount 里干了啥、update 里又干了啥」。

2. **无 this，闭包清晰**  
   函数组件 + Hooks 没有 `this`，state 和更新函数都来自 `useState` 等 API，依赖关系写在 Hook 的依赖数组里，减少「this 指向错了」「忘了 bind」这类问题。

3. **复用即「调用 Hook」**  
   复用带状态的逻辑不再依赖 HOC 或 render props 的层层包装，直接「调用自定义 Hook」即可，组件树扁平、数据来源一目了然。

在此基础上，**用好现成的 Hooks 库**（如 ahooks）可以进一步减少「自己管请求、防抖、节流、缓存」的心智负担，把精力放在业务 UI 和交互上。

---

## 六、推荐 ahooks：为业务而生的 Hooks 库

**[ahooks](https://ahooks.js.org/zh-CN)** 是阿里开源的 React Hooks 库，目标是做 Hooks 领域的「lodash」——稳定、可长期依赖。它用 TypeScript 编写，提供完整类型，且针对**闭包、SSR** 等做了处理，适合在真实项目里直接使用。

### 安装

```bash
npm install ahooks
# 或 pnpm add ahooks / yarn add ahooks
```

### 常用 Hooks 一览

| 场景           | Hook           | 作用简述                     |
|----------------|----------------|------------------------------|
| 异步请求       | `useRequest`   | 自动/手动请求、loading、重试、轮询、缓存 |
| 防抖 / 节流    | `useDebounce` / `useThrottle` | 值或函数的防抖/节流          |
| 状态与存储     | `useLocalStorageState` | 持久化到 localStorage        |
| DOM / 尺寸     | `useSize`、`useScroll` | 元素尺寸、滚动位置            |
| 生命周期相关   | `useUnmount`、`useUpdateEffect` | 仅卸载时执行、仅更新时执行    |

### 与本文 demo 的对应关系

- **Demo 2** 用了 `useRequest`，可直接替换手写的 `useEffect` + fetch，并享受重试、轮询、缓存等能力。
- **Demo 3** 用了 `useDebounce`，把「防抖后的值」从状态和定时器里抽离出来，代码更短、更稳。

更多 API 和用法见官网：[https://ahooks.js.org/zh-CN](https://ahooks.js.org/zh-CN)。

---

## 总结

- **高阶函数（HOC/render props）** 能复用逻辑，但带来嵌套、this、生命周期分散等心智负担。
- **Hooks** 通过「按功能组织、无 this、复用即调 Hook」减轻负担；用 **自定义 Hook** 替代 HOC，组件树更扁平、数据流更清晰。
- 文中用 **窗口尺寸、请求数据、防抖输入** 三个 demo 对比手写/HOC 与 Hook/ahooks 的写法，直观看到 Hooks 的优势。
- **ahooks** 提供 `useRequest`、`useDebounce` 等常用能力，建议在项目中直接使用，进一步减少重复逻辑与心智负担。

若对你有用，欢迎点赞、收藏；有更好的 Hooks 实践或 ahooks 用法也欢迎在评论区分享。
