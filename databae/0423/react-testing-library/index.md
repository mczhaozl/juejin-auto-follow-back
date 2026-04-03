# React Testing Library 完全指南：从基础到最佳实践

React Testing Library 是测试 React 组件的事实标准。本文将带你全面掌握 React 组件测试。

## 一、React Testing Library 基础

### 1. 安装

```bash
npm install --save-dev @testing-library/react @testing-library/jest-dom @testing-library/user-event jest
```

### 2. 第一个测试

```javascript
// Greeting.js
function Greeting({ name }) {
  return <h1>Hello, {name}!</h1>;
}

export default Greeting;
```

```javascript
// Greeting.test.js
import { render, screen } from '@testing-library/react';
import Greeting from './Greeting';

test('renders greeting with name', () => {
  render(<Greeting name="Alice" />);
  expect(screen.getByText('Hello, Alice!')).toBeInTheDocument();
});
```

## 二、查询方法

### 1. getBy* 查询

```javascript
import { render, screen } from '@testing-library/react';

test('getBy queries', () => {
  render(
    <div>
      <h1>Title</h1>
      <input placeholder="Enter name" />
      <button>Submit</button>
      <img alt="Profile" />
    </div>
  );

  // 通过文本查询
  expect(screen.getByText('Title')).toBeInTheDocument();
  
  // 通过占位符查询
  expect(screen.getByPlaceholderText('Enter name')).toBeInTheDocument();
  
  // 通过角色查询
  expect(screen.getByRole('button', { name: /submit/i })).toBeInTheDocument();
  
  // 通过 alt 文本查询
  expect(screen.getByAltText('Profile')).toBeInTheDocument();
  
  // 通过标签文本查询
  expect(screen.getByLabelText('Username')).toBeInTheDocument();
  
  // 通过显示值查询
  expect(screen.getByDisplayValue('Hello')).toBeInTheDocument();
  
  // 通过标题查询
  expect(screen.getByTitle('Tooltip')).toBeInTheDocument();
  
  // 通过测试 ID 查询
  expect(screen.getByTestId('custom-element')).toBeInTheDocument();
});
```

### 2. queryBy* 和 findBy*

```javascript
test('queryBy and findBy', async () => {
  render(<Component />);
  
  // queryBy: 找不到返回 null（不会抛出错误）
  expect(screen.queryByText('Not here')).not.toBeInTheDocument();
  
  // findBy: 异步查询（返回 Promise）
  expect(await screen.findByText('Loaded')).toBeInTheDocument();
});
```

### 3. 多个元素

```javascript
test('multiple elements', () => {
  render(
    <ul>
      <li>Item 1</li>
      <li>Item 2</li>
      <li>Item 3</li>
    </ul>
  );
  
  const items = screen.getAllByRole('listitem');
  expect(items).toHaveLength(3);
  
  const noItems = screen.queryAllByText('Not found');
  expect(noItems).toHaveLength(0);
});
```

### 4. 查询优先级

```
1. getByRole
2. getByLabelText
3. getByPlaceholderText
4. getByText
5. getByDisplayValue
6. getByAltText
7. getByTitle
8. getByTestId (最后手段)
```

## 三、用户交互

### 1. 基本交互

```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

test('click button', () => {
  render(<Counter />);
  
  // 使用 fireEvent
  fireEvent.click(screen.getByRole('button', { name: /increment/i }));
  
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});

test('user event', async () => {
  const user = userEvent.setup();
  render(<Form />);
  
  // 输入文本
  await user.type(screen.getByLabelText('Name'), 'Alice');
  
  // 点击
  await user.click(screen.getByRole('button', { name: /submit/i }));
  
  // 选择选项
  await user.selectOptions(screen.getByRole('combobox'), 'Option 1');
  
  // 上传文件
  const file = new File(['hello'], 'hello.txt', { type: 'text/plain' });
  await user.upload(screen.getByLabelText('Upload'), file);
});
```

### 2. 表单测试

```javascript
// LoginForm.js
function LoginForm({ onSubmit }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({ username, password });
  };

  return (
    <form onSubmit={handleSubmit}>
      <label htmlFor="username">Username</label>
      <input
        id="username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      
      <label htmlFor="password">Password</label>
      <input
        id="password"
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      
      <button type="submit">Login</button>
    </form>
  );
}
```

```javascript
// LoginForm.test.js
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import LoginForm from './LoginForm';

test('submits form with username and password', async () => {
  const user = userEvent.setup();
  const handleSubmit = jest.fn();
  
  render(<LoginForm onSubmit={handleSubmit} />);
  
  await user.type(screen.getByLabelText('Username'), 'alice');
  await user.type(screen.getByLabelText('Password'), 'password123');
  await user.click(screen.getByRole('button', { name: /login/i }));
  
  expect(handleSubmit).toHaveBeenCalledTimes(1);
  expect(handleSubmit).toHaveBeenCalledWith({
    username: 'alice',
    password: 'password123'
  });
});
```

## 四、Jest 匹配器

### 1. 基础匹配器

```javascript
test('basic matchers', () => {
  expect(2 + 2).toBe(4);
  expect(null).toBeNull();
  expect(undefined).toBeUndefined();
  expect(true).toBeTruthy();
  expect(false).toBeFalsy();
});
```

### 2. @testing-library/jest-dom 匹配器

```javascript
import '@testing-library/jest-dom';

test('jest-dom matchers', () => {
  render(<Component />);
  
  // 元素存在
  expect(screen.getByText('Hello')).toBeInTheDocument();
  
  // 元素可见
  expect(screen.getByText('Visible')).toBeVisible();
  
  // 元素为空
  expect(screen.getByTestId('empty')).toBeEmptyDOMElement();
  
  // 元素有属性
  expect(screen.getByRole('button')).toHaveAttribute('disabled');
  expect(screen.getByRole('textbox')).toHaveValue('Hello');
  
  // 元素有类名
  expect(screen.getByTestId('container')).toHaveClass('active');
  
  // 元素有样式
  expect(screen.getByTestId('box')).toHaveStyle({ color: 'red' });
  
  // 元素被选中
  expect(screen.getByRole('checkbox')).toBeChecked();
  
  // 元素被禁用
  expect(screen.getByRole('button')).toBeDisabled();
  
  // 元素包含文本
  expect(screen.getByTestId('container')).toContainHTML('<span>Hello</span>');
});
```

### 3. Mock 函数匹配器

```javascript
test('mock matchers', () => {
  const mockFn = jest.fn();
  
  mockFn('arg1', 'arg2');
  
  expect(mockFn).toHaveBeenCalled();
  expect(mockFn).toHaveBeenCalledTimes(1);
  expect(mockFn).toHaveBeenCalledWith('arg1', 'arg2');
  expect(mockFn).toHaveBeenLastCalledWith('arg1', 'arg2');
});
```

## 五、异步测试

### 1. 异步组件

```javascript
// AsyncComponent.js
function AsyncComponent() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData().then(result => {
      setData(result);
      setLoading(false);
    });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return <div>Data: {data}</div>;
}
```

```javascript
// AsyncComponent.test.js
import { render, screen } from '@testing-library/react';
import AsyncComponent from './AsyncComponent';

jest.mock('./api', () => ({
  fetchData: jest.fn(() => Promise.resolve('Test data'))
}));

test('renders loading state first, then data', async () => {
  render(<AsyncComponent />);
  
  expect(screen.getByText('Loading...')).toBeInTheDocument();
  
  const dataElement = await screen.findByText('Data: Test data');
  expect(dataElement).toBeInTheDocument();
  expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
});
```

### 2. waitFor

```javascript
import { render, screen, waitFor } from '@testing-library/react';

test('waits for condition', async () => {
  render(<Component />);
  
  await waitFor(() => {
    expect(screen.getByText('Loaded')).toBeInTheDocument();
  }, {
    timeout: 1000,
    interval: 50
  });
});
```

## 六、Mock 外部依赖

### 1. Mock API 调用

```javascript
// api.js
export const fetchUser = async (id) => {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
};
```

```javascript
// UserProfile.js
import { fetchUser } from './api';

function UserProfile({ userId }) {
  const [user, setUser] = useState(null);
  
  useEffect(() => {
    fetchUser(userId).then(setUser);
  }, [userId]);
  
  if (!user) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  );
}
```

```javascript
// UserProfile.test.js
import { render, screen } from '@testing-library/react';
import UserProfile from './UserProfile';

jest.mock('./api', () => ({
  fetchUser: jest.fn()
}));

const mockFetchUser = fetchUser as jest.MockedFunction<typeof fetchUser>;

test('renders user profile', async () => {
  mockFetchUser.mockResolvedValue({
    id: 1,
    name: 'Alice',
    email: 'alice@example.com'
  });
  
  render(<UserProfile userId={1} />);
  
  expect(screen.getByText('Loading...')).toBeInTheDocument();
  
  const nameElement = await screen.findByText('Alice');
  expect(nameElement).toBeInTheDocument();
  expect(screen.getByText('alice@example.com')).toBeInTheDocument();
  expect(mockFetchUser).toHaveBeenCalledWith(1);
});
```

### 2. Mock 模块

```javascript
// Mock 整个模块
jest.mock('axios');
import axios from 'axios';
const mockedAxios = axios as jest.Mocked<typeof axios>;

mockedAxios.get.mockResolvedValue({ data: 'test' });

// Mock 部分模块
jest.mock('./utils', () => ({
  ...jest.requireActual('./utils'),
  expensiveFunction: jest.fn(() => 'mocked')
}));
```

## 七、测试 React Hooks

```javascript
// useCounter.js
import { useState, useCallback } from 'react';

export function useCounter(initialValue = 0) {
  const [count, setCount] = useState(initialValue);
  
  const increment = useCallback(() => setCount(c => c + 1), []);
  const decrement = useCallback(() => setCount(c => c - 1), []);
  const reset = useCallback(() => setCount(initialValue), [initialValue]);
  
  return { count, increment, decrement, reset };
}
```

```javascript
// useCounter.test.js
import { renderHook, act } from '@testing-library/react';
import { useCounter } from './useCounter';

test('useCounter', () => {
  const { result } = renderHook(() => useCounter(10));
  
  expect(result.current.count).toBe(10);
  
  act(() => {
    result.current.increment();
  });
  expect(result.current.count).toBe(11);
  
  act(() => {
    result.current.decrement();
  });
  expect(result.current.count).toBe(10);
  
  act(() => {
    result.current.reset();
  });
  expect(result.current.count).toBe(10);
});
```

## 八、测试 Context

```javascript
// ThemeContext.js
import { createContext, useContext, useState } from 'react';

const ThemeContext = createContext();

export function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  return (
    <ThemeContext.Provider value={{ theme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  return useContext(ThemeContext);
}
```

```javascript
// ThemeButton.js
import { useTheme } from './ThemeContext';

function ThemeButton() {
  const { theme, setTheme } = useTheme();
  
  return (
    <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
      Toggle theme: {theme}
    </button>
  );
}
```

```javascript
// ThemeButton.test.js
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from './ThemeContext';
import ThemeButton from './ThemeButton';

function renderWithTheme(ui, { theme = 'light' } = {}) {
  return render(
    <ThemeProvider initialTheme={theme}>
      {ui}
    </ThemeProvider>
  );
}

test('toggles theme', async () => {
  const user = userEvent.setup();
  renderWithTheme(<ThemeButton />);
  
  expect(screen.getByText('Toggle theme: light')).toBeInTheDocument();
  
  await user.click(screen.getByRole('button'));
  expect(screen.getByText('Toggle theme: dark')).toBeInTheDocument();
});
```

## 九、测试 Redux

```javascript
// counterSlice.js
import { createSlice } from '@reduxjs/toolkit';

const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0 },
  reducers: {
    increment: state => { state.value += 1; },
    decrement: state => { state.value -= 1; }
  }
});

export const { increment, decrement } = counterSlice.actions;
export default counterSlice.reducer;
```

```javascript
// Counter.js
import { useSelector, useDispatch } from 'react-redux';
import { increment, decrement } from './counterSlice';

function Counter() {
  const count = useSelector(state => state.counter.value);
  const dispatch = useDispatch();
  
  return (
    <div>
      <span>Count: {count}</span>
      <button onClick={() => dispatch(increment())}>+</button>
      <button onClick={() => dispatch(decrement())}>-</button>
    </div>
  );
}
```

```javascript
// Counter.test.js
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import counterReducer from './counterSlice';
import Counter from './Counter';

function renderWithStore(ui, { preloadedState = {} } = {}) {
  const store = configureStore({
    reducer: { counter: counterReducer },
    preloadedState
  });
  
  return render(<Provider store={store}>{ui}</Provider>);
}

test('increments and decrements counter', async () => {
  const user = userEvent.setup();
  renderWithStore(<Counter />, {
    preloadedState: { counter: { value: 5 } }
  });
  
  expect(screen.getByText('Count: 5')).toBeInTheDocument();
  
  await user.click(screen.getByText('+'));
  expect(screen.getByText('Count: 6')).toBeInTheDocument();
  
  await user.click(screen.getByText('-'));
  expect(screen.getByText('Count: 5')).toBeInTheDocument();
});
```

## 十、最佳实践

1. 测试用户行为，而非实现细节
2. 使用推荐的查询方法
3. 模拟外部依赖
4. 保持测试简单和快速
5. 一个测试只测一件事
6. 测试边界情况
7. 使用 findBy* 测试异步代码
8. 避免测试实现细节

## 十一、总结

React Testing Library 核心：
- 从用户视角测试
- 使用语义化查询
- 模拟用户交互
- 使用 findBy* 处理异步
- Mock 外部依赖
- 测试 Hooks 和 Context
- 遵循最佳实践

开始测试你的 React 组件吧！
