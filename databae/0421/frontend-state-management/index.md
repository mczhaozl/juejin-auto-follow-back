# 前端状态管理完全指南：从 React Context 到 Redux 再到 Zustand

前端状态管理是一个永恒的话题。本文将带你了解各种状态管理方案，帮助你选择最适合的工具。

## 一、为什么需要状态管理

### 1. 组件间共享状态

```javascript
// 兄弟组件共享状态的问题
function App() {
  const [count, setCount] = useState(0);
  return (
    <>
      <ChildA count={count} setCount={setCount} />
      <ChildB count={count} />
    </>
  );
}
```

### 2. 深层传递 Props

```javascript
// Prop Drilling 问题
function App() {
  const [user, setUser] = useState(null);
  return <Layout user={user} setUser={setUser} />;
}

function Layout({ user, setUser }) {
  return <Header user={user} setUser={setUser} />;
}

function Header({ user, setUser }) {
  return <UserMenu user={user} setUser={setUser} />;
}
```

## 二、React Context

### 1. 基础用法

```javascript
import { createContext, useContext, useState } from 'react';

const UserContext = createContext();

function UserProvider({ children }) {
  const [user, setUser] = useState(null);
  
  return (
    <UserContext.Provider value={{ user, setUser }}>
      {children}
    </UserContext.Provider>
  );
}

function useUser() {
  return useContext(UserContext);
}

function App() {
  return (
    <UserProvider>
      <Header />
    </UserProvider>
  );
}

function Header() {
  const { user } = useUser();
  return <div>{user?.name}</div>;
}
```

### 2. Context 的问题

- 所有消费者都会重新渲染
- 没有中间件支持
- 调试困难

## 三、Redux

### 1. 基础用法

```javascript
import { createStore } from 'redux';
import { Provider, useSelector, useDispatch } from 'react-redux';

const initialState = { count: 0 };

function reducer(state = initialState, action) {
  switch (action.type) {
    case 'INCREMENT':
      return { count: state.count + 1 };
    case 'DECREMENT':
      return { count: state.count - 1 };
    default:
      return state;
  }
}

const store = createStore(reducer);

function App() {
  return (
    <Provider store={store}>
      <Counter />
    </Provider>
  );
}

function Counter() {
  const count = useSelector(state => state.count);
  const dispatch = useDispatch();
  
  return (
    <div>
      <span>{count}</span>
      <button onClick={() => dispatch({ type: 'INCREMENT' })}>+</button>
      <button onClick={() => dispatch({ type: 'DECREMENT' })}>-</button>
    </div>
  );
}
```

### 2. Redux Toolkit

```javascript
import { createSlice, configureStore } from '@reduxjs/toolkit';

const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    increment: state => { state.value += 1; },
    decrement: state => { state.value -= 1; },
  },
});

export const { increment, decrement } = counterSlice.actions;

const store = configureStore({
  reducer: {
    counter: counterSlice.reducer,
  },
});
```

## 四、Zustand

### 1. 基础用法

```javascript
import { create } from 'zustand';

const useStore = create((set) => ({
  count: 0,
  increment: () => set((state) => ({ count: state.count + 1 })),
  decrement: () => set((state) => ({ count: state.count - 1 })),
}));

function Counter() {
  const count = useStore((state) => state.count);
  const increment = useStore((state) => state.increment);
  const decrement = useStore((state) => state.decrement);
  
  return (
    <div>
      <span>{count}</span>
      <button onClick={increment}>+</button>
      <button onClick={decrement}>-</button>
    </div>
  );
}
```

### 2. 高级用法

```javascript
const useStore = create((set, get) => ({
  count: 0,
  user: null,
  fetchUser: async (id) => {
    const response = await fetch(`/api/users/${id}`);
    const user = await response.json();
    set({ user });
  },
  doubleCount: () => {
    const currentCount = get().count;
    set({ count: currentCount * 2 });
  },
}));
```

## 五、Jotai

```javascript
import { atom, useAtom } from 'jotai';

const countAtom = atom(0);
const doubleCountAtom = atom((get) => get(countAtom) * 2);

function Counter() {
  const [count, setCount] = useAtom(countAtom);
  const [doubleCount] = useAtom(doubleCountAtom);
  
  return (
    <div>
      <span>{count} * 2 = {doubleCount}</span>
      <button onClick={() => setCount(c => c + 1)}>+</button>
    </div>
  );
}
```

## 六、选择建议

| 场景 | 推荐方案 |
|------|---------|
| 小型应用，少量全局状态 | React Context |
| 大型应用，复杂状态逻辑 | Redux Toolkit |
| 中型应用，想要简单 API | Zustand |
| 细粒度更新，原子化状态 | Jotai |

## 七、总结

状态管理没有银弹，选择最适合你项目的方案：

1. Context：简单，但注意性能
2. Redux：强大，但复杂
3. Zustand：简单且强大，推荐
4. Jotai：原子化，灵活

选择适合的工具，而不是追逐潮流！
