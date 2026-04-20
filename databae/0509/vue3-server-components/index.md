# Vue 3 Server Components 完全指南

## 一、Nuxt 3 服务端组件

```vue
<!-- app.vue -->
<template>
  <div>
    <h1>Hello Nuxt</h1>
    <!-- 服务端组件 -->
    <ServerSideComponent />
    <!-- 客户端组件 -->
    <ClientSideComponent />
  </div>
</template>

<!-- components/ServerSideComponent.server.vue -->
<template>
  <div>服务端渲染内容：{{ serverData }}</div>
</template>

<script setup>
// 服务端组件可以直接使用服务端 API
const serverData = await fetch('https://api.example.com/data').then(r => r.json());
</script>

<!-- components/ClientSideComponent.client.vue -->
<template>
  <div>客户端内容：{{ count }}</div>
  <button @click="count++">+1</button>
</template>

<script setup>
import { ref } from 'vue';
const count = ref(0);
</script>
```

## 二、数据获取

```vue
<script setup>
// useFetch 在服务端和客户端都执行
const { data } = await useFetch('/api/data');

// useAsyncData 自定义逻辑
const { data: posts } = await useAsyncData('posts', () => 
  $fetch('/api/posts')
);

// 服务端直接获取（服务器组件）
const data = await $fetch('https://api.example.com/data');
</script>
```

## 三、Island Components

```vue
<!-- 岛屿组件：部分客户端水合 -->
<template>
  <div>
    <p>服务端内容</p>
    <ClientOnly>
      <!-- 仅在客户端水合 -->
      <ClientComponent />
      <template #fallback>
        <div>加载中...</div>
      </template>
    </ClientOnly>
  </div>
</template>
```

## 四、最佳实践

- 服务端组件用于数据获取和无交互内容
- 客户端组件用于用户交互
- 合理使用 useFetch 和 useAsyncData
- 监控水合时间和 TTI
- 使用 islands 优化性能
- 数据缓存策略优化
