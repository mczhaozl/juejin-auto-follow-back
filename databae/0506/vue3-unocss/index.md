# Vue 3 UnoCSS 原子化 CSS 完全指南

## 一、配置 UnoCSS

```ts
// vite.config.ts
import UnoCSS from 'unocss/vite';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [
    vue(),
    UnoCSS({
      presets: [
        presetUno(),
        presetAttributify(),
        presetIcons(),
      ],
    }),
  ],
});
```

```ts
// main.ts
import 'virtual:uno.css';
import { createApp } from 'vue';
import App from './App.vue';

createApp(App).mount('#app');
```

## 二、基础使用

```vue
<template>
  <div class="flex flex-col gap-4">
    <div class="p-4 bg-blue-500 text-white rounded-lg">
      Hello, UnoCSS!
    </div>
    <button class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600">
      Click Me
    </button>
  </div>
</template>
```

## 三、Attributify 模式

```vue
<template>
  <div flex flex-col gap-4 p-8>
    <h1 text="xl" font="bold" text="blue-600">
      Hello, Attributify!
    </h1>
    <div border="rounded-lg">
      Content here
    </div>
  </div>
</template>
```

## 四、Icon 组件

```vue
<template>
  <div class="flex gap-2">
    <div class="i-heroicons-home w-6 h-6" />
    <div class="i-heroicons-search w-6 h-6 text-blue-500" />
  </div>
</template>
```

## 五、自定义规则

```ts
// uno.config.ts
import { defineConfig, presetUno } from 'unocss';

export default defineConfig({
  presets: [presetUno()],
  rules: [
    [/^m-(\d+)$/, ([, d]) => ({ margin: `${d}px` })],
    ['m-10', { margin: '10px' }],
  ],
  shortcuts: {
    'btn': 'px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600',
    'card': 'p-4 bg-white border rounded shadow-md',
  },
  theme: {
    colors: {
      brand: {
        100: '#e6f7ff',
        500: '#1890ff',
        900: '#003a8c',
      },
    },
  },
});
```

## 六、响应式设计

```vue
<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    <div class="p-4 bg-gray-100" v-for="i in 6" :key="i">
      {{ i }}
    </div>
  </div>
</template>
```

## 七、最佳实践

- 从基础工具类开始
- 合理使用 Attributify 模式
- 利用 Icons 提高效率
- 创建常用组件 shortcuts
- 配置自定义主题
- 性能优化：按需使用
