# CSS 嵌套规则（Nesting）：告别 Sass 的原生方案

> 原生 CSS 嵌套语法详解，与 Sass 对比及迁移建议

---

## 一、CSS 嵌套的意义

传统 CSS 需要重复写选择器：

```css
.card { }
.card .title { }
.card .content { }
.card .footer { }
```

CSS 嵌套让代码更简洁：

```css
.card {
  & .title { }
  & .content { }
  & .footer { }
}
```

---

## 二、基础语法

### 使用 & 符号

```css
.button {
  background: blue;
  
  &:hover {
    background: darkblue;
  }
  
  &.primary {
    background: green;
  }
  
  & .icon {
    margin-right: 8px;
  }
}
```

---

## 三、与 Sass 对比

| 特性 | CSS Nesting | Sass |
|------|------------|------|
| 浏览器支持 | 原生 | 需编译 |
| & 符号 | 必须 | 可选 |
| 性能 | 更好 | 依赖编译 |
| 功能 | 基础 | 更强大 |

---

## 四、浏览器支持

- Chrome 112+
- Safari 16.5+
- Firefox 117+

---

## 五、迁移建议

Sass 项目可以逐步迁移到原生 CSS 嵌套：

1. 新代码使用原生语法
2. 旧代码保持 Sass
3. 逐步替换

---

## 总结

CSS 原生嵌套是现代化的选择：

- 无需预处理器
- 性能更好
- 语法简洁
- 浏览器原生支持

在支持的浏览器中，推荐使用原生 CSS 嵌套。

如果这篇文章对你有帮助，欢迎点赞收藏！
