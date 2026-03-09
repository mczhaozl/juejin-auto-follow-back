# 封装史上最优雅的 Axios：洋葱模型 + 插件化架构

> 请求重试、取消、缓存、鉴权、错误处理一网打尽

---

## 一、设计目标

- 洋葱模型中间件
- 插件化扩展
- TypeScript 类型安全
- 统一错误处理
- 请求/响应拦截

---

## 二、核心架构

```typescript
class HttpClient {
  private axios: AxiosInstance;
  private middlewares: Middleware[] = [];
  
  constructor(config: HttpConfig) {
    this.axios = axios.create(config);
    this.setupInterceptors();
  }
  
  use(middleware: Middleware) {
    this.middlewares.push(middleware);
    return this;
  }
  
  async request<T>(config: RequestConfig): Promise<T> {
    // 洋葱模型执行
    const chain = this.compose(this.middlewares);
    return chain(config);
  }
}
```

---

## 三、洋葱模型实现

```typescript
type Middleware = (
  config: RequestConfig,
  next: () => Promise<any>
) => Promise<any>;

function compose(middlewares: Middleware[]) {
  return function(config: RequestConfig) {
    let index = -1;
    
    function dispatch(i: number): Promise<any> {
      if (i <= index) {
        return Promise.reject(new Error('next() called multiple times'));
      }
      index = i;
      
      const middleware = middlewares[i];
      if (!middleware) {
        return Promise.resolve(config);
      }
      
      return middleware(config, () => dispatch(i + 1));
    }
    
    return dispatch(0);
  };
}
```

---

## 四、核心插件

### 1. 重试插件

```typescript
const retryPlugin: Middleware = async (config, next) => {
  const { retryCount = 3, retryDelay = 1000 } = config;
  
  for (let i = 0; i <= retryCount; i++) {
    try {
      return await next();
    } catch (error) {
      if (i === retryCount) throw error;
      await sleep(retryDelay * Math.pow(2, i));
    }
  }
};
```

### 2. 缓存插件

```typescript
const cache = new Map();

const cachePlugin: Middleware = async (config, next) => {
  if (config.method !== 'GET') return next();
  
  const key = JSON.stringify(config);
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const response = await next();
  cache.set(key, response);
  
  setTimeout(() => cache.delete(key), config.cacheTime || 60000);
  return response;
};
```

### 3. 鉴权插件

```typescript
const authPlugin: Middleware = async (config, next) => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  try {
    return await next();
  } catch (error) {
    if (error.response?.status === 401) {
      await refreshToken();
      return next();
    }
    throw error;
  }
};
```

---

## 五、使用示例

```typescript
const http = new HttpClient({
  baseURL: 'https://api.example.com',
  timeout: 10000
});

// 注册插件
http
  .use(authPlugin)
  .use(retryPlugin)
  .use(cachePlugin)
  .use(logPlugin);

// 发起请求
const data = await http.request<User>({
  url: '/user/profile',
  method: 'GET',
  retryCount: 3,
  cacheTime: 60000
});
```

---

## 六、完整实现

GitHub: [elegant-axios](https://github.com/yourname/elegant-axios)

---

## 总结

通过洋葱模型和插件化，我们实现了一个优雅、可扩展的 HTTP 客户端。

如果这篇文章对你有帮助，欢迎点赞收藏！
