# CSS View Transitions API：实现原生级别的页面切换动效

> 告别复杂的 JavaScript 动效库，深度掌握 CSS View Transitions API，轻松实现跨页面的平滑转场与共享元素动画，让 Web 应用拥有原生 APP 般的流畅体验。

---

## 目录 (Outline)
- [一、 动效的「石器时代」：为什么 Web 页面转场一直很难？](#一-动效的石器时代为什么-web-页面转场一直很难)
- [二、 View Transitions API：浏览器原生的「幻灯片切换」](#二-view-transitions-api浏览器原生的幻灯片切换)
- [三、 核心机制：快照、树结构与伪元素布局](#三-核心机制快照树结构与伪元素布局)
- [四、 实战 1：单页应用 (SPA) 中的基础转场](#四-实战-1单页应用-spa-中的基础转场)
- [五、 实战 2：共享元素动画 (Hero Animation) 的实现](#五-实战-2共享元素动画-hero-animation-的实现)
- [六、 实战 3：多页应用 (MPA) 的跨页面转场（Chrome 126+）](#六-实战-3多页应用-mpa-的跨页面转场chrome-126)
- [七、 性能优化与渐进增强策略](#七-性能优化与渐进增强策略)
- [八、 总结：Web 动效的新标准](#八-总结web-动效的新标准)

---

## 一、 动效的「石器时代」：为什么 Web 页面转场一直很难？

### 1. 历史背景
在过去，要在 Web 上实现平滑的页面切换，开发者必须面对以下难题：
- **DOM 冲突**：新旧页面的 DOM 节点无法同时存在。
- **状态同步**：需要手动计算元素的位置、大小，并用绝对定位模拟位移。
- **性能开销**：大量 JavaScript 计算和频繁的 Reflow/Repaint 导致低端设备卡顿。

### 2. 标志性方案
- **初期**：使用 `jQuery.animate()` 强行改变 `opacity`。
- **中期**：`React Transition Group` 或 `Framer Motion`，通过克隆 DOM 节点并管理其生命周期来实现。

---

## 二、 View Transitions API：浏览器原生的「幻灯片切换」

View Transitions API 提供了一种全新的思路：**让浏览器负责截图并自动补间**。

### 核心优势
1. **开发者心智负担极低**：只需一行 `document.startViewTransition()`。
2. **真正的共享元素**：浏览器会自动识别具有相同 `view-transition-name` 的元素并进行平滑过渡。
3. **跨文档支持**：不仅支持 SPA，现在连传统的 MPA 也能实现无缝跳转。

---

## 三、 核心机制：快照、树结构与伪元素布局

当你调用 `document.startViewTransition(callback)` 时，浏览器会经历以下过程：

1. **旧快照**：截取当前页面的图像。
2. **执行回调**：运行 `callback`，更新 DOM 到新状态。
3. **新快照**：截取更新后的页面图像。
4. **伪元素渲染**：生成一个特殊的伪元素树：
   - `::view-transition`
     - `::view-transition-group(root)`
       - `::view-transition-image-pair(root)`
         - `::view-transition-old(root)`
         - `::view-transition-new(root)`

通过 CSS，你可以对这些伪元素应用任何动画效果。

---

## 四、 实战 1：单页应用 (SPA) 中的基础转场

### 基础用法
```javascript
function updatePage() {
  // 如果浏览器不支持，直接更新 DOM
  if (!document.startViewTransition) {
    renderNextPage();
    return;
  }

  // 开启原生转场
  document.startViewTransition(() => {
    renderNextPage(); // 在这个回调里修改 DOM
  });
}
```

### 自定义 CSS 动画
默认是淡入淡出，我们可以通过伪元素自定义：
```css
::view-transition-old(root) {
  animation: 0.4s cubic-bezier(0.4, 0, 0.2, 1) both fade-out,
             0.4s cubic-bezier(0.4, 0, 0.2, 1) both slide-to-left;
}

::view-transition-new(root) {
  animation: 0.4s cubic-bezier(0.4, 0, 0.2, 1) both fade-in,
             0.4s cubic-bezier(0.4, 0, 0.2, 1) both slide-from-right;
}
```

---

## 五、 实战 2：共享元素动画 (Hero Animation) 的实现

这是 View Transitions API 最强大的地方。假设你有一个列表页，点击图片跳转到详情页，图片需要平滑放大。

### 步骤
1. **在列表页指定名称**：
   ```css
   .list-item-img {
     view-transition-name: product-hero;
   }
   ```
2. **在详情页指定相同的名称**：
   ```css
   .detail-page-img {
     view-transition-name: product-hero;
   }
   ```
3. **执行转场**：
   浏览器会自动识别这两个元素是「同一个」，并自动计算位置、大小、甚至圆角的补间动画。

---

## 六、 实战 3：多页应用 (MPA) 的跨页面转场（Chrome 126+）

以前这需要 Service Worker 或复杂的预加载技术，现在只需要一行 CSS：

### 开启方式
在 HTML 的 `<head>` 中添加：
```css
@view-transition {
  navigation: auto;
}
```

### 跨页面共享元素
在 `a.html` 和 `b.html` 中，只要两个元素拥有相同的 `view-transition-name`，在跳转时就会触发共享元素动画。

---

## 七、 性能优化与渐进增强策略

### 1. 渐进增强
始终提供回退方案，确保在不支持该 API 的浏览器（如旧版 Safari）中功能正常。
```javascript
const transition = document.startViewTransition?.(updateDOM);
if (!transition) {
  updateDOM();
}
```

### 2. 避免大面积重绘
不要给过多的元素设置 `view-transition-name`，这会增加浏览器的内存负担。只对关键的视觉引导元素使用。

### 3. 动画性能
利用 `will-change` 和硬件加速，确保转场动画达到 60fps。

---

## 八、 总结：Web 动效的新标准

CSS View Transitions API 的出现，标志着 Web 动画从「手动模拟」进入了「声明式渲染」时代。它极大地降低了实现复杂交互的门槛，同时也为 Web 应用带来了前所未有的用户体验。

**建议：** 在你的下一个项目中尝试使用它，哪怕只是简单的页面切换，也能让用户感受到明显的品质提升。

---
> 关注我，深入前端底层原理，掌握最新 Web 技术。
