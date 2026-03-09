# 从 float 到 Flex/Grid：CSS 左右布局简史与「刁钻」布局怎么搞

> 对比以前用 float、inline-block、table 做左右布局的写法，再看 Flex 如何用几行代码搞定同样效果、如何应对两端对齐与等高之类需求，并简要介绍 Grid 二维布局的适用场景。

---

## 一、以前是怎么做左右布局的

在 Flexbox 普及之前，左右分栏、多列等高、垂直居中都要靠「拼手艺」：**float**、**inline-block**、**table 布局** 是三种常见手段，代码多、易踩坑、响应式要写一堆 media。

### 1.1 float + clearfix

左栏左浮、右栏右浮或给右栏设 `margin-left` 把位置「挤」出来；父容器高度塌陷，得加 **clearfix**（或 `overflow: hidden`）把父元素「撑起来」。

```css
/* 父容器 */
.wrap::after {
    content: '';
    display: block;
    clear: both;
}
.wrap { overflow: hidden; } /* 或直接用 overflow 清浮动 */

/* 左右两列 */
.left { float: left; width: 200px; }
.right { margin-left: 200px; } /* 或 float: left; width: calc(100% - 200px); */
```

**痛点**：要手算宽度、清浮动、注意子元素顺序；多列时每个都要设宽度或 `calc`，改一列就要改好几处。

### 1.2 inline-block

子元素设 `display: inline-block` 并 `vertical-align: top` 避免基线对齐错位，父级用 `font-size: 0` 吃掉空白间隙（或子项间不留空格）。

```css
.wrap { font-size: 0; }
.left, .right { display: inline-block; vertical-align: top; font-size: 16px; }
.left { width: 200px; }
.right { width: calc(100% - 200px); }
```

**痛点**：宽度仍要自己算、要处理空白间隙和 `vertical-align`，多列等高还要额外 hack。

### 1.3 table / table-cell

父 `display: table`，子 `display: table-cell`，天然等高、可不用算宽度（用百分比或留一列不设宽）。

```css
.wrap { display: table; width: 100%; }
.left { display: table-cell; width: 200px; }
.right { display: table-cell; }
```

**痛点**：语义上是「表格」，可访问性和 SEO 不理想；改布局要动 HTML 结构或大量覆盖样式，灵活性差。

---

## 二、Flex 登场：同样的左右布局，简化了多少

**Flexbox**（弹性盒子）是为一维布局设计的：一根主轴（行或列），子项沿主轴排列，对齐、均分、换行都用属性声明，不用再算宽度、清浮动。

### 2.1 最简左右布局

父容器 `display: flex`，子项默认横排、不会塌陷，右栏用 `flex: 1` 占满剩余空间，左栏定宽即可。

```css
.wrap {
    display: flex;
}
.left { width: 200px; flex-shrink: 0; }
.right { flex: 1; }
```

**对比**：以前要写 clearfix、`float`、`margin-left` 或 `calc`，现在 3 行核心样式；父级不再塌陷，无需 `overflow: hidden` 或 `::after`。

### 2.2 对齐一句话搞定

垂直居中、两端对齐、间距均匀，用 **justify-content**（主轴）和 **align-items**（交叉轴）即可。

```css
.wrap {
    display: flex;
    justify-content: space-between; /* 两端对齐 */
    align-items: center;           /* 垂直居中 */
}
```

以前垂直居中要 `line-height`、`position + transform` 或 table-cell，现在一个属性就够。

---

## 三、Flex 如何搞定各种「刁钻」布局

很多以前要写很多 hack 的效果，用 Flex 都能直接表达。

### 3.1 两端对齐 + 最后一列左对齐

`justify-content: space-between` 最后一行会贴两边，若希望最后一行也从左开始、项之间间距一致，可以配合 **flex-wrap** 和 **gap**（或用 margin）在子项上做间距，或外层再包一层 flex。

```css
.wrap {
    display: flex;
    flex-wrap: wrap;
    gap: 16px;
}
.item { width: calc(33.333% - 11px); } /* 三列时大致均分，具体可用 min-width 替代固定宽度 */
```

更稳的「多列等分 + 最后一行左对齐」可以用 **Grid**（见第四节）；Flex 里也可用 `margin-right` + 负 margin 或 `:last-child` 等方式收尾。

### 3.2 等高、底部对齐、垂直居中

- **等高**：Flex 默认 `align-items: stretch`，子项会被拉成同一高度，无需 table 或 JS。
- **底部对齐**：`align-items: flex-end`。
- **垂直居中**：`align-items: center`；单行文本还可配合 `justify-content: center` 做水平+垂直居中。

```css
.wrap {
    display: flex;
    align-items: stretch;  /* 默认，等高 */
}
.wrap.bottom { align-items: flex-end; }
.wrap.center { align-items: center; justify-content: center; }
```

### 3.3 换行、均分、顺序

- **flex-wrap: wrap**：子项总宽超出一行就换行。
- **flex: 1**：子项均分剩余空间；**flex-grow / flex-shrink** 控制放大与收缩比例。
- **order**：调整子项视觉顺序，不用改 DOM。

```css
.wrap { display: flex; flex-wrap: wrap; gap: 12px; }
.item { flex: 1 1 200px; }  /* 最小 200px，有空间就均分 */
.item.first { order: -1; }
```

---

## 四、Grid 布局简介：二维「画格子」

**Grid** 是二维布局：先定义**行和列**，再把子项放到网格里（或让它们自动流进去），适合**卡片网格、整页骨架、多列多行对齐**。

### 4.1 和 Flex 的取舍

- **Flex**：一维，沿一根主轴排，适合导航栏、表头、表单项、左右分栏。
- **Grid**：二维，行+列同时控制，适合多列等分卡片、整页多区域排版。

### 4.2 简单示例：三列等分 + 间距

```css
.wrap {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
}
```

子项不用再设 `width`、`flex`，自动按列排布；**gap** 统一处理间距，比用 margin 干净。若要「最后一行左对齐」，Grid 天然就是从左到右、从上到下填格子，不会像 `space-between` 那样最后一行被撑开。

### 4.3 进阶：多行多列与区域命名

可以定义多行多列，甚至用 **grid-template-areas** 给区域起名，布局一目了然。

```css
.page {
    display: grid;
    grid-template-columns: 200px 1fr 200px;
    grid-template-rows: auto 1fr auto;
    grid-template-areas:
        "header header header"
        "aside  main   side"
        "footer footer footer";
}
.header { grid-area: header; }
.aside  { grid-area: aside; }
.main   { grid-area: main; }
```

---

## 五、总结与参考

- **以前**：左右布局靠 float + clearfix、inline-block 或 table，代码多、易塌陷、对齐和等高都要 hack。
- **Flex**：`display: flex` + `flex: 1`、`justify-content`、`align-items` 几行就能搞定左右分栏、垂直居中、等高、两端对齐；换行与顺序用 `flex-wrap`、`order`、`gap` 即可，**一维布局首选 Flex**。
- **Grid**：`display: grid` + `grid-template-columns/rows`、`gap`，适合多列等分、整页骨架等**二维**布局；和 Flex 搭配使用，能覆盖绝大部分页面排版需求。

**参考**：

- MDN：[Flexbox](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Flexbox)、[Grid](https://developer.mozilla.org/zh-CN/docs/Learn/CSS/CSS_layout/Grids)
- Can I Use：查 [Flex](https://caniuse.com/flexbox)、[Grid](https://caniuse.com/css-grid) 兼容性

如果你还在维护老项目里的 float 布局，不妨在新需求里用 Flex/Grid 替代，能省不少心智和代码。觉得有用欢迎点赞、收藏或评论区聊聊你的布局经历。
