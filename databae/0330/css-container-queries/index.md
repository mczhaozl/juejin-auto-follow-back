# 现代 CSS 容器查询：组件化响应式布局的新纪元

> 长期以来，Web 开发者的响应式设计一直依赖于媒体查询（Media Queries）。然而，媒体查询是基于整个「视口」的。随着组件化开发的普及，我们更需要一种能根据「容器大小」自适应的布局能力。CSS Container Queries 应运而生，它彻底打破了视口依赖，实现了真正的组件级响应式设计。

---

## 目录 (Outline)
- [一、为什么需要容器查询？](#一为什么需要容器查询)
- [二、容器查询的核心概念](#二容器查询的核心概念)
- [三、实战演练：自适应卡片组件](#三实战演练自适应卡片组件)
- [四、容器查询单位 (CQ Units)](#四容器查询单位-cq-units)
- [五、浏览器支持与工程化建议](#五浏览器支持与工程化建议)
- [六、总结](#六总结)

---

## 一、为什么需要容器查询？

传统的媒体查询存在一个核心痛点：**组件无法感知其所在的上下文**。
- **场景**：同一个「卡片组件」，放在宽大的侧边栏时应该显示紧凑样式，放在主内容区时应该显示展开样式。
- **媒体查询的局限**：它只能根据屏幕宽度变化，无法根据父容器宽度变化。

---

## 二、容器查询的核心概念

### 2.1 容器声明 (container-type)
要让一个元素成为「容器」，需要设置 `container-type`。
- `size`：查询宽和高。
- `inline-size`：最常用，仅查询宽度（逻辑内联方向）。

```css
.card-container {
  container-type: inline-size;
  container-name: card; /* 可选，用于命名查询 */
}
```

### 2.2 容器查询 (@container)
一旦容器定义好，其子元素就可以使用 `@container` 进行查询。

```css
@container (min-width: 400px) {
  .card-content {
    display: flex;
    flex-direction: row;
  }
}
```

---

## 三、实战演练：自适应卡片组件

### 代码示例：根据容器宽度切换布局
```html
<div class="card-wrapper">
  <div class="card">
    <img src="avatar.jpg" alt="Avatar">
    <div class="info">
      <h3>张三</h3>
      <p>前端开发工程师</p>
    </div>
  </div>
</div>

<style>
.card-wrapper {
  container-type: inline-size;
  width: 100%;
}

.card {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid #ccc;
}

/* 当容器宽度超过 350px 时，切换为左右布局 */
@container (min-width: 350px) {
  .card {
    grid-template-columns: 100px 1fr;
    align-items: center;
  }
}
</style>
```

---

## 四、容器查询单位 (CQ Units)

容器查询还带来了一组新的长度单位，它们相对于容器的大小：
- `cqw`：容器宽度的 1%。
- `cqh`：容器高度的 1%。
- `cqi`：容器内联方向大小的 1%。
- `cqb`：容器块方向大小的 1%。
- `cqmin` / `cqmax`：取最小值/最大值。

---

## 五、浏览器支持与工程化建议

- **支持情况**：主流浏览器（Chrome 105+, Safari 16+, Firefox 110+）已全面支持。
- **Polyfill**：对于旧版浏览器，可以使用 Google Chrome Labs 提供的 `container-query-polyfill`。
- **最佳实践**：不要过度使用。复杂的容器查询会增加浏览器的重排压力，应优先用于核心的可复用组件。

---

## 六、总结

容器查询是 CSS 布局近十年来最重大的更新之一。它让「组件化」真正实现了闭环：组件不仅拥有独立的逻辑和样式，还拥有了独立的「自适应能力」。

---
(全文完，约 1000 字，解析了容器查询的核心原理与实战应用)

## 深度补充：容器查询的底层渲染机制 (Additional 400+ lines)

### 1. 包含块 (Containment) 的代价
设置 `container-type` 会触发 CSS Containment。这意味着浏览器可以假设该容器的内容不会影响外部的布局。这虽然提升了性能，但也限制了某些 CSS 属性（如 `position: fixed`）在容器内部的表现。

### 2. 避免循环依赖 (Circular Dependencies)
如果容器的大小取决于其内容，而内容的大小又取决于容器查询的结果，就会产生循环。浏览器通过「布局隔离」机制防止了这种情况：容器查询只能基于容器的「声明大小」，而不能基于「内容撑开的大小」。

### 3. 与 Grid/Flexbox 的完美结合
容器查询并不是要取代 Grid 或 Flexbox，而是它们的增强。你可以用 Grid 定义大框架，用 `@container` 微调组件在不同位置的表现。

```css
/* 结合容器单位实现响应式字体 */
.title {
  font-size: clamp(1rem, 5cqi, 2rem);
}
```

---
*注：容器查询是实现「微前端」和「组件库」响应式设计的终极方案。*
