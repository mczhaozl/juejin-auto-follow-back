# 工作多年，我学会了写防御性 CSS

> 通过防御性 CSS 技巧，提前规避内容溢出、布局错位等常见问题，让页面更健壮。

---

## 一、什么是防御性 CSS

防御性 CSS 是指在编写样式时，提前考虑各种边界情况，避免因内容变化、用户操作或环境差异导致的布局问题。

常见场景：

- 文本过长导致溢出
- 图片加载失败或尺寸异常
- Flex/Grid 子元素数量不确定
- 多语言环境下文本长度差异

核心思想：**不假设内容是理想状态，而是为最坏情况做准备**。

## 二、文本溢出处理

### 1. 单行文本溢出

```css
.text-ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
```

### 2. 多行文本溢出

```css
.text-clamp {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3; /* 显示 3 行 */
  overflow: hidden;
}
```

### 3. 长单词/URL 换行

```css
.word-break {
  /* 允许在单词内换行 */
  word-break: break-word;
  /* 或者在合适位置换行 */
  overflow-wrap: break-word;
}
```

**实际案例**：用户名、评论、链接等用户输入内容，必须加换行处理。

## 三、Flexbox 防御

### 1. 防止子元素被压缩

```css
.flex-item {
  /* 防止内容被压缩到小于最小内容宽度 */
  min-width: 0;
  /* 或者明确指定最小宽度 */
  flex-shrink: 0;
}
```

**问题场景**：Flex 容器宽度不足时，子元素会被压缩，导致文本溢出。

```css
/* ❌ 问题代码 */
.card {
  display: flex;
}
.card-content {
  flex: 1;
}

/* ✅ 防御性写法 */
.card-content {
  flex: 1;
  min-width: 0; /* 允许缩小到 0，配合 overflow 处理 */
  overflow: hidden;
}
```

### 2. 间距用 gap 而非 margin

```css
/* ❌ 传统写法 */
.list > * {
  margin-right: 10px;
}
.list > *:last-child {
  margin-right: 0;
}

/* ✅ 防御性写法 */
.list {
  display: flex;
  gap: 10px; /* 自动处理最后一个元素 */
}
```

### 3. 防止内容撑开容器

```css
.container {
  display: flex;
}
.content {
  flex: 1;
  /* 防止长文本撑开 */
  min-width: 0;
  overflow: hidden;
}
```

## 四、图片防御

### 1. 图片加载失败处理

```css
img {
  /* 加载失败时显示背景色 */
  background-color: #f0f0f0;
  /* 或者显示默认图标 */
  background-image: url('data:image/svg+xml,...');
  background-size: 50%;
  background-repeat: no-repeat;
  background-position: center;
}
```

### 2. 防止图片变形

```css
img {
  /* 保持宽高比 */
  object-fit: cover;
  /* 或者 */
  object-fit: contain;
}
```

### 3. 图片容器固定比例

```css
.image-wrapper {
  position: relative;
  /* 16:9 比例 */
  padding-bottom: 56.25%;
  overflow: hidden;
}
.image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

## 五、Grid 布局防御

### 1. 自适应列数

```css
.grid {
  display: grid;
  /* 最小 200px，自动填充 */
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}
```

### 2. 防止内容溢出

```css
.grid-item {
  /* 防止内容撑开网格 */
  min-width: 0;
  overflow: hidden;
}
```

## 六、定位与层级

### 1. 固定定位元素的安全区域

```css
.fixed-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  /* 考虑刘海屏 */
  padding-top: env(safe-area-inset-top);
}
```

### 2. z-index 管理

```css
/* 定义 z-index 变量 */
:root {
  --z-dropdown: 1000;
  --z-modal: 2000;
  --z-toast: 3000;
}

.dropdown {
  z-index: var(--z-dropdown);
}
```

## 七、表单防御

### 1. 输入框宽度

```css
input, textarea {
  /* 防止超出容器 */
  max-width: 100%;
  /* 防止被压缩 */
  min-width: 0;
}
```

### 2. 按钮文本换行

```css
button {
  /* 防止文本过长 */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  /* 或者允许换行 */
  white-space: normal;
}
```

## 八、响应式防御

### 1. 容器查询代替媒体查询

```css
.card-container {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    display: flex;
  }
}
```

### 2. clamp() 实现流式字体

```css
h1 {
  /* 最小 16px，最大 32px，中间根据视口宽度计算 */
  font-size: clamp(16px, 4vw, 32px);
}
```

### 3. 最小点击区域

```css
button, a {
  /* 移动端最小点击区域 44x44px */
  min-width: 44px;
  min-height: 44px;
}
```

## 九、滚动防御

### 1. 防止滚动穿透

```css
.modal {
  /* 模态框打开时禁止背景滚动 */
  overflow: hidden;
}

/* 或者用 JS */
document.body.style.overflow = 'hidden';
```

### 2. 平滑滚动

```css
html {
  scroll-behavior: smooth;
}
```

### 3. 滚动条样式

```css
/* 防止滚动条导致布局抖动 */
html {
  overflow-y: scroll; /* 始终显示滚动条占位 */
}

/* 或者 */
.container {
  scrollbar-gutter: stable; /* 为滚动条预留空间 */
}
```

## 十、性能与兼容性

### 1. will-change 谨慎使用

```css
/* ❌ 不要滥用 */
* {
  will-change: transform;
}

/* ✅ 只在需要时使用 */
.animated-element:hover {
  will-change: transform;
}
.animated-element {
  will-change: auto; /* 动画结束后重置 */
}
```

### 2. 渐进增强

```css
.card {
  /* 基础样式 */
  display: block;
}

/* 支持 Grid 的浏览器 */
@supports (display: grid) {
  .card {
    display: grid;
  }
}
```

## 十一、实战检查清单

在写 CSS 时，问自己这些问题：

- [ ] 文本过长会怎样？（加 `text-overflow` 或 `word-break`）
- [ ] 图片加载失败会怎样？（加 `background-color` 或默认图）
- [ ] Flex/Grid 子元素数量不确定会怎样？（用 `gap`、`min-width: 0`）
- [ ] 移动端点击区域够大吗？（最小 44x44px）
- [ ] 多语言环境下文本长度差异会怎样？（用 `clamp`、`overflow`）
- [ ] 滚动条出现会导致布局抖动吗？（用 `scrollbar-gutter`）

## 总结

防御性 CSS 的核心是**不信任内容**：

- 文本可能很长 → 加溢出处理
- 图片可能失败 → 加默认样式
- 容器可能很窄 → 加最小宽度和换行
- 用户可能用小屏 → 加响应式和最小点击区域

养成防御性思维，能大幅减少线上样式问题。建议在组件库或基础样式中统一处理这些情况，避免每次都重复写。
