# React 测试完全指南

## 一、基础组件测试

```tsx
import { render, screen, fireEvent } from '@testing-library/react';
import Counter from './Counter';

test('counter', () => {
  render(<Counter />);
  expect(screen.getByText('0')).toBeInTheDocument();
  
  fireEvent.click(screen.getByText('+'));
  expect(screen.getByText('1')).toBeInTheDocument();
});
```

## 二、异步测试

```tsx
test('async data', async () => {
  render(<UserProfile userId="1" />);
  
  // 等待加载完成
  const name = await screen.findByText('Alice');
  expect(name).toBeInTheDocument();
});
```

## 三、模拟 API

```tsx
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/user', (req, res, ctx) => {
    return res(ctx.json({ name: 'Alice' }));
  })
);

beforeAll(() => server.listen());
afterAll(() => server.close());
afterEach(() => server.resetHandlers());
```

## 四、测试 Hooks

```tsx
import { renderHook, act } from '@testing-library/react';

function useCounter() {
  const [count, setCount] = useState(0);
  const inc = () => setCount(c => c + 1);
  return { count, inc };
}

test('hook', () => {
  const { result } = renderHook(() => useCounter());
  expect(result.current.count).toBe(0);
  
  act(() => result.current.inc());
  expect(result.current.count).toBe(1);
});
```

## 五、最佳实践

- 测试组件的行为而非实现细节
- 使用 findBy* 处理异步更新
- 合理模拟外部依赖
- 避免过度模拟
- 保持测试独立性
- 测试错误边界和边界情况
