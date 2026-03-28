# WeakMap与WeakSet：你不知道的JavaScript高级特性

> 深入解析WeakMap和WeakSet的垃圾回收机制、适用场景与实际应用，帮你解决内存泄漏和私有数据存储问题。

## 一、引言

WeakMap 和 WeakSet 是 JavaScript 中两个相对「冷门」的数据结构，但它们在解决特定问题时非常强大。本文将带你深入了解这两个高级特性。

## 二、什么是弱引用

### 2.1 强引用 vs 弱引用

```javascript
// 强引用（普通对象）
const obj = { name: 'test' };
const arr = [obj];
obj = null; // obj 不会被回收，因为 arr 还引用着它

// 弱引用（WeakMap/WeakSet）
const weakMap = new WeakMap();
const obj2 = { name: 'test2' };
weakMap.set(obj2, 'value');
obj2 = null; // obj2 可以被垃圾回收，因为只有 WeakMap 持有弱引用
```

### 2.2 弱引用的特点

- **不影响垃圾回收**：当对象只被 WeakMap/WeakSet 引用时，垃圾回收器可以回收该对象
- **不可枚举**：WeakMap 和 WeakSet 不能遍历，没有 `size`、`keys()`、`values()` 等方法
- **键必须是对象**：WeakMap 的键必须是对象，WeakSet 只能存储对象

## 三、WeakMap 详解

### 3.1 基本API

```javascript
const weakMap = new WeakMap();

// 设置值
const obj = { id: 1 };
weakMap.set(obj, 'associated data');

// 获取值
console.log(weakMap.get(obj)); // 'associated data'

// 检查是否存在
console.log(weakMap.has(obj)); // true

// 删除值
weakMap.delete(obj);
console.log(weakMap.has(obj)); // false
```

### 3.2 典型应用：私有数据存储

```javascript
const privateData = new WeakMap();

class User {
  constructor(name, age) {
    // 将私有数据存储在 WeakMap 中
    privateData.set(this, { name, age });
  }
  
  getName() {
    return privateData.get(this).name;
  }
  
  getAge() {
    return privateData.get(this).age;
  }
}

const user = new User('张三', 25);
console.log(user.getName()); // '张三'
// user 对象被回收后，privateData 中的数据也会自动消失
```

### 3.3 缓存场景

```javascript
const cache = new WeakMap();

function processData(data) {
  if (cache.has(data)) {
    return cache.get(data);
  }
  
  const result = expensiveComputation(data);
  cache.set(data, result);
  return result;
}
```

## 四、WeakSet 详解

### 4.1 基本API

```javascript
const weakSet = new WeakSet();

// 添加对象
const obj1 = { id: 1 };
const obj2 = { id: 2 };
weakSet.add(obj1);
weakSet.add(obj2);

// 检查是否存在
console.log(weakSet.has(obj1)); // true

// 删除对象
weakSet.delete(obj1);
console.log(weakSet.has(obj1)); // false
```

### 4.2 典型应用：对象追踪

```javascript
const trackedObjects = new WeakSet();

function trackObject(obj) {
  if (trackedObjects.has(obj)) {
    console.log('对象已被追踪');
    return false;
  }
  trackedObjects.add(obj);
  return true;
}

const obj = {};
console.log(trackObject(obj)); // true
console.log(trackObject(obj)); // false

// obj 被回收后，weakSet 会自动清理
```

## 五、与普通Map/Set的对比

### 5.1 对比表格

| 特性 | Map/Set | WeakMap/WeakSet |
|------|---------|-----------------|
| 键类型 | 任意类型 | 必须是对象 |
| 可枚举 | 是 | 否 |
| 内存管理 | 手动管理 | 自动垃圾回收 |
| 迭代器 | 支持 | 不支持 |
| size属性 | 有 | 无 |

### 5.2 内存泄漏对比

```javascript
// 使用 Map（可能导致内存泄漏）
const mapCache = new Map();
function withCache(key, value) {
  if (mapCache.has(key)) {
    return mapCache.get(key);
  }
  const result = compute(value);
  mapCache.set(key, result);
  return result;
}

// 使用 WeakMap（自动清理）
const weakCache = new WeakMap();
function withWeakCache(key, value) {
  if (weakCache.has(key)) {
    return weakCache.get(key);
  }
  const result = compute(value);
  weakCache.set(key, result);
  return result;
}
```

## 六、高级应用场景

### 6.1 DOM节点数据关联

```javascript
const elementData = new WeakMap();

function attachData(element, data) {
  elementData.set(element, data);
}

function getData(element) {
  return elementData.get(element);
}

// 元素从 DOM 移除后，关联数据会自动被回收
```

### 6.2 事件处理器管理

```javascript
const handlers = new WeakMap();

function addHandler(element, event, handler) {
  const elementHandlers = handlers.get(element) || {};
  elementHandlers[event] = handler;
  handlers.set(element, elementHandlers);
  element.addEventListener(event, handler);
}

function removeAllHandlers(element) {
  const elementHandlers = handlers.get(element);
  if (elementHandlers) {
    Object.entries(elementHandlers).forEach(([event, handler]) => {
      element.removeEventListener(event, handler);
    });
    handlers.delete(element);
  }
}
```

### 6.3 防止对象被修改

```javascript
const frozenObjects = new WeakSet();

function freezeObject(obj) {
  if (frozenObjects.has(obj)) {
    return obj;
  }
  Object.freeze(obj);
  frozenObjects.add(obj);
  return obj;
}

const obj = { x: 1 };
freezeObject(obj);
obj.x = 2; // 在严格模式下会报错
console.log(obj.x); // 1
```

## 七、注意事项

### 7.1 不能作为缓存

```javascript
// WeakMap 不适合做普通缓存
const cache = new WeakMap();

// 错误示例：键是字符串，不是对象
// cache.set('key', 'value'); // TypeError

// 正确示例：键必须是对象
cache.set(new String('key'), 'value');
```

### 7.2 不支持遍历

```javascript
const weakMap = new WeakMap();
weakMap.set({ a: 1 }, 'value1');
weakMap.set({ b: 2 }, 'value2');

// 这些都会报错
// for (const [key, value] of weakMap) {}
// weakMap.keys()
// weakMap.values()
```

### 7.3 键的不可变性

```javascript
const obj = { id: 1 };
const weakMap = new WeakMap();
weakMap.set(obj, 'value');

// obj 被修改不影响
obj.id = 2;
console.log(weakMap.get(obj)); // 'value'

// 但如果obj被替换，则无法获取
const newObj = { id: 1 };
console.log(weakMap.get(newObj)); // undefined
```

## 八、总结

WeakMap 和 WeakSet 是 JavaScript 中处理特定场景的强大工具：

1. **WeakMap**：适合存储与对象关联的私有数据、缓存、DOM数据
2. **WeakSet**：适合追踪对象、防止重复处理

核心优势：
- **自动垃圾回收**：无需手动清理
- **防止内存泄漏**：特别适合长时间运行的应用
- **私有数据存储**：实现真正的数据封装

掌握这些高级特性，能帮助你在特定场景下写出更优雅、更高效的代码。

---

**推荐阅读**：
- [MDN WeakMap 文档](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WeakMap)
- [MDN WeakSet 文档](https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/WeakSet)

**如果对你有帮助，欢迎点赞收藏！**
