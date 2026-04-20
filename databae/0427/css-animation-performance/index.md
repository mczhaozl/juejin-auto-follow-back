# CSS 动画性能优化完全指南

> 深入理解 CSS 动画原理，掌握性能优化策略，创建流畅的 60fps 动画。

## 一、CSS 动画概述

CSS 动画是前端开发的重要技能，但性能问题很常见。

### 1.1 动画方式对比

```css
/* 1. transition */
.element {
  transition: transform 0.3s ease;
}
.element:hover {
  transform: scale(1.1);
}

/* 2. animation */
@keyframes slide {
  from { transform: translateX(-100%); }
  to { transform: translateX(0); }
}
.element {
  animation: slide 0.5s ease;
}

/* 3. JavaScript 动画 */
// requestAnimationFrame
```

---

## 二、浏览器渲染流程

### 2.1 渲染管道

```
1. Recalculate Style（样式计算）
   ↓
2. Layout（重排/布局）
   ↓
3. Paint（重绘）
   ↓
4. Composite（合成）
```

### 2.2 不同属性触发的阶段

```css
/* 触发布局、重绘、合成 */
.box {
  width: 200px;
  height: 200px;
  margin: 10px;
  padding: 10px;
  border: 1px solid;
}

/* 触发重绘、合成 */
.box {
  color: red;
  background: blue;
  box-shadow: 0 0 10px;
}

/* 只触发合成（性能最好） */
.box {
  transform: scale(1.1);
  opacity: 0.5;
}
```

---

## 三、使用 transform 和 opacity

### 3.1 为什么这两个属性性能好

```css
/* 不推荐：触发布局 */
.animate-left {
  left: 100px;
  transition: left 0.3s;
}

/* 推荐：只触发合成 */
.animate-transform {
  transform: translateX(100px);
  transition: transform 0.3s;
}

/* 不推荐：触发重绘 */
.animate-visibility {
  display: none;
}

/* 推荐：只触发合成 */
.animate-opacity {
  opacity: 0;
  transition: opacity 0.3s;
}
```

### 3.2 性能对比

| 属性 | 布局 | 重绘 | 合成 | 性能 |
|------|------|------|------|------|
| left | ✅ | ✅ | ✅ | 差 |
| width | ✅ | ✅ | ✅ | 差 |
| background | ❌ | ✅ | ✅ | 中 |
| transform | ❌ | ❌ | ✅ | 优 |
| opacity | ❌ | ❌ | ✅ | 优 |

---

## 四、提升到合成层

### 4.1 will-change 属性

```css
/* 提前告诉浏览器元素会变化 */
.element {
  will-change: transform, opacity;
}

/* 按需使用 */
.element:hover {
  will-change: transform;
}
```

### 4.2 transform: translateZ(0)

```css
/* 旧方法，创建新层 */
.element {
  transform: translateZ(0);
  backface-visibility: hidden;
}
```

### 4.3 注意事项

```css
/* 不要过度使用 */
* {
  will-change: all; /* ❌ 错误 */
}

/* 适量使用 */
.animated-element {
  will-change: transform;
}
```

---

## 五、避免布局抖动

### 5.1 什么是布局抖动

```javascript
// 问题：反复读取和写入布局属性
function animate(element) {
  for (let i = 0; i < 100; i++) {
    // 读取
    const width = element.offsetWidth;
    // 写入
    element.style.width = width + 1 + 'px';
  }
}
```

### 5.2 解决方案：批量读写

```javascript
// 推荐：先读后写
function animateBetter(element) {
  // 批量读取
  const width = element.offsetWidth;
  
  // 批量写入
  requestAnimationFrame(() => {
    element.style.width = width + 1 + 'px';
  });
}
```

---

## 六、减少重绘区域

### 6.1 合理的 DOM 结构

```html
<!-- 不推荐：变化影响大面积 -->
<div class="container">
  <div class="animated"></div>
  <div class="content">大量内容...</div>
</div>

<!-- 推荐：独立层级 -->
<div class="container">
  <div class="content">大量内容...</div>
</div>
<div class="animated"></div>
```

### 6.2 使用 contain 属性

```css
.element {
  /* 限制影响范围 */
  contain: layout paint size;
}
```

---

## 七、使用 requestAnimationFrame

### 7.1 JavaScript 动画基础

```javascript
function animate() {
  const element = document.querySelector('.box');
  let progress = 0;
  
  function step() {
    progress += 0.01;
    element.style.transform = `translateX(${progress * 100}px)`;
    
    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }
  
  requestAnimationFrame(step);
}
```

### 7.2 使用 Web Animations API

```javascript
const element = document.querySelector('.box');

element.animate([
  { transform: 'translateX(0px)' },
  { transform: 'translateX(100px)' }
], {
  duration: 1000,
  easing: 'ease-out'
});
```

---

## 八、性能测量工具

### 8.1 Chrome DevTools Performance

```
1. 打开 DevTools (F12)
2. 切换到 Performance 标签
3. 点击 Record
4. 执行动画
5. 停止录制
6. 分析结果
```

### 8.2 Layers 面板

```
1. More Tools -> Layers
2. 查看分层情况
3. 检查合成层数量
```

### 8.3 Rendering 面板

```
1. More Tools -> Rendering
2. 开启 Paint flashing（重绘闪烁）
3. 开启 Layout Shift Regions
4. 观察动画时的重绘区域
```

---

## 九、实战案例优化

### 9.1 案例一：滚动动画

```css
/* 不推荐 */
.nav {
  position: fixed;
  top: 0;
  transition: top 0.3s;
}

/* 推荐 */
.nav {
  position: fixed;
  top: 0;
  transform: translateY(0);
  transition: transform 0.3s;
}
.nav.hide {
  transform: translateY(-100%);
}
```

### 9.2 案例二：卡片悬停效果

```css
/* 不推荐 */
.card:hover {
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
  margin-top: -10px;
}

/* 推荐 */
.card {
  transition: transform 0.3s, box-shadow 0.3s;
  will-change: transform;
}
.card:hover {
  transform: translateY(-10px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}
```

### 9.3 案例三：列表动画

```css
/* 使用 FLIP 技术 */
/* First, Last, Invert, Play */
```

---

## 十、移动端优化

### 10.1 减少 GPU 层数量

```css
/* 不要创建过多合成层 */
.animated {
  will-change: transform; /* 适量使用 */
}
```

### 10.2 使用硬件加速但注意内存

```css
/* 合理使用 */
.animated {
  transform: translateZ(0);
  backface-visibility: hidden;
}
```

---

## 十一、最佳实践总结

1. **优先使用 transform 和 opacity**
2. **使用 will-change 提前声明**
3. **避免布局和重绘**
4. **使用 requestAnimationFrame**
5. **批量读写 DOM**
6. **使用性能工具测量**
7. **合理使用硬件加速**

---

## 十二、总结

CSS 动画性能优化的核心是减少布局和重绘，尽量只触发合成阶段。通过合理使用 transform 和 opacity，配合性能工具，可以创建流畅的 60fps 动画。

希望这篇文章对你有帮助！
