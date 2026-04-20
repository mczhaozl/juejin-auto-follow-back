# Vue 3 i18n 完全指南

## 一、安装配置

```ts
// main.ts
import { createApp } from 'vue';
import { createI18n } from 'vue-i18n';
import App from './App.vue';

const messages = {
  'zh-CN': {
    hello: '你好',
    welcome: '欢迎来到 {name}'
  },
  'en-US': {
    hello: 'Hello',
    welcome: 'Welcome to {name}'
  }
};

const i18n = createI18n({
  legacy: false,
  locale: 'zh-CN',
  fallbackLocale: 'en-US',
  messages
});

createApp(App).use(i18n).mount('#app');
```

## 二、基础使用

```vue
<template>
  <div>
    <h1>{{ $t('hello') }}</h1>
    <p>{{ $t('welcome', { name: 'Vue' }) }}</p>
    
    <button @click="toggleLocale">切换语言</button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n';
const { locale, t } = useI18n();

function toggleLocale() {
  locale.value = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN';
}
</script>
```

## 三、复数和选择

```ts
const messages = {
  'zh-CN': {
    apple: '苹果 | 苹果'
  }
};
```

## 四、日期和数字格式化

```ts
const datetimeFormats = {
  'zh-CN': {
    short: { year: 'numeric', month: 'short', day: 'numeric' }
  }
};
```

## 五、最佳实践

- 使用命名空间组织翻译
- 延迟加载语言包优化加载时间
- 配置 fallback locale
- 格式化日期和数字
- 与路由集成（语言前缀）
