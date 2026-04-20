# CSS Houdini 完全指南：从 Paint API 到自定义布局

## 一、Houdini 概述

### 1.1 什么是 Houdini

CSS Houdini 是一组 API，允许开发者扩展浏览器的渲染引擎。

### 1.2 主要 API

- **Paint Worklet**：自定义绘制
- **Layout Worklet**：自定义布局
- **Animation Worklet**：自定义动画
- **Typed OM**：类型化 CSS 对象模型
- **Properties and Values**：自定义 CSS 属性

---

## 二、Paint Worklet

### 2.1 注册 paint worklet

```javascript
// paint.js
if (typeof registerPaint !== 'undefined') {
  registerPaint('grid', class {
    static get inputProperties() {
      return ['--grid-color', '--grid-size'];
    }
    
    paint(ctx, size, properties) {
      const color = properties.get('--grid-color').toString();
      const size = parseInt(properties.get('--grid-size').toString());
      
      ctx.strokeStyle = color;
      ctx.lineWidth = 1;
      
      for (let x = 0; x < size.width; x += size) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, size.height);
        ctx.stroke();
      }
      
      for (let y = 0; y < size.height; y += size) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(size.width, y);
        ctx.stroke();
      }
    }
  });
}
```

### 2.2 使用 paint worklet

```javascript
// main.js
CSS.paintWorklet.addModule('paint.js');
```

```css
.box {
  --grid-color: #e0e0e0;
  --grid-size: 20;
  background-image: paint(grid);
}
```

### 2.3 复杂图形绘制

```javascript
registerPaint('circles', class {
  static get inputProperties() {
    return ['--circle-count', '--circle-color'];
  }
  
  paint(ctx, size, properties) {
    const count = parseInt(properties.get('--circle-count').toString());
    const color = properties.get('--circle-color').toString();
    
    ctx.fillStyle = color;
    
    for (let i = 0; i < count; i++) {
      const x = Math.random() * size.width;
      const y = Math.random() * size.height;
      const radius = Math.random() * 20 + 5;
      
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.fill();
    }
  }
});
```

---

## 三、Properties and Values

### 3.1 注册自定义属性

```javascript
CSS.registerProperty({
  name: '--gradient-color',
  syntax: '<color>',
  initialValue: '#000000',
  inherits: false
});

CSS.registerProperty({
  name: '--animation-progress',
  syntax: '<number>',
  initialValue: '0',
  inherits: true
});
```

### 3.2 使用自定义属性

```css
.box {
  --gradient-color: #ff0000;
  transition: --gradient-color 1s;
}

.box:hover {
  --gradient-color: #0000ff;
}

@keyframes progress {
  from { --animation-progress: 0; }
  to { --animation-progress: 1; }
}

.animated {
  animation: progress 2s linear infinite;
}
```

---

## 四、Typed OM

### 4.1 使用 Typed OM

```javascript
const element = document.querySelector('.box');

// 获取 CSS 属性
const width = element.attributeStyleMap.get('width');
console.log(width.value, width.unit);

// 设置 CSS 属性
element.attributeStyleMap.set('transform', new CSSTransformValue([
  new CSSTranslate(CSS.px(100), CSS.px(50)),
  new CSSRotate(CSS.deg(45))
]));

element.attributeStyleMap.set('opacity', CSS.number(0.5));
```

### 4.2 CSS Unit Values

```javascript
CSS.px(100);
CSS.percent(50);
CSS.em(1.5);
CSS.rem(2);
CSS.vw(50);
CSS.vh(50);
CSS.deg(45);
CSS.rad(Math.PI / 4);
CSS.s(2);
CSS.ms(1000);
```

---

## 五、Animation Worklet

### 5.1 注册动画

```javascript
// animation.js
registerAnimator('scroll-animation', class {
  constructor(options) {
    this.options = options;
  }
  
  animate(currentTime, effect) {
    const scrollPosition = currentTime / 1000;
    effect.localTime = scrollPosition * 1000;
  }
});
```

### 5.2 使用动画

```javascript
CSS.animationWorklet.addModule('animation.js').then(() => {
  const element = document.querySelector('.animated');
  const workletAnimation = new WorkletAnimation(
    'scroll-animation',
    new KeyframeEffect(
      element,
      [
        { transform: 'translateY(0)' },
        { transform: 'translateY(100px)' }
      ],
      { duration: 1000 }
    ),
    document.timeline
  );
  
  workletAnimation.play();
});
```

---

## 六、实战：自定义背景图案

### 6.1 Paint Worklet 实现

```javascript
// pattern.js
registerPaint('diagonal-lines', class {
  static get inputProperties() {
    return [
      '--line-color',
      '--line-width',
      '--line-spacing',
      '--line-angle'
    ];
  }
  
  paint(ctx, size, properties) {
    const color = properties.get('--line-color').toString();
    const width = parseInt(properties.get('--line-width').toString());
    const spacing = parseInt(properties.get('--line-spacing').toString());
    const angle = parseFloat(properties.get('--line-angle').toString());
    
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    
    const rad = (angle * Math.PI) / 180;
    const diagonal = Math.sqrt(size.width * size.width + size.height * size.height);
    
    for (let i = -diagonal; i < size.width + diagonal; i += spacing) {
      ctx.beginPath();
      ctx.moveTo(i, 0);
      ctx.lineTo(i + Math.cos(rad) * size.height, size.height);
      ctx.stroke();
    }
  }
});
```

### 6.2 CSS 使用

```css
.pattern-box {
  --line-color: #4a90e2;
  --line-width: 2;
  --line-spacing: 30;
  --line-angle: 45;
  background-image: paint(diagonal-lines);
}
```

### 6.3 页面集成

```html
<!DOCTYPE html>
<html>
<head>
  <style>
    .pattern-box {
      width: 300px;
      height: 300px;
      --line-color: #4a90e2;
      --line-width: 2;
      --line-spacing: 30;
      --line-angle: 45;
      background-image: paint(diagonal-lines);
    }
  </style>
</head>
<body>
  <div class="pattern-box"></div>
  
  <script>
    CSS.paintWorklet.addModule('pattern.js');
  </script>
</body>
</html>
```

---

## 七、浏览器支持与降级

### 7.1 特性检测

```javascript
if ('paintWorklet' in CSS) {
  CSS.paintWorklet.addModule('paint.js');
} else {
  // 降级处理
  console.log('Paint Worklet not supported');
}
```

### 7.2 Polyfill

```javascript
import 'css-paint-polyfill';
```

---

## 总结

CSS Houdini 提供了强大的渲染引擎扩展能力，通过 Paint Worklet、Typed OM 等 API，我们可以创建丰富的自定义视觉效果。虽然浏览器支持还在发展中，但已经可以在现代浏览器中使用部分功能。
