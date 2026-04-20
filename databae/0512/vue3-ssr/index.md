# Vue 3 SSR 完全指南

## 一、Vue 3 SSR 基础

```typescript
// server.js
import { createSSRApp } from 'vue';
import App from './App.vue';
import { renderToString } from 'vue/server-renderer';
import express from 'express';

const app = express();

app.get('/', async (req, res) => {
  const vueApp = createSSRApp(App);
  const html = await renderToString(vueApp);
  
  res.send(`
    <!DOCTYPE html>
    <html>
      <body>${html}</body>
    </html>
  `);
});

app.listen(3000);
```

## 二、同构应用

```typescript
// entry-server.ts
import { createSSRApp } from 'vue';
import App from './App.vue';

export function createApp() {
  const app = createSSRApp(App);
  return { app };
}

// entry-client.ts
import { createApp } from './entry-server';
const { app } = createApp();
app.mount('#app');
```

## 三、数据预获取

```typescript
// 1. 使用 useSSRContext
import { useSSRContext } from 'vue';

export default {
  async serverPrefetch() {
    const data = await fetchData();
    this.data = data;
  },
  
  setup() {
    const ssrContext = useSSRContext();
    if (ssrContext) {
      // 服务端
    } else {
      // 客户端
    }
  }
};

// 2. Nuxt 3 useAsyncData
const { data, pending, error } = await useAsyncData('key', () => $fetch('/api/data'));
```

## 四、流式渲染

```typescript
import { renderToNodeStream } from 'vue/server-renderer';

app.get('/', (req, res) => {
  const vueApp = createSSRApp(App);
  
  res.write('<!DOCTYPE html><html><body>');
  
  const stream = renderToNodeStream(vueApp);
  stream.pipe(res, { end: false });
  
  stream.on('end', () => {
    res.end('</body></html>');
  });
});
```

## 最佳实践
- 预取关键数据
- 避免直接访问浏览器 API
- 使用流式渲染优化 TTFB
- 缓存渲染结果
- 合理的组件拆分
