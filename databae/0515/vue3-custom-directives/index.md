# Vue 3 自定义指令完全指南

## 一、基本指令

```typescript
// directives/focus.ts
export const vFocus = {
  mounted(el) {
    el.focus();
  }
};
```

```vue
<script setup>
import { vFocus } from './directives/focus';
</script>

<template>
  <input v-focus />
</template>
```

## 二、带参数的指令

```typescript
export const vColor = {
  mounted(el, binding) {
    el.style.color = binding.value;
  },
  updated(el, binding) {
    el.style.color = binding.value;
  }
};
```

```vue
<input v-color="'red'" />
<input v-color="color" />
```

## 三、生命周期钩子

```typescript
export const vMyDir = {
  created(el, binding) {},
  beforeMount() {},
  mounted() {},
  beforeUpdate() {},
  updated() {},
  beforeUnmount() {},
  unmounted() {}
};
```

## 四、指令修饰符

```vue
<input v-foo.once.bar />
```

```typescript
if (binding.modifiers.once) {
  // 执行一次
}
```

## 最佳实践
- 小范围 DOM 操作使用指令
- 复杂逻辑考虑组件
- 文档化自定义指令
- 注意副作用
- 优先用组合式
