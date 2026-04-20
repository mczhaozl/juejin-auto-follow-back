# CSS Grid 完全指南：从基础到高级复杂布局

> 系统学习 CSS Grid 布局，从入门到精通，掌握各种布局技巧，轻松实现复杂页面布局。

## 一、CSS Grid 概述

CSS Grid 是 CSS 中最强大的二维布局系统，能够同时处理行和列，让复杂布局变得简单。

### 1.1 为什么选择 CSS Grid

- **二维布局**：同时控制行和列，真正的网格布局
- **灵活的轨道尺寸**：使用 fr、百分比、像素等多种单位
- **自动放置**：元素可以自动填充网格位置
- **响应式设计**：轻松创建响应式布局
- **与 Flexbox 互补**：Grid 和 Flexbox 各有优势，可配合使用

### 1.2 Grid 与 Flexbox 的对比

| 特性 | Grid | Flexbox |
|------|------|---------|
| 维度 | 二维（行+列） | 一维（行或列） |
| 用途 | 整体页面布局 | 组件内部布局 |
| 内容优先 | 布局优先 | 内容优先 |

---

## 二、Grid 基础概念

### 2.1 基本术语

```
┌─────────────────────────────────┐
│   Grid Container（网格容器）    │
│  ┌─────┬─────┬─────┬─────┐  │
│  │  A  │  B  │  C  │  D  │  │ ← Grid Track（行）
│  ├─────┼─────┼─────┼─────┤  │
│  │  E  │  F  │  G  │  H  │  │
│  ├─────┼─────┼─────┼─────┤  │
│  └─────┴─────┴─────┴─────┘  │
│     ↑                       │
│  Grid Track（列）          │
└─────────────────────────────────┘
```

- **Grid Container**：应用 `display: grid` 的元素
- **Grid Item**：容器的直接子元素
- **Grid Line**：划分网格的线
- **Grid Track**：两条相邻网格线之间的空间（行或列）
- **Grid Cell**：两条相邻行和列交叉形成的单元格
- **Grid Area**：一个或多个单元格组成的区域

### 2.2 创建第一个 Grid 布局

```html
<div class="grid-container">
  <div class="item">1</div>
  <div class="item">2</div>
  <div class="item">3</div>
  <div class="item">4</div>
  <div class="item">5</div>
  <div class="item">6</div>
</div>
```

```css
.grid-container {
  display: grid;
  grid-template-columns: 100px 100px 100px;
  grid-template-rows: 100px 100px;
  gap: 10px;
}

.item {
  background: #4CAF50;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}
```

---

## 三、Grid 容器属性

### 3.1 grid-template-columns 与 grid-template-rows

定义网格的列和行：

```css
.grid-container {
  /* 像素 */
  grid-template-columns: 100px 100px 100px;
  
  /* 百分比 */
  grid-template-columns: 33.33% 33.33% 33.33%;
  
  /* fr 单位（fraction，比例） */
  grid-template-columns: 1fr 1fr 1fr;
  
  /* 混合单位 */
  grid-template-columns: 200px 1fr 2fr;
  
  /* repeat() 函数 */
  grid-template-columns: repeat(3, 1fr);
  grid-template-columns: repeat(3, 100px 200px);
  
  /* auto-fill 自动填充 */
  grid-template-columns: repeat(auto-fill, 100px);
  
  /* auto-fit 自适应 */
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
}
```

### 3.2 gap（间距）

```css
.grid-container {
  /* 旧写法 */
  grid-gap: 10px;
  grid-column-gap: 10px;
  grid-row-gap: 10px;
  
  /* 新写法（推荐） */
  gap: 10px;
  column-gap: 10px;
  row-gap: 10px;
  
  /* 分别设置行间距和列间距 */
  gap: 10px 20px; /* row column */
}
```

### 3.3 grid-template-areas 命名区域

```css
.grid-container {
  grid-template-areas:
    "header header header"
    "sidebar content content"
    "footer footer footer";
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.content { grid-area: content; }
.footer { grid-area: footer; }
```

### 3.4 justify-items 与 align-items

对齐网格项在单元格内的对齐方式：

```css
.grid-container {
  /* 水平对齐 */
  justify-items: start | end | center | stretch;
  
  /* 垂直对齐 */
  align-items: start | end | center | stretch;
  
  /* 简写 */
  place-items: center center;
}
```

### 3.5 justify-content 与 align-content

对齐整个网格内容：

```css
.grid-container {
  /* 水平对齐 */
  justify-content: start | end | center | stretch | space-around | space-between | space-evenly;
  
  /* 垂直对齐 */
  align-content: start | end | center | stretch | space-around | space-between | space-evenly;
  
  /* 简写 */
  place-content: center center;
}
```

### 3.6 grid-auto-columns 与 grid-auto-rows

定义自动创建的轨道大小：

```css
.grid-container {
  grid-auto-rows: 100px;
  grid-auto-columns: 100px;
}
```

### 3.7 grid-auto-flow 控制自动放置

```css
.grid-container {
  /* 先行后列 */
  grid-auto-flow: row;
  
  /* 先列后行 */
  grid-auto-flow: column;
  
  /* 密集填充 */
  grid-auto-flow: dense;
}
```

---

## 四、Grid 项目属性

### 4.1 grid-column 与 grid-row 定位项目

```css
.item {
  /* 简写 */
  grid-column: 1 / 3; /* 从第 1 列线到第 3 列线 */
  grid-row: 1 / 2;     /* 从第 1 行线到第 2 行线 */
  
  /* 完整写法 */
  grid-column-start: 1;
  grid-column-end: 3;
  grid-row-start: 1;
  grid-row-end: 2;
  
  /* 使用 span */
  grid-column: 1 / span 2; /* 跨越 2 列 */
  grid-row: span 1;        /* 跨越 1 行 */
  
  /* 只指定一端，另一端自动 */
  grid-column: 2; /* 从第 2 列开始，跨越 1 列 */
}
```

### 4.2 grid-area 使用命名区域

```css
.item {
  grid-area: header; /* 使用命名区域 */
  
  /* 或者用线位置 */
  grid-area: 1 / 1 / 2 / 4; /* row-start / column-start / row-end / column-end */
}
```

### 4.3 justify-self 与 align-self

单个项目在单元格内的对齐：

```css
.item {
  /* 水平对齐 */
  justify-self: start | end | center | stretch;
  
  /* 垂直对齐 */
  align-self: start | end | center | stretch;
  
  /* 简写 */
  place-self: center center;
}
```

### 4.4 order 控制项目顺序

```css
.item:nth-child(1) { order: 3; }
.item:nth-child(2) { order: 1; }
.item:nth-child(3) { order: 2; }
```

---

## 五、实用函数与单位

### 5.1 fr 单位详解

fr（fraction）是 Grid 特有的单位，表示可用空间的比例：

```css
.grid-container {
  /* 三等分 */
  grid-template-columns: 1fr 1fr 1fr;
  
  /* 1:2 的比例 */
  grid-template-columns: 1fr 2fr;
  
  /* 固定宽度 + 比例 */
  grid-template-columns: 200px 1fr 2fr;
}
```

### 5.2 repeat() 函数

```css
.grid-container {
  /* 重复 3 次 1fr */
  grid-template-columns: repeat(3, 1fr);
  
  /* 重复模式 */
  grid-template-columns: repeat(2, 100px 200px);
  
  /* 结合 minmax() */
  grid-template-columns: repeat(3, minmax(100px, 1fr));
  
  /* auto-fill */
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  
  /* auto-fit */
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
}
```

### 5.3 minmax() 函数

```css
.grid-container {
  /* 最小 100px，最大 1fr */
  grid-template-columns: minmax(100px, 1fr) 1fr 1fr;
  
  /* 结合 repeat() */
  grid-template-columns: repeat(3, minmax(100px, 1fr));
}
```

### 5.4 min()、max()、clamp() 函数

```css
.grid-container {
  grid-template-columns: min(200px, 30%) 1fr 1fr;
  grid-template-columns: max(150px, 20%) 1fr 1fr;
  grid-template-columns: clamp(100px, 25%, 300px) 1fr 1fr;
}
```

---

## 六、响应式 Grid 布局

### 6.1 使用 auto-fit 和 minmax()

```css
.grid-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}
```

这会自动创建响应式布局，列数根据容器宽度自动调整。

### 6.2 媒体查询调整 Grid

```css
/* 默认：1 列 */
.grid-container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

/* 平板：2 列 */
@media (min-width: 768px) {
  .grid-container {
    grid-template-columns: 1fr 1fr;
  }
}

/* 桌面：3 列 */
@media (min-width: 1024px) {
  .grid-container {
    grid-template-columns: 1fr 1fr 1fr;
  }
}

/* 大屏：4 列 */
@media (min-width: 1440px) {
  .grid-container {
    grid-template-columns: 1fr 1fr 1fr 1fr;
  }
}
```

### 6.3 使用命名区域的响应式布局

```css
.grid-container {
  display: grid;
  gap: 20px;
  grid-template-areas:
    "header"
    "sidebar"
    "content"
    "footer";
}

@media (min-width: 768px) {
  .grid-container {
    grid-template-columns: 200px 1fr;
    grid-template-areas:
      "header header"
      "sidebar content"
      "footer footer";
  }
}
```

---

## 七、深入理解 Grid 布局算法

### 7.1 轨道尺寸计算

Grid 计算轨道尺寸的过程：

```javascript
// 简化的计算流程
function calculateGridTracks(container) {
  const { gridTemplateColumns, gap, availableWidth } = container;
  
  // 1. 处理固定尺寸
  // 2. 处理百分比
  // 3. 分配 fr 单位
  
  return computedTracks;
}
```

### 7.2 自动放置算法

Grid 的自动放置有两种策略：

```css
/* row - 先行后列（默认） */
.grid-container {
  grid-auto-flow: row;
}

/* column - 先列后行 */
.grid-container {
  grid-auto-flow: column;
}

/* dense - 密集填充，不留空隙 */
.grid-container {
  grid-auto-flow: dense;
}
```

### 7.3 隐式网格

当项目位置超出显式定义的网格时，会创建隐式网格：

```css
.grid-container {
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: 100px;
  
  /* 定义隐式网格 */
  grid-auto-rows: 80px;
  grid-auto-columns: 100px;
}
```

---

## 八、实战案例

### 8.1 经典 Holy Grail 布局

```html
<div class="holy-grail">
  <header>Header</header>
  <nav>Navigation</nav>
  <main>Main Content</main>
  <aside>Sidebar</aside>
  <footer>Footer</footer>
</div>
```

```css
.holy-grail {
  display: grid;
  min-height: 100vh;
  grid-template:
    "header header header" auto
    "nav main aside" 1fr
    "footer footer footer" auto /
    200px 1fr 200px;
  gap: 10px;
}

header { grid-area: header; background: #333; color: white; }
nav { grid-area: nav; background: #ddd; }
main { grid-area: main; background: #f5f5f5; }
aside { grid-area: aside; background: #ddd; }
footer { grid-area: footer; background: #333; color: white; }
```

### 8.2 卡片网格布局

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  padding: 2rem;
}

.card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-image {
  height: 200px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.card-content {
  padding: 1.5rem;
}
```

### 8.3 瀑布流布局（Masonry）

```css
.masonry {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
  grid-auto-rows: 10px;
}

.masonry-item {
  margin-bottom: 1rem;
}

/* 不同高度的项目 */
.masonry-item:nth-child(3n+1) { grid-row: span 20; }
.masonry-item:nth-child(3n+2) { grid-row: span 25; }
.masonry-item:nth-child(3n) { grid-row: span 15; }
```

---

## 九、Grid 与 Flexbox 配合使用

### 9.1 何时使用 Grid，何时使用 Flexbox

```css
/* Grid 适用于： */
/* - 页面整体布局
/* - 二维布局（同时控制行和列 */
/* - 需要精确控制位置 */

/* Flexbox 适用于： */
/* - 组件内部布局 */
/* - 一维布局（行或列） */
/* - 内容优先的布局 */
```

### 9.2 组合使用示例

```css
/* Grid 作为外层布局 */
.page-layout {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 20px;
}

/* Flexbox 作为内部组件布局 */
.nav-menu {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.card-list {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}
```

---

## 十、性能优化与最佳实践

### 10.1 性能优化建议

```css
/* 使用 grid-template 简写 */
.grid-container {
  /* 不推荐：分开写 */
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto 1fr;
  grid-template-areas: "header header" "main sidebar";
  
  /* 推荐：简写 */
  grid-template:
    "header header" auto
    "main sidebar" 1fr /
    1fr 1fr;
}
```

### 10.2 最佳实践

1. 使用 `fr` 单位代替百分比
2. 利用 `auto-fit` + `minmax()` 做响应式
3. 使用命名区域提高可读性
4. 合理使用 `gap` 代替 `margin`
5. 与 Flexbox 配合使用

---

## 十一、总结

CSS Grid 是现代前端开发不可或缺的布局工具。掌握 Grid，你可以轻松实现各种复杂布局，提升开发效率。

通过本文的学习，你应该能够：
- 理解 Grid 的核心概念和术语
- 掌握 Grid 容器和项目的属性
- 使用函数和单位创建灵活布局
- 实现响应式 Grid 布局
- 与 Flexbox 配合使用

希望这篇文章对你有帮助，欢迎点赞收藏！
