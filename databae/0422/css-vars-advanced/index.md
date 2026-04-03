# CSS 变量高级技巧：动态主题、复杂布局与响应式计算

CSS 变量（自定义属性）不仅仅是存储颜色的工具，它还能实现强大的动态效果。本文将带你探索 CSS 变量的高级用法。

## 一、CSS 变量基础回顾

### 1. 定义和使用

```css
:root {
  --primary-color: #007bff;
  --font-size-base: 16px;
}

.button {
  background-color: var(--primary-color);
  font-size: var(--font-size-base);
}
```

### 2.  fallback 值

```css
.button {
  background-color: var(--primary-color, #007bff);
}
```

### 3. 作用域

```css
:root {
  --color: blue;
}

.card {
  --color: green;
}

.card .button {
  background-color: var(--color); /* green */
}
```

## 二、动态主题切换

### 1. 基础主题

```css
:root {
  --bg-color: #ffffff;
  --text-color: #333333;
  --border-color: #dddddd;
}

[data-theme="dark"] {
  --bg-color: #1a1a1a;
  --text-color: #ffffff;
  --border-color: #333333;
}

body {
  background-color: var(--bg-color);
  color: var(--text-color);
}
```

```javascript
document.documentElement.setAttribute('data-theme', 'dark');
```

### 2. 多主题系统

```css
:root {
  --theme-primary: #007bff;
  --theme-secondary: #6c757d;
  --theme-success: #28a745;
}

[data-theme="ocean"] {
  --theme-primary: #00bcd4;
  --theme-secondary: #009688;
  --theme-success: #4caf50;
}

[data-theme="sunset"] {
  --theme-primary: #ff5722;
  --theme-secondary: #ff9800;
  --theme-success: #ffc107;
}
```

### 3. 实时主题定制

```css
:root {
  --hue: 210;
  --primary: hsl(var(--hue), 100%, 50%);
  --primary-light: hsl(var(--hue), 100%, 70%);
  --primary-dark: hsl(var(--hue), 100%, 30%);
}
```

```javascript
const hueInput = document.querySelector('#hue-slider');
hueInput.addEventListener('input', (e) => {
  document.documentElement.style.setProperty('--hue', e.target.value);
});
```

## 三、响应式设计

### 1. 响应式变量

```css
:root {
  --font-size: 16px;
  --spacing: 16px;
}

@media (min-width: 768px) {
  :root {
    --font-size: 18px;
    --spacing: 24px;
  }
}

@media (min-width: 1024px) {
  :root {
    --font-size: 20px;
    --spacing: 32px;
  }
}

body {
  font-size: var(--font-size);
}

.container {
  padding: var(--spacing);
  gap: var(--spacing);
}
```

### 2. 流体排版

```css
:root {
  --font-size-min: 16;
  --font-size-max: 20;
  --viewport-min: 400;
  --viewport-max: 1200;
  
  --font-size: calc(
    var(--font-size-min) * 1px + 
    (var(--font-size-max) - var(--font-size-min)) * 
    (100vw - var(--viewport-min) * 1px) / 
    (var(--viewport-max) - var(--viewport-min))
  );
}

body {
  font-size: clamp(
    var(--font-size-min) * 1px,
    var(--font-size),
    var(--font-size-max) * 1px
  );
}
```

### 3. 响应式间距系统

```css
:root {
  --spacing-unit: 8px;
  --spacing-1: calc(var(--spacing-unit) * 1);
  --spacing-2: calc(var(--spacing-unit) * 2);
  --spacing-3: calc(var(--spacing-unit) * 3);
  --spacing-4: calc(var(--spacing-unit) * 4);
  --spacing-6: calc(var(--spacing-unit) * 6);
  --spacing-8: calc(var(--spacing-unit) * 8);
}

.card {
  padding: var(--spacing-4);
  margin-bottom: var(--spacing-6);
}
```

## 四、复杂布局计算

### 1. 动态计算

```css
:root {
  --header-height: 64px;
  --footer-height: 48px;
}

.main-content {
  min-height: calc(100vh - var(--header-height) - var(--footer-height));
}
```

### 2. 网格系统

```css
:root {
  --columns: 12;
  --gutter: 24px;
  --container-max: 1200px;
}

.container {
  max-width: var(--container-max);
  padding: 0 calc(var(--gutter) / 2);
}

.row {
  display: flex;
  flex-wrap: wrap;
  margin: 0 calc(var(--gutter) / -2);
}

.col {
  padding: 0 calc(var(--gutter) / 2);
}

.col-6 {
  width: calc(100% / var(--columns) * 6);
}

.col-4 {
  width: calc(100% / var(--columns) * 4);
}
```

### 3. 比例计算

```css
:root {
  --aspect-ratio: 16 / 9;
}

.video-container {
  position: relative;
  width: 100%;
}

.video-container::before {
  content: '';
  display: block;
  padding-bottom: calc(100% / (var(--aspect-ratio)));
}

.video-container iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
}
```

## 五、动画与交互

### 1. 动态过渡

```css
:root {
  --transition-speed: 0.3s;
  --transition-easing: ease;
}

.button {
  background-color: var(--primary-color);
  transition: 
    background-color var(--transition-speed) var(--transition-easing),
    transform var(--transition-speed) var(--transition-easing);
}

.button:hover {
  --primary-color: #0056b3;
  transform: translateY(-2px);
}
```

### 2. 动画延迟序列

```css
:root {
  --item-count: 5;
  --animation-delay-base: 0.1s;
}

.item {
  opacity: 0;
  transform: translateY(20px);
  animation: fadeInUp 0.5s forwards;
}

.item:nth-child(1) { animation-delay: calc(var(--animation-delay-base) * 0); }
.item:nth-child(2) { animation-delay: calc(var(--animation-delay-base) * 1); }
.item:nth-child(3) { animation-delay: calc(var(--animation-delay-base) * 2); }
.item:nth-child(4) { animation-delay: calc(var(--animation-delay-base) * 3); }
.item:nth-child(5) { animation-delay: calc(var(--animation-delay-base) * 4); }

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

## 六、组件库设计

### 1. 按钮组件

```css
:root {
  --button-padding-y: 0.5rem;
  --button-padding-x: 1rem;
  --button-radius: 0.25rem;
  --button-font-size: 1rem;
  --button-primary-bg: #007bff;
  --button-primary-color: #fff;
  --button-secondary-bg: #6c757d;
  --button-secondary-color: #fff;
  --button-danger-bg: #dc3545;
  --button-danger-color: #fff;
}

.button {
  padding: var(--button-padding-y) var(--button-padding-x);
  border-radius: var(--button-radius);
  font-size: var(--button-font-size);
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.button--primary {
  background-color: var(--button-primary-bg);
  color: var(--button-primary-color);
}

.button--secondary {
  background-color: var(--button-secondary-bg);
  color: var(--button-secondary-color);
}

.button--danger {
  background-color: var(--button-danger-bg);
  color: var(--button-danger-color);
}

.button--small {
  --button-padding-y: 0.25rem;
  --button-padding-x: 0.5rem;
  --button-font-size: 0.875rem;
}

.button--large {
  --button-padding-y: 0.75rem;
  --button-padding-x: 1.5rem;
  --button-font-size: 1.125rem;
}
```

### 2. 卡片组件

```css
:root {
  --card-padding: 1.5rem;
  --card-radius: 0.5rem;
  --card-shadow: 0 2px 4px rgba(0,0,0,0.1);
  --card-bg: #ffffff;
  --card-border: 1px solid #e9ecef;
}

.card {
  background-color: var(--card-bg);
  border: var(--card-border);
  border-radius: var(--card-radius);
  padding: var(--card-padding);
  box-shadow: var(--card-shadow);
}

.card--outlined {
  --card-shadow: none;
}

.card--elevated {
  --card-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
```

## 七、与 JavaScript 结合

### 1. 动态修改变量

```javascript
const root = document.documentElement;

// 设置变量
root.style.setProperty('--primary-color', '#ff5722');

// 获取变量
const primaryColor = getComputedStyle(root).getPropertyValue('--primary-color');
console.log(primaryColor); // '#ff5722'

// 删除变量
root.style.removeProperty('--primary-color');
```

### 2. 主题切换器

```javascript
const themes = {
  light: {
    '--bg-color': '#ffffff',
    '--text-color': '#333333',
    '--primary-color': '#007bff'
  },
  dark: {
    '--bg-color': '#1a1a1a',
    '--text-color': '#ffffff',
    '--primary-color': '#4dabf7'
  },
  ocean: {
    '--bg-color': '#e3f2fd',
    '--text-color': '#0d47a1',
    '--primary-color': '#0288d1'
  }
};

function setTheme(themeName) {
  const theme = themes[themeName];
  const root = document.documentElement;
  
  for (const [key, value] of Object.entries(theme)) {
    root.style.setProperty(key, value);
  }
  
  localStorage.setItem('theme', themeName);
}

document.querySelector('#theme-select').addEventListener('change', (e) => {
  setTheme(e.target.value);
});
```

### 3. 实时调整

```html
<label>
  主色调：
  <input type="color" id="primary-color-picker" value="#007bff">
</label>

<label>
  圆角大小：
  <input type="range" id="radius-slider" min="0" max="20" value="4">
</label>
```

```javascript
document.querySelector('#primary-color-picker').addEventListener('input', (e) => {
  document.documentElement.style.setProperty('--primary-color', e.target.value);
});

document.querySelector('#radius-slider').addEventListener('input', (e) => {
  document.documentElement.style.setProperty('--button-radius', `${e.target.value}px`);
});
```

## 八、性能优化

### 1. 避免过度使用 calc

```css
/* ✅ 好：预计算值 */
:root {
  --spacing-1: 8px;
  --spacing-2: 16px;
  --spacing-3: 24px;
}

/* ❌ 避免：每次都计算 */
.element {
  margin: calc(8px * 3);
}
```

### 2. 合理使用作用域

```css
/* ✅ 好：全局变量放 :root */
:root {
  --primary-color: #007bff;
}

/* ✅ 好：组件变量放组件作用域 */
.card {
  --card-bg: #fff;
}
```

## 九、浏览器兼容性

```css
/* 检查支持 */
@supports (--color: red) {
  :root {
    --primary-color: #007bff;
  }
}

/* 降级方案 */
.button {
  background-color: #007bff;
  background-color: var(--primary-color, #007bff);
}
```

## 十、最佳实践

1. 建立设计系统
2. 使用语义化的变量名
3. 提供 fallback 值
4. 组织变量层级
5. 文档化变量
6. 考虑性能

## 十一、总结

CSS 变量让样式更灵活：
- 实现动态主题
- 简化响应式设计
- 构建可复用组件
- 与 JavaScript 无缝配合
- 提升开发效率

开始使用 CSS 变量，让你的样式更强大！
