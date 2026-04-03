# CSS Flexbox 高级技巧：从基础到复杂布局

Flexbox 是 CSS 中最强大的布局工具之一。本文将带你全面掌握 Flexbox 的高级技巧。

## 一、Flexbox 基础回顾

### 1. 基本概念

```css
.container {
  display: flex; /* 或 inline-flex */
}
```

```
Flex Container (flex container)
├── Flex Item 1
├── Flex Item 2
└── Flex Item 3
```

### 2. 容器属性

```css
.flex-container {
  display: flex;
  
  /* 主轴方向 */
  flex-direction: row; /* row | row-reverse | column | column-reverse */
  
  /* 换行 */
  flex-wrap: nowrap; /* nowrap | wrap | wrap-reverse */
  
  /* 简写 */
  flex-flow: row nowrap;
  
  /* 主轴对齐 */
  justify-content: flex-start; /* flex-start | flex-end | center | space-between | space-around | space-evenly */
  
  /* 交叉轴对齐 */
  align-items: stretch; /* stretch | flex-start | flex-end | center | baseline */
  
  /* 多行交叉轴对齐 */
  align-content: stretch; /* stretch | flex-start | flex-end | center | space-between | space-around */
}
```

### 3. 项目属性

```css
.flex-item {
  /* 顺序 */
  order: 0;
  
  /* 放大比例 */
  flex-grow: 0;
  
  /* 缩小比例 */
  flex-shrink: 1;
  
  /* 基础大小 */
  flex-basis: auto;
  
  /* 简写 */
  flex: 0 1 auto;
  
  /* 单独对齐 */
  align-self: auto; /* auto | flex-start | flex-end | center | baseline | stretch */
}
```

## 二、经典布局模式

### 1. 水平居中

```css
.center-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
```

### 2. 两端对齐

```css
.between-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
```

### 3. 等分布局

```css
.equal-columns {
  display: flex;
}

.equal-columns > * {
  flex: 1;
}
```

### 4. 圣杯布局

```html
<div class="holy-grail">
  <header>Header</header>
  <div class="body">
    <nav>Nav</nav>
    <main>Main</main>
    <aside>Aside</aside>
  </div>
  <footer>Footer</footer>
</div>
```

```css
.holy-grail {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.holy-grail .body {
  display: flex;
  flex: 1;
}

.holy-grail nav {
  flex: 0 0 200px;
}

.holy-grail main {
  flex: 1;
}

.holy-grail aside {
  flex: 0 0 200px;
}
```

## 三、高级技巧

### 1. 可伸缩的输入框

```css
.search-box {
  display: flex;
}

.search-box input {
  flex: 1;
}

.search-box button {
  flex-shrink: 0;
}
```

### 2. 媒体对象

```html
<div class="media">
  <img class="media-image" src="avatar.jpg" alt="">
  <div class="media-body">
    <h3>Title</h3>
    <p>Content goes here...</p>
  </div>
</div>
```

```css
.media {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.media-image {
  flex-shrink: 0;
  width: 64px;
  height: 64px;
}

.media-body {
  flex: 1;
  min-width: 0; /* 防止溢出 */
}
```

### 3. 粘性页脚

```css
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex: 1;
}
```

### 4. 响应式卡片网格

```css
.card-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.card {
  flex: 1 1 300px;
  max-width: 400px;
}
```

### 5. 自动边距

```css
.nav {
  display: flex;
  align-items: center;
}

.nav-left {
  display: flex;
  gap: 16px;
}

.nav-right {
  margin-left: auto; /* 推到右边 */
  display: flex;
  gap: 16px;
}
```

### 6. 等间距但首尾不留空

```css
.item-list {
  display: flex;
  flex-wrap: wrap;
  margin: -10px;
}

.item-list > * {
  margin: 10px;
  flex: 1 1 200px;
}
```

## 四、复杂布局实战

### 1. 卡片布局

```html
<div class="card-container">
  <div class="card">
    <img src="image.jpg" alt="">
    <div class="card-content">
      <h3>Card Title</h3>
      <p>Some quick example text...</p>
      <button>Read More</button>
    </div>
  </div>
</div>
```

```css
.card-container {
  display: flex;
  flex-wrap: wrap;
  gap: 24px;
}

.card {
  display: flex;
  flex-direction: column;
  flex: 1 1 300px;
  max-width: 400px;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
}

.card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.card-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  padding: 16px;
}

.card-content button {
  margin-top: auto;
  align-self: flex-start;
}
```

### 2. 表单布局

```html
<form class="form">
  <div class="form-row">
    <label>First Name</label>
    <input type="text">
  </div>
  <div class="form-row">
    <label>Last Name</label>
    <input type="text">
  </div>
  <div class="form-row">
    <label>Email</label>
    <input type="email">
  </div>
  <div class="form-actions">
    <button type="button">Cancel</button>
    <button type="submit">Submit</button>
  </div>
</form>
```

```css
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 600px;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.form-row label {
  font-weight: bold;
}

.form-row input {
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
```

### 3. 仪表板布局

```html
<div class="dashboard">
  <aside class="sidebar">
    <nav>
      <a href="#">Dashboard</a>
      <a href="#">Users</a>
      <a href="#">Settings</a>
    </nav>
  </aside>
  <main class="main">
    <header class="header">
      <h1>Dashboard</h1>
      <div class="user">User</div>
    </header>
    <div class="content">
      <div class="widgets">
        <div class="widget">Widget 1</div>
        <div class="widget">Widget 2</div>
        <div class="widget">Widget 3</div>
      </div>
    </div>
  </main>
</div>
```

```css
.dashboard {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  flex: 0 0 250px;
  background: #333;
  color: white;
  padding: 16px;
}

.sidebar nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.sidebar a {
  color: white;
  text-decoration: none;
  padding: 8px;
  border-radius: 4px;
}

.sidebar a:hover {
  background: #555;
}

.main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #ddd;
}

.content {
  flex: 1;
  padding: 16px;
}

.widgets {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.widget {
  flex: 1 1 300px;
  padding: 16px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
}
```

## 五、常见问题与解决方案

### 1. 文本溢出

```css
/* ❌ 问题：文本溢出 */
.flex-item {
  white-space: nowrap;
  overflow: hidden;
}

/* ✅ 解决：添加 min-width: 0 */
.flex-item {
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

### 2. 图片变形

```css
/* ❌ 问题：图片被拉伸 */
img {
  flex: 1;
}

/* ✅ 解决：保持比例 */
img {
  align-self: flex-start;
  max-width: 100%;
  height: auto;
}
```

### 3. 元素高度不一致

```css
/* ❌ 问题：高度不一致 */
.container {
  display: flex;
}

/* ✅ 解决：stretch 对齐 */
.container {
  display: flex;
  align-items: stretch;
}
```

### 4. 换行与间距

```css
/* 使用 gap 属性 */
.container {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

/* 或使用 margin */
.container {
  display: flex;
  flex-wrap: wrap;
  margin: -10px;
}

.container > * {
  margin: 10px;
}
```

## 六、响应式 Flexbox

```css
/* 移动端单列，桌面端多列 */
.container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

@media (min-width: 768px) {
  .container {
    flex-direction: row;
    flex-wrap: wrap;
  }
  
  .container > * {
    flex: 1 1 45%;
  }
}

@media (min-width: 1024px) {
  .container > * {
    flex: 1 1 30%;
  }
}
```

## 七、调试 Flexbox

```css
/* 给容器添加边框 */
.flex-container {
  border: 2px solid red;
}

.flex-container > * {
  border: 1px solid blue;
}

/* 使用浏览器开发工具 */
/* Chrome DevTools → Elements → Styles → Flex 图标 */
```

## 八、最佳实践

1. 从简单布局开始
2. 合理使用 flex 简写
3. 注意 min-width: 0 防止溢出
4. 使用 gap 代替 margin
5. 考虑响应式设计
6. 使用浏览器工具调试
7. 保持代码简单

## 九、总结

Flexbox 高级技巧：
- 掌握容器和项目属性
- 使用经典布局模式
- 实现复杂的响应式布局
- 解决常见问题
- 调试 Flexbox 布局
- 遵循最佳实践

Flexbox 让复杂布局变得简单！
