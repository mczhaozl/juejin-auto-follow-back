# 深入浅出 CSS：2026 年你必须掌握的 CSS Container Queries 实践指南

> 响应式设计不仅仅是媒体查询。CSS Container Queries（容器查询）的全面普及，让我们可以基于父元素的尺寸而非整个视口的宽度来调整样式。本文将带你通过 3 个实战案例，掌握这一现代 CSS 的核心技术。

## 一、为什么媒体查询不再足够？

在组件化的今天，同一个卡片组件可能出现在侧边栏（宽度 300px）或主内容区（宽度 800px）。

**媒体查询的局限性：** 它是基于整个浏览器的视口（Viewport）宽度的。如果视口宽度是 1200px，那么无论组件在侧边栏还是主内容区，样式都是一样的。

**容器查询的优势：** 它可以让组件根据自己所在的「父容器」宽度来决定样式。

## 二、核心语法：container-type

要使用容器查询，首先需要定义谁是「容器」。

```css
.card-container {
  /* 定义容器类型：size (宽高) 或 inline-size (宽度) */
  container-type: inline-size;
  /* 可选：给容器起个名字 */
  container-name: sidebar-card;
}
```

接下来，你就可以像写 `@media` 一样写 `@container` 了：

```css
@container (min-width: 500px) {
  .card-content {
    display: grid;
    grid-template-columns: 1fr 2fr;
  }
}
```

## 三、实战案例：响应式卡片

假设我们有一个商品卡片，我们希望它在窄容器下是垂直布局，在宽容器下是水平布局。

```html
<div class="product-wrapper">
  <div class="product-card">
    <img src="thumb.jpg" />
    <div class="info">
      <h3>Awesome Product</h3>
      <p>This is a great description.</p>
    </div>
  </div>
</div>
```

**CSS：**
```css
.product-wrapper {
  container-type: inline-size;
}

.product-card {
  display: flex;
  flex-direction: column;
}

@container (min-width: 400px) {
  .product-card {
    flex-direction: row;
    gap: 16px;
  }
}
```

## 四、容器查询单位：cqw, cqh

容器查询还引入了新的长度单位，类似于 `vw/vh`，但它们是相对于容器尺寸的：
- **`cqw`**：容器宽度的 1%。
- **`cqh`**：容器高度的 1%。

这在做字体自适应时非常有用：
```css
.card-title {
  font-size: clamp(1rem, 5cqw, 2rem);
}
```

## 五、浏览器支持情况 (2026 年)

到 2026 年，所有主流浏览器（Chrome, Safari, Firefox, Edge）的现代版本都已经完美支持 Container Queries。如果你还在兼容远古版本的 IE，可能需要引入 polyfill。

## 六、总结

容器查询是响应式设计的一次巨大飞跃，它真正实现了「组件自适应」。掌握它，能让你的组件库更加健壮和灵活。

**你已经在项目中使用过容器查询了吗？欢迎在评论区分享你的实战心得！**
