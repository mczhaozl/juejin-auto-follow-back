# Web Components 深度解析：从基础到实战

Web Components 是原生的组件化方案。本文将带你从基础到高级，全面掌握 Web Components。

## 一、Web Components 基础

### 1. 核心技术

```
Web Components 由三部分组成：
- Custom Elements: 自定义 HTML 元素
- Shadow DOM: 封装 DOM 和样式
- HTML Templates: 可复用的 HTML 模板
```

### 2. 第一个自定义元素

```html
<!DOCTYPE html>
<html>
<head>
  <title>Web Components</title>
</head>
<body>
  <my-button text="Click me"></my-button>

  <script>
    class MyButton extends HTMLElement {
      constructor() {
        super();
        this.attachShadow({ mode: 'open' });
      }
      
      connectedCallback() {
        const text = this.getAttribute('text') || 'Button';
        this.shadowRoot.innerHTML = `
          <style>
            button {
              padding: 10px 20px;
              background: #007bff;
              color: white;
              border: none;
              border-radius: 4px;
              cursor: pointer;
            }
            button:hover {
              background: #0056b3;
            }
          </style>
          <button>${text}</button>
        `;
      }
    }
    
    customElements.define('my-button', MyButton);
  </script>
</body>
</html>
```

## 二、Custom Elements

### 1. 生命周期回调

```javascript
class MyElement extends HTMLElement {
  constructor() {
    super();
    console.log('Constructor called');
  }
  
  connectedCallback() {
    console.log('Element added to DOM');
    this.render();
  }
  
  disconnectedCallback() {
    console.log('Element removed from DOM');
  }
  
  adoptedCallback() {
    console.log('Element moved to new document');
  }
  
  static get observedAttributes() {
    return ['text', 'color'];
  }
  
  attributeChangedCallback(name, oldValue, newValue) {
    console.log(`Attribute ${name} changed: ${oldValue} → ${newValue}`);
    if (oldValue !== newValue) {
      this.render();
    }
  }
  
  render() {
    // 渲染逻辑
  }
}

customElements.define('my-element', MyElement);
```

### 2. 属性和 Props

```javascript
class UserCard extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
  }
  
  static get observedAttributes() {
    return ['name', 'email', 'avatar'];
  }
  
  get name() {
    return this.getAttribute('name');
  }
  
  set name(value) {
    this.setAttribute('name', value);
  }
  
  get email() {
    return this.getAttribute('email');
  }
  
  set email(value) {
    this.setAttribute('email', value);
  }
  
  get avatar() {
    return this.getAttribute('avatar');
  }
  
  set avatar(value) {
    this.setAttribute('avatar', value);
  }
  
  attributeChangedCallback() {
    this.render();
  }
  
  connectedCallback() {
    this.render();
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
          width: 100px;
          height: 100px;
          border-radius: 50%;
          object-fit: cover;
        }
        .name {
          font-weight: bold;
          margin: 8px 0;
        }
        .email {
          color: #666;
          font-size: 14px;
        }
      </style>
      <div class="card">
        <img class="avatar" src="${this.avatar || 'https://via.placeholder.com/100'}" alt="avatar">
        <div class="name">${this.name || 'Anonymous'}</div>
        <div class="email">${this.email || 'no-email@example.com'}</div>
      </div>
    `;
  }
}

customElements.define('user-card', UserCard);
```

```html
<user-card 
  name="John Doe" 
  email="john@example.com" 
  avatar="https://example.com/avatar.jpg">
</user-card>

<script>
  const card = document.querySelector('user-card');
  card.name = 'Jane Smith';
</script>
```

## 三、Shadow DOM

### 1. Shadow DOM 模式

```javascript
class ShadowElement extends HTMLElement {
  constructor() {
    super();
    
    // Open: 外部可以访问 shadowRoot
    this.attachShadow({ mode: 'open' });
    
    // Closed: 外部无法访问 shadowRoot
    // this.attachShadow({ mode: 'closed' });
  }
}

const el = document.querySelector('shadow-element');
console.log(el.shadowRoot);  // open 模式下可以访问
```

### 2. 样式封装

```html
<template id="button-template">
  <style>
    :host {
      display: inline-block;
    }
    
    :host(:hover) button {
      background: #0056b3;
    }
    
    :host(.primary) button {
      background: #007bff;
    }
    
    :host(.danger) button {
      background: #dc3545;
    }
    
    ::slotted(span) {
      color: #666;
      font-size: 12px;
    }
    
    button {
      padding: 10px 20px;
      border: none;
      border-radius: 4px;
      color: white;
      cursor: pointer;
    }
  </style>
  <button>
    <slot></slot>
    <slot name="suffix"></slot>
  </button>
</template>

<script>
  class StyledButton extends HTMLElement {
    constructor() {
      super();
      const template = document.getElementById('button-template');
      const shadow = this.attachShadow({ mode: 'open' });
      shadow.appendChild(template.content.cloneNode(true));
    }
  }
  
  customElements.define('styled-button', StyledButton);
</script>

<styled-button class="primary">
  Click Me
  <span slot="suffix"> →</span>
</styled-button>
```

### 3. 插槽（Slots）

```html
<template id="card-template">
  <style>
    .card {
      border: 1px solid #e0e0e0;
      border-radius: 8px;
      padding: 16px;
    }
    .header {
      font-weight: bold;
      margin-bottom: 8px;
    }
    .content {
      color: #333;
    }
    .footer {
      margin-top: 16px;
      padding-top: 8px;
      border-top: 1px solid #e0e0e0;
    }
  </style>
  <div class="card">
    <div class="header">
      <slot name="header">Default Header</slot>
    </div>
    <div class="content">
      <slot>Default Content</slot>
    </div>
    <div class="footer">
      <slot name="footer"></slot>
    </div>
  </div>
</template>

<my-card>
  <span slot="header">Custom Header</span>
  This is the main content
  <span slot="footer">Custom Footer</span>
</my-card>
```

## 四、HTML Templates

### 1. 基础模板

```html
<template id="todo-template">
  <style>
    .todo {
      display: flex;
      align-items: center;
      padding: 8px;
      border-bottom: 1px solid #e0e0e0;
    }
    .todo-text {
      flex: 1;
    }
    .todo.completed .todo-text {
      text-decoration: line-through;
      color: #999;
    }
    button {
      margin-left: 8px;
    }
  </style>
  <div class="todo">
    <input type="checkbox" class="toggle">
    <span class="todo-text"></span>
    <button class="delete">Delete</button>
  </div>
</template>

<div id="todo-list"></div>

<script>
  const template = document.getElementById('todo-template');
  const todoList = document.getElementById('todo-list');
  
  function addTodo(text) {
    const clone = template.content.cloneNode(true);
    const todo = clone.querySelector('.todo');
    todo.querySelector('.todo-text').textContent = text;
    
    todo.querySelector('.toggle').addEventListener('change', (e) => {
      todo.classList.toggle('completed', e.target.checked);
    });
    
    todo.querySelector('.delete').addEventListener('click', () => {
      todo.remove();
    });
    
    todoList.appendChild(clone);
  }
  
  addTodo('Learn Web Components');
  addTodo('Build something cool');
</script>
```

### 2. 动态模板

```javascript
class DynamicList extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    this._items = [];
  }
  
  set items(value) {
    this._items = value;
    this.render();
  }
  
  get items() {
    return this._items;
  }
  
  render() {
    this.shadowRoot.innerHTML = `
      <style>
        ul {
          list-style: none;
          padding: 0;
        }
        li {
          padding: 8px;
          border-bottom: 1px solid #e0e0e0;
        }
      </style>
      <ul>
        ${this._items.map(item => `<li>${item}</li>`).join('')}
      </ul>
    `;
  }
}

customElements.define('dynamic-list', DynamicList);
```

## 五、实战组件库

### 1. 模态框（Modal）

```html
<template id="modal-template">
  <style>
    :host {
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      z-index: 1000;
    }
    
    :host(.open) {
      display: block;
    }
    
    .backdrop {
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
      padding: 24px;
      min-width: 300px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    }
    
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }
    
    .title {
      font-size: 18px;
      font-weight: bold;
    }
    
    .close {
      background: none;
      border: none;
      font-size: 24px;
      cursor: pointer;
    }
    
    .footer {
      margin-top: 16px;
      display: flex;
      justify-content: flex-end;
      gap: 8px;
    }
    
    button {
      padding: 8px 16px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
    }
    
    .btn-cancel {
      background: #e0e0e0;
    }
    
    .btn-confirm {
      background: #007bff;
      color: white;
    }
  </style>
  <div class="backdrop"></div>
  <div class="modal">
    <div class="header">
      <span class="title"><slot name="title">Modal</slot></span>
      <button class="close">&times;</button>
    </div>
    <div class="content">
      <slot></slot>
    </div>
    <div class="footer">
      <slot name="footer">
        <button class="btn-cancel">Cancel</button>
        <button class="btn-confirm">Confirm</button>
      </slot>
    </div>
  </div>
</template>

<script>
  class MyModal extends HTMLElement {
    constructor() {
      super();
      const template = document.getElementById('modal-template');
      const shadow = this.attachShadow({ mode: 'open' });
      shadow.appendChild(template.content.cloneNode(true));
      
      this.shadowRoot.querySelector('.close').addEventListener('click', () => this.close());
      this.shadowRoot.querySelector('.backdrop').addEventListener('click', () => this.close());
    }
    
    open() {
      this.classList.add('open');
      this.dispatchEvent(new CustomEvent('open'));
    }
    
    close() {
      this.classList.remove('open');
      this.dispatchEvent(new CustomEvent('close'));
    }
  }
  
  customElements.define('my-modal', MyModal);
</script>

<my-modal id="modal">
  <span slot="title">Confirm Delete</span>
  Are you sure you want to delete this item?
</my-modal>

<button onclick="document.getElementById('modal').open()">Open Modal</button>
```

### 2. 轮播图（Carousel）

```html
<template id="carousel-template">
  <style>
    :host {
      display: block;
      position: relative;
      width: 100%;
      max-width: 600px;
      overflow: hidden;
    }
    
    .slides {
      display: flex;
      transition: transform 0.3s ease;
    }
    
    .slide {
      min-width: 100%;
    }
    
    .slide img {
      width: 100%;
      height: 300px;
      object-fit: cover;
    }
    
    .controls {
      position: absolute;
      top: 50%;
      width: 100%;
      display: flex;
      justify-content: space-between;
      transform: translateY(-50%);
    }
    
    .prev, .next {
      background: rgba(0, 0, 0, 0.5);
      color: white;
      border: none;
      padding: 16px;
      cursor: pointer;
      font-size: 24px;
    }
    
    .dots {
      position: absolute;
      bottom: 16px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 8px;
    }
    
    .dot {
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.5);
      border: none;
      cursor: pointer;
    }
    
    .dot.active {
      background: white;
    }
  </style>
  <div class="slides">
    <slot></slot>
  </div>
  <div class="controls">
    <button class="prev">&lt;</button>
    <button class="next">&gt;</button>
  </div>
  <div class="dots"></div>
</template>

<div class="slide"><img src="slide1.jpg"></div>
<div class="slide"><img src="slide2.jpg"></div>
<div class="slide"><img src="slide3.jpg"></div>

<script>
  class MyCarousel extends HTMLElement {
    constructor() {
      super();
      const template = document.getElementById('carousel-template');
      const shadow = this.attachShadow({ mode: 'open' });
      shadow.appendChild(template.content.cloneNode(true));
      
      this.currentIndex = 0;
      this.slides = [];
      
      this.slidesContainer = shadow.querySelector('.slides');
      this.prevBtn = shadow.querySelector('.prev');
      this.nextBtn = shadow.querySelector('.next');
      this.dotsContainer = shadow.querySelector('.dots');
      
      this.prevBtn.addEventListener('click', () => this.prev());
      this.nextBtn.addEventListener('click', () => this.next());
    }
    
    connectedCallback() {
      this.slides = Array.from(this.querySelectorAll('.slide'));
      this.renderDots();
      this.updateCarousel();
      
      setInterval(() => this.next(), 3000);
    }
    
    renderDots() {
      this.dotsContainer.innerHTML = '';
      this.slides.forEach((_, index) => {
        const dot = document.createElement('button');
        dot.className = 'dot' + (index === 0 ? ' active' : '');
        dot.addEventListener('click', () => this.goTo(index));
        this.dotsContainer.appendChild(dot);
      });
    }
    
    updateCarousel() {
      this.slidesContainer.style.transform = `translateX(-${this.currentIndex * 100}%)`;
      
      const dots = this.dotsContainer.querySelectorAll('.dot');
      dots.forEach((dot, index) => {
        dot.classList.toggle('active', index === this.currentIndex);
      });
    }
    
    next() {
      this.currentIndex = (this.currentIndex + 1) % this.slides.length;
      this.updateCarousel();
    }
    
    prev() {
      this.currentIndex = (this.currentIndex - 1 + this.slides.length) % this.slides.length;
      this.updateCarousel();
    }
    
    goTo(index) {
      this.currentIndex = index;
      this.updateCarousel();
    }
  }
  
  customElements.define('my-carousel', MyCarousel);
</script>

<my-carousel>
  <div class="slide"><img src="slide1.jpg" alt="Slide 1"></div>
  <div class="slide"><img src="slide2.jpg" alt="Slide 2"></div>
  <div class="slide"><img src="slide3.jpg" alt="Slide 3"></div>
</my-carousel>
```

## 六、最佳实践

1. 使用自定义元素封装逻辑
2. 利用 Shadow DOM 封装样式
3. 正确使用生命周期回调
4. 实现响应式属性
5. 使用插槽提高灵活性
6. 模板复用
7. 事件通信
8. 可访问性
9. 性能优化
10. 测试

## 七、总结

Web Components 核心要点：
- Custom Elements（自定义元素）
- Shadow DOM（样式封装）
- HTML Templates（模板复用）
- 生命周期回调
- 属性和 Props
- 插槽
- 实战组件（Modal、Carousel）

开始用 Web Components 构建你的组件库吧！
