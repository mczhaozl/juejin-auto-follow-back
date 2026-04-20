# Vue 3 Nuxt 3 完全指南

## 一、页面路由

```vue
<!-- pages/index.vue -->
<template>
  <h1>Home Page</h1>
</template>

<!-- pages/about.vue -->
<template>
  <h1>About Page</h1>
</template>
```

## 二、数据获取

```vue
<script setup>
const { data: posts } = await useFetch('/api/posts');

// 或使用 useAsyncData
const { data: users } = await useAsyncData('users', () => $fetch('/api/users'));
</script>
```

## 三、API 路由

```ts
// server/api/hello.ts
export default defineEventHandler(() => {
  return {
    message: 'Hello, Nuxt!'
  };
});
```

## 四、Composables

```ts
// composables/useCounter.ts
export const useCounter = () => {
  const count = ref(0);
  const increment = () => count.value++;
  
  return { count, increment };
};
```

## 五、中间件

```ts
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const user = useUser();
  if (!user.value) {
    return navigateTo('/login');
  }
});
```

## 六、配置

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxtjs/tailwindcss'],
  devtools: { enabled: true },
});
```

## 七、最佳实践

- 约定优于配置
- 合理使用 Composables
- API 路由组织
- 数据获取策略
- 性能优化：缓存和预加载
- SEO 优化
