# 你不会使用 CSS 函数 clamp()？那你太 low 了😀

> 一个函数搞定响应式字体、间距、宽度，告别繁琐的媒体查询，让你的 CSS 优雅 10 倍。

---

## 一、clamp() 是什么

`clamp()` 是 CSS 的一个数学函数，用于在一个范围内限制值。语法：

```css
clamp(最小值, 首选值, 最大值)
```

浏览器会：

1. 计算首选值
2. 如果首选值 < 最小值，返回最小值
3. 如果首选值 > 最大值，返回最大值
4. 否则返回首选值

简单来说：**在最小值和最大值之间，取一个动态的值**。

## 二、为什么要用 clamp()

### 2.1 传统方案的痛点

响应式字体大小，传统做法：

```css
.title {
  font-size: 16px;
}

@media (min-width: 768px) {
  .title {
    font-size: 20px;
  }
}

@media (min-width: 1024px) {
  .title {
    font-size: 24px;
  }
}

@media (min-width: 1440px) {
  .title {
    font-size: 28px;
  }
}
```

问题：

- 代码冗长，难维护
- 断点之间是跳跃的，不够平滑
- 需要写多个媒体查询

### 2.2 用 clamp() 的方案

```css
.title {
  font-size: clamp(16px, 4vw, 28px);
}
```

一行搞定！

- 最小 16px（小屏幕）
- 最大 28px（大屏幕）
- 中间根据视口宽度（4vw）动态变化

## 三、基础用法

### 3.1 响应式字体

```css
h1 {
  font-size: clamp(1.5rem, 5vw, 3rem);
}

p {
  font-size: clamp(1rem, 2.5vw, 1.25rem);
}
```

效果：

- 小屏幕（320px）：h1 = 24px，p = 16px
- 中屏幕（768px）：h1 = 38.4px，p = 19.2px
- 大屏幕（1920px）：h1 = 48px（最大值），p = 20px

### 3.2 响应式间距

```css
.container {
  padding: clamp(1rem, 5vw, 3rem);
  gap: clamp(0.5rem, 2vw, 2rem);
}
```

### 3.3 响应式宽度

```css
.card {
  width: clamp(300px, 50vw, 600px);
}
```

卡片宽度：

- 最小 300px（不会太窄）
- 最大 600px（不会太宽）
- 中间占视口宽度的 50%

## 四、进阶技巧

### 4.1 结合 calc() 使用

```css
.title {
  font-size: clamp(1rem, 1rem + 2vw, 3rem);
}
```

解释：

- 基础大小 1rem
- 加上 2vw 的动态增量
- 最大不超过 3rem

### 4.2 用 rem 和 vw 混合

```css
.text {
  font-size: clamp(1rem, 0.875rem + 0.5vw, 1.5rem);
}
```

好处：

- 基础大小用 rem（尊重用户字体设置）
- 动态部分用 vw（响应视口）
- 最大值用 rem（保持可读性）

### 4.3 负值和小数

```css
.element {
  margin-top: clamp(-2rem, -5vw, 0);
  opacity: clamp(0.5, 0.5 + 0.1vw, 1);
}
```

### 4.4 多个属性共用一个变量

```css
:root {
  --fluid-spacing: clamp(1rem, 3vw, 3rem);
}

.container {
  padding: var(--fluid-spacing);
  gap: var(--fluid-spacing);
}
```

## 五、实战案例

### 案例 1：流式排版

```css
:root {
  --font-size-sm: clamp(0.875rem, 0.8rem + 0.3vw, 1rem);
  --font-size-base: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
  --font-size-lg: clamp(1.25rem, 1rem + 1vw, 2rem);
  --font-size-xl: clamp(1.5rem, 1.2rem + 1.5vw, 3rem);
}

body {
  font-size: var(--font-size-base);
}

h1 {
  font-size: var(--font-size-xl);
}

h2 {
  font-size: var(--font-size-lg);
}

small {
  font-size: var(--font-size-sm);
}
```

### 案例 2：响应式卡片网格

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(clamp(250px, 30vw, 400px), 1fr));
  gap: clamp(1rem, 3vw, 2rem);
}
```

效果：

- 卡片最小 250px，最大 400px
- 间距最小 1rem，最大 2rem
- 自动换行，响应式布局

### 案例 3：流式容器

```css
.container {
  width: clamp(320px, 90vw, 1200px);
  margin: 0 auto;
  padding: clamp(1rem, 5vw, 3rem);
}
```

### 案例 4：动态行高

```css
p {
  font-size: clamp(1rem, 0.9rem + 0.5vw, 1.25rem);
  line-height: clamp(1.5, 1.4 + 0.2vw, 1.8);
}
```

## 六、计算公式

### 6.1 如何确定首选值

公式：

```
首选值 = 基础值 + (增量 × vw)
```

示例：想要字体在 375px 屏幕上是 16px，在 1920px 屏幕上是 24px。

```
增量 = (24 - 16) / (1920 - 375) × 100 = 0.518vw
基础值 = 16 - (375 × 0.518 / 100) = 14.06px

首选值 = 14.06px + 0.518vw
```

CSS：

```css
font-size: clamp(16px, 14.06px + 0.518vw, 24px);
```

### 6.2 在线计算器

推荐工具：

- https://clamp.font-size.app/
- https://min-max-calculator.9elements.com/

输入最小值、最大值、视口范围，自动生成 `clamp()` 代码。

## 七、浏览器兼容性

| 浏览器 | 版本 |
|--------|------|
| Chrome | 79+ |
| Firefox | 75+ |
| Safari | 13.1+ |
| Edge | 79+ |

兼容性很好，覆盖 95%+ 的用户。

### 7.1 降级方案

```css
.title {
  font-size: 20px; /* 降级 */
  font-size: clamp(16px, 4vw, 28px);
}
```

不支持 `clamp()` 的浏览器会用 20px。

## 八、常见误区

### 误区 1：滥用 vw

```css
/* ❌ 差：在小屏幕上太小 */
font-size: clamp(10px, 5vw, 30px);

/* ✅ 好：保证最小可读性 */
font-size: clamp(16px, 5vw, 30px);
```

### 误区 2：忽略可访问性

```css
/* ❌ 差：用户放大字体时不生效 */
font-size: clamp(16px, 4vw, 28px);

/* ✅ 好：用 rem，尊重用户设置 */
font-size: clamp(1rem, 1rem + 1vw, 1.75rem);
```

### 误区 3：过度复杂

```css
/* ❌ 差：难以理解和维护 */
font-size: clamp(
  calc(1rem + 0.5vw - 2px),
  calc(1rem + 1vw + 0.2vh),
  calc(2rem - 0.3vw + 5px)
);

/* ✅ 好：简洁明了 */
font-size: clamp(1rem, 1rem + 1vw, 2rem);
```

## 九、与其他方案对比

### 9.1 vs 媒体查询

| 方案 | 优点 | 缺点 |
|------|------|------|
| 媒体查询 | 精确控制断点 | 代码冗长，跳跃式变化 |
| clamp() | 代码简洁，平滑过渡 | 不适合复杂布局 |

结论：简单响应式用 `clamp()`，复杂布局用媒体查询。

### 9.2 vs min() / max()

```css
/* min()：取最小值 */
width: min(500px, 100%);  /* 最大 500px */

/* max()：取最大值 */
width: max(300px, 50%);   /* 最小 300px */

/* clamp()：限制范围 */
width: clamp(300px, 50%, 500px);  /* 300px ~ 500px */
```

`clamp()` 是 `min()` 和 `max()` 的结合。

## 十、实用代码片段

### 片段 1：全局流式排版

```css
:root {
  --step--2: clamp(0.69rem, 0.66rem + 0.18vw, 0.84rem);
  --step--1: clamp(0.83rem, 0.78rem + 0.29vw, 1.05rem);
  --step-0: clamp(1rem, 0.91rem + 0.43vw, 1.31rem);
  --step-1: clamp(1.2rem, 1.07rem + 0.63vw, 1.64rem);
  --step-2: clamp(1.44rem, 1.26rem + 0.89vw, 2.05rem);
  --step-3: clamp(1.73rem, 1.48rem + 1.24vw, 2.56rem);
  --step-4: clamp(2.07rem, 1.73rem + 1.70vw, 3.20rem);
  --step-5: clamp(2.49rem, 2.03rem + 2.31vw, 4.00rem);
}
```

### 片段 2：流式间距

```css
:root {
  --space-3xs: clamp(0.25rem, 0.23rem + 0.11vw, 0.31rem);
  --space-2xs: clamp(0.5rem, 0.46rem + 0.21vw, 0.63rem);
  --space-xs: clamp(0.75rem, 0.68rem + 0.32vw, 0.94rem);
  --space-s: clamp(1rem, 0.91rem + 0.43vw, 1.25rem);
  --space-m: clamp(1.5rem, 1.36rem + 0.64vw, 1.88rem);
  --space-l: clamp(2rem, 1.82rem + 0.85vw, 2.50rem);
  --space-xl: clamp(3rem, 2.73rem + 1.28vw, 3.75rem);
  --space-2xl: clamp(4rem, 3.64rem + 1.70vw, 5.00rem);
  --space-3xl: clamp(6rem, 5.45rem + 2.55vw, 7.50rem);
}
```

### 片段 3：响应式容器

```css
.container {
  width: clamp(320px, 90vw, 1200px);
  margin-inline: auto;
  padding-inline: clamp(1rem, 5vw, 3rem);
}
```

## 十一、调试技巧

### 技巧 1：用 CSS 变量方便调试

```css
:root {
  --min: 1rem;
  --val: 1rem + 1vw;
  --max: 2rem;
}

.title {
  font-size: clamp(var(--min), var(--val), var(--max));
}
```

### 技巧 2：用浏览器开发者工具

Chrome DevTools 会显示 `clamp()` 的计算结果：

```
font-size: clamp(16px, 4vw, 28px)
计算值: 24px
```

### 技巧 3：用注释标注

```css
.title {
  /* 小屏 16px，大屏 28px，中间平滑过渡 */
  font-size: clamp(16px, 1rem + 1vw, 28px);
}
```

## 十二、最佳实践

1. **优先用 rem**：尊重用户字体设置
2. **保证最小可读性**：字体最小 16px，间距最小 0.5rem
3. **避免过度复杂**：首选值尽量简单
4. **用 CSS 变量**：方便维护和调试
5. **测试多种屏幕**：320px、768px、1920px 都要看
6. **提供降级方案**：不支持的浏览器用固定值

## 总结

`clamp()` 的核心价值：

- 一行代码搞定响应式
- 平滑过渡，不跳跃
- 代码简洁，易维护

常用场景：

- 响应式字体：`clamp(1rem, 1rem + 1vw, 2rem)`
- 响应式间距：`clamp(1rem, 3vw, 3rem)`
- 响应式宽度：`clamp(300px, 50vw, 600px)`

记住公式：

```css
clamp(最小值, 基础值 + 动态值, 最大值)
```

不会用 `clamp()`？那你真的太 low 了😀

现在学还不晚，赶紧用起来！
