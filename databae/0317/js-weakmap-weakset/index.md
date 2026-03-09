# JavaScript WeakMap 与 WeakSet：内存管理的隐藏利器

> 从垃圾回收到实战应用，掌握弱引用集合的正确用法

---

## 一、Map/Set 的内存问题

普通的 Map 和 Set 会阻止垃圾回收。

```javascript
let user = { name: 'Alice' };
const map = new Map();
map.set(user, 'metadata');

user = null;  // 想释放 user
// 但 map 仍然持有引用，user 不会被回收
```

WeakMap 和 WeakSet 使用弱引用，不会阻止垃圾回收。

---

## 二、WeakMap 基础

### 特点

- 键必须是对象
- 键是弱引用
- 不可遍历
- 没有 size 属性

```javascript
const wm = new WeakMap();

let obj = { name: 'Alice' };
wm.set(obj, 'metadata');

console.log(wm.get(obj));  // 'metadata'

obj = null;  // obj 可以被垃圾回收
// wm 中的条目也会自动删除
```

### API

```javascript
const wm = new WeakMap();

wm.set(key, value);  // 设置
wm.get(key);  // 获取
wm.has(key);  // 检查
wm.delete(key);  // 删除
```

---

## 三、WeakMap 实战应用

### 应用 1：私有属性

```javascript
const privateData = new WeakMap();

class Person {
  constructor(name, age) {
    privateData.set(this, { name, age });
  }
  
  getName() {
    return privateData.get(this).name;
  }
  
  getAge() {
    return privateData.get(this).age;
  }
}

const person = new Person('Alice', 25);
console.log(person.getName());  // 'Alice'
console.log(person.name);  // undefined（无法直接访问）
```

### 应用 2：DOM 节点缓存

```javascript
const cache = new WeakMap();

function processElement(element) {
  if (cache.has(element)) {
    return cache.get(element);
  }
  
  const result = expensiveOperation(element);
  cache.set(element, result);
  return result;
}

// 当 DOM 节点被移除时，缓存自动清理
```

### 应用 3：对象元数据

```javascript
const metadata = new WeakMap();

function addMetadata(obj, data) {
  metadata.set(obj, data);
}

function getMetadata(obj) {
  return metadata.get(obj);
}

const user = { name: 'Alice' };
addMetadata(user, { createdAt: Date.now(), role: 'admin' });
```

---

## 四、WeakSet 基础

### 特点

- 值必须是对象
- 值是弱引用
- 不可遍历
- 没有 size 属性

```javascript
const ws = new WeakSet();

let obj = { name: 'Alice' };
ws.add(obj);

console.log(ws.has(obj));  // true

obj = null;  // obj 可以被垃圾回收
```

### API

```javascript
const ws = new WeakSet();

ws.add(value);  // 添加
ws.has(value);  // 检查
ws.delete(value);  // 删除
```

---

## 五、WeakSet 实战应用

### 应用 1：标记对象

```javascript
const disabledElements = new WeakSet();

function disableElement(element) {
  disabledElements.add(element);
  element.setAttribute('disabled', true);
}

function isDisabled(element) {
  return disabledElements.has(element);
}
```

### 应用 2：防止循环引用

```javascript
function traverse(obj, visited = new WeakSet()) {
  if (visited.has(obj)) {
    return;  // 已访问过，避免死循环
  }
  
  visited.add(obj);
  
  for (const key in obj) {
    if (typeof obj[key] === 'object') {
      traverse(obj[key], visited);
    }
  }
}
```

---

## 六、与 Map/Set 对比

| 特性 | Map/Set | WeakMap/WeakSet |
|------|---------|-----------------|
| 键/值类型 | 任意 | 只能是对象 |
| 垃圾回收 | 阻止 | 不阻止 |
| 可遍历 | 是 | 否 |
| size | 有 | 无 |
| 使用场景 | 通用集合 | 内存敏感场景 |

---

## 七、实用技巧

### 技巧 1：实现观察者模式

```javascript
const observers = new WeakMap();

function observe(target, callback) {
  if (!observers.has(target)) {
    observers.set(target, new Set());
  }
  observers.get(target).add(callback);
}

function notify(target, data) {
  const callbacks = observers.get(target);
  if (callbacks) {
    callbacks.forEach(cb => cb(data));
  }
}
```

### 技巧 2：记忆化函数

```javascript
const memoCache = new WeakMap();

function memoize(fn) {
  return function(obj) {
    if (memoCache.has(obj)) {
      return memoCache.get(obj);
    }
    const result = fn(obj);
    memoCache.set(obj, result);
    return result;
  };
}
```

---

## 总结

WeakMap 和 WeakSet 是处理对象关联数据的最佳选择，它们：

- 自动管理内存
- 避免内存泄漏
- 适合缓存和元数据
- 防止循环引用

在需要关联对象数据时，优先考虑使用 WeakMap/WeakSet。

如果这篇文章对你有帮助，欢迎点赞收藏！
