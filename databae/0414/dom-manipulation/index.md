# DOM 操作完全指南：高效操作与性能优化

> 深入讲解 DOM 操作，包括选择器、DOM 树操作、事件委托，以及重绘回流优化和虚拟 DOM 原理。

## 一、选择元素

### 1.1 选择单个元素

```javascript
const element = document.querySelector('.container');
const id = document.getElementById('header');
```

### 1.2 选择多个元素

```javascript
const elements = document.querySelectorAll('.item');
elements.forEach(el => console.log(el));
```

### 1.3 关系查找

```javascript
const parent = element.parentElement;
const children = element.children;
const firstChild = element.firstElementChild;
const nextSibling = element.nextElementSibling;
```

## 二、DOM 操作

### 2.1 创建元素

```javascript
const div = document.createElement('div');
div.textContent = 'Hello';
div.innerHTML = '<span>World</span>';
```

### 2.2 插入元素

```javascript
parent.appendChild(newElement);
parent.insertBefore(newElement, reference);

parent.append(newElement1, newElement2);
parent.prepend(newElement);
```

### 2.3 删除元素

```javascript
element.remove();
parent.removeChild(element);
```

### 2.4 修改元素

```javascript
element.setAttribute('class', 'active');
element.classList.add('active');
element.style.color = 'red';

element.dataset.id = '123';
```

## 三、事件

### 3.1 事件绑定

```javascript
element.addEventListener('click', (e) => {
  console.log(e.target);
});

element.onclick = () => {};
```

### 3.2 事件委托

```javascript
// 不好的方式
items.forEach(item => {
  item.addEventListener('click', handleClick);
});

// 好的方式
container.addEventListener('click', (e) => {
  const item = e.target.closest('.item');
  if (item) handleClick(e);
});
```

## 四、性能优化

### 4.1 减少回流

```javascript
// 不好 - 多次回流
element.style.width = '100px';
element.style.height = '100px';
element.style.color = 'red';

// 好 - 一次性修改
element.style.cssText = 'width: 100px; height: 100px; color: red;';
// 或使用 class
element.classList.add('active');
```

### 4.2 文档片段

```javascript
const fragment = document.createDocumentFragment();

for (let i = 0; i < 100; i++) {
  const li = document.createElement('li');
  li.textContent = i;
  fragment.appendChild(li);
}

ul.appendChild(fragment); // 只触发一次回流
```

### 4.3 requestAnimationFrame

```javascript
function animate() {
  element.style.transform = `translateX(${position}px)`;
  position += 1;
  requestAnimationFrame(animate);
}
```

## 五、总结

DOM 操作核心要点：

1. **选择器**：querySelector
2. **增删改**：DOM API
3. **事件委托**：性能优化
4. **减少回流**：cssText/class
5. **DocumentFragment**：批量插入

掌握这些，DOM 操作更高效！

---

**推荐阅读**：
- [MDN DOM](https://developer.mozilla.org/en-US/docs/Web/API/Document_Object_Model)

**如果对你有帮助，欢迎点赞收藏！**
