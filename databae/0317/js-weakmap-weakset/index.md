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
## 八、深入理解弱引用

### 8.1 JavaScript 垃圾回收机制

JavaScript 使用标记-清除（Mark-and-Sweep）算法进行垃圾回收。垃圾回收器会定期从根对象（如全局对象）出发，标记所有可达的对象，未被标记的对象则被视为垃圾并被回收。

普通 Map 和 Set 持有的对象引用是强引用，这意味着只要 Map 或 Set 存在，它们引用的对象就不会被垃圾回收。WeakMap 和 WeakSet 使用弱引用，当对象没有其他强引用时，即使它们存在于 WeakMap 或 WeakSet 中，也会被垃圾回收。

```javascript
// 强引用 vs 弱引用
let obj = { name: 'Test' };

// 强引用
const map = new Map();
map.set(obj, 'data');
obj = null;  // obj 不会被回收，因为 map 仍持有引用

// 弱引用
const wm = new WeakMap();
wm.set(obj, 'data');
obj = null;  // obj 可以被回收，wm 中的条目也会消失
```

### 8.2 WeakMap 内部实现原理

虽然 JavaScript 规范没有规定 WeakMap 的具体实现，但通常使用哈希表和弱引用表的组合来实现。弱引用表允许垃圾回收器在回收对象时自动清理对应的条目。

WeakMap 的键使用的是弱引用，而值使用的是强引用。这意味着只要键对象没有被其他强引用指向，它就可以被回收，即使对应的值还存在于 WeakMap 中。

```javascript
// 值的强引用特性
let obj = { name: 'Test' };
const wm = new WeakMap();
wm.set(obj, { largeData: new Array(1000000) });

obj = null;  // 键被回收，值也会被回收
```

### 8.3 WeakSet 的使用场景详解

WeakSet 主要用于存储对象集合，而不需要担心内存泄漏。以下是一些典型的使用场景。

```javascript
// 场景 1：追踪已处理的对象
const processedItems = new WeakSet();

function processItem(item) {
  if (processedItems.has(item)) {
    console.log('Item already processed');
    return;
  }
  
  // 处理逻辑
  console.log('Processing item');
  processedItems.add(item);
}

// 场景 2：安全存储对象
const secrets = new WeakSet();

function storeSecret(obj, secret) {
  if (!secrets.has(obj)) {
    secrets.add(obj);
  }
  // 使用闭包或其他方式存储 secret
}

// 场景 3：对象类型检查
const arrays = new WeakSet();

function ensureArray(value) {
  if (Array.isArray(value)) {
    arrays.add(value);
    return true;
  }
  return false;
}
```

## 九、性能考量

### 9.1 内存使用

WeakMap 和 WeakSet 的内存使用与普通 Map 和 Set 有显著不同。由于它们不阻止垃圾回收，当键对象不再使用时，相关的条目会自动被清理，不会造成内存泄漏。

```javascript
// 使用 WeakMap 避免内存泄漏
const cache = new WeakMap();

function createExpensiveObject(key) {
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const obj = createExpensiveObjectImpl(key);
  cache.set(key, obj);
  return obj;
}

// 当 key 不再使用时，缓存条目会自动清理
```

### 9.2 性能特点

WeakMap 和 WeakSet 的性能特点与普通 Map 和 Set 不同。由于弱引用的实现开销，WeakMap 和 WeakSet 的操作可能比普通 Map 和 Set 稍慢。但这种差异通常可以忽略不计，因为内存管理的优势远大于性能的小幅下降。

```javascript
// 性能对比
const map = new Map();
const wm = new WeakMap();

const keys = Array.from({ length: 1000 }, () => ({}));

// Map 操作
console.time('Map');
for (const key of keys) {
  map.set(key, Math.random());
}
console.timeEnd('Map');

// WeakMap 操作
console.time('WeakMap');
for (const key of keys) {
  wm.set(key, Math.random());
}
console.timeEnd('WeakMap');
```

### 9.3 何时使用 WeakMap/WeakSet

选择使用 WeakMap/WeakSet 还是 Map/Set 需要根据具体场景决定。

当需要将数据与对象关联，但不希望这些对象因为存在于集合中而无法被垃圾回收时，应该使用 WeakMap/WeakSet。这在缓存、元数据存储、DOM 节点关联等场景中特别有用。

当需要遍历集合、获取大小或使用迭代器时，应该使用 Map/Set。WeakMap 和 WeakSet 不支持这些操作。

```javascript
// 使用 WeakMap 的场景
const metadata = new WeakMap();
const caches = new WeakMap();
const observers = new WeakMap();

// 使用 Map 的场景
const config = new Map();
const translations = new Map();
const cache = new Map();  // 需要遍历或获取大小时
```

## 十、常见问题与解决方案

### 10.1 为什么 WeakMap 不能遍历

WeakMap 不支持遍历是因为其键是弱引用。如果允许遍历，JavaScript 运行时需要在遍历过程中保持所有键对象的强引用，这与弱引用的设计初衷相矛盾。

```javascript
// 以下操作都不支持
const wm = new WeakMap();
wm[Symbol.iterator];  // undefined
for (const key of wm) {}  // TypeError
wm.forEach;  // undefined
wm.size;  // undefined
wm.keys();  // undefined
wm.values();  // undefined
wm.entries();  // undefined
```

### 10.2 如何清空 WeakMap

由于 WeakMap 不支持 clear 方法和遍历，清空 WeakMap 的唯一方式是让所有键对象不再被其他变量引用。

```javascript
// 清空 WeakMap 的方法
const wm = new WeakMap();
let obj1 = {};
let obj2 = {};

wm.set(obj1, 'data1');
wm.set(obj2, 'data2');

// 方法 1：让所有键对象不再被引用
obj1 = null;
obj2 = null;
// 垃圾回收后，wm 自动清空

// 方法 2：使用新的 WeakMap
const newWm = new WeakMap();
// 旧 wm 会被垃圾回收
```

### 10.3 WeakMap 键的唯一性

WeakMap 的键遵循对象引用相等的规则。两个不同的对象即使内容相同，也被视为不同的键。

```javascript
const wm = new WeakMap();

// 相同的对象引用
const obj = {};
wm.set(obj, 'first');
wm.set(obj, 'second');
console.log(wm.get(obj));  // 'second'

// 不同的对象引用
wm.set({ name: 'test' }, 'first');
wm.set({ name: 'test' }, 'second');
console.log(wm.get({ name: 'test' }));  // undefined
console.log(wm.has({ name: 'test' }));  // false
```

## 十一、与其他语言特性的结合

### 11.1 与 Proxy 结合

WeakMap 常与 Proxy 结合使用，实现各种高级功能。

```javascript
const handlers = new WeakMap();

function createProxy(target) {
  const handler = {
    get(target, property) {
      console.log(`Getting ${property}`);
      return target[property];
    },
    set(target, property, value) {
      console.log(`Setting ${property} to ${value}`);
      return target[property] = value;
    }
  };
  
  if (!handlers.has(target)) {
    handlers.set(target, handler);
  }
  
  return new Proxy(target, handlers.get(target));
}
```

### 11.2 与闭包结合

WeakMap 可以与闭包结合，实现私有数据存储。

```javascript
const privateData = new WeakMap();

class Counter {
  constructor() {
    privateData.set(this, { count: 0 });
  }
  
  increment() {
    const data = privateData.get(this);
    data.count++;
    return data.count;
  }
  
  getCount() {
    return privateData.get(this).count;
  }
}

const counter = new Counter();
console.log(counter.increment());  // 1
console.log(counter.getCount());  // 1
console.log(counter.count);  // undefined（私有）
```

### 11.3 与模块模式结合

在模块开发中，WeakMap 可以用于存储模块级别的私有数据。

```javascript
// module.js
const moduleCache = new WeakMap();
const moduleMetadata = new WeakMap();

export function createModule(id) {
  const module = { id };
  
  moduleCache.set(module, {
    loaded: false,
    exports: null
  });
  
  moduleMetadata.set(module, {
    createdAt: Date.now(),
    lastAccessed: Date.now()
  });
  
  return module;
}

export function loadModule(module) {
  const cache = moduleCache.get(module);
  if (cache && !cache.loaded) {
    // 加载模块逻辑
    cache.loaded = true;
    cache.exports = {};
  }
  
  const metadata = moduleMetadata.get(module);
  if (metadata) {
    metadata.lastAccessed = Date.now();
  }
}
```

## 十二、总结与最佳实践

### 核心要点回顾

WeakMap 和 WeakSet 是 JavaScript 中处理对象关联数据的强大工具。它们的主要优势在于内存管理——使用弱引用意味着当键对象不再被其他变量引用时，它们会自动被垃圾回收，不会造成内存泄漏。

在实际开发中，应该优先考虑使用 WeakMap/WeakSet 的场景包括：私有数据存储、DOM 节点缓存、对象元数据、追踪已处理对象等。同时，当需要遍历集合、获取大小或使用迭代器时，应该使用 Map/Set。

### 最佳实践建议

第一，将对象与数据关联时，优先使用 WeakMap 而不是 Map。这样可以避免内存泄漏，特别是在长时间运行的应用程序中。

第二，使用 WeakSet 来追踪对象集合，而不是使用 Set。这确保了当对象不再需要时，它们可以被垃圾回收。

第三，利用 WeakMap 实现私有属性。这是一种比 Symbol 私有属性更灵活的方案，特别适合需要存储大量私有数据的类。

第四，在缓存场景中使用 WeakMap。缓存的对象键会自动清理，避免缓存无限增长导致的内存问题。

第五，避免在 WeakMap 中存储大量小对象。如果键对象很快就会被创建和销毁，WeakMap 的性能开销可能不值得。

### 未来发展

JavaScript 的弱引用特性在不断演进。WeakRef 和 FinalizationRegistry 是最近添加的特性，它们提供了更灵活的弱引用能力。了解 WeakMap 和 WeakSet 的使用是掌握这些更高级特性的基础。

```javascript
// WeakRef 示例
let obj = { name: 'Test' };
const ref = new WeakRef(obj);

obj = null;
const deref = ref.deref();
if (deref) {
  console.log(deref.name);  // 'Test'
}

// FinalizationRegistry 示例
const registry = new FinalizationRegistry((heldValue) => {
  console.log(`Cleaned up: ${heldValue}`);
});

let obj2 = {};
registry.register(obj2, 'some data');
obj2 = null;  // 垃圾回收后，注册的回调会被调用
```

通过掌握 WeakMap 和 WeakSet，你将能够编写出更加内存高效、更具可扩展性的 JavaScript 代码。这些看似简单的特性，在大型应用程序和长期运行的系统中能够发挥巨大的作用。