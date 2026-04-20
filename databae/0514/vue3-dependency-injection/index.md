# Vue 3 依赖注入完全指南

## 一、provide/inject

```vue
<!-- 父组件 -->
<script setup>
import { provide, ref } from 'vue';
const theme = ref('dark');
provide('theme', theme);
</script>

<!-- 子组件 -->
<script setup>
import { inject } from 'vue';
const theme = inject('theme');
</script>
```

## 二、Symbol Key

```typescript
// 定义 Key
export const ThemeKey = Symbol();

// 提供
provide(ThemeKey, 'dark');

// 注入
const theme = inject(ThemeKey);
```

## 三、提供响应式数据

```vue
<script setup>
import { provide, ref, reactive } from 'vue';
const state = reactive({ count: 0 });
const increment = () => state.count++;

provide('state', state);
provide('increment', increment);
</script>
```

## 四、默认值与检查

```tsx
const value = inject('key', 'default');
const value = inject('key', () => 'factory');
```

## 最佳实践
- 使用 Symbol 避免命名冲突
- provide 与类型声明
- keep 响应式的响应性
- 合理设计注入层级
- 使用组合式函数封装
