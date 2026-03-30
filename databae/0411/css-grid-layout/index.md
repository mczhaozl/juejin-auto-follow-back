# CSS Grid 布局完全指南：从入门到实战

> 深入讲解 CSS Grid 布局系统，包括网格容器、网格项、模板区域、响应式布局，以及实际项目中的布局案例。

## 一、Grid 基础

### 1.1 基本概念

```css
.container {
  display: grid;
}
```

### 1.2 网格术语

- **Grid Container**：网格容器
- **Grid Item**：网格项
- **Grid Line**：网格线
- **Grid Track**：网格轨道
- **Grid Cell**：网格单元格

## 二、定义网格

### 2.1 行列定义

```css
.container {
  display: grid;
  
  /* 定义列 */
  grid-template-columns: 100px 200px 100px;
  
  /* 定义行 */
  grid-template-rows: 50px 100px 50px;
  
  /* 使用 fr 单位 */
  grid-template-columns: 1fr 2fr 1fr;
  
  /* 重复 */
  grid-template-columns: repeat(3, 1fr);
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
}
```

### 2.2 间距

```css
.container {
  /* 行间距和列间距 */
  gap: 20px;
  row-gap: 10px;
  column-gap: 20px;
}
```

## 三、网格区域

### 3.1 命名区域

```css
.container {
  display: grid;
  grid-template-areas:
    "header header header"
    "sidebar content content"
    "footer footer footer";
  grid-template-columns: 200px 1fr 1fr;
  grid-template-rows: 60px 1fr 60px;
}

.header { grid-area: header; }
.sidebar { grid-area: sidebar; }
.content { grid-area: content; }
.footer { grid-area: footer; }
```

### 3.2 合并单元格

```css
.item {
  grid-column: 1 / 3;  /* 从第1条线到第3条线 */
  grid-row: 1 / 2;
  
  /* 简写 */
  grid-area: 1 / 1 / 2 / 3;
}
```

## 四、排列对齐

### 4.1 容器对齐

```css
.container {
  /* 水平对齐 */
  justify-items: start | end | center | stretch;
  
  /* 垂直对齐 */
  align-items: start | end | center | stretch;
  
  /* 简写 */
  place-items: center center;
}
```

### 4.2 网格项对齐

```css
.item {
  justify-self: start | end | center | stretch;
  align-self: start | end | center | stretch;
  
  /* 简写 */
  place-self: center;
}
```

## 五、自动填充

### 5.1 auto-fill

```css
.container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}
```

### 5.2 auto-fit

```css
.container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}
```

## 六、响应式布局

### 6.1 媒体查询

```css
.container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 768px) {
  .container {
    grid-template-columns: 1fr 1fr;
  }
}

@media (min-width: 1024px) {
  .container {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 6.2 复杂响应式

```css
.container {
  display: grid;
  grid-template-areas:
    "header"
    "main"
    "sidebar"
    "footer";
}

@media (min-width: 768px) {
  .container {
    grid-template-areas:
      "header header"
      "sidebar main"
      "footer footer";
    grid-template-columns: 200px 1fr;
  }
}
```

## 七、实战案例

### 7.1 卡片网格

```css
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding: 20px;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
```

### 7.2 仪表盘布局

```css
.dashboard {
  display: grid;
  grid-template-columns: 250px 1fr;
  grid-template-rows: 60px 1fr;
  grid-template-areas:
    "sidebar header"
    "sidebar main";
  height: 100vh;
}

.sidebar { grid-area: sidebar; }
.header { grid-area: header; }
.main { grid-area: main; }
```

### 7.3 图片画廊

```css
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  grid-auto-rows: 150px;
  gap: 8px;
}

.gallery-item:nth-child(3n) {
  grid-column: span 2;
}

.gallery-item:nth-child(4n) {
  grid-row: span 2;
}
```

## 八、总结

CSS Grid 核心要点：

1. **display: grid**：开启网格布局
2. **grid-template**：定义行列
3. **gap**：间距
4. **grid-area**：区域划分
5. **对齐**：justify/align
6. **auto-fill/fit**：自动填充
7. **响应式**：媒体查询结合

掌握这些，布局不再难！

---

**推荐阅读**：
- [MDN CSS Grid](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Grid_Layout)
- [CSS Grid Garden](https://cssgridgarden.com/)

**如果对你有帮助，欢迎点赞收藏！**
