# SVG 完全指南：从基础到实战

> 全面介绍 SVG 的基本概念、常用元素、在前端项目中的使用方式，以及优化技巧。

---

## 一、SVG 是什么

SVG（Scalable Vector Graphics）= 可缩放矢量图形，是一种基于 XML 的图像格式。

### 核心特点

- 矢量图：无限缩放不失真
- 文本格式：可用代码编辑
- 体积小：适合图标、Logo
- 可交互：支持 CSS 和 JS 操作
- SEO 友好：内容可被搜索引擎读取

### 与位图对比

| 特性 | SVG（矢量） | PNG/JPG（位图） |
|------|-------------|-----------------|
| 缩放 | 不失真 | 放大模糊 |
| 文件大小 | 简单图形小 | 复杂图像小 |
| 编辑 | 可用代码 | 需要图像编辑器 |
| 适用场景 | 图标、Logo、图表 | 照片、复杂图像 |

## 二、基础语法

### 最简单的 SVG

```html
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <circle cx="50" cy="50" r="40" fill="red" />
</svg>
```

### 视口与视图框

```html
<svg width="200" height="200" viewBox="0 0 100 100">
  <!-- viewBox: 定义坐标系统 -->
  <!-- width/height: 实际显示大小 -->
  <circle cx="50" cy="50" r="40" fill="blue" />
</svg>
```

`viewBox="minX minY width height"`：

- 前两个参数：坐标系原点
- 后两个参数：坐标系宽高
- 实际大小由 width/height 决定

## 三、常用基本形状

### 1. 矩形 rect

```html
<svg width="200" height="100">
  <rect x="10" y="10" width="180" height="80" 
        fill="lightblue" stroke="navy" stroke-width="2" 
        rx="10" ry="10" />
  <!-- rx/ry: 圆角半径 -->
</svg>
```

### 2. 圆形 circle

```html
<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" fill="orange" />
  <!-- cx/cy: 圆心坐标, r: 半径 -->
</svg>
```

### 3. 椭圆 ellipse

```html
<svg width="200" height="100">
  <ellipse cx="100" cy="50" rx="80" ry="30" fill="pink" />
  <!-- rx: 水平半径, ry: 垂直半径 -->
</svg>
```

### 4. 线条 line

```html
<svg width="200" height="100">
  <line x1="10" y1="10" x2="190" y2="90" 
        stroke="black" stroke-width="2" />
</svg>
```

### 5. 折线 polyline

```html
<svg width="200" height="100">
  <polyline points="10,10 50,50 90,10 130,50 170,10" 
            fill="none" stroke="purple" stroke-width="2" />
</svg>
```

### 6. 多边形 polygon

```html
<svg width="200" height="200">
  <!-- 五角星 -->
  <polygon points="100,10 40,198 190,78 10,78 160,198" 
           fill="gold" stroke="orange" stroke-width="2" />
</svg>
```

## 四、路径 path（最强大）

### 基本命令

```html
<svg width="200" height="200">
  <path d="M 10 10 L 90 90 L 10 90 Z" 
        fill="lightgreen" stroke="green" stroke-width="2" />
</svg>
```

命令说明：

- `M x y`：移动到（Move to）
- `L x y`：直线到（Line to）
- `H x`：水平线到
- `V y`：垂直线到
- `Z`：闭合路径
- `C x1 y1 x2 y2 x y`：三次贝塞尔曲线
- `Q x1 y1 x y`：二次贝塞尔曲线
- `A rx ry rotation large-arc sweep x y`：弧线

### 曲线示例

```html
<svg width="200" height="200">
  <!-- 二次贝塞尔曲线 -->
  <path d="M 10 80 Q 95 10 180 80" 
        fill="none" stroke="blue" stroke-width="2" />
  
  <!-- 三次贝塞尔曲线 -->
  <path d="M 10 150 C 40 100 160 100 190 150" 
        fill="none" stroke="red" stroke-width="2" />
</svg>
```

## 五、文本

```html
<svg width="200" height="100">
  <text x="10" y="50" font-size="20" fill="navy">
    Hello SVG
  </text>
  
  <!-- 沿路径的文本 -->
  <defs>
    <path id="curve" d="M 10 80 Q 95 10 180 80" />
  </defs>
  <text font-size="14" fill="purple">
    <textPath href="#curve">
      Text along a curve
    </textPath>
  </text>
</svg>
```

## 六、渐变与图案

### 线性渐变

```html
<svg width="200" height="100">
  <defs>
    <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:rgb(255,255,0);stop-opacity:1" />
      <stop offset="100%" style="stop-color:rgb(255,0,0);stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="200" height="100" fill="url(#grad1)" />
</svg>
```

### 径向渐变

```html
<svg width="200" height="200">
  <defs>
    <radialGradient id="grad2">
      <stop offset="0%" style="stop-color:white" />
      <stop offset="100%" style="stop-color:blue" />
    </radialGradient>
  </defs>
  <circle cx="100" cy="100" r="80" fill="url(#grad2)" />
</svg>
```

## 七、在前端项目中使用 SVG

### 方式 1：内联 SVG

```html
<div>
  <svg width="50" height="50">
    <circle cx="25" cy="25" r="20" fill="red" />
  </svg>
</div>
```

优点：可用 CSS/JS 操作
缺点：HTML 体积大

### 方式 2：img 标签

```html
<img src="icon.svg" alt="icon" width="50" height="50" />
```

优点：简单，可缓存
缺点：不能用 CSS 改颜色

### 方式 3：CSS 背景

```css
.icon {
  width: 50px;
  height: 50px;
  background: url('icon.svg') no-repeat center;
  background-size: contain;
}
```

### 方式 4：symbol + use（推荐）

```html
<!-- 定义 symbol -->
<svg style="display: none;">
  <symbol id="icon-heart" viewBox="0 0 24 24">
    <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
  </symbol>
</svg>

<!-- 使用 -->
<svg width="24" height="24">
  <use href="#icon-heart" fill="red" />
</svg>
```

### 方式 5：React 组件

```jsx
// Icon.jsx
function Icon({ name, size = 24, color = 'currentColor' }) {
  return (
    <svg width={size} height={size} fill={color}>
      <use href={`#icon-${name}`} />
    </svg>
  );
}

// 使用
<Icon name="heart" size={32} color="red" />
```

## 八、Vite 项目中使用 SVG

### 安装插件

```bash
npm install vite-plugin-svg-icons -D
```

### 配置 vite.config.js

```javascript
import { defineConfig } from 'vite';
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons';
import path from 'path';

export default defineConfig({
  plugins: [
    createSvgIconsPlugin({
      iconDirs: [path.resolve(process.cwd(), 'src/icons')],
      symbolId: 'icon-[name]'
    })
  ]
});
```

### 在 main.js 中引入

```javascript
import 'virtual:svg-icons-register';
```

### 封装组件

```vue
<!-- SvgIcon.vue -->
<template>
  <svg :width="size" :height="size" :fill="color">
    <use :href="`#icon-${name}`" />
  </svg>
</template>

<script setup>
defineProps({
  name: String,
  size: { type: Number, default: 24 },
  color: { type: String, default: 'currentColor' }
});
</script>
```

### 使用

```vue
<SvgIcon name="heart" :size="32" color="red" />
```

## 九、SVG 动画

### CSS 动画

```html
<svg width="100" height="100">
  <circle cx="50" cy="50" r="40" fill="blue" class="pulse" />
</svg>

<style>
.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { r: 40; opacity: 1; }
  50% { r: 45; opacity: 0.5; }
}
</style>
```

### SMIL 动画

```html
<svg width="200" height="100">
  <circle cx="50" cy="50" r="20" fill="red">
    <animate attributeName="cx" from="50" to="150" 
             dur="2s" repeatCount="indefinite" />
  </circle>
</svg>
```

### JavaScript 动画

```javascript
const circle = document.querySelector('circle');
let x = 50;

function animate() {
  x += 1;
  if (x > 150) x = 50;
  circle.setAttribute('cx', x);
  requestAnimationFrame(animate);
}

animate();
```

## 十、优化技巧

### 1. 压缩 SVG

使用 SVGO：

```bash
npm install -g svgo
svgo input.svg -o output.svg
```

### 2. 移除无用属性

```html
<!-- ❌ 冗余 -->
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     version="1.1" id="Layer_1" x="0px" y="0px">
  
<!-- ✅ 精简 -->
<svg viewBox="0 0 24 24">
```

### 3. 使用 currentColor

```html
<svg fill="currentColor">
  <path d="..." />
</svg>
```

```css
.icon { color: red; } /* SVG 会继承颜色 */
```

### 4. 懒加载

```javascript
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const svg = entry.target;
      svg.innerHTML = svg.dataset.svg;
      observer.unobserve(svg);
    }
  });
});

document.querySelectorAll('.lazy-svg').forEach(svg => {
  observer.observe(svg);
});
```

## 十一、常见问题

### 1. SVG 在 img 中无法改颜色

解决：用内联 SVG 或 CSS mask：

```css
.icon {
  mask: url('icon.svg') no-repeat center;
  mask-size: contain;
  background-color: red; /* 可改颜色 */
}
```

### 2. SVG 在不同浏览器显示不一致

解决：明确设置 viewBox 和 preserveAspectRatio。

### 3. SVG 文件过大

解决：

- 用 SVGO 压缩
- 简化路径
- 移除不必要的分组和属性

## 总结

SVG 的核心优势：

- 矢量图，无限缩放不失真
- 体积小，适合图标和 Logo
- 可用 CSS/JS 操作，支持动画
- SEO 友好

前端使用建议：

- 图标：symbol + use 或 vite-plugin-svg-icons
- 简单图形：内联 SVG
- 大量图标：雪碧图（sprite）
- 需要缓存：img 标签

优化要点：

- 用 SVGO 压缩
- 移除无用属性
- 使用 currentColor 继承颜色
- 按需加载

SVG 是现代前端必备技能，掌握后能大幅提升图标和图形的开发效率。
