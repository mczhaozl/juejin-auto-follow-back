# JavaScript 性能优化完全指南：从原理到实战技巧

## 一、性能测量

```javascript
// Performance API
const start = performance.now();
// ... code ...
const end = performance.now();
console.log(`Took ${end - start}ms`);

// console.time
console.time('Loop');
for (let i = 0; i < 1000000; i++) {}
console.timeEnd('Loop');
```

---

## 二、DOM 操作优化

```javascript
// 不好：多次重排
for (let i = 0; i < 100; i++) {
  document.body.innerHTML += `<div>${i}</div>`;
}

// 好：文档片段
const fragment = document.createDocumentFragment();
for (let i = 0; i < 100; i++) {
  const div = document.createElement('div');
  div.textContent = i;
  fragment.appendChild(div);
}
document.body.appendChild(fragment);
```

---

## 三、事件委托

```javascript
// 不好：多个监听器
document.querySelectorAll('li').forEach(li => {
  li.addEventListener('click', handleClick);
});

// 好：事件委托
document.querySelector('ul').addEventListener('click', (e) => {
  if (e.target.tagName === 'LI') {
    handleClick(e);
  }
});
```

---

## 四、循环优化

```javascript
// 好：缓存 length
const arr = [1, 2, 3];
for (let i = 0, len = arr.length; i < len; i++) {}

// 好：for...of（现代浏览器）
for (const item of arr) {}

// 好：while 循环
let i = arr.length;
while (i--) {}
```

---

## 五、避免内存泄漏

```javascript
// 不好：忘记移除监听器
const element = document.getElementById('btn');
element.addEventListener('click', handleClick);

// 好：保存引用，清理
const element = document.getElementById('btn');
element.addEventListener('click', handleClick);

// 后来
element.removeEventListener('click', handleClick);
```

---

## 六、防抖与节流

```javascript
// 防抖
function debounce(fn, delay = 300) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// 节流
function throttle(fn, delay = 300) {
  let last = 0;
  return function(...args) {
    const now = Date.now();
    if (now - last > delay) {
      fn.apply(this, args);
      last = now;
    }
  };
}

// 使用
const handleSearch = debounce(search, 300);
const handleScroll = throttle(onScroll, 100);
```

---

## 七、Web Workers

```javascript
// main.js
const worker = new Worker('worker.js');

worker.postMessage({ data: [1, 2, 3] });
worker.onmessage = (e) => {
  console.log('Result:', e.data);
};

// worker.js
self.onmessage = (e) => {
  const result = heavyComputation(e.data.data);
  self.postMessage(result);
};

function heavyComputation(data) {
  // 复杂计算...
  return result;
}
```

---

## 八、懒加载

```javascript
// 图片懒加载
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      observer.unobserve(img);
    }
  });
});

document.querySelectorAll('img[data-src]').forEach(img => {
  observer.observe(img);
});
```

---

## 九、数据结构选择

```javascript
// 好：Map 快速查找
const cache = new Map();
cache.set('key', 'value');
cache.get('key'); // O(1)

// 好：Set 去重
const unique = [...new Set([1, 2, 2, 3])];

// 好：Object 还是 Map？
// - 键是字符串/数字：Object
// - 需要频繁增删：Map
```

---

## 十、V8 优化

```javascript
// 好：保持对象形状一致
const user1 = { name: 'Alice', age: 30 };
const user2 = { name: 'Bob', age: 25 }; // 相同形状

// 不好：形状变化
user1.address = 'Street'; // 改变形状
```

---

## 十一、最佳实践

1. 先测量，再优化
2. 减少 DOM 操作
3. 使用事件委托
4. 避免内存泄漏
5. 合理使用 Web Workers

---

## 十二、总结

JavaScript 性能优化需要理解底层原理，才能写出高效的代码。
