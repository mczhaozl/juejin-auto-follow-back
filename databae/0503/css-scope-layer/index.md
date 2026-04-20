# CSS @scope 与 @layer 完全指南

## 一、@layer 概述

### 1.1 什么是 @layer

声明式管理 CSS 层级，无需提高选择器优先级。

### 1.2 基础使用

```css
@layer base, components, utilities;

@layer base {
  h1 {
    font-size: 2rem;
  }
}

@layer components {
  .card {
    padding: 1rem;
  }
}

@layer utilities {
  .text-red {
    color: red;
  }
}
```

---

## 二、@layer 优先级

```css
@layer base, theme, components;

/* 后声明的层优先级更高 */
@layer base {
  button {
    background: blue;
  }
}

@layer components {
  button {
    background: green;
  }
}

@layer theme {
  button {
    background: red;
  }
}

/* 非层样式最高优先级 */
button {
  background: purple !important;
}
```

---

## 三、嵌套 @layer

```css
@layer framework {
  @layer base {
    /* ... */
  }
  
  @layer components {
    /* ... */
  }
}

@layer app {
  /* ... */
}

/* 完整优先级：framework.base < framework.components < app */
```

---

## 四、@scope 概述

### 4.1 什么是 @scope

将样式限定在 DOM 子树内的新功能。

### 4.2 基础用法

```css
@scope (.card) {
  h2 {
    color: blue;
  }
  
  p {
    margin: 0.5rem;
  }
}

/* 只在 .card 内生效 */
```

---

## 五、@scope 边界

```css
@scope (.card) to (.card-content) {
  /* 仅在 .card 和 .card-content 之间生效 */
  img {
    border-radius: 8px;
  }
}

/* 结构
.card
  img (匹配)
  .card-content
    img (不匹配)
*/
```

---

## 六、@scope 与 @layer 组合

```css
@layer components {
  @scope (.card) {
    h2 {
      color: blue;
    }
  }
}

@layer theme {
  @scope (.card) {
    h2 {
      color: red;
    }
  }
}
```

---

## 七、实战：组件样式

```css
/* 定义层顺序 */
@layer reset, base, components, utilities;

@layer reset {
  * {
    box-sizing: border-box;
  }
}

@layer base {
  body {
    font-family: system-ui;
  }
}

@layer components {
  @scope (.button) {
    :scope {
      padding: 0.5rem 1rem;
      background: blue;
      color: white;
    }
    
    :scope:hover {
      background: darkblue;
    }
    
    .icon {
      margin-right: 0.5rem;
    }
  }
}

@layer utilities {
  .text-center {
    text-align: center;
  }
}
```

---

## 八、最佳实践

- 合理规划层顺序
- 使用 @scope 组织组件样式
- 保持层声明简单
- 文档化层用途

---

## 总结

@layer 和 @scope 让 CSS 管理更加清晰，@layer 解决优先级问题，@scope 解决作用域问题。
