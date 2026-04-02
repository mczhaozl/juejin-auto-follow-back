# CSS Houdini Paint API 完全指南：开启 CSS 渲染的新纪元

> 一句话摘要：深入解析 CSS Houdini Paint API，学习如何通过 JavaScript 扩展 CSS 渲染引擎，创建自定义图案、渐变和视觉效果，让你的网页设计突破传统 CSS 的限制。

## 一、引言：什么是 Houdini？

### 1.1 CSS 渲染的困境

传统 CSS 的限制：

- **无法访问渲染引擎**：CSS 属性由浏览器内置实现，无法自定义
- **性能瓶颈**：复杂的视觉效果通常需要 Canvas、WebGL 或 SVG
- **跨浏览器差异**：某些 CSS 属性在不同浏览器表现不一致

```css
/* 传统 CSS 的局限性 */
.element {
    /* 我们只能使用浏览器提供的属性 */
    background: linear-gradient(...);  /* 浏览器实现的渐变 */
    filter: blur(10px);  /* 浏览器实现的模糊 */
}
```

### 1.2 Houdini 的解决方案

CSS Houdini 是浏览器提供的一套 API，允许开发者**扩展 CSS 引擎**：

```
┌─────────────────────────────────────────────────┐
│                 CSS Engine                       │
├─────────────────────────────────────────────────┤
│  CSS Parser → Style Tree → Layout → Paint → Composite │
└─────────────────────────────────────────────────┘
                        ↑
                   Houdini API
                   (可以介入这些阶段)
```

Houdini 包含多个 API：

| API | 功能 | 状态 |
|-----|------|------|
| Paint API | 自定义绘制图案 | ✅ 已支持 |
| Layout API | 自定义布局算法 | 🔄 开发中 |
| Properties & Values API | 自定义 CSS 属性 | ✅ 已支持 |
| Animation Worklet | 自定义动画 | 🔄 开发中 |
| Parser API | 扩展 CSS 解析器 | 🔄 开发中 |

### 1.3 本文目标

1. 理解 Houdini Paint API 的核心概念
2. 掌握自定义 Paint Worklet 的开发方法
3. 学习各种实际应用场景
4. 了解浏览器兼容性和降级策略

## 二、Paint API 基础

### 2.1 工作原理

```
┌──────────────────────────────────────────────┐
│           JavaScript (Paint Worklet)         │
│                                               │
│  registerPaint('myPattern', class MyPattern { │
│      paint(ctx, size, properties) {           │
│          // 自定义绘制逻辑                    │
│      }                                        │
│  })                                           │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│                 CSS Engine                   │
│                                               │
│  .element {                                   │
│      background-image: paint(myPattern);      │
│  }                                            │
└──────────────────────────────────────────────┘
```

### 2.2 核心概念

#### Paint Worklet

Paint Worklet 是一个 JavaScript 模块，包含自定义绘制逻辑：

```javascript
// my-paint.js
registerPaint('myPattern', class {
    // 必须实现 paint 方法
    paint(ctx, size, properties) {
        // ctx: CanvasRenderingContext2D
        // size: { width, height } - 元素尺寸
        // properties: CSSProperties - CSS 变量
    }
});
```

#### 注册与使用

```javascript
// 注册 Worklet（需要在 CSS Paint API 之前加载）
CSS.paintWorklet.addModule('my-paint.js');
```

```css
/* CSS 中使用 */
.element {
    background-image: paint(myPattern);
}
```

### 2.3 基本示例

```javascript
// checkerboard.js
registerPaint('checkerboard', class {
    static get inputProperties() {
        // 监听 CSS 变量变化
        return ['--square-size', '--square-color'];
    }

    paint(ctx, size, properties) {
        // 获取 CSS 变量值
        const squareSize = parseInt(properties.get('--square-size')) || 20;
        const color = properties.get('--square-color').toString().trim() || '#000';

        // 绘制棋盘格
        ctx.fillStyle = '#eee';
        ctx.fillRect(0, 0, size.width, size.height);

        ctx.fillStyle = color;
        for (let y = 0; y < size.height; y += squareSize) {
            for (let x = 0; x < size.width; x += squareSize) {
                if ((x / squareSize + y / squareSize) % 2 === 0) {
                    ctx.fillRect(x, y, squareSize, squareSize);
                }
            }
        }
    }
});
```

```css
/* 使用 */
.checkerboard {
    --square-size: 20px;
    --square-color: #333;
    background-image: paint(checkerboard);
}
```

## 三、inputProperties 详解

### 3.1 监听 CSS 属性

通过 `inputProperties` 声明需要监听的 CSS 属性：

```javascript
registerPaint('myPaint', class {
    // 方式 1：返回属性名数组
    static get inputProperties() {
        return ['--my-color', '--my-size'];
    }

    paint(ctx, size, properties) {
        // 获取 --my-color
        const color = properties.get('--my-color');

        // 返回的是 CSSUnitValue 或 CSSKeywordValue
        if (color.cssText === 'mycolor') {
            // 处理关键字
        } else {
            const numericValue = color.value;  // 数值部分
            const unit = color.unit;  // 单位
        }
    }
});
```

### 3.2 类型判断

```javascript
paint(ctx, size, properties) {
    const value = properties.get('--my-value');

    if (value instanceof CSSUnitValue) {
        console.log(`数值: ${value.value}, 单位: ${value.unit}`);
    } else if (value instanceof CSSKeywordValue) {
        console.log(`关键字: ${value.value}`);
    } else if (value instanceof CSSColorValue) {
        console.log(`颜色: ${value.toString()}`);
    } else if (value instanceof CSSTransformValue) {
        console.log(`变换: ${value.toString()}`);
    }
}
```

### 3.3 inputProperties 示例

```javascript
registerPaint('gradient-circles', class {
    static get inputProperties() {
        return [
            '--circle-count',
            '--circle-color',
            '--circle-spacing'
        ];
    }

    paint(ctx, size, properties) {
        const count = parseInt(properties.get('--circle-count').toString()) || 5;
        const color = properties.get('--circle-color').toString() || '#007bff';
        const spacing = parseFloat(properties.get('--circle-spacing').toString()) || 10;

        const radius = (Math.min(size.width, size.height) - spacing * 2) / 2;
        const centerX = size.width / 2;
        const centerY = size.height / 2;

        ctx.fillStyle = color;
        for (let i = 0; i < count; i++) {
            const angle = (i / count) * Math.PI * 2;
            const x = centerX + Math.cos(angle) * radius;
            const y = centerY + Math.sin(angle) * radius;

            ctx.beginPath();
            ctx.arc(x, y, radius / count, 0, Math.PI * 2);
            ctx.fill();
        }
    }
});
```

```css
.gradient-circles {
    --circle-count: 8;
    --circle-color: #ff6b6b;
    --circle-spacing: 20;
    background-image: paint(gradient-circles);
}
```

## 四、实际应用场景

### 4.1 自定义图案背景

#### 案例 1：波浪纹

```javascript
// waves.js
registerPaint('waves', class {
    static get inputProperties() {
        return ['--wave-color', '--wave-height', '--wave-count'];
    }

    paint(ctx, size, properties) {
        const color = properties.get('--wave-color').toString() || '#007bff';
        const waveHeight = parseFloat(properties.get('--wave-height').toString()) || 20;
        const count = parseInt(properties.get('--wave-count').toString()) || 3;

        ctx.fillStyle = color;
        ctx.globalAlpha = 0.3;

        for (let layer = 0; layer < count; layer++) {
            ctx.beginPath();
            ctx.moveTo(0, size.height);

            const yOffset = layer * waveHeight;
            const amplitude = waveHeight * (1 - layer / count);
            const frequency = 0.02 * (layer + 1);

            for (let x = 0; x <= size.width; x++) {
                const y = size.height / 2 +
                    Math.sin(x * frequency + layer * Math.PI) * amplitude -
                    yOffset;
                ctx.lineTo(x, y);
            }

            ctx.lineTo(size.width, size.height);
            ctx.closePath();
            ctx.fill();
        }
    }
});
```

```css
.waves-bg {
    width: 100%;
    height: 200px;
    --wave-color: #3498db;
    --wave-height: 30;
    --wave-count: 4;
    background-image: paint(waves);
}
```

#### 案例 2：网格点阵

```javascript
// dot-grid.js
registerPaint('dotGrid', class {
    static get inputProperties() {
        return ['--dot-size', '--dot-color', '--dot-spacing'];
    }

    paint(ctx, size, properties) {
        const dotSize = parseFloat(properties.get('--dot-size').toString()) || 4;
        const color = properties.get('--dot-color').toString() || '#ccc';
        const spacing = parseFloat(properties.get('--dot-spacing').toString()) || 20;

        ctx.fillStyle = color;

        const cols = Math.ceil(size.width / spacing);
        const rows = Math.ceil(size.height / spacing);

        for (let row = 0; row <= rows; row++) {
            for (let col = 0; col <= cols; col++) {
                const x = col * spacing;
                const y = row * spacing;

                ctx.beginPath();
                ctx.arc(x, y, dotSize / 2, 0, Math.PI * 2);
                ctx.fill();
            }
        }
    }
});
```

#### 案例 3：条纹渐变

```javascript
// stripes.js
registerPaint('stripes', class {
    static get inputProperties() {
        return ['--stripe-color-1', '--stripe-color-2', '--stripe-width', '--stripe-angle'];
    }

    paint(ctx, size, properties) {
        const color1 = properties.get('--stripe-color-1').toString() || '#fff';
        const color2 = properties.get('--stripe-color-2').toString() || '#eee';
        const stripeWidth = parseFloat(properties.get('--stripe-width').toString()) || 10;
        const angle = parseFloat(properties.get('--stripe-angle').toString()) || 45;

        const radians = (angle * Math.PI) / 180;
        const diagonal = Math.sqrt(size.width ** 2 + size.height ** 2);

        ctx.save();
        ctx.translate(size.width / 2, size.height / 2);
        ctx.rotate(radians);

        // 绘制条纹
        const totalWidth = diagonal * 2;
        for (let x = -totalWidth; x < totalWidth; x += stripeWidth * 2) {
            ctx.fillStyle = color1;
            ctx.fillRect(x, -totalWidth, stripeWidth, totalWidth * 2);
            ctx.fillStyle = color2;
            ctx.fillRect(x + stripeWidth, -totalWidth, stripeWidth, totalWidth * 2);
        }

        ctx.restore();
    }
});
```

### 4.2 动态边框效果

```javascript
// gradient-border.js
registerPaint('gradientBorder', class {
    static get inputProperties() {
        return [
            '--border-width',
            '--gradient-start',
            '--gradient-end',
            '--border-radius'
        ];
    }

    paint(ctx, size, properties) {
        const borderWidth = parseFloat(properties.get('--border-width').toString()) || 4;
        const startColor = properties.get('--gradient-start').toString() || '#ff6b6b';
        const endColor = properties.get('--gradient-end').toString() || '#4ecdc4';
        const radius = parseFloat(properties.get('--border-radius').toString()) || 8;

        const gradient = ctx.createLinearGradient(0, 0, size.width, size.height);
        gradient.addColorStop(0, startColor);
        gradient.addColorStop(1, endColor);

        ctx.strokeStyle = gradient;
        ctx.lineWidth = borderWidth;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';

        // 绘制圆角矩形边框
        ctx.beginPath();
        ctx.roundRect(
            borderWidth / 2,
            borderWidth / 2,
            size.width - borderWidth,
            size.height - borderWidth,
            radius
        );
        ctx.stroke();
    }
});
```

```css
.gradient-border-box {
    --border-width: 4;
    --gradient-start: #ff6b6b;
    --gradient-end: #4ecdc4;
    --border-radius: 12;
    padding: 20px;
    background: #1a1a1a;
    background-image: paint(gradientBorder);
}
```

### 4.3 进度指示器

```javascript
// progress-ring.js
registerPaint('progressRing', class {
    static get inputProperties() {
        return [
            '--progress',
            '--ring-color',
            '--ring-bg',
            '--ring-width',
            '--ring-size'
        ];
    }

    paint(ctx, size, properties) {
        const progress = parseFloat(properties.get('--progress').toString()) || 0;
        const color = properties.get('--ring-color').toString() || '#007bff';
        const bgColor = properties.get('--ring-bg').toString() || '#e0e0e0';
        const lineWidth = parseFloat(properties.get('--ring-width').toString()) || 8;

        const radius = (Math.min(size.width, size.height) - lineWidth) / 2;
        const centerX = size.width / 2;
        const centerY = size.height / 2;

        // 背景圆环
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.strokeStyle = bgColor;
        ctx.lineWidth = lineWidth;
        ctx.stroke();

        // 进度圆弧
        const startAngle = -Math.PI / 2;
        const endAngle = startAngle + (progress / 100) * Math.PI * 2;

        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.strokeStyle = color;
        ctx.stroke();
    }
});
```

```html
<div class="progress-ring" style="--progress: 75; --ring-color: #28a745;">
    <span>75%</span>
</div>
```

```css
.progress-ring {
    width: 120px;
    height: 120px;
    --ring-width: 10;
    --ring-bg: #e9ecef;
    background-image: paint(progressRing);
    display: flex;
    align-items: center;
    justify-content: center;
}
```

### 4.4 文字效果

```javascript
// textOutline.js
registerPaint('textOutline', class {
    static get contextOptions() {
        return { textureRendering: 'crisp-edges' };
    }

    static get inputProperties() {
        return ['--outline-color', '--outline-width', '--text'];
    }

    paint(ctx, size, properties) {
        const outlineColor = properties.get('--outline-color').toString() || '#000';
        const outlineWidth = parseFloat(properties.get('--outline-width').toString()) || 2;
        const text = properties.get('--text').toString() || 'TEXT';

        ctx.font = 'bold 48px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';

        const x = size.width / 2;
        const y = size.height / 2;

        // 绘制描边
        ctx.strokeStyle = outlineColor;
        ctx.lineWidth = outlineWidth;
        ctx.lineJoin = 'round';
        ctx.miterLimit = 2;

        ctx.strokeText(text, x, y);
        ctx.fillStyle = '#fff';
        ctx.fillText(text, x, y);
    }
});
```

### 4.5 动态图案

```javascript
// animated-dots.js
registerPaint('animatedDots', class {
    static get inputProperties() {
        return ['--dot-color', '--dot-size', '--animation-phase'];
    }

    paint(ctx, size, properties) {
        const color = properties.get('--dot-color').toString() || '#007bff';
        const dotSize = parseFloat(properties.get('--dot-size').toString()) || 8;
        const phase = parseFloat(properties.get('--animation-phase').toString()) || 0;

        const spacing = dotSize * 3;
        const cols = Math.ceil(size.width / spacing);
        const rows = Math.ceil(size.height / spacing);

        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const x = col * spacing + spacing / 2;
                const y = row * spacing + spacing / 2;

                // 基于位置和时间的动画
                const offset = Math.sin((col + row) * 0.5 + phase) * (dotSize / 2);
                const currentSize = dotSize + offset;

                ctx.beginPath();
                ctx.arc(x, y, currentSize / 2, 0, Math.PI * 2);
                ctx.fillStyle = color;
                ctx.fill();
            }
        }
    }
});
```

```css
@keyframes animateDots {
    from { --animation-phase: 0; }
    to { --animation-phase: 6.28; }
}

.animated-dots {
    --dot-color: #6c5ce7;
    --dot-size: 6;
    animation: animateDots 3s linear infinite;
    background-image: paint(animatedDots);
}
```

## 五、高级技巧

### 5.1 使用 Canvas 2D API

```javascript
registerPaint('complexPattern', class {
    paint(ctx, size, properties) {
        // 创建渐变
        const gradient = ctx.createRadialGradient(
            size.width / 2, size.height / 2, 0,
            size.width / 2, size.height / 2, size.width / 2
        );
        gradient.addColorStop(0, '#ff6b6b');
        gradient.addColorStop(1, '#4ecdc4');

        // 绘制形状
        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.moveTo(size.width / 2, 0);
        ctx.lineTo(size.width, size.height / 2);
        ctx.lineTo(size.width / 2, size.height);
        ctx.lineTo(0, size.height / 2);
        ctx.closePath();
        ctx.fill();

        // 添加阴影
        ctx.shadowColor = 'rgba(0, 0, 0, 0.3)';
        ctx.shadowBlur = 20;
        ctx.shadowOffsetX = 5;
        ctx.shadowOffsetY = 5;
    }
});
```

### 5.2 组合多个 Paint Worklet

```css
.combined-effects {
    /* 先绘制底层图案 */
    background-image:
        /* 然后叠加渐变（使用 CSS 叠加） */
        linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)),
        /* Paint API 图案 */
        paint(gridPattern);
    background-blend-mode: overlay;
}
```

### 5.3 处理高 DPI 屏幕

```javascript
registerPaint('highDpiPattern', class {
    paint(ctx, size, properties) {
        // ctx 已经处理了 devicePixelRatio
        // 但我们可以用它来优化
        const dpr = window.devicePixelRatio || 1;

        // 绘制时使用实际像素
        ctx.save();
        ctx.scale(dpr, dpr);

        // 绘制内容
        ctx.fillStyle = '#007bff';
        ctx.fillRect(0, 0, size.width / dpr, size.height / dpr);

        ctx.restore();
    }
});
```

### 5.4 响应式 Paint Worklet

```javascript
registerPaint('responsivePattern', class {
    static get inputProperties() {
        return ['--base-size'];
    }

    paint(ctx, size, properties) {
        const baseSize = parseFloat(properties.get('--base-size').toString()) || 20;

        // 根据元素大小调整图案
        const scale = Math.min(size.width, size.height) / 300;
        const actualSize = baseSize * Math.max(0.5, scale);

        ctx.fillStyle = '#3498db';
        ctx.fillRect(0, 0, actualSize, actualSize);
    }
});
```

## 六、性能优化

### 6.1 缓存策略

```javascript
registerPaint('cachedPattern', class {
    paint(ctx, size, properties) {
        // 创建离屏 canvas 缓存
        const cacheKey = `pattern-${size.width}x${size.height}`;

        // 检查是否有缓存（需要自己实现缓存机制）
        if (this.cache && this.cache.key === cacheKey) {
            ctx.drawImage(this.cache.canvas, 0, 0);
            return;
        }

        // ... 执行绘制 ...

        // 保存到缓存
        this.cache = {
            key: cacheKey,
            canvas: ctx.canvas
        };
    }
});
```

### 6.2 避免不必要的重绘

```javascript
registerPaint('optimizedPattern', class {
    paint(ctx, size, properties) {
        // 比较尺寸是否变化
        if (this.lastSize &&
            this.lastSize.width === size.width &&
            this.lastSize.height === size.height) {
            // 尺寸没变，可能不需要重绘
            // 但 Houdini 每次都会调用 paint，这是必要的
        }

        this.lastSize = { width: size.width, height: size.height };

        // 执行绘制
    }
});
```

### 6.3 简化绘制逻辑

```javascript
// ❌ 低效：复杂路径
registerPaint('inefficient', class {
    paint(ctx, size) {
        for (let i = 0; i < 1000; i++) {
            ctx.beginPath();
            ctx.arc(
                Math.random() * size.width,
                Math.random() * size.height,
                5, 0, Math.PI * 2
            );
            ctx.fill();
        }
    }
});

// ✅ 高效：使用 fillRect 批量绘制
registerPaint('efficient', class {
    paint(ctx, size) {
        ctx.fillStyle = '#007bff';
        for (let i = 0; i < 1000; i++) {
            ctx.fillRect(
                Math.random() * size.width,
                Math.random() * size.height,
                5, 5
            );
        }
    }
});
```

## 七、浏览器兼容性与降级

### 7.1 检测支持

```javascript
if ('paintWorklet' in CSS) {
    CSS.paintWorklet.addModule('my-paint.js');
} else {
    // 使用 fallback 背景
    document.documentElement.classList.add('no-houdini');
}
```

### 7.2 CSS @supports

```css
/* 有 Houdini 支持时 */
.my-element {
    background-image: paint(myPattern);
}

/* 降级方案 */
@supports (background-image: paint(myPattern)) {
    .my-element {
        background-image: paint(myPattern);
    }
}

.my-element {
    /* 默认使用传统 CSS */
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
}
```

### 7.3 完整降级策略

```javascript
// index.js
async function loadPaintWorklet() {
    if ('paintWorklet' in CSS) {
        try {
            await CSS.paintWorklet.addModule('paint.js');
            document.body.classList.add('houdini-supported');
        } catch (e) {
            console.warn('Paint Worklet 加载失败:', e);
            setupFallback();
        }
    } else {
        console.info('浏览器不支持 Paint API');
        setupFallback();
    }
}

function setupFallback() {
    // 设置降级样式
    document.body.classList.add('houdini-unsupported');

    // 动态添加降级 CSS
    const style = document.createElement('style');
    style.textContent = `
        .my-element {
            background:
                repeating-linear-gradient(
                    45deg,
                    #667eea,
                    #667eea 10px,
                    #764ba2 10px,
                    #764ba2 20px
                ) !important;
        }
    `;
    document.head.appendChild(style);
}

loadPaintWorklet();
```

## 八、开发工具与调试

### 8.1 Chrome DevTools

在 DevTools 中调试 Paint Worklet：

1. 打开 DevTools → Sources
2. 找到 `paintworklet/` 目录
3. 设置断点
4. 触发重绘（修改 CSS 或调整窗口大小）

### 8.2 热重载

```javascript
// 开发时使用 HMR
if (module.hot) {
    module.hot.accept('./my-paint.js', async () => {
        // 重新加载模块
        await CSS.paintWorklet.addModule('./my-paint.js' + '?t=' + Date.now());
        // 触发重绘
        document.querySelectorAll('[style*="paint("]').forEach(el => {
            el.style.backgroundImage = el.style.backgroundImage;
        });
    });
}
```

## 九、完整项目示例

### 9.1 项目结构

```
project/
├── index.html
├── styles.css
└── scripts/
    ├── main.js
    └── paint/
        ├── checkerboard.js
        ├── waves.js
        ├── grid.js
        └── progress.js
```

### 9.2 HTML

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSS Houdini Paint API 示例</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <header>
        <h1>CSS Houdini Paint API 示例</h1>
    </header>

    <main>
        <section class="demo-section">
            <h2>棋盘格背景</h2>
            <div class="checkerboard-demo"></div>
        </section>

        <section class="demo-section">
            <h2>波浪背景</h2>
            <div class="waves-demo"></div>
        </section>

        <section class="demo-section">
            <h2>网格点阵</h2>
            <div class="grid-demo"></div>
        </section>

        <section class="demo-section">
            <h2>进度环</h2>
            <div class="progress-demo" style="--progress: 65;"></div>
        </section>
    </main>

    <script type="module" src="scripts/main.js"></script>
</body>
</html>
```

### 9.3 JavaScript

```javascript
// scripts/main.js

async function registerPaintModules() {
    if (!('paintWorklet' in CSS)) {
        console.warn('浏览器不支持 Paint API');
        return;
    }

    const paintModules = [
        './paint/checkerboard.js',
        './paint/waves.js',
        './paint/grid.js',
        './paint/progress.js'
    ];

    try {
        for (const module of paintModules) {
            await CSS.paintWorklet.addModule(module);
        }
        console.log('所有 Paint Worklet 模块注册成功');
    } catch (error) {
        console.error('Paint Worklet 模块注册失败:', error);
    }
}

document.addEventListener('DOMContentLoaded', registerPaintModules);
```

## 十、总结与展望

### 10.1 核心要点

1. **CSS Houdini Paint API 允许开发者自定义 CSS 渲染**
2. **通过 registerPaint 注册自定义绘制逻辑**
3. **inputProperties 允许 CSS 变量控制绘制行为**
4. **需要考虑浏览器兼容性，提供降级方案**

### 10.2 浏览器支持

| 浏览器 | 支持情况 |
|--------|----------|
| Chrome | ✅ 65+ |
| Edge | ✅ 79+ |
| Safari | 🔄 技术预览版 |
| Firefox | 🔄 开发中 |

### 10.3 未来展望

- Layout API 的成熟将带来更强大的自定义布局
- Animation Worklet 将实现更流畅的自定义动画
- 更多的 CSS 属性将支持 Houdini 扩展

### 10.4 学习资源

- [CSS Houdini Draft Specification](https://drafts.css-houdini.org/)
- [Chrome Houdini Samples](https://googlechromelabs.github.io/houdini-samples/)
- [Is Houdini Ready Yet?](https://ishoudinireadyyet.com/)

> 如果对你有帮助，欢迎点赞、收藏！有任何问题欢迎在评论区讨论。
