# CSS Grid 与 Flexbox 高级布局完全指南：从基础到复杂布局

## 一、Flexbox 深入

### 1.1 Flex 容器

```css
.container {
  display: flex;
  flex-direction: row; /* row | row-reverse | column | column-reverse */
  flex-wrap: wrap;     /* nowrap | wrap | wrap-reverse */
  flex-flow: row wrap; /* flex-direction + flex-wrap */
  
  justify-content: flex-start; /* 主轴对齐 */
  align-items: stretch;        /* 交叉轴对齐 */
  align-content: stretch;      /* 多根轴线对齐 */
  gap: 10px;
}
```

### 1.2 Flex 项目

```css
.item {
  order: 0;
  flex-grow: 0;
  flex-shrink: 1;
  flex-basis: auto;
  flex: 0 1 auto; /* grow + shrink + basis */
  align-self: auto; /* 覆盖 align-items */
}
```

---

## 二、Grid 深入

### 2.1 Grid 容器

```css
.container {
  display: grid;
  
  grid-template-columns: 1fr 2fr 1fr;
  grid-template-rows: auto 100px;
  grid-template-areas:
    "header header header"
    "sidebar main main"
    "footer footer footer";
  
  gap: 20px;
  justify-items: stretch; /* 项目在单元格对齐 */
  align-items: stretch;
  justify-content: center; /* 网格在容器对齐 */
  align-content: center;
}
```

### 2.2 Grid 项目

```css
.item {
  grid-column: 1 / 3;       /* 开始 / 结束 */
  grid-row: 1 / span 2;     /* 跨越 */
  grid-area: header;        /* 命名区域 */
  justify-self: center;     /* 单个项目对齐 */
  align-self: center;
}
```

---

## 三、实战布局

### 3.1 圣杯布局（Grid）

```css
.layout {
  display: grid;
  grid-template-areas:
    "header header header"
    "nav content aside"
    "footer footer footer";
  grid-template-columns: 200px 1fr 150px;
  grid-template-rows: auto 1fr auto;
  min-height: 100vh;
}

.header { grid-area: header; }
.nav { grid-area: nav; }
.content { grid-area: content; }
.aside { grid-area: aside; }
.footer { grid-area: footer; }
```

### 3.2 响应式卡片布局

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.card {
  display: flex;
  flex-direction: column;
}

.card-body {
  flex-grow: 1;
}
```

---

## 四、高级技巧

### 4.1 Grid 自动填充

```css
.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 10px;
}
```

### 4.2 子网格（Subgrid）

```css
.container {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}

.subcontainer {
  display: grid;
  grid-template-columns: subgrid;
  grid-column: span 3;
}
```

### 4.3 Flexbox 等高列

```css
.columns {
  display: flex;
  gap: 20px;
}

.column {
  flex: 1;
  display: flex;
  flex-direction: column;
}
```

---

## 五、响应式设计

```css
.container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 768px) {
  .container {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .container {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## 六、选择 Grid 还是 Flexbox

| 场景 | 选择 |
|------|------|
| 一维布局（行或列） | Flexbox |
| 二维布局（同时控制行和列） | Grid |
| 项目对齐和空间分配 | Flexbox |
| 复杂页面布局 | Grid |
| 卡片网格 | Grid |
| 导航栏 | Flexbox |

---

## 七、最佳实践

1. 合理使用 minmax() 和 auto-fill/auto-fit
2. 使用命名区域提高可读性
3. 结合 Grid 和 Flexbox 一起使用
4. 使用 gap 代替 margin
5. 从移动端开始响应式设计

---

## 八、总结

Grid 和 Flexbox 是现代 CSS 布局的利器，掌握它们能实现各种复杂布局。
