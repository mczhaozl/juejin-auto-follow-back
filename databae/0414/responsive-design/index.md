# 响应式设计完全指南：媒体查询与移动优先

> 深入讲解响应式设计，包括媒体查询、移动优先策略、视口单位，以及实际项目中的断点设计和适配方案。

## 一、视口设置

### 1.1 viewport meta

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

### 1.2 参数说明

| 参数 | 说明 |
|------|------|
| width | 视口宽度 |
| height | 视口高度 |
| initial-scale | 初始缩放 |
| maximum-scale | 最大缩放 |
| user-scalable | 允许缩放 |

## 二、媒体查询

### 2.1 媒体类型

```css
@media screen {
  /* 屏幕设备 */
}

@media print {
  /* 打印设备 */
}

@media all {
  /* 所有设备 */
}
```

### 2.2 媒体特性

```css
/* 宽度 */
@media (min-width: 768px) {}

/* 最大宽度 */
@media (max-width: 768px) {}

/* 方向 */
@media (orientation: portrait) {}
@media (orientation: landscape) {}

/* 像素比 */
@media (-webkit-min-device-pixel-ratio: 2) {}
```

### 2.3 逻辑操作

```css
/* 与 */
@media (min-width: 768px) and (max-width: 1024px) {}

/* 或 */
@media (min-width: 768px), (orientation: portrait) {}

/* 非 */
@media not (max-width: 768px) {}
```

## 三、断点设计

### 3.1 常见断点

```css
/* 手机 */
@media (max-width: 576px) {}

/* 平板 */
@media (min-width: 577px) and (max-width: 992px) {}

/* 桌面 */
@media (min-width: 993px) and (max-width: 1200px) {}

/* 大屏 */
@media (min-width: 1201px) {}
```

### 3.2 Bootstrap 断点

| 断点 | 尺寸 |
|------|------|
| xs | < 576px |
| sm | ≥ 576px |
| md | ≥ 768px |
| lg | ≥ 992px |
| xl | ≥ 1200px |
| xxl | ≥ 1400px |

## 四、移动优先

### 4.1 基础样式

```css
/* 基础样式（手机） */
.container {
  width: 100%;
  padding: 10px;
}

/* 平板及以上 */
@media (min-width: 768px) {
  .container {
    width: 750px;
    padding: 20px;
  }
}

/* 桌面及以上 */
@media (min-width: 992px) {
  .container {
    width: 970px;
    padding: 30px;
  }
}
```

### 4.2 弹性单位

```css
.container {
  width: 90%;
  max-width: 1200px;
}

/* 视口单位 */
.box {
  width: 50vw;
  height: 100vh;
}

/* rem */
html {
  font-size: 16px;
}

.box {
  width: 10rem;
}
```

## 五、实战案例

### 5.1 响应式导航

```css
/* 默认：汉堡菜单 */
.nav-links {
  display: none;
}

.nav-links.active {
  display: flex;
}

/* 桌面：横向菜单 */
@media (min-width: 768px) {
  .nav-links {
    display: flex;
    gap: 20px;
  }
  
  .menu-toggle {
    display: none;
  }
}
```

### 5.2 响应式网格

```css
.grid {
  display: grid;
  gap: 20px;
  grid-template-columns: 1fr;
}

@media (min-width: 576px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 992px) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

## 六、总结

响应式设计核心要点：

1. **viewport**：视口配置
2. **媒体查询**：@media
3. **断点设计**：合理划分
4. **移动优先**：从小到大
5. **视口单位**：vw/vh/rem

掌握这些，响应式布局 so easy！

---

**推荐阅读**：
- [MDN 响应式设计](https://developer.mozilla.org/en-US/docs/Web/Progressive_web_apps/Responsive/responsive_design_building_blocks)

**如果对你有帮助，欢迎点赞收藏！**
