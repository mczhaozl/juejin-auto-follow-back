# Tailwind CSS 完全指南：实用优先的 CSS 框架

> 深入讲解 Tailwind CSS，包括实用类、响应式设计、自定义配置，以及 JIT 模式和生产优化。

## 一、快速开始

### 1.1 安装

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 1.2 配置

```javascript
// tailwind.config.js
module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

### 1.3 基础用法

```html
<div class="flex items-center justify-center min-h-screen bg-gray-100">
  <div class="p-6 bg-white rounded-lg shadow-lg">
    <h1 class="text-2xl font-bold text-gray-800">Hello</h1>
  </div>
</div>
```

## 二、常用类

### 2.1 布局

```html
<!-- Flex -->
<div class="flex flex-row gap-4">
  <div class="flex-1">1</div>
  <div class="flex-1">2</div>
</div>

<!-- Grid -->
<div class="grid grid-cols-3 gap-4">
  <div>1</div>
  <div>2</div>
  <div>3</div>
</div>
```

### 2.2 间距

```html
<!-- Padding -->
<div class="p-4">       <!-- 全部 -->
<div class="px-4 py-2"> <!-- 水平/垂直 -->
<div class="pt-4">      <!-- 单独方向 -->

<!-- Margin -->
<div class="m-4">
<div class="mx-auto">   <!-- 水平居中 -->
```

### 2.3 颜色

```html
<!-- 文本 -->
<p class="text-gray-500">灰色文本</p>

<!-- 背景 -->
<div class="bg-blue-500">蓝色背景</div>

<!-- 边框 -->
<div class="border border-gray-300"></div>
```

### 2.4 响应式

```html
<!-- 响应式前缀 -->
<div class="text-sm md:text-base lg:text-lg">
  响应式文本
</div>

<!-- 断点 -->
<!-- sm: 640px -->
<!-- md: 768px -->
<!-- lg: 1024px -->
<!-- xl: 1280px -->
```

## 三、自定义

### 3.1 主题扩展

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: '#007bff',
        secondary: '#6c757d'
      },
      spacing: {
        '128': '32rem'
      }
    }
  }
}
```

### 3.2 自定义类

```css
@layer components {
  .btn-primary {
    @apply px-4 py-2 bg-blue-500 text-white rounded;
  }
}
```

## 四、状态变体

### 4.1 Hover/Focus

```html
<button class="hover:bg-blue-600 focus:ring-2">
  按钮
</button>

<input class="focus:outline-none focus:ring-2 focus:ring-blue-500">
```

### 4.2 Active/Disabled

```html
<button class="active:bg-blue-700 disabled:opacity-50">
  按钮
</button>
```

## 五、总结

Tailwind CSS 核心要点：

1. **实用类**：直接编写样式
2. **响应式**：断点前缀
3. **状态变体**：hover/focus/active
4. **自定义**：tailwind.config.js
5. **JIT**：按需生成

掌握这些，Tailwind 不再难！

---

**推荐阅读**：
- [Tailwind CSS 文档](https://tailwindcss.com/docs)

**如果对你有帮助，欢迎点赞收藏！**
