# CSS 动画与过渡完全指南：从基础到高级效果

## 一、CSS Transition（过渡）

### 1.1 基本用法

```css
.button {
  background: blue;
  transition: background 0.3s ease;
}

.button:hover {
  background: red;
}
```

### 1.2 transition 属性详解

```css
.element {
  /* 属性 | 持续时间 | 时间函数 | 延迟 */
  transition: all 0.3s ease-in-out 0.1s;
  
  /* 分别设置 */
  transition-property: background, transform;
  transition-duration: 0.3s, 0.5s;
  transition-timing-function: ease, linear;
  transition-delay: 0s, 0.1s;
}
```

---

## 二、贝塞尔曲线

```css
.element {
  transition-timing-function: ease; /* 默认 */
  transition-timing-function: ease-in;
  transition-timing-function: ease-out;
  transition-timing-function: ease-in-out;
  transition-timing-function: linear;
  
  /* 自定义 cubic-bezier */
  transition-timing-function: cubic-bezier(0.68, -0.55, 0.265, 1.55);
}
```

---

## 三、CSS Animation（动画）

### 3.1 基本示例

```css
@keyframes slideIn {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.element {
  animation: slideIn 0.5s ease-out forwards;
}
```

### 3.2 多关键帧

```css
@keyframes bounce {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-20px);
  }
}

.element {
  animation: bounce 1s ease infinite;
}
```

### 3.3 animation 属性

```css
.element {
  /* 名称 | 持续时间 | 时间函数 | 延迟 | 次数 | 方向 | 填充模式 | 播放状态 */
  animation: bounce 1s ease 0.1s infinite alternate both running;
  
  animation-name: bounce;
  animation-duration: 1s;
  animation-timing-function: ease;
  animation-delay: 0.1s;
  animation-iteration-count: infinite; /* 或数字 */
  animation-direction: normal; /* reverse | alternate | alternate-reverse */
  animation-fill-mode: none; /* forwards | backwards | both */
  animation-play-state: running; /* paused */
}
```

---

## 四、Transform 变换

### 4.1 2D 变换

```css
.transform {
  transform: translate(50px, 20px);
  transform: rotate(45deg);
  transform: scale(1.5);
  transform: skewX(20deg);
  transform: skewY(10deg);
  
  /* 组合 */
  transform: translateX(100px) rotate(45deg) scale(1.5);
}
```

### 4.2 3D 变换

```css
.container {
  perspective: 1000px;
  perspective-origin: 50% 50%;
}

.box {
  transform-style: preserve-3d;
  transform: rotateY(45deg) translateZ(50px);
}
```

---

## 五、实战效果

### 5.1 悬浮卡片

```css
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.card:hover {
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}
```

### 5.2 加载动画

```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}
```

### 5.3 脉冲动画

```css
@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}
```

### 5.4 打字效果

```css
@keyframes typing {
  from { width: 0; }
  to { width: 100%; }
}

@keyframes blink {
  50% { border-color: transparent; }
}

.typewriter {
  overflow: hidden;
  white-space: nowrap;
  border-right: 3px solid black;
  animation: typing 3s steps(40, end), blink 0.75s step-end infinite;
}
```

### 5.5 波浪效果

```css
@keyframes wave {
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-10px);
  }
}

.wave span {
  display: inline-block;
  animation: wave 1s ease-in-out infinite;
}

.wave span:nth-child(2) { animation-delay: 0.1s; }
.wave span:nth-child(3) { animation-delay: 0.2s; }
.wave span:nth-child(4) { animation-delay: 0.3s; }
```

---

## 六、性能优化

### 6.1 使用 transform 和 opacity

```css
/* 好 - 只触发合成层 */
.element {
  transform: translateX(100px);
  opacity: 0.5;
  transition: transform 0.3s, opacity 0.3s;
}

/* 不好 - 触发布局和绘制 */
.element {
  left: 100px;
  width: 200px;
}
```

### 6.2 will-change

```css
.element {
  will-change: transform, opacity;
}
```

### 6.3 硬件加速

```css
.element {
  transform: translateZ(0);
  /* 或 */
  transform: translate3d(0, 0, 0);
}
```

---

## 七、动画与 JavaScript 结合

```javascript
const element = document.querySelector('.animated');

// 触发重绘
element.classList.add('start-animation');

// 监听动画事件
element.addEventListener('animationstart', () => {
  console.log('Animation started');
});

element.addEventListener('animationend', () => {
  console.log('Animation ended');
});

element.addEventListener('animationiteration', () => {
  console.log('Animation iteration');
});
```

---

## 八、CSS 变量与动画

```css
:root {
  --animation-duration: 0.3s;
  --primary-color: #3498db;
}

.element {
  color: var(--primary-color);
  transition: color var(--animation-duration);
}

.element:hover {
  --primary-color: #e74c3c;
}
```

---

## 九、最佳实践

1. 优先使用 transform 和 opacity 动画
2. 合理使用 will-change
3. 避免动画过多导致性能问题
4. 使用 CSS 变量增加可维护性
5. 在移动设备上测试动画性能

---

## 十、总结

CSS 动画与过渡能为用户提供流畅的交互体验，但需注意性能优化。
