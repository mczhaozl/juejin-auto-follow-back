# Vue 3 Pinia 完全指南

## 一、创建 Store

```typescript
// stores/counter.ts
import { defineStore } from 'pinia';

export const useCounterStore = defineStore('counter', {
  state: () => ({ count: 0 }),
  getters: {
    double: (state) => state.count * 2
  },
  actions: {
    inc() {
      this.count++;
    }
  }
});
```

## 二、使用 Store

```vue
<script setup>
import { useCounterStore } from '@/stores/counter';

const store = useCounterStore();
</script>

<template>
  <div>
    Count: {{ store.count }}
    Double: {{ store.double }}
    <button @click="store.inc">+</button>
  </div>
</template>
```

## 三、Setup Stores

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useCounterStore = defineStore('counter', () => {
  const count = ref(0);
  const double = computed(() => count.value * 2);
  function inc() {
    count.value++;
  }
  return { count, double, inc };
});
```

## 四、持久化

```typescript
// 插件持久化
import { createPinia } from 'pinia';
import piniaPluginPersistedstate from 'pinia-plugin-persistedstate';

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);
```

## 五、最佳实践

- 使用 setup 风格 store（更现代）
- 合理划分 store 模块
- 使用 getters 计算派生状态
- 错误处理在 actions 中
- 持久化敏感数据要加密
