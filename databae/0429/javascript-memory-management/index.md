# JavaScript 内存管理与性能优化完全指南：从原理到实战

## 一、JavaScript 内存模型

### 1.1 栈与堆
- **栈**：存储基本类型和引用，大小固定
- **堆**：存储对象和函数，大小动态

---

## 二、垃圾回收

### 2.1 标记-清除算法

```javascript
// 垃圾回收器会定期运行
// 从根对象（如 window）开始标记可达对象
// 未标记的对象会被清除
```

### 2.2 引用计数（已过时）

```javascript
let obj = { name: 'Alice' }; // 引用计数：1
let obj2 = obj; // 引用计数：2
obj = null; // 引用计数：1
obj2 = null; // 引用计数：0，可回收
```

---

## 三、常见内存泄漏

### 3.1 意外的全局变量

```javascript
function createGlobal() {
  leak = 'This will leak'; // 未声明变量变成全局
}

function safe() {
  let noLeak = 'Safe'; // 局部变量，函数结束后释放
}
```

### 3.2 未清理的定时器

```javascript
// 错误示例
function startTimer() {
  setInterval(() => {
    console.log('Running');
  }, 1000);
}

// 正确示例
function startSafeTimer() {
  const intervalId = setInterval(() => {
    console.log('Running');
  }, 1000);
  
  return () => clearInterval(intervalId);
}

// React 组件中
useEffect(() => {
  const intervalId = setInterval(() => {
    console.log('Running');
  }, 1000);
  
  return () => clearInterval(intervalId);
}, []);
```

### 3.3 闭包引用

```javascript
function createClosure() {
  const largeData = new Array(1000000).fill('data');
  
  return function() {
    console.log('Closure function');
  };
}

const closure = createClosure();
// largeData 可能不会被 GC，因为闭包持有引用
```

### 3.4 未移除的事件监听器

```javascript
// 错误示例
function addListener() {
  const button = document.getElementById('btn');
  button.addEventListener('click', () => {
    console.log('Clicked');
  });
}

// 正确示例
function addSafeListener() {
  const button = document.getElementById('btn');
  const handler = () => console.log('Clicked');
  button.addEventListener('click', handler);
  
  return () => button.removeEventListener('click', handler);
}
```

### 3.5 DOM 引用

```javascript
// 错误示例
const elements = [];
function addElement() {
  const div = document.createElement('div');
  document.body.appendChild(div);
  elements.push(div); // 保留引用
}

// 正确示例
function addElement() {
  const div = document.createElement('div');
  document.body.appendChild(div);
}
```

---

## 四、内存检测工具

### 4.1 Chrome DevTools

```javascript
// 1. 打开 Memory 面板
// 2. 点击 Take heap snapshot
// 3. 分析快照查找内存泄漏
```

### 4.2 Performance Monitor

```javascript
// Performance 面板监控内存使用
```

---

## 五、内存优化策略

### 5.1 对象池

```javascript
class ObjectPool {
  constructor(createFn, initialSize = 10) {
    this.pool = [];
    this.createFn = createFn;
    
    for (let i = 0; i < initialSize; i++) {
      this.pool.push(createFn());
    }
  }
  
  acquire() {
    return this.pool.pop() || this.createFn();
  }
  
  release(obj) {
    this.pool.push(obj);
  }
}

const particlePool = new ObjectPool(() => ({ x: 0, y: 0, active: false }));

function createParticle() {
  const p = particlePool.acquire();
  p.x = Math.random();
  p.y = Math.random();
  p.active = true;
  return p;
}

function destroyParticle(p) {
  p.active = false;
  particlePool.release(p);
}
```

### 5.2 避免频繁创建对象

```javascript
// 错误示例
function processArray(arr) {
  return arr.map(item => ({ value: item * 2 }));
}

// 更好的做法
const tempObj = { value: 0 };
function processArray(arr) {
  return arr.map(item => {
    tempObj.value = item * 2;
    return { ...tempObj }; // 如果必须返回新对象
  });
}
```

### 5.3 及时释放引用

```javascript
function processData(data) {
  const result = heavyComputation(data);
  data = null; // 不再需要 data，释放引用
  return result;
}
```

---

## 六、WeakMap 与 WeakSet

```javascript
// 弱引用，不阻止 GC
const cache = new WeakMap();

function processObject(obj) {
  if (cache.has(obj)) {
    return cache.get(obj);
  }
  
  const result = heavyComputation(obj);
  cache.set(obj, result);
  return result;
}

let data = { id: 1 };
processObject(data);
data = null; // WeakMap 中的条目可能被 GC
```

---

## 七、字符串优化

```javascript
// 避免频繁拼接
let result = '';
for (let i = 0; i < 1000; i++) {
  result += i; // 每次创建新字符串
}

// 更好：Array.join
const parts = [];
for (let i = 0; i < 1000; i++) {
  parts.push(i);
}
const result = parts.join('');
```

---

## 八、React 内存优化

```jsx
// 使用 useMemo
const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b);
}, [a, b]);

// 使用 useCallback
const memoizedCallback = useCallback(() => {
  doSomething(a, b);
}, [a, b]);

// 清理副作用
useEffect(() => {
  const subscription = subscribe();
  return () => subscription.unsubscribe();
}, []);
```

---

## 九、内存泄漏检测示例

```javascript
function detectLeaks() {
  const initialHeap = performance.memory.usedJSHeapSize;
  
  // 执行可能泄漏的操作
  for (let i = 0; i < 1000; i++) {
    const obj = { data: new Array(1000) };
    // 如果 obj 没有被正确释放...
  }
  
  const finalHeap = performance.memory.usedJSHeapSize;
  const increase = finalHeap - initialHeap;
  
  console.log(`Memory increase: ${increase / 1024 / 1024}MB`);
}
```

---

## 十、最佳实践

1. 避免不必要的全局变量
2. 及时清理定时器、事件监听器
3. 使用 WeakMap/WeakSet 缓存
4. 避免内存泄漏的闭包
5. 定期使用 DevTools 分析内存

---

## 十一、总结

良好的内存管理是高性能 JavaScript 应用的基础，需注意避免常见的内存泄漏陷阱。
