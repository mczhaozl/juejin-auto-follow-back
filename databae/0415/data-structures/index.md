# 数据结构完全指南：数组、链表、树与图

> 深入讲解核心数据结构，包括数组、链表、栈、队列、哈希表、二叉树、堆与图，以及 JavaScript 实现和算法应用。

## 一、数组

### 1.1 基础操作

```javascript
const arr = [1, 2, 3, 4, 5];

// 访问 - O(1)
arr[0]; // 1

// 搜索 - O(n)
arr.indexOf(3); // 2

// 插入/删除 - O(n)
arr.push(6);       // 末尾添加
arr.pop();         // 末尾删除
arr.unshift(0);    // 开头添加
arr.shift();       // 开头删除
```

### 1.2 常用方法

```javascript
// 遍历
arr.forEach((v, i) => console.log(i, v));
arr.map(v => v * 2);
arr.filter(v => v > 2);
arr.reduce((acc, v) => acc + v, 0);

// 搜索
arr.find(v => v > 2);
arr.findIndex(v => v > 2);
arr.includes(3);

// 排序
arr.sort((a, b) => a - b);
arr.reverse();
```

## 二、链表

### 2.1 单链表

```javascript
class ListNode {
  constructor(val) {
    this.val = val;
    this.next = null;
  }
}

class LinkedList {
  constructor() {
    this.head = null;
  }
  
  append(val) {
    const node = new ListNode(val);
    if (!this.head) {
      this.head = node;
      return;
    }
    let curr = this.head;
    while (curr.next) curr = curr.next;
    curr.next = node;
  }
  
  delete(val) {
    if (!this.head) return;
    if (this.head.val === val) {
      this.head = this.head.next;
      return;
    }
    let curr = this.head;
    while (curr.next && curr.next.val !== val) {
      curr = curr.next;
    }
    if (curr.next) curr.next = curr.next.next;
  }
}
```

### 2.2 双向链表

```javascript
class DoublyListNode {
  constructor(val) {
    this.val = val;
    this.prev = null;
    this.next = null;
  }
}
```

## 三、栈与队列

### 3.1 栈（Stack）

```javascript
class Stack {
  constructor() {
    this.items = [];
  }
  
  push(item) {
    this.items.push(item);
  }
  
  pop() {
    return this.items.pop();
  }
  
  peek() {
    return this.items[this.items.length - 1];
  }
  
  isEmpty() {
    return this.items.length === 0;
  }
}
```

### 3.2 队列（Queue）

```javascript
class Queue {
  constructor() {
    this.items = [];
  }
  
  enqueue(item) {
    this.items.push(item);
  }
  
  dequeue() {
    return this.items.shift();
  }
  
  front() {
    return this.items[0];
  }
  
  isEmpty() {
    return this.items.length === 0;
  }
}
```

## 四、哈希表

### 4.1 JavaScript Map

```javascript
const map = new Map();

// 设置
map.set('name', '张三');
map.set('age', 25);

// 获取
map.get('name'); // '张三'

// 检查
map.has('name'); // true

// 删除
map.delete('name');
map.clear();

// 遍历
for (const [key, value] of map) {
  console.log(key, value);
}
```

### 4.2 Set

```javascript
const set = new Set();

set.add(1);
set.add(2);
set.add(1); // 重复被忽略

set.has(1); // true
set.delete(1);

for (const item of set) {
  console.log(item);
}
```

## 五、树

### 5.1 二叉树

```javascript
class TreeNode {
  constructor(val) {
    this.val = val;
    this.left = null;
    this.right = null;
  }
}

class BinaryTree {
  constructor() {
    this.root = null;
  }
  
  // 前序遍历
  preorder(node = this.root) {
    if (!node) return [];
    return [
      node.val,
      ...this.preorder(node.left),
      ...this.preorder(node.right)
    ];
  }
  
  // 中序遍历
  inorder(node = this.root) {
    if (!node) return [];
    return [
      ...this.inorder(node.left),
      node.val,
      ...this.inorder(node.right)
    ];
  }
  
  // 后序遍历
  postorder(node = this.root) {
    if (!node) return [];
    return [
      ...this.postorder(node.left),
      ...this.postorder(node.right),
      node.val
    ];
  }
}
```

### 5.2 二叉搜索树

```javascript
class BST {
  constructor() {
    this.root = null;
  }
  
  insert(val) {
    const node = new TreeNode(val);
    if (!this.root) {
      this.root = node;
      return;
    }
    let curr = this.root;
    while (true) {
      if (val < curr.val) {
        if (!curr.left) {
          curr.left = node;
          break;
        }
        curr = curr.left;
      } else {
        if (!curr.right) {
          curr.right = node;
          break;
        }
        curr = curr.right;
      }
    }
  }
  
  search(val) {
    let curr = this.root;
    while (curr) {
      if (val === curr.val) return curr;
      curr = val < curr.val ? curr.left : curr.right;
    }
    return null;
  }
}
```

## 六、堆

### 6.1 最小堆

```javascript
class MinHeap {
  constructor() {
    this.heap = [];
  }
  
  parent(i) { return Math.floor((i - 1) / 2); }
  left(i) { return 2 * i + 1; }
  right(i) { return 2 * i + 2; }
  
  insert(val) {
    this.heap.push(val);
    this.bubbleUp(this.heap.length - 1);
  }
  
  bubbleUp(i) {
    while (i > 0 && this.heap[this.parent(i)] > this.heap[i]) {
      [this.heap[i], this.heap[this.parent(i)]] = 
        [this.heap[this.parent(i)], this.heap[i]];
      i = this.parent(i);
    }
  }
  
  extractMin() {
    if (this.heap.length === 0) return null;
    if (this.heap.length === 1) return this.heap.pop();
    
    const min = this.heap[0];
    this.heap[0] = this.heap.pop();
    this.bubbleDown(0);
    return min;
  }
  
  bubbleDown(i) {
    while (this.left(i) < this.heap.length) {
      let smallest = this.left(i);
      if (this.right(i) < this.heap.length && 
          this.heap[this.right(i)] < this.heap[smallest]) {
        smallest = this.right(i);
      }
      if (this.heap[i] <= this.heap[smallest]) break;
      [this.heap[i], this.heap[smallest]] = 
        [this.heap[smallest], this.heap[i]];
      i = smallest;
    }
  }
}
```

## 七、总结

数据结构核心要点：

1. **数组**：连续内存，随机访问 O(1)
2. **链表**：指针链接，插入 O(1)
3. **栈**：后进先出
4. **队列**：先进先出
5. **哈希表**：键值对，查找 O(1)
6. **树**：层级结构
7. **堆**：优先级队列

掌握这些，算法基础更扎实！

---

**推荐阅读**：
- [数据结构与算法 JavaScript 描述](https://book.douban.com/subject/26590221/)

**如果对你有帮助，欢迎点赞收藏！**
