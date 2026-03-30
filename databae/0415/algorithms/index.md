# 算法完全指南：排序、搜索与递归

> 深入讲解基础算法，包括排序算法（冒泡、选择、归并、快速）、搜索算法（二分、DFS、BFS），以及递归与动态规划基础。

## 一、排序算法

### 1.1 冒泡排序

```javascript
function bubbleSort(arr) {
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    for (let j = 0; j < n - i - 1; j++) {
      if (arr[j] > arr[j + 1]) {
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
      }
    }
  }
  return arr;
}
// 时间: O(n²) 空间: O(1)
```

### 1.2 快速排序

```javascript
function quickSort(arr) {
  if (arr.length <= 1) return arr;
  
  const pivot = arr[Math.floor(arr.length / 2)];
  const left = arr.filter(x => x < pivot);
  const middle = arr.filter(x => x === pivot);
  const right = arr.filter(x => x > pivot);
  
  return [...quickSort(left), ...middle, ...quickSort(right)];
}
// 时间: O(n log n) 空间: O(n)
```

### 1.3 归并排序

```javascript
function mergeSort(arr) {
  if (arr.length <= 1) return arr;
  
  const mid = Math.floor(arr.length / 2);
  const left = mergeSort(arr.slice(0, mid));
  const right = mergeSort(arr.slice(mid));
  
  return merge(left, right);
}

function merge(left, right) {
  const result = [];
  while (left.length && right.length) {
    result.push(left[0] <= right[0] ? left.shift() : right.shift());
  }
  return [...result, ...left, ...right];
}
// 时间: O(n log n) 空间: O(n)
```

## 二、搜索算法

### 2.1 二分查找

```javascript
function binarySearch(arr, target) {
  let left = 0;
  let right = arr.length - 1;
  
  while (left <= right) {
    const mid = Math.floor((left + right) / 2);
    if (arr[mid] === target) return mid;
    if (arr[mid] < target) left = mid + 1;
    else right = mid - 1;
  }
  return -1;
}
// 时间: O(log n)
```

### 2.2 DFS（深度优先）

```javascript
function dfs(graph, start) {
  const visited = new Set();
  const result = [];
  
  function traverse(node) {
    if (visited.has(node)) return;
    visited.add(node);
    result.push(node);
    
    for (const neighbor of graph[node]) {
      traverse(neighbor);
    }
  }
  
  traverse(start);
  return result;
}
```

### 2.3 BFS（广度优先）

```javascript
function bfs(graph, start) {
  const visited = new Set();
  const queue = [start];
  const result = [];
  
  while (queue.length) {
    const node = queue.shift();
    if (visited.has(node)) continue;
    visited.add(node);
    result.push(node);
    
    for (const neighbor of graph[node]) {
      queue.push(neighbor);
    }
  }
  
  return result;
}
```

## 三、递归

### 3.1 阶乘

```javascript
function factorial(n) {
  if (n <= 1) return 1;
  return n * factorial(n - 1);
}
```

### 3.2 斐波那契

```javascript
function fibonacci(n) {
  if (n <= 1) return n;
  return fibonacci(n - 1) + fibonacci(n - 2);
}

// 优化：记忆化
function fibonacciMemo(n, memo = {}) {
  if (n in memo) return memo[n];
  if (n <= 1) return n;
  memo[n] = fibonacciMemo(n - 1, memo) + fibonacciMemo(n - 2, memo);
  return memo[n];
}
```

## 四、动态规划基础

### 4.1 爬楼梯

```javascript
function climbStairs(n) {
  if (n <= 2) return n;
  
  const dp = [0, 1, 2];
  for (let i = 3; i <= n; i++) {
    dp[i] = dp[i - 1] + dp[i - 2];
  }
  return dp[n];
}

// 空间优化
function climbStairsOpt(n) {
  if (n <= 2) return n;
  
  let prev2 = 1, prev1 = 2;
  for (let i = 3; i <= n; i++) {
    const curr = prev1 + prev2;
    prev2 = prev1;
    prev1 = curr;
  }
  return prev1;
}
```

### 4.2 最长公共子序列

```javascript
function lcs(s1, s2) {
  const m = s1.length;
  const n = s2.length;
  const dp = Array(m + 1).fill(null).map(() => Array(n + 1).fill(0));
  
  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (s1[i - 1] === s2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1] + 1;
      } else {
        dp[i][j] = Math.max(dp[i - 1][j], dp[i][j - 1]);
      }
    }
  }
  
  return dp[m][n];
}
```

## 五、时间复杂度

### 5.1 常见复杂度

| 复杂度 | 名称 | 示例 |
|--------|------|------|
| O(1) | 常数 | 数组访问 |
| O(log n) | 对数 | 二分查找 |
| O(n) | 线性 | 遍历 |
| O(n log n) | 线性对数 | 快速排序 |
| O(n²) | 平方 | 冒泡排序 |
| O(2ⁿ) | 指数 | 递归斐波那契 |

## 六、总结

算法核心要点：

1. **排序**：快排、归并
2. **搜索**：二分、DFS、BFS
3. **递归**：函数自调用
4. **DP**：状态转移
5. **复杂度**：时间空间

掌握这些，算法面试不用愁！

---

**推荐阅读**：
- [算法图解](https://book.douban.com/subject/26979890/)
- [剑指 Offer](https://book.douban.com/subject/27008702/)

**如果对你有帮助，欢迎点赞收藏！**
