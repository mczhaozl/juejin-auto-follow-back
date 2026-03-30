# 浏览器网络请求完全指南：fetch、axios 与并发控制

> 深入讲解浏览器网络请求，包括 fetch API、axios 使用、请求拦截、响应拦截，以及并发控制和缓存策略。

## 一、fetch API

### 1.1 基本用法

```javascript
fetch('/api/users')
  .then(response => response.json())
  .then(data => console.log(data))
  .catch(error => console.error(error));

// async/await
async function getUsers() {
  try {
    const response = await fetch('/api/users');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(error);
  }
}
```

### 1.2 配置选项

```javascript
fetch('/api/users', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer token'
  },
  body: JSON.stringify({ name: '张三' }),
  credentials: 'include',
  cache: 'no-cache'
})
```

### 1.3 响应处理

```javascript
const response = await fetch('/api/users');

console.log(response.ok);      // true/false
console.log(response.status);  // 200/404/500
console.log(response.headers);  // Headers 对象

const data = await response.json();
const text = await response.text();
const blob = await response.blob();
```

## 二、axios

### 2.1 基础用法

```javascript
import axios from 'axios';

axios.get('/api/users')
  .then(res => console.log(res.data));

// async/await
async function getUsers() {
  const res = await axios.get('/api/users');
  return res.data;
}
```

### 2.2 请求配置

```javascript
axios({
  url: '/api/users',
  method: 'post',
  data: { name: '张三' },
  headers: { 'X-Requested-With': 'XMLHttpRequest' },
  timeout: 5000
});
```

### 2.3 并发请求

```javascript
const [users, posts] = await Promise.all([
  axios.get('/api/users'),
  axios.get('/api/posts')
]);

console.log(users.data, posts.data);
```

## 三、拦截器

### 3.1 请求拦截

```javascript
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);
```

### 3.2 响应拦截

```javascript
axios.interceptors.response.use(
  response => {
    return response.data;
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

## 四、错误处理

### 4.1 fetch 错误处理

```javascript
async function fetchWithErrorHandling(url) {
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  
  return response.json();
}
```

### 4.2 axios 错误处理

```javascript
try {
  const res = await axios.get('/api/users');
  console.log(res.data);
} catch (error) {
  if (error.response) {
    console.log(error.response.status);
    console.log(error.response.data);
  } else if (error.request) {
    console.log('无响应', error.request);
  } else {
    console.log('请求错误', error.message);
  }
}
```

## 五、并发控制

### 5.1 限制并发数

```javascript
async function limitConcurrency(tasks, limit) {
  const results = [];
  const executing = [];
  
  for (const task of tasks) {
    const promise = task().then(result => {
      results.push(result);
    });
    
    executing.push(promise);
    
    if (executing.length >= limit) {
      await Promise.race(executing);
      executing.splice(executing.findIndex(p => p === promise), 1);
    }
  }
  
  return Promise.all(executing).then(() => results);
}
```

### 5.2 请求队列

```javascript
class RequestQueue {
  constructor(concurrency = 2) {
    this.concurrency = concurrency;
    this.running = 0;
    this.queue = [];
  }
  
  add(task) {
    return new Promise((resolve, reject) => {
      this.queue.push({ task, resolve, reject });
      this.run();
    });
  }
  
  async run() {
    if (this.running >= this.concurrency || !this.queue.length) return;
    
    this.running++;
    const { task, resolve, reject } = this.queue.shift();
    
    try {
      const result = await task();
      resolve(result);
    } catch (e) {
      reject(e);
    } finally {
      this.running--;
      this.run();
    }
  }
}
```

## 六、缓存策略

### 6.1 内存缓存

```javascript
const cache = new Map();

async function fetchWithCache(url, cacheTime = 60000) {
  const cached = cache.get(url);
  
  if (cached && Date.now() - cached.time < cacheTime) {
    return cached.data;
  }
  
  const response = await fetch(url);
  const data = await response.json();
  
  cache.set(url, { data, time: Date.now() });
  return data;
}
```

### 6.2 Cache API

```javascript
async function fetchWithCacheAPI(url) {
  const cache = await caches.open('api-cache');
  
  const cached = await cache.match(url);
  if (cached) return cached.json();
  
  const response = await fetch(url);
  cache.put(url, response.clone());
  
  return response.json();
}
```

## 七、总结

网络请求核心要点：

1. **fetch API**：原生请求方式
2. **axios**：更强大的 HTTP 客户端
3. **拦截器**：统一处理请求响应
4. **错误处理**：区分不同错误类型
5. **并发控制**：限制并发数
6. **缓存**：内存和 Cache API

掌握这些，网络请求不再难！

---

**推荐阅读**：
- [MDN fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [axios 文档](https://axios-http.com/)

**如果对你有帮助，欢迎点赞收藏！**
