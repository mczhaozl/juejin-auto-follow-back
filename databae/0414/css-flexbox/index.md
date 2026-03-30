# CSS Flexbox 完全指南：弹性布局实战

> 深入讲解 CSS Flexbox，包括主轴交叉轴、对齐方式、flex 属性，以及实际项目中的常见布局模式和最佳实践。

## 一、基础概念

### 1.1 容器与项目

```css
.container {
  display: flex;
}

.item {
  /* flex 项目 */
}
```

### 1.2 轴

```
         交叉轴
            │
            ▼
    ┌───┬───┬───┐
    │ 1 │ 2 │ 3 │ ──► 主轴
    └───┴───┴───┘
```

### 1.3 常用属性

```css
.container {
  display: flex;
  flex-direction: row;        /* row | column */
  flex-wrap: nowrap;          /* nowrap | wrap */
  justify-content: center;    /* 主轴对齐 */
  align-items: center;        /* 交叉轴对齐 */
}
```

## 二、对齐方式

### 2.1 主轴对齐

```css
/* 居中 */
justify-content: center;

/* 两端对齐 */
justify-content: space-between;

/* 等间距 */
justify-content: space-around;

/* 等间距（两端也有） */
justify-content: space-evenly;

/* 起始对齐 */
justify-content: flex-start;

/* 结束对齐 */
justify-content: flex-end;
```

### 2.2 交叉轴对齐

```css
/* 单行对齐 */
align-items: center;
align-items: flex-start;
align-items: flex-end;
align-items: stretch;
align-items: baseline;
```

### 2.3 多行对齐

```css
.container {
  flex-wrap: wrap;
  align-content: center;
  align-content: space-between;
  align-content: space-around;
}
```

## 三、Flex 属性

### 3.1 flex-grow

```css
.item {
  flex-grow: 1;  /* 伸展比例 */
}

/* 等分 */
.item1 { flex-grow: 1; }
.item2 { flex-grow: 1; }
.item3 { flex-grow: 1; }

/* 按比例 */
.item1 { flex-grow: 2; }
.item2 { flex-grow: 1; }
```

### 3.2 flex-shrink

```css
.item {
  flex-shrink: 0;  /* 不允许收缩 */
}
```

### 3.3 flex-basis

```css
.item {
  flex-basis: 200px;  /* 初始尺寸 */
}
```

### 3.4 简写

```css
/* flex: grow shrink basis */
.item {
  flex: 1 1 auto;
  flex: 1;  /* flex: 1 1 0% */
}
```

## 四、实战案例

### 4.1 垂直居中

```css
.container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
}
```

### 4.2 列表布局

```css
.nav {
  display: flex;
  gap: 20px;
}

.nav a {
  /* 自动等宽 */
  flex: 1;
  text-align: center;
}
```

### 4.3 圣杯布局

```css
.container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.header, .footer {
  flex: 0 0 auto;
}

.main {
  flex: 1;
  display: flex;
}

.content {
  flex: 1;
}

.sidebar {
  flex: 0 0 200px;
}
```

## 五、总结

Flexbox 核心要点：

1. **display: flex**：启用弹性盒
2. **主轴**：justify-content
3. **交叉轴**：align-items
4. **flex-grow**：伸展
5. **flex-shrink**：收缩

掌握这些，布局更灵活！

---

**推荐阅读**：
- [MDN Flexbox](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Flexible_Box_Layout)

**如果对你有帮助，欢迎点赞收藏！**
