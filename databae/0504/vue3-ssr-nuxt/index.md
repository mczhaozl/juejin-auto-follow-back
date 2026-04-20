# Vue 3 SSR 与 Nuxt 3 完全指南

## 一、Nuxt 3 项目初始化

```bash
npx nuxi init my-nuxt-app
cd my-nuxt-app
npm install
npm run dev
```

## 二、页面与路由

```vue
<!-- pages/posts/[id].vue -->
<script setup>
const route = useRoute();
const { data: post } = await useFetch(`/api/posts/${route.params.id}`);
</script>

<template>
  <div>
    <h1>{{ post.title }}</h1>
  </div>
</template>
```

## 三、数据获取

```typescript
// useFetch
const { data, pending, error, refresh } = await useFetch('/api/posts');

// useAsyncData
const { data } = await useAsyncData('posts', () => $fetch('/api/posts'));

// useLazyFetch
const { data } = useLazyFetch('/api/posts');
```

## 四、SEO 优化

```vue
<script setup>
useHead({
  title: 'My Blog',
  meta: [{ name: 'description', content: '...' }]
});
</script>
```

## 五、中间件

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const user = useUser();
  if (!user.value) return navigateTo('/login');
});
```

## 六、服务端 API

```typescript
// server/api/posts.get.ts
export default defineEventHandler(async (event) => {
  const posts = await db.posts.findMany();
  return posts;
});
```

## 七、部署

```bash
# 构建生产构建
npm run build

# 预览
npm run preview

# 静态站点
npm run generate
```

## 八、最佳实践

- 使用组合式函数复用逻辑
- 合理使用缓存策略
- 优化图片资源预加载
- 使用 TypeScript 增强类型安全
