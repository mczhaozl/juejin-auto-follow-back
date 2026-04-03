# Tailwind CSS 高级技巧完全指南：从基础到复杂布局

Tailwind CSS 是一个功能类优先的 CSS 框架，让你可以快速构建现代化界面。本文将带你全面掌握 Tailwind 的高级技巧。

## 一、Tailwind 基础回顾

### 1. 安装与配置

```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

```javascript
// tailwind.config.js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

```css
/* src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 2. 基础使用

```html
<button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  Click me
</button>

<div class="flex justify-center items-center min-h-screen">
  <div class="bg-white shadow-lg rounded-lg p-6 max-w-md w-full">
    <h1 class="text-2xl font-bold text-gray-800 mb-4">Welcome</h1>
    <p class="text-gray-600">Hello, Tailwind CSS!</p>
  </div>
</div>
```

## 二、响应式设计

### 1. 断点系统

```
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
```

```html
<!-- 移动端单列，平板双列，桌面三列 -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
  <div class="bg-blue-100 p-4">1</div>
  <div class="bg-blue-200 p-4">2</div>
  <div class="bg-blue-300 p-4">3</div>
  <div class="bg-blue-400 p-4">4</div>
  <div class="bg-blue-500 p-4">5</div>
  <div class="bg-blue-600 p-4">6</div>
</div>

<!-- 响应式文本 -->
<h1 class="text-xl sm:text-2xl md:text-3xl lg:text-4xl">
  Responsive Heading
</h1>

<!-- 响应式间距 -->
<div class="p-4 md:p-6 lg:p-8">
  Content
</div>

<!-- 响应式显示/隐藏 -->
<div class="hidden md:block">
  只在平板及以上显示
</div>
<div class="block md:hidden">
  只在移动端显示
</div>
```

### 2. 自定义断点

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    screens: {
      'xs': '360px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
      '3xl': '1920px',
    },
  }
}
```

## 三、深色模式

### 1. 启用深色模式

```html
<!-- 基于类名 -->
<div class="dark">
  <div class="bg-white dark:bg-gray-800 text-gray-900 dark:text-white">
    Content
  </div>
</div>

<!-- 基于系统偏好 -->
<!-- tailwind.config.js -->
module.exports = {
  darkMode: 'media', // 或 'class'
}
```

### 2. 完整的深色模式实现

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <script>
    // 初始化深色模式
    if (localStorage.theme === 'dark' || 
        (!('theme' in localStorage) && 
         window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  </script>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  <button 
    onclick="toggleDarkMode()"
    class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700"
  >
    Toggle Dark Mode
  </button>
  
  <script>
    function toggleDarkMode() {
      if (document.documentElement.classList.contains('dark')) {
        document.documentElement.classList.remove('dark');
        localStorage.theme = 'light';
      } else {
        document.documentElement.classList.add('dark');
        localStorage.theme = 'dark';
      }
    }
  </script>
</body>
</html>
```

## 四、自定义主题

### 1. 自定义颜色

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          900: '#1e3a8a',
        },
        brand: {
          light: '#6366f1',
          DEFAULT: '#4f46e5',
          dark: '#4338ca',
        },
      },
    },
  }
}
```

```html
<button class="bg-brand hover:bg-brand-dark text-white">
  Brand Button
</button>
<div class="text-primary-500 bg-primary-50">
  Primary Color
</div>
```

### 2. 自定义字体

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Merriweather', 'serif'],
        mono: ['Fira Code', 'monospace'],
        display: ['Oswald', 'sans-serif'],
      },
      fontSize: {
        'xxs': '0.65rem',
        'fluid-xl': 'clamp(1.5rem, 3vw, 3rem)',
      },
    },
  }
}
```

```html
<h1 class="font-display text-fluid-xl">Display Title</h1>
<code class="font-mono text-xxs">console.log()</code>
```

### 3. 自定义间距和尺寸

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      width: {
        '128': '32rem',
      },
      height: {
        '128': '32rem',
      },
      maxWidth: {
        '8xl': '88rem',
        '9xl': '96rem',
      },
    },
  }
}
```

## 五、组件抽象

### 1. @apply 指令

```css
/* 自定义按钮 */
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors duration-200;
  }
  
  .btn-primary {
    @apply btn bg-blue-600 hover:bg-blue-700 text-white;
  }
  
  .btn-secondary {
    @apply btn bg-gray-200 hover:bg-gray-300 text-gray-800;
  }
  
  .btn-danger {
    @apply btn bg-red-600 hover:bg-red-700 text-white;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-md overflow-hidden;
  }
  
  .form-input {
    @apply w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none;
  }
}
```

```html
<button class="btn-primary">Primary</button>
<button class="btn-secondary">Secondary</button>
<button class="btn-danger">Danger</button>

<div class="card">
  <div class="p-4">
    <input class="form-input" placeholder="Enter text">
  </div>
</div>
```

### 2. 插件创建组件

```javascript
// tailwind.config.js
const plugin = require('tailwindcss/plugin');

module.exports = {
  plugins: [
    plugin(function({ addComponents, theme }) {
      const buttons = {
        '.btn': {
          padding: `${theme('spacing.2')} ${theme('spacing.4')}`,
          borderRadius: theme('borderRadius.lg'),
          fontWeight: theme('fontWeight.medium'),
          transition: 'color 0.2s, background-color 0.2s',
        },
        '.btn-primary': {
          backgroundColor: theme('colors.blue.600'),
          color: theme('colors.white'),
          '&:hover': {
            backgroundColor: theme('colors.blue.700'),
          },
        },
      };
      
      addComponents(buttons);
    }),
  ],
}
```

## 六、复杂布局

### 1. 圣杯布局

```html
<div class="flex flex-col min-h-screen">
  <header class="bg-gray-800 text-white p-4">
    Header
  </header>
  
  <div class="flex flex-1">
    <aside class="w-64 bg-gray-100 p-4 hidden md:block">
      Sidebar
    </aside>
    
    <main class="flex-1 p-4">
      Main Content
    </main>
    
    <aside class="w-64 bg-gray-100 p-4 hidden lg:block">
      Right Sidebar
    </aside>
  </div>
  
  <footer class="bg-gray-800 text-white p-4">
    Footer
  </footer>
</div>
```

### 2. 响应式导航栏

```html
<nav class="bg-white shadow-lg">
  <div class="max-w-7xl mx-auto px-4">
    <div class="flex justify-between items-center h-16">
      <div class="flex items-center">
        <span class="text-xl font-bold text-gray-800">Logo</span>
      </div>
      
      <div class="hidden md:flex space-x-8">
        <a href="#" class="text-gray-600 hover:text-gray-900">Home</a>
        <a href="#" class="text-gray-600 hover:text-gray-900">About</a>
        <a href="#" class="text-gray-600 hover:text-gray-900">Services</a>
        <a href="#" class="text-gray-600 hover:text-gray-900">Contact</a>
      </div>
      
      <div class="md:hidden">
        <button class="mobile-menu-btn p-2">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>
      </div>
    </div>
    
    <div class="mobile-menu hidden md:hidden pb-4">
      <a href="#" class="block py-2 text-gray-600 hover:text-gray-900">Home</a>
      <a href="#" class="block py-2 text-gray-600 hover:text-gray-900">About</a>
      <a href="#" class="block py-2 text-gray-600 hover:text-gray-900">Services</a>
      <a href="#" class="block py-2 text-gray-600 hover:text-gray-900">Contact</a>
    </div>
  </div>
</nav>
```

### 3. 卡片网格

```html
<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
  <article class="bg-white rounded-lg shadow-md overflow-hidden transition-transform hover:scale-105">
    <img src="image.jpg" alt="" class="w-full h-48 object-cover">
    <div class="p-4">
      <h3 class="text-lg font-semibold mb-2">Card Title</h3>
      <p class="text-gray-600 mb-4">Card description goes here...</p>
      <button class="text-blue-600 hover:text-blue-800 font-medium">
        Read More →
      </button>
    </div>
  </article>
  
  <!-- 更多卡片... -->
</div>
```

## 七、动画与过渡

### 1. 过渡动画

```html
<button class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-all duration-300 transform hover:scale-105">
  Hover Me
</button>

<div class="w-24 h-24 bg-red-500 hover:bg-blue-500 hover:w-32 hover:h-32 transition-all duration-500">
  Animated
</div>
```

### 2. 关键帧动画

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        bounce: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-25%)' },
        },
        wiggle: {
          '0%, 100%': { transform: 'rotate(-3deg)' },
          '50%': { transform: 'rotate(3deg)' },
        },
        pulse: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '.5' },
        },
      },
      animation: {
        bounce: 'bounce 1s infinite',
        wiggle: 'wiggle 1s ease-in-out infinite',
        pulse: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  }
}
```

```html
<div class="animate-bounce">Bouncing</div>
<div class="animate-wiggle">Wiggling</div>
<div class="animate-pulse">Pulsing</div>
```

## 八、性能优化

### 1. 内容优化（Content）

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
}
```

### 2. 生产优化

```bash
npm install -D @tailwindcss/aspect-ratio @tailwindcss/forms @tailwindcss/typography
```

```javascript
// tailwind.config.js
module.exports = {
  plugins: [
    require('@tailwindcss/aspect-ratio'),
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

## 九、常用插件

### 1. 表单插件

```bash
npm install -D @tailwindcss/forms
```

```javascript
// tailwind.config.js
module.exports = {
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
```

```html
<input type="text" class="form-input rounded-lg">
<select class="form-select rounded-lg">
  <option>Option 1</option>
</select>
```

### 2. 排版插件

```bash
npm install -D @tailwindcss/typography
```

```html
<article class="prose prose-lg max-w-none">
  <h1>Heading</h1>
  <p>Paragraph...</p>
  <ul>
    <li>Item 1</li>
    <li>Item 2</li>
  </ul>
</article>
```

## 十、最佳实践

1. 保持类名顺序（基础 → 布局 → 间距 → 颜色 → 交互）
2. 使用 @apply 抽象公共组件
3. 合理使用主题扩展
4. 利用响应式断点
5. 深色模式支持
6. 性能优化（content 配置）
7. 使用官方插件
8. 团队约定和规范
9. 组件化思维
10. 持续学习新特性

## 十一、总结

Tailwind CSS 高级技巧：
- 掌握响应式设计
- 实现深色模式
- 自定义主题
- 组件抽象（@apply 和插件）
- 复杂布局实现
- 动画与过渡
- 性能优化
- 常用插件使用
- 遵循最佳实践

开始用 Tailwind CSS 构建你的界面吧！
