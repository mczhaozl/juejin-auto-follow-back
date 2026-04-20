# CSS Container Queries 完全指南

## 一、Container Queries 概述

### 1.1 什么是容器查询

根据容器的尺寸而不是视口尺寸来调整样式。

### 1.2 对比媒体查询

```css
/* 媒体查询 - 视口 */
@media (min-width: 600px) {
  .card { ... }
}

/* 容器查询 - 容器 */
@container (min-width: 600px) {
  .card { ... }
}
```

---

## 二、基础用法

### 2.1 定义容器

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

/* 简写 */
.card-container {
  container: card / inline-size;
}
```

### 2.2 使用容器查询

```css
@container card (min-width: 400px) {
  .card {
    display: flex;
    flex-direction: row;
  }
  
  .card-image {
    width