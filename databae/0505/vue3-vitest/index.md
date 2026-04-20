# Vue 3 Vitest 测试完全指南

## 一、配置 Vitest

```ts
// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: ['./vitest.setup.ts']
  }
});
```

## 二、组件测试

```vue
<!-- Counter.vue -->
<script setup>
import { ref } from 'vue';
const count = ref(0);
const increment = () => count.value++;
</script>

<template>
  <p>Count: {{ count }}</p>
  <button @click="increment">+</button>
</template>
```

```ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Counter from './Counter.vue';

describe('Counter', () => {
  it('renders properly', () => {
    const wrapper = mount(Counter);
    expect(wrapper.text()).toContain('Count: 0');
  });

  it('increments when button clicked', async () => {
    const wrapper = mount(Counter);
    await wrapper.find('button').trigger('click');
    expect(wrapper.text()).toContain('Count: 1');
  });
});
```

## 三、Composables 测试

```ts
// useCounter.ts
export function useCounter() {
  const count = ref(0);
  const increment = () => count.value++;
  return { count, increment };
}
```

```ts
import { useCounter } from './useCounter';

it('increments count', () => {
  const { count, increment } = useCounter();
  increment();
  expect(count.value).toBe(1);
});
```

## 四、Pinia Store 测试

```ts
import { setActivePinia, createPinia } from 'pinia';
import { useUserStore } from './userStore';

beforeEach(() => {
  setActivePinia(createPinia());
});

it('updates user', () => {
  const store = useUserStore();
  store.setUser({ name: 'Alice' });
  expect(store.user.name).toBe('Alice');
});
```

## 五、网络请求测试

```ts
import { http, HttpResponse } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  http.get('/api/user', () => {
    return HttpResponse.json({ name: 'Alice' });
  })
);

beforeAll(() => server.listen());
afterAll(() => server.close());
afterEach(() => server.resetHandlers());

it('fetches user', async () => {
  const wrapper = mount(UserProfile);
  await flushPromises();
  expect(wrapper.text()).toContain('Alice');
});
```

## 六、断言工具

```ts
import { expect, vi } from 'vitest';

// 模拟函数
const mockFn = vi.fn();
mockFn();
expect(mockFn).toHaveBeenCalled();

// 定时器
vi.useFakeTimers();
setTimeout();
vi.runAllTimers();
```

## 七、最佳实践

- 测试组件行为而不是实现细节
- 合理使用 mock 和 stub
- 保持测试独立和可重复
- 测试边界情况
- 使用 describe 和 it 组织测试
- 定期运行测试
