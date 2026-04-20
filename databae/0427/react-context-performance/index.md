# React Context 性能优化完全指南

> 深入理解 React Context 的工作原理，掌握性能优化策略，避免不必要的重渲染。

## 一、React Context 概述

Context 是 React 中跨组件层级传递数据的重要方式，但使用不当容易导致性能问题。

### 1.1 Context 的用途

- 主题切换（亮色/暗色）
- 用户认证信息
- 国际化语言
- 全局状态管理
- 应用配置

### 1.2 基本用法

```jsx
// 创建 Context
const ThemeContext = React.createContext('light');

// Provider 提供数据
function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}

// Consumer 消费数据
function Toolbar() {
  return (
    <ThemeContext.Consumer>
      {theme => <div>当前主题: {theme}</div>}
    </ThemeContext.Consumer>
  );
}

// useContext Hook
function Button() {
  const theme = useContext(ThemeContext);
  return <button style={{ background: theme === 'dark' ? '#333' : '#fff' }}>
    按钮
  </button>;
}
```

---

## 二、Context 重渲染问题

### 2.1 为什么会有重渲染

```jsx
// 问题示例
const ThemeContext = React.createContext();

function App() {
  const [theme, setTheme] = useState('light');
  const [count, setCount] = useState(0);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <Button />
      <Counter />
    </ThemeContext.Provider>
  );
}

// Button 会在 count 变化时重渲染！
function Button() {
  const { theme } = useContext(ThemeContext);
  console.log('Button 重渲染');
  return <button>主题: {theme}</button>;
}

function Counter() {
  const { setTheme } = useContext(ThemeContext);
  const [count, setCount] = useState(0);
  return (
    <div>
      <p>{count}</p>
      <button onClick={() => setCount(count + 1)}>增加</button>
    </div>
  );
}
```

问题：count 变化时，整个 App 重渲染，Provider 的 value 是新对象，导致所有 Consumer 都重渲染。

### 2.2 验证重渲染

```jsx
// 使用 React DevTools Profiler 验证
// 或使用 console.log 观察
```

---

## 三、优化策略一：拆分 Context

### 3.1 将不相关的数据分开

```jsx
// 之前：一个 Context 包含所有数据
const AppContext = React.createContext();

function App() {
  const [theme, setTheme] = useState('light');
  const [user, setUser] = useState(null);

  return (
    <AppContext.Provider value={{ theme, setTheme, user, setUser }}>
      <ComponentTree />
    </AppContext.Provider>
  );
}

// 优化后：拆分多个 Context
const ThemeContext = React.createContext();
const UserContext = React.createContext();

function App() {
  const [theme, setTheme] = useState('light');
  const [user, setUser] = useState(null);

  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      <UserContext.Provider value={{ user, setUser }}>
        <ComponentTree />
      </UserContext.Provider>
    </ThemeContext.Provider>
  );
}
```

### 3.2 按需消费

```jsx
// 只消费需要的 Context
function ThemeButton() {
  const { theme } = useContext(ThemeContext);
  return <button>主题按钮</button>;
}

function UserProfile() {
  const { user } = useContext(UserContext);
  return <div>用户: {user?.name}</div>;
}
```

---

## 四、优化策略二：使用 useMemo

### 4.1 稳定 value 引用

```jsx
// 使用 useMemo 缓存 value
function App() {
  const [theme, setTheme] = useState('light');
  const [count, setCount] = useState(0);

  const themeValue = useMemo(() => ({
    theme,
    setTheme
  }), [theme]);

  return (
    <ThemeContext.Provider value={themeValue}>
      <Button />
      <Counter />
    </ThemeContext.Provider>
  );
}
```

### 4.2 拆分 state 和 setState

```jsx
// 分离 state 和 dispatch
const ThemeStateContext = React.createContext();
const ThemeDispatchContext = React.createContext();

function App() {
  const [theme, setTheme] = useState('light');

  return (
    <ThemeStateContext.Provider value={theme}>
      <ThemeDispatchContext.Provider value={setTheme}>
        <ComponentTree />
      </ThemeDispatchContext.Provider>
    </ThemeStateContext.Provider>
  );
}
```

---

## 五、优化策略三：使用 useCallback

### 5.1 缓存回调函数

```jsx
function App() {
  const [theme, setTheme] = useState('light');

  const toggleTheme = useCallback(() => {
    setTheme(prev => prev === 'light' ? 'dark' : 'light');
  }, []);

  const contextValue = useMemo(() => ({
    theme,
    toggleTheme
  }), [theme, toggleTheme]);

  return (
    <ThemeContext.Provider value={contextValue}>
      <Child />
    </ThemeContext.Provider>
  );
}
```

---

## 六、优化策略四：组件拆分与 memo

### 6.1 使用 React.memo

```jsx
const Button = React.memo(function Button({ theme }) {
  console.log('Button 渲染');
  return <button style={{ background: theme }}>按钮</button>;
});

function ButtonWithContext() {
  const { theme } = useContext(ThemeContext);
  return <Button theme={theme} />;
}
```

### 6.2 拆分消费组件

```jsx
// 提取 Context 消费逻辑
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
}

// 组件只负责渲染
function ThemedButton() {
  const { theme } = useTheme();
  return <button style={{ background: theme === 'dark' ? '#333' : '#fff' }}>
    按钮
  </button>
}
```

---

## 七、深入理解 Context 的工作原理

### 7.1 Context 的内部机制

```javascript
// 简化的 Context 实现
function createContext(defaultValue) {
  const context = {
    _currentValue: defaultValue,
    Provider: function Provider({ value, children }) {
      context._currentValue = value;
      return children;
    },
    Consumer: function Consumer({ children }) {
      return children(context._currentValue);
    }
  };
  return context;
}
```

### 7.2 React 如何追踪 Context 变化

React 使用 fiber 树追踪 Context 消费者：

```javascript
// 简化的 useContext 实现
function useContext(context) {
  const fiber = getCurrentFiber();
  fiber.dependencies = fiber.dependencies || { contexts: [] };
  if (!fiber.dependencies.contexts.includes(context)) {
    fiber.dependencies.contexts.push(context);
  }
  return context._currentValue;
}
```

---

## 八、高级优化：选择器模式

### 8.1 实现 useSelector 模式

```jsx
// 创建一个支持选择器的 Context
function createContextWithSelector(initialValue) {
  const StateContext = React.createContext(initialValue);
  const UpdateContext = React.createContext(() => {});

  function Provider({ value, children }) {
    const [state, setState] = useState(value);
    return (
      <StateContext.Provider value={state}>
        <UpdateContext.Provider value={setState}>
          {children}
        </UpdateContext.Provider>
      </StateContext.Provider>
    );
  }

  function useSelector(selector) {
    const state = useContext(StateContext);
    const [selected, setSelected] = useState(() => selector(state));
    const prevSelector = useRef(selector);
    const prevState = useRef(state);

    useEffect(() => {
      if (selector !== prevSelector.current || state !== prevState.current) {
        const newSelected = selector(state);
        if (!Object.is(newSelected, selected)) {
          setSelected(newSelected);
        }
        prevSelector.current = selector;
        prevState.current = state;
      }
    }, [selector, state, selected]);

    return selected;
  }

  function useUpdate() {
    return useContext(UpdateContext);
  }

  return { Provider, useSelector, useUpdate };
}
```

### 8.2 使用选择器

```jsx
const { Provider, useSelector, useUpdate } = createContextWithSelector({
  theme: 'light',
  user: null,
  notifications: []
});

function ThemeButton() {
  // 只选择 theme
  const theme = useSelector(state => state.theme);
  return <button>主题: {theme}</button>;
}

function NotificationsBadge() {
  // 只选择通知数量
  const count = useSelector(state => state.notifications.length);
  return <span>通知: {count}</span>;
}
```

---

## 九、使用第三方库优化

### 9.1 use-context-selector

```jsx
import { createContext, useContextSelector } from 'use-context-selector';

const MyContext = createContext();

function MyProvider({ children }) {
  const [state, setState] = useState({ theme: 'light', user: null });
  return <MyContext.Provider value={state}>{children}</MyContext.Provider>;
}

function ThemeButton() {
  const theme = useContextSelector(MyContext, state => state.theme);
  return <button>主题: {theme}</button>;
}
```

### 9.2 Zustand 替代 Context

```jsx
import { create } from 'zustand';

const useStore = create((set) => ({
  theme: 'light',
  user: null,
  setTheme: (theme) => set({ theme }),
  setUser: (user) => set({ user })
}));

function ThemeButton() {
  const theme = useStore(state => state.theme);
  return <button>主题: {theme}</button>;
}
```

---

## 十、性能测量与调试

### 10.1 使用 React DevTools Profiler

```jsx
// 在组件中标记
function Button() {
  const { theme } = useContext(ThemeContext);
  return <button>按钮</button>;
}
```

### 10.2 性能测试

```jsx
// 使用 console.time
function App() {
  console.time('App render');
  // ...
  console.timeEnd('App render');
}
```

---

## 十一、最佳实践总结

1. **拆分 Context**：将不相关的数据分开
2. **使用 useMemo**：稳定 value 引用
3. **拆分 state 和 dispatch**：分别提供
4. **使用 React.memo**：优化组件重渲染
5. **选择器模式**：按需消费数据
6. **考虑替代方案**：Zustand、Jotai 等库
7. **测量性能**：使用 Profiler 验证优化

---

## 十二、总结

React Context 是强大的工具，但需要注意性能优化。通过合理拆分、使用 useMemo、选择器模式等策略，可以避免不必要的重渲染，提升应用性能。

希望这篇文章对你有帮助！
