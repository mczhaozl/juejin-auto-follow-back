# CSS :has() 选择器：父元素选择的革命性突破

> 告别 JavaScript，用纯 CSS 实现"根据子元素状态改变父元素样式"的能力

---

## 一、:has() 解决了什么问题

在 :has() 出现之前，CSS 只能"向下"选择（父选子），无法"向上"选择（子影响父）。

```css
/* 传统：只能选择 .card 内的 img */
.card img {
  border-radius: 8px;
}

/* 无法实现：当 .card 包含 img 时，给 .card 加样式 */
/* ❌ 这样写是无效的 */
.card:contains(img) {
  padding: 0;
}
```

以前只能用 JavaScript：

```javascript
document.querySelectorAll('.card').forEach(card => {
  if (card.querySelector('img')) {
    card.classList.add('has-image');
  }
});
```

现在用 :has()：

```css
/* ✅ 当 .card 包含 img 时，给 .card 加样式 */
.card:has(img) {
  padding: 0;
  background: #f5f5f5;
}
```

---

## 二、基础用法

### 1. 检查是否包含某元素

```css
/* 包含图片的卡片 */
.card:has(img) {
  display: grid;
  grid-template-columns: 200px 1fr;
}

/* 包含视频的卡片 */
.card:has(video) {
  aspect-ratio: 16 / 9;
}

/* 不包含任何子元素的空卡片 */
.card:not(:has(*)) {
  display: none;
}
```

### 2. 检查子元素状态

```css
/* 表单包含无效输入时，显示错误提示 */
form:has(input:invalid) .error-message {
  display: block;
}

/* 复选框被选中时，改变父容器样式 */
.option:has(input:checked) {
  background: #e3f2fd;
  border-color: #2196f3;
}

/* 输入框获得焦点时，高亮整个表单组 */
.form-group:has(input:focus) {
  box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
}
```

---

## 三、实战案例

### 案例 1：表单验证样式

```html
<div class="form-field">
  <label>邮箱</label>
  <input type="email" required />
  <span class="error">请输入有效邮箱</span>
</div>
```

```css
.form-field {
  position: relative;
  margin-bottom: 20px;
}

/* 默认隐藏错误提示 */
.error {
  display: none;
  color: #f44336;
  font-size: 12px;
}

/* 输入无效时显示错误 */
.form-field:has(input:invalid:not(:placeholder-shown)) .error {
  display: block;
}

/* 输入无效时，输入框变红 */
.form-field:has(input:invalid:not(:placeholder-shown)) input {
  border-color: #f44336;
}

/* 输入有效时，输入框变绿 */
.form-field:has(input:valid:not(:placeholder-shown)) input {
  border-color: #4caf50;
}
```

### 案例 2：卡片悬停效果

```html
<article class="card">
  <img src="cover.jpg" alt="封面" />
  <h3>文章标题</h3>
  <p>文章摘要...</p>
  <a href="/detail">阅读更多</a>
</article>
```

```css
.card {
  transition: transform 0.3s;
}

/* 鼠标悬停在卡片内任意元素时，整个卡片抬起 */
.card:has(*:hover) {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

/* 悬停在链接上时，图片缩放 */
.card:has(a:hover) img {
  transform: scale(1.05);
}
```

### 案例 3：导航高亮

```html
<nav>
  <a href="#home">首页</a>
  <a href="#about">关于</a>
  <a href="#contact" class="active">联系</a>
</nav>
```

```css
/* 包含激活链接的导航栏，显示指示器 */
nav:has(.active)::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: var(--indicator-left);
  width: var(--indicator-width);
  height: 3px;
  background: #2196f3;
  transition: all 0.3s;
}
```

### 案例 4：购物车空状态

```html
<div class="cart">
  <div class="cart-items">
    <!-- 购物车商品列表 -->
  </div>
  <div class="empty-state">购物车是空的</div>
</div>
```

```css
/* 默认隐藏空状态 */
.empty-state {
  display: none;
}

/* 购物车没有商品时，显示空状态 */
.cart:not(:has(.cart-item)) .empty-state {
  display: flex;
}

/* 购物车有商品时，隐藏空状态 */
.cart:has(.cart-item) .empty-state {
  display: none;
}
```

---

## 四、高级技巧

### 1. 组合使用

```css
/* 同时包含图片和视频的卡片 */
.card:has(img):has(video) {
  grid-template-columns: 1fr 1fr;
}

/* 包含图片但不包含视频 */
.card:has(img):not(:has(video)) {
  grid-template-columns: 200px 1fr;
}
```

### 2. 兄弟元素影响

```css
/* 选中复选框后，影响后续兄弟元素 */
.checkbox:has(input:checked) ~ .content {
  display: block;
}

/* 第一个输入框有值时，显示第二个输入框 */
.step-1:has(input:not(:placeholder-shown)) ~ .step-2 {
  opacity: 1;
  pointer-events: auto;
}
```

### 3. 数量查询

```css
/* 只有一个子元素时 */
.list:has(> :only-child) {
  text-align: center;
}

/* 超过 5 个子元素时，切换为网格布局 */
.list:has(> :nth-child(6)) {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
}
```

---

## 五、浏览器支持

:has() 在现代浏览器中支持良好：

- Chrome 105+
- Safari 15.4+
- Firefox 121+
- Edge 105+

检测支持：

```css
@supports selector(:has(*)) {
  /* 支持 :has() 的样式 */
  .card:has(img) {
    padding: 0;
  }
}

@supports not selector(:has(*)) {
  /* 降级方案 */
  .card.has-image {
    padding: 0;
  }
}
```

---

## 六、性能注意事项

:has() 的性能开销比普通选择器大，因为需要向下遍历 DOM 树。

优化建议：

1. **限制作用域**：使用具体的选择器，避免全局匹配

```css
/* ❌ 性能差 */
*:has(.active) { }

/* ✅ 性能好 */
.nav:has(.active) { }
```

2. **避免深层嵌套**

```css
/* ❌ 性能差 */
.container:has(.wrapper:has(.inner:has(.active))) { }

/* ✅ 性能好 */
.container:has(.active) { }
```

3. **配合其他选择器**

```css
/* 限制在特定上下文 */
.sidebar .menu:has(.active) { }
```

---

## 七、与 JavaScript 对比

| 场景 | CSS :has() | JavaScript |
|------|-----------|-----------|
| 表单验证样式 | ✅ 简洁 | ❌ 需监听事件 |
| 动态内容 | ✅ 自动响应 | ❌ 需手动更新 |
| 性能 | ✅ 浏览器优化 | ⚠️ 依赖实现 |
| 复杂逻辑 | ❌ 能力有限 | ✅ 灵活强大 |
| 浏览器支持 | ⚠️ 需考虑兼容 | ✅ 广泛支持 |

---

## 总结

:has() 选择器是 CSS 的重大进步，它让我们能用纯 CSS 实现以前需要 JavaScript 才能完成的功能。从表单验证到卡片交互，:has() 都能提供更简洁、更高效的解决方案。

在现代浏览器环境下，建议优先使用 :has()，并为旧浏览器提供降级方案。

如果这篇文章对你有帮助，欢迎点赞收藏！
