# CSS 容器查询深度指南：响应式设计的未来

> 一文掌握容器查询核心用法，与媒体查询的区别与配合。

## 一、为什么需要容器查询

响应式设计长期以来依赖媒体查询（Media Queries）来适配不同视口尺寸。但媒体查询存在一个根本限制：它只能根据**浏览器视口**来判断布局，而无法根据**父容器**的实际宽度来调整样式。

考虑一个典型的卡片组件场景：卡片在首页展示时宽度可能是 300px，在文章详情页可能是 400px，在侧边栏可能是 250px。使用媒体查询时，你需要为不同页面写不同的样式类，或者依赖父容器的 class 来做条件判断。容器查询的出现彻底解决了这个问题——组件可以自己感知**父容器的宽度**，并据此调整自身的展示方式。

容器查询的核心价值在于**组件的独立性**。同一个卡片组件可以在不同容器中呈现不同的布局，而无需关心它所在的页面结构。这种能力对于构建可复用的设计系统、搭建页面组件库有着重要意义。

## 二、容器查询的基本用法

### 2.1 定义容器

使用 `container` 属性将元素声明为查询容器。这告诉浏览器该元素的后代可以使用容器查询来应用样式。

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}
```

`container-type` 有两个可选值：`inline-size` 表示根据容器的**行内方向尺寸**（通常是宽度）进行查询，`size` 表示同时根据宽度和高度进行查询。绝大多数场景下使用 `inline-size` 就足够了。

`container-name` 是可选的，用于给容器命名，这样在查询时可以指定具体的容器。如果不命名，则使用匿名容器。

### 2.2 编写容器查询

容器查询使用 `@container` 规则，语法与媒体查询类似。

```css
@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 150px 1fr;
    gap: 1rem;
  }
}

@container card (min-width: 600px) {
  .card {
    grid-template-columns: 200px 1fr;
    gap: 1.5rem;
  }
}
```

上面的代码表示：当名为 `card` 的容器宽度至少为 400px 时，卡片内部使用两列布局；当宽度达到 600px 时，左侧列宽从 150px 增加到 200px。

### 2.3 容器查询单位

容器查询引入了一组新的相对单位，这些单位是相对于**容器尺寸**而非视口尺寸计算的：

- `cqw`：容器宽度的 1%
- `cqh`：容器高度的 1%
- `cqi`：容器行内尺寸的 1%（通常是宽度）
- `cqb`：容器块级尺寸的 1%（通常是高度）
- `cmin`：取 cqi 和 cqb 中的较小值
- `cmax`：取 cqi 和 cqb 中的较大值

```css
.card-title {
  font-size: clamp(1rem, 5cqi, 2rem);
}
```

这段代码确保标题字体大小始终在 1rem 到 2rem 之间，并且会根据容器宽度动态计算。

## 三、容器查询与媒体查询的配合

容器查询并不是要完全取代媒体查询，两者各有适用场景。媒体查询适合整体页面布局的调整，比如导航栏在移动端显示汉堡菜单、在桌面端显示完整菜单。容器查询适合组件内部的布局变化，比如卡片在不同宽度下展示不同的内部结构。

一个常见的配合模式是：外层使用媒体查询做整体布局，内层使用容器查询做组件适配。

```css
/* 整体布局：移动端单列，桌面端三列 */
@media (min-width: 768px) {
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
  }
}

/* 组件适配：卡片在小容器中紧凑展示 */
@container card (max-width: 300px) {
  .card {
    padding: 0.75rem;
    font-size: 0.875rem;
  }
}
```

## 四、实战：响应式卡片组件

下面通过一个完整的卡片组件示例，展示容器查询的实际应用。

```html
<article class="card-container">
  <div class="card">
    <img class="card-image" src="cover.jpg" alt="" />
    <div class="card-content">
      <h3 class="card-title">文章标题</h3>
      <p class="card-excerpt">这是一段文章摘要...</p>
      <div class="card-footer">
        <span class="card-author">作者名</span>
        <span class="card-date">2026-03-18</span>
      </div>
    </div>
  </div>
</article>
```

对应的 CSS 样式：

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

.card {
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 160px;
  object-fit: cover;
}

.card-content {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.card-excerpt {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.5;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #9ca3af;
}

/* 容器宽度 >= 350px：横向布局 */
@container card (min-width: 350px) {
  .card {
    flex-direction: row;
  }
  
  .card-image {
    width: 40%;
    height: auto;
  }
  
  .card-content {
    width: 60%;
  }
}

/* 容器宽度 >= 500px：显示更多内容 */
@container card (min-width: 500px) {
  .card-image {
    height: 200px;
  }
  
  .card-title {
    font-size: 1.25rem;
  }
  
  .card-excerpt {
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
}
```

这个卡片组件在不同容器宽度下会自动调整布局：小于 350px 时保持垂直布局，350px 以上变为横向布局，500px 以上则增加图片高度并允许摘要显示三行。

## 五、浏览器兼容性

容器查询的浏览器支持情况已经相当不错。截至 2026 年，Chrome、Firefox、Safari 和 Edge 的最新版本都原生支持容器查询，无需任何 polyfill。

对于需要兼容旧版浏览器的项目，可以使用 `@supports` 检测是否支持容器查询，并提供降级方案：

```css
.card {
  /* 默认样式：适用于不支持容器查询的浏览器 */
  display: block;
}

@supports (container-type: inline-size) {
  .card-container {
    container-type: inline-size;
  }
  
  @container (min-width: 350px) {
    .card {
      display: flex;
    }
  }
}
```

## 六、常见问题与注意事项

容器查询虽然强大，但使用时需要注意几个关键点。首先，容器查询只能查询**直接祖先**的容器尺寸，不能跨层级查询。其次，容器查询的单位是相对于容器计算的，与视口无关，这一点与媒体查询的单位有本质区别。

另外，容器查询可能导致样式计算的性能开销增加，特别是在大量使用容器查询的复杂页面上。如果发现性能问题，可以考虑使用 `contain` 属性来限制布局影响范围，或者减少不必要的查询嵌套。

## 总结

容器查询是 CSS 布局能力的一次重要升级，它让组件真正具备了响应式的能力。通过将组件的样式与组件的容器尺寸绑定，我们可以构建出更加灵活、可复用的 UI 组件。建议在新的项目中优先使用容器查询来构建响应式组件，同时保留媒体查询用于整体页面布局的调整。

如果这篇文章对你有帮助，欢迎点赞、收藏和关注。