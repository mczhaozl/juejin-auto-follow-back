# Web Components 完全指南：从零构建可复用组件

Web Components 是一套原生 Web 标准，允许你创建可复用的自定义元素。本文将全面介绍 Web Components 的核心概念和实践技巧。

## 一、Web Components 概述

Web Components 由以下四个主要技术组成：

1. **Custom Elements（自定义元素）**：定义新的 HTML 元素
2. **Shadow DOM（影子 DOM）**：封装样式和结构
3. **HTML Templates（HTML 模板）**：定义可复用的 HTML 结构
4. **Slots（插槽）**：实现内容分发

### 为什么选择 Web Components？

- **原生支持**：无需框架，直接使用浏览器 API
- **跨框架兼容**：可以在 React、Vue、Angular 等框架中使用
- **封装性**：Shadow DOM 提供样式隔离
- **可复用性**：一次编写，到处使用
- **未来保障**：基于 Web 标准

## 二、Custom Elements（自定义元素）

### 1. 创建自定义元素

```javascript
class MyButton extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.render()
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        button {
          padding: 10px 20px;
          background: #1890ff;
          color: white;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        button:hover {
          background: #40a9ff;
        }
      </style>
      <button><slot></slot></button>
    `
  }
}

customElements.define('my-button', MyButton)
```

使用：

```html
<my-button>点击我</my-button>
```

### 2. 生命周期钩子

```javascript
class MyComponent extends HTMLElement {
  constructor() {
    super()
    console.log('元素被创建')
  }

  connectedCallback() {
    console.log('元素被添加到 DOM')
    this.render()
  }

  disconnectedCallback() {
    console.log('元素从 DOM 中移除')
  }

  adoptedCallback() {
    console.log('元素被移动到新文档')
  }

  static get observedAttributes() {
    return ['size', 'color']
  }

  attributeChangedCallback(name, oldValue, newValue) {
    console.log(`属性 ${name} 从 ${oldValue} 变为 ${newValue}`)
    this.render()
  }

  render() {
    this.innerHTML = `
      <div style="color: ${this.getAttribute('color') || 'black'}">
        <slot></slot>
      </div>
    `
  }
}

customElements.define('my-component', MyComponent)
```

### 3. 属性和 Props

```javascript
class UserCard extends HTMLElement {
  static get observedAttributes() {
    return ['name', 'avatar', 'email']
  }

  get name() {
    return this.getAttribute('name')
  }

  set name(value) {
    this.setAttribute('name', value)
  }

  get avatar() {
    return this.getAttribute('avatar')
  }

  set avatar(value) {
    this.setAttribute('avatar', value)
  }

  get email() {
    return this.getAttribute('email')
  }

  set email(value) {
    this.setAttribute('email', value)
  }

  connectedCallback() {
    this.attachShadow({ mode: 'open' })
    this.render()
  }

  attributeChangedCallback() {
    this.render()
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        .card {
          border: 1px solid #e0e0e0;
          border-radius: 8px;
          padding: 16px;
          max-width: 300px;
          text-align: center;
        }
        .avatar {
          width: 80px;
          height: 80px;
          border-radius: 50%;
          object-fit: cover;
        }
        .name {
          font-size: 18px;
          font-weight: bold;
          margin: 8px 0;
        }
        .email {
          color: #666;
          font-size: 14px;
        }
      </style>
      <div class="card">
        <img class="avatar" src="${this.avatar || 'https://via.placeholder.com/80'}" alt="avatar">
        <div class="name">${this.name || '未知用户'}</div>
        <div class="email">${this.email || ''}</div>
      </div>
    `
  }
}

customElements.define('user-card', UserCard)
```

使用：

```html
<user-card 
  name="张三" 
  email="zhangsan@example.com" 
  avatar="https://via.placeholder.com/80">
</user-card>
```

## 三、Shadow DOM（影子 DOM）

### 1. Shadow DOM 基础

```javascript
class ShadowComponent extends HTMLElement {
  constructor() {
    super()
    const shadow = this.attachShadow({ mode: 'open' })
    
    const div = document.createElement('div')
    div.textContent = '我在 Shadow DOM 中'
    
    const style = document.createElement('style')
    style.textContent = `
      div {
        color: blue;
        font-size: 20px;
      }
    `
    
    shadow.appendChild(style)
    shadow.appendChild(div)
  }
}

customElements.define('shadow-component', ShadowComponent)
```

### 2. Shadow DOM 模式

```javascript
// open 模式：外部可以访问 shadowRoot
class OpenShadow extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
  }
}

// closed 模式：外部无法访问 shadowRoot
class ClosedShadow extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'closed' })
  }
}
```

### 3. CSS 变量和样式穿透

```javascript
class StyledComponent extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          --primary-color: #1890ff;
          --font-size: 16px;
        }
        
        .content {
          color: var(--primary-color);
          font-size: var(--font-size);
        }
        
        ::slotted(*) {
          margin: 8px 0;
        }
        
        ::slotted(h2) {
          color: #333;
        }
      </style>
      <div class="content">
        <slot name="header"></slot>
        <slot></slot>
      </div>
    `
  }
}

customElements.define('styled-component', StyledComponent)
```

使用：

```html
<style>
  styled-component {
    --primary-color: #52c41a;
    --font-size: 18px;
  }
</style>

<styled-component>
  <h2 slot="header">标题</h2>
  <p>这是主要内容</p>
</styled-component>
```

## 四、HTML Templates（HTML 模板）

### 1. 使用 &lt;template&gt; 元素

```html
<template id="card-template">
  <style>
    .card {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 16px;
      margin: 8px;
    }
    .title {
      font-weight: bold;
      margin-bottom: 8px;
    }
  </style>
  <div class="card">
    <div class="title"></div>
    <div class="content"></div>
  </div>
</template>
```

```javascript
class CardComponent extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
  }

  connectedCallback() {
    const template = document.getElementById('card-template')
    const content = template.content.cloneNode(true)
    
    const title = content.querySelector('.title')
    title.textContent = this.getAttribute('title') || '标题'
    
    const contentEl = content.querySelector('.content')
    contentEl.textContent = this.getAttribute('content') || '内容'
    
    this.shadowRoot.appendChild(content)
  }
}

customElements.define('card-component', CardComponent)
```

### 2. 使用 &lt;slot&gt; 分发内容

```javascript
class LayoutComponent extends HTMLElement {
  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
    this.shadowRoot.innerHTML = `
      <style>
        .container {
          display: flex;
          gap: 16px;
        }
        .sidebar {
          width: 200px;
          background: #f5f5f5;
          padding: 16px;
        }
        .main {
          flex: 1;
          padding: 16px;
        }
      </style>
      <div class="container">
        <aside class="sidebar">
          <slot name="sidebar"></slot>
        </aside>
        <main class="main">
          <slot></slot>
        </main>
      </div>
    `
  }
}

customElements.define('layout-component', LayoutComponent)
```

使用：

```html
<layout-component>
  <nav slot="sidebar">
    <ul>
      <li><a href="#">首页</a></li>
      <li><a href="#">关于</a></li>
      <li><a href="#">联系</a></li>
    </ul>
  </nav>
  <article>
    <h1>主要内容</h1>
    <p>这是页面的主要内容区域。</p>
  </article>
</layout-component>
```

## 五、实战案例

### 1. 完整的计数器组件

```javascript
class Counter extends HTMLElement {
  static get observedAttributes() {
    return ['count']
  }

  get count() {
    return parseInt(this.getAttribute('count')) || 0
  }

  set count(value) {
    this.setAttribute('count', value)
  }

  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
  }

  connectedCallback() {
    this.render()
    this.bindEvents()
  }

  attributeChangedCallback() {
    this.render()
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        .counter {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          border: 1px solid #d9d9d9;
          border-radius: 4px;
          padding: 4px;
        }
        button {
          width: 32px;
          height: 32px;
          border: none;
          border-radius: 4px;
          background: #f0f0f0;
          cursor: pointer;
          font-size: 18px;
        }
        button:hover {
          background: #e6e6e6;
        }
        .count {
          min-width: 40px;
          text-align: center;
          font-size: 18px;
          font-weight: bold;
        }
      </style>
      <div class="counter">
        <button class="decrement">-</button>
        <span class="count">${this.count}</span>
        <button class="increment">+</button>
      </div>
    `
  }

  bindEvents() {
    const shadow = this.shadowRoot
    shadow.querySelector('.increment').addEventListener('click', () => {
      this.count++
      this.dispatchEvent(new CustomEvent('change', { detail: { count: this.count } }))
    })
    shadow.querySelector('.decrement').addEventListener('click', () => {
      this.count--
      this.dispatchEvent(new CustomEvent('change', { detail: { count: this.count } }))
    })
  }
}

customElements.define('my-counter', Counter)
```

使用：

```html
<my-counter count="0"></my-counter>

<script>
  const counter = document.querySelector('my-counter')
  counter.addEventListener('change', (e) => {
    console.log('计数器变化:', e.detail.count)
  })
</script>
```

### 2. 数据表格组件

```javascript
class DataTable extends HTMLElement {
  static get observedAttributes() {
    return ['data', 'columns']
  }

  get data() {
    try {
      return JSON.parse(this.getAttribute('data')) || []
    } catch {
      return []
    }
  }

  set data(value) {
    this.setAttribute('data', JSON.stringify(value))
  }

  get columns() {
    try {
      return JSON.parse(this.getAttribute('columns')) || []
    } catch {
      return []
    }
  }

  set columns(value) {
    this.setAttribute('columns', JSON.stringify(value))
  }

  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
  }

  connectedCallback() {
    this.render()
  }

  attributeChangedCallback() {
    this.render()
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        table {
          width: 100%;
          border-collapse: collapse;
          font-family: Arial, sans-serif;
        }
        th, td {
          border: 1px solid #e0e0e0;
          padding: 12px;
          text-align: left;
        }
        th {
          background: #f5f5f5;
          font-weight: bold;
        }
        tr:hover {
          background: #fafafa;
        }
      </style>
      <table>
        <thead>
          <tr>
            ${this.columns.map(col => `<th>${col.title}</th>`).join('')}
          </tr>
        </thead>
        <tbody>
          ${this.data.map(row => `
            <tr>
              ${this.columns.map(col => `<td>${row[col.key] || ''}</td>`).join('')}
            </tr>
          `).join('')}
        </tbody>
      </table>
    `
  }
}

customElements.define('data-table', DataTable)
```

使用：

```html
<data-table id="my-table"></data-table>

<script>
  const table = document.getElementById('my-table')
  table.columns = [
    { key: 'id', title: 'ID' },
    { key: 'name', title: '姓名' },
    { key: 'age', title: '年龄' },
    { key: 'email', title: '邮箱' }
  ]
  table.data = [
    { id: 1, name: '张三', age: 28, email: 'zhangsan@example.com' },
    { id: 2, name: '李四', age: 32, email: 'lisi@example.com' },
    { id: 3, name: '王五', age: 25, email: 'wangwu@example.com' }
  ]
</script>
```

### 3. 模态对话框组件

```javascript
class ModalDialog extends HTMLElement {
  static get observedAttributes() {
    return ['open', 'title']
  }

  get open() {
    return this.hasAttribute('open')
  }

  set open(value) {
    if (value) {
      this.setAttribute('open', '')
    } else {
      this.removeAttribute('open')
    }
  }

  get title() {
    return this.getAttribute('title') || ''
  }

  set title(value) {
    this.setAttribute('title', value)
  }

  constructor() {
    super()
    this.attachShadow({ mode: 'open' })
  }

  connectedCallback() {
    this.render()
    this.bindEvents()
  }

  attributeChangedCallback() {
    this.render()
    this.bindEvents()
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: ${this.open ? 'block' : 'none'};
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 1000;
        }
        .overlay {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
        }
        .modal {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          background: white;
          border-radius: 8px;
          min-width: 400px;
          max-width: 90%;
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 16px 24px;
          border-bottom: 1px solid #e0e0e0;
        }
        .title {
          font-size: 18px;
          font-weight: bold;
        }
        .close-btn {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
          color: #999;
        }
        .close-btn:hover {
          color: #333;
        }
        .body {
          padding: 24px;
        }
        .footer {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          padding: 16px 24px;
          border-top: 1px solid #e0e0e0;
        }
        .btn {
          padding: 8px 16px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
        }
        .btn-primary {
          background: #1890ff;
          color: white;
        }
        .btn-primary:hover {
          background: #40a9ff;
        }
        .btn-default {
          background: #f0f0f0;
        }
        .btn-default:hover {
          background: #e6e6e6;
        }
      </style>
      <div class="overlay"></div>
      <div class="modal">
        <div class="header">
          <span class="title">${this.title}</span>
          <button class="close-btn">&times;</button>
        </div>
        <div class="body">
          <slot></slot>
        </div>
        <div class="footer">
          <slot name="footer"></slot>
        </div>
      </div>
    `
  }

  bindEvents() {
    const shadow = this.shadowRoot
    const closeBtn = shadow.querySelector('.close-btn')
    const overlay = shadow.querySelector('.overlay')

    closeBtn?.addEventListener('click', () => this.close())
    overlay?.addEventListener('click', () => this.close())
  }

  open() {
    this.open = true
    this.dispatchEvent(new CustomEvent('open'))
  }

  close() {
    this.open = false
    this.dispatchEvent(new CustomEvent('close'))
  }
}

customElements.define('modal-dialog', ModalDialog)
```

使用：

```html
<button onclick="document.getElementById('my-modal').open = true">打开对话框</button>

<modal-dialog id="my-modal" title="确认">
  <p>你确定要执行此操作吗？</p>
  <div slot="footer">
    <button class="btn btn-default" onclick="document.getElementById('my-modal').open = false">取消</button>
    <button class="btn btn-primary" onclick="confirm()">确定</button>
  </div>
</modal-dialog>

<script>
  function confirm() {
    console.log('确认操作')
    document.getElementById('my-modal').open = false
  }
</script>
```

## 六、与框架集成

### 1. 在 React 中使用 Web Components

```jsx
import React, { useRef, useEffect } from 'react'

function WebComponentWrapper() {
  const counterRef = useRef(null)

  useEffect(() => {
    const counter = counterRef.current
    const handleChange = (e) => {
      console.log('计数器值:', e.detail.count)
    }
    counter.addEventListener('change', handleChange)
    return () => counter.removeEventListener('change', handleChange)
  }, [])

  return (
    <div>
      <h2>React 中使用 Web Components</h2>
      <my-counter ref={counterRef} count="0"></my-counter>
    </div>
  )
}
```

### 2. 在 Vue 中使用 Web Components

```vue
<template>
  <div>
    <h2>Vue 中使用 Web Components</h2>
    <my-counter :count="count" @change="handleChange"></my-counter>
  </div>
</template>

<script>
export default {
  data() {
    return {
      count: 0
    }
  },
  methods: {
    handleChange(e) {
      console.log('计数器值:', e.detail.count)
      this.count = e.detail.count
    }
  }
}
</script>
```

## 七、最佳实践

### 1. 命名规范

```javascript
// 使用短横线命名
customElements.define('my-component', MyComponent)

// 避免单个单词
customElements.define('user-profile', UserProfile)
```

### 2. 属性设计

```javascript
class BestPracticeComponent extends HTMLElement {
  static get observedAttributes() {
    return ['title', 'disabled']
  }

  get title() {
    return this.getAttribute('title') || ''
  }

  set title(value) {
    this.setAttribute('title', value)
  }

  get disabled() {
    return this.hasAttribute('disabled')
  }

  set disabled(value) {
    if (value) {
      this.setAttribute('disabled', '')
    } else {
      this.removeAttribute('disabled')
    }
  }
}
```

### 3. 事件设计

```javascript
class EventComponent extends HTMLElement {
  connectedCallback() {
    this.addEventListener('click', () => {
      this.dispatchEvent(new CustomEvent('my-event', {
        bubbles: true,
        composed: true,
        detail: { data: 'some data' }
      }))
    })
  }
}
```

## 八、总结

Web Components 提供了一套强大的原生 API，让你可以创建可复用、封装良好的组件。通过本文的介绍，你应该已经掌握了：

1. Custom Elements 的创建和使用
2. Shadow DOM 的样式隔离
3. HTML Templates 和 Slots 的内容分发
4. 完整的实战案例
5. 与主流框架的集成方法
6. 最佳实践和设计原则

Web Components 是构建现代 Web 应用的重要工具，值得深入学习和实践。

## 参考资料

- [MDN Web Components](https://developer.mozilla.org/zh-CN/docs/Web/Web_Components)
- [Web Components 官网](https://www.webcomponents.org/)
- [Custom Elements Everywhere](https://custom-elements-everywhere.com/)
