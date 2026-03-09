# CSS 容器查询（@container）：响应式设计的新范式

> 告别媒体查询的局限，让组件根据自身容器大小自适应

---

## 一、媒体查询的局限

传统的媒体查询只能根据视口（viewport）大小来调整样式：

```css
/* 只能根据整个页面宽度 */
@media (max-width: 768px) {
  .card {
    flex-direction: column;
  }
}
```

问题：同一个组件在不同位置可能需要不同的样式，但媒体查询无法感知组件所在容器的大小。

```html
<!-- 侧边栏中的卡片（窄） -->
<aside style="width: 300px">
  <div class="card">...</div>
</aside>

<!-- 主内容区的卡片（宽） -->
<main style="width: 800px">
  <div class="card">...</div>
</main>
```

两个卡片在同一视口下，但容器宽度不同，媒体查询无法区分。

---

## 二、容器查询的解决方案

容器查询让元素可以根据**父容器**的大小来调整样式。

### 基础用法

```css
/* 1. 定义容器 */
.sidebar {
  container-type: inline-size;  /* 或 size */
  container-name: sidebar;  /* 可选：命名容器 */
}

/* 2. 根据容器大小应用样式 */
@container (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
  }
}

@container (max-width: 399px) {
  .card {
    display: block;
  }
}
```

---

## 三、container-type 详解

`container-type` 定义容器的查询类型：

```css
/* inline-size: 只查询内联方向（通常是宽度） */
.container {
  container-type: inline-size;
}

/* size: 查询宽度和高度 */
.container {
  container-type: size;
}

/* normal: 不是容器（默认值） */
.container {
  container-type: normal;
}
```

注意：使用 `size` 时，容器的高度必须是确定的，否则可能导致布局问题。

---

## 四、容器单位

容器查询引入了新的单位，类似于视口单位（vw, vh）：

| 单位 | 含义 | 等价于 |
|------|------|--------|
| cqw | 容器宽度的 1% | 1% of container width |
| cqh | 容器高度的 1% | 1% of container height |
| cqi | 容器内联尺寸的 1% | 1% of container inline size |
| cqb | 容器块尺寸的 1% | 1% of container block size |
| cqmin | cqi 和 cqb 中较小的 | min(cqi, cqb) |
| cqmax | cqi 和 cqb 中较大的 | max(cqi, cqb) |

```css
.card {
  container-type: inline-size;
}

.card h2 {
  font-size: 5cqw;  /* 字体大小随容器宽度变化 */
  padding: 2cqw;
}
```

---

## 五、实战案例

### 案例 1：自适应卡片

```html
<div class="container">
  <div class="card">
    <img src="cover.jpg" alt="封面" />
    <div class="content">
      <h3>标题</h3>
      <p>描述文字...</p>
    </div>
  </div>
</div>
```

```css
.container {
  container-type: inline-size;
}

/* 容器宽度 < 400px：垂直布局 */
@container (max-width: 400px) {
  .card {
    display: flex;
    flex-direction: column;
  }
  
  .card img {
    width: 100%;
    height: 200px;
  }
}

/* 容器宽度 >= 400px：水平布局 */
@container (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
    gap: 20px;
  }
  
  .card img {
    width: 200px;
    height: 100%;
  }
}

/* 容器宽度 >= 600px：更大间距 */
@container (min-width: 600px) {
  .card {
    gap: 40px;
    padding: 30px;
  }
}
```

### 案例 2：响应式表格

```css
.table-container {
  container-type: inline-size;
}

/* 窄容器：卡片式布局 */
@container (max-width: 600px) {
  table {
    display: block;
  }
  
  thead {
    display: none;
  }
  
  tbody, tr, td {
    display: block;
  }
  
  td::before {
    content: attr(data-label) ": ";
    font-weight: bold;
  }
}

/* 宽容器：正常表格 */
@container (min-width: 601px) {
  table {
    width: 100%;
  }
}
```

### 案例 3：动态字体大小

```css
.article-container {
  container-type: inline-size;
}

.article h1 {
  font-size: clamp(1.5rem, 5cqw, 3rem);
}

.article p {
  font-size: clamp(0.875rem, 2cqw, 1.125rem);
  line-height: 1.6;
}
```

---

## 六、命名容器

当有多层嵌套容器时，可以通过命名来指定查询哪个容器。

```css
.sidebar {
  container-type: inline-size;
  container-name: sidebar;
}

.main {
  container-type: inline-size;
  container-name: main;
}

/* 查询名为 sidebar 的容器 */
@container sidebar (max-width: 300px) {
  .widget {
    font-size: 14px;
  }
}

/* 查询名为 main 的容器 */
@container main (min-width: 800px) {
  .widget {
    font-size: 18px;
  }
}
```

简写语法：

```css
/* 等价于上面的写法 */
.sidebar {
  container: sidebar / inline-size;
}
```

---

## 七、与媒体查询对比

| 特性 | 媒体查询 | 容器查询 |
|------|---------|---------|
| 查询对象 | 视口 | 父容器 |
| 组件复用 | ❌ 困难 | ✅ 容易 |
| 嵌套支持 | ❌ 不支持 | ✅ 支持 |
| 性能 | ✅ 好 | ✅ 好 |
| 浏览器支持 | ✅ 广泛 | ⚠️ 较新 |

---

## 八、浏览器支持

容器查询在现代浏览器中支持良好：

- Chrome 105+
- Safari 16+
- Firefox 110+
- Edge 105+

检测支持：

```css
@supports (container-type: inline-size) {
  /* 支持容器查询 */
  .container {
    container-type: inline-size;
  }
}

@supports not (container-type: inline-size) {
  /* 降级方案：使用媒体查询 */
  @media (max-width: 768px) {
    .card {
      flex-direction: column;
    }
  }
}
```

---

## 九、性能注意事项

1. **避免过度嵌套**：每层容器都会增加计算成本

```css
/* ❌ 性能差 */
.level1 { container-type: inline-size; }
.level2 { container-type: inline-size; }
.level3 { container-type: inline-size; }
.level4 { container-type: inline-size; }

/* ✅ 性能好：只在必要的层级定义 */
.main-container { container-type: inline-size; }
```

2. **谨慎使用 size**：`container-type: size` 会影响高度计算，可能导致布局问题

```css
/* 推荐：大多数情况用 inline-size */
.container {
  container-type: inline-size;
}
```

---

## 十、实用技巧

### 1. 组合使用媒体查询和容器查询

```css
/* 全局布局用媒体查询 */
@media (max-width: 768px) {
  .layout {
    grid-template-columns: 1fr;
  }
}

/* 组件样式用容器查询 */
@container (max-width: 400px) {
  .card {
    padding: 10px;
  }
}
```

### 2. 使用 CSS 变量

```css
.container {
  container-type: inline-size;
  --card-gap: 20px;
}

@container (max-width: 400px) {
  .container {
    --card-gap: 10px;
  }
}

.card {
  gap: var(--card-gap);
}
```

---

## 总结

容器查询是响应式设计的重大进步，它让组件能够根据自身所在容器的大小自适应，而不是依赖全局视口。这使得组件更加独立、可复用，特别适合现代组件化开发。

在支持的浏览器中，建议优先使用容器查询来实现组件级别的响应式设计，并为旧浏览器提供媒体查询作为降级方案。

如果这篇文章对你有帮助，欢迎点赞收藏！
