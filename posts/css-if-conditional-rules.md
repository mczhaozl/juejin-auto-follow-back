# CSS 里的「if」：@media、@supports 与即将到来的 @when/@else

> 梳理 CSS 中实现「条件判断」的几种方式：媒体查询、特性查询，以及规范中的 @when/@else，并给出简单用法与兼容性说明。

---

## 一、CSS 有 if 吗？

CSS 没有像 JavaScript 那样的 `if (x) { }` 语句，但可以通过 **@ 规则** 做「条件式」样式：**满足某条件时才应用某段样式**。常见的有两类：**媒体查询（@media）** 和 **特性查询（@supports）**；规范里还有正在推进的 **@when / @else**，写法更接近「if-else」，但目前浏览器尚未普遍支持。下面按「能用 today」和「即将到来」分开说。

---

## 二、@media：按视口/设备「if」

**@media** 用来根据**媒体类型与媒体特征**（如视口宽度、横竖屏、分辨率）决定是否应用样式，相当于「**如果**屏幕满足某条件，**就**用这段 CSS」。

```css
/* 视口宽度 ≥ 768px 时用栅格布局 */
@media (min-width: 768px) {
  .grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
  }
}

/* 横屏时调整内边距 */
@media (orientation: landscape) {
  .panel {
    padding: 2rem;
  }
}
```

**常见条件**：`min-width` / `max-width`、`min-height`、`orientation`、`prefers-color-scheme`（深色/浅色）、`prefers-reduced-motion` 等。多条件用 **and** 连接；需要「或」时写多个 `@media` 或在一个规则里用逗号。**兼容性**：现代浏览器均支持，是响应式布局的基础。

---

## 三、@supports：按浏览器能力「if」

**@supports** 是**特性查询**：**如果**浏览器支持某 CSS 属性或语法，**就**应用这段样式；不支持则跳过。适合做渐进增强（先写基础样式，再在支持新特性的浏览器里增强）。

```css
/* 支持 Grid 时用 Grid 布局 */
@supports (display: grid) {
  .container {
    display: grid;
    gap: 1rem;
  }
}

/* 不支持时回退 */
@supports not (display: grid) {
  .container {
    display: flex;
    flex-wrap: wrap;
  }
}

/* 同时支持多个特性时 */
@supports (display: grid) and (gap: 1rem) {
  .container {
    display: grid;
    gap: 1rem;
  }
}
```

**逻辑**：`@supports (条件)`、`not`、`and`、`or`；还可检测**选择器**，如 `@supports selector(:has(a))`。**兼容性**：主流浏览器早已支持，可放心用。

---

## 四、@when / @else：规范里的「if-else」（即将到来）

**@when** 和 **@else** 是 [CSS Conditional Rules Level 5](https://www.w3.org/TR/css-conditional-5/) 中的新规则，用来**统一写条件**：把媒体条件、特性支持等写进同一套「when-else」链里，语义更接近「if-else if-else」，减少多层 @media 嵌套。

**示例（语法以最终规范为准）**：

```css
@when media(min-width: 800px) {
  .sidebar { width: 300px; }
}
@else media(min-width: 600px) {
  .sidebar { width: 240px; }
}
@else {
  .sidebar { width: 100%; }
}
```

还可组合 **media** 与 **supports**：

```css
@when media(min-width: 1024px) and supports(display: grid) {
  .layout { display: grid; }
}
@else {
  .layout { display: block; }
}
```

**现状**：截至 2024–2025 年，**主流浏览器尚未支持** @when/@else，目前只能在支持该规范的实验环境或未来版本中使用。写新项目时仍以 **@media + @supports** 为主；等 @when/@else 普及后，再考虑重构为更简洁的条件链。

---

## 五、对比与使用建议

| 方式        | 作用           | 兼容性     | 典型场景               |
|-------------|----------------|------------|------------------------|
| **@media**  | 视口/设备条件  | 全面支持   | 响应式、深色模式、动效偏好 |
| **@supports** | 浏览器能力条件 | 全面支持   | 渐进增强、Grid/Flex 回退   |
| **@when/@else** | 统一条件链     | 尚未支持   | 未来多条件、互斥分支     |

**建议**：  
- 需要「根据屏幕大小/横竖屏/主题」切换样式 → 用 **@media**。  
- 需要「根据是否支持某 CSS 特性」切换样式 → 用 **@supports**。  
- 两者可以组合：先 `@media` 再在块内写 `@supports`，或反过来。  
- **@when/@else** 先了解语法即可，等 Can I Use 显示普遍支持后再在实际项目中使用。

---

## 六、小结

- **CSS 没有字面意义的 if**，但用 **@media**（媒体条件）和 **@supports**（特性条件）可以实现「满足条件才应用样式」。
- **@media**：按视口宽度、横竖屏、`prefers-*` 等写响应式与偏好适配。  
- **@supports**：按浏览器是否支持某属性/选择器写渐进增强与回退。  
- **@when/@else**：规范中的统一条件语法，可读性更好，目前浏览器未支持，可关注 [CSS Conditional Level 5](https://www.w3.org/TR/css-conditional-5/) 与 Can I Use 的更新。

若对你有用，欢迎点赞、收藏；你若有基于 @supports 或 @media 的实战写法，也欢迎在评论区分享。
