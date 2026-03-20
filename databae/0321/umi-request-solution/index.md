# umi/request：统一请求解决方案，告别重复的HTTP请求封装

> 深入解析umi/request如何通过统一拦截器、自动错误处理、缓存策略和类型安全，解决前端项目中HTTP请求的重复封装、错误处理混乱、类型安全缺失等核心难题。

---

## 一、背景：前端HTTP请求的痛点

在传统的前端项目中，我们经常遇到以下问题：

1. **重复代码**：每个请求都需要手动处理loading、error、data状态
2. **错误处理混乱**：每个请求都要重复处理错误
3. **类型安全缺失**：TypeScript类型定义不完整
4. **缓存策略缺失**：重复请求、缓存失效问题
5. **拦截器混乱**：每个项目都有自己的拦截器实现

## 二、umi/request的核心特性

### 1. 统一配置，一处配置，处处使用

```typescript
// 传统方式：每个请求都要写一遍
const fetchData = async () => {
  try {
    const response = await fetch('/api/data');
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('请求失败:', error);
    throw error;
  }
};

// umi/request方式
import { request } from 'umi';

// 全局配置
const request = request.extend({
  prefix: '/api',
  timeout: 10000,
  errorHandler: (error) => {
    // 统一错误处理
    console.error('请求错误:', error);
    throw error;
  }
});

// 使用
const data = await request('/users');
```

### 2. 自动错误处理

```typescript
// 传统方式：每个请求都要写try-catch
try {
  const data = await fetchData();
} catch (error) {
  // 每个请求都要写错误处理
  if (error.status === 401) {
    // 处理未授权
  } else if (error.status === 500) {
    // 处理服务器错误
  }
}

// umi/request：统一错误处理
const request = request.extend({
  errorHandler: (error) => {
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 跳转到登录页
          window.location.href = '/login';
          break;
        case 500:
          // 服务器错误
          message.error('服务器错误，请稍后重试');
          break;
      }
    }
    throw error;
  }
});
```

### 3. 类型安全与TypeScript支持

```typescript
// 传统方式：手动定义类型，容易出错
interface User {
  id: number;
  name: string;
  email: string;
}

// 手动类型断言，容易出错
const user: User = await getUser();

// umi/request：类型安全
import { request } from 'umi';

interface User {
  id: number;
  name: string;
  email: string;
}

// 类型安全的请求
const user = await request<User>('/api/user/1');
// user 自动推断为 User 类型
```

### 4. 拦截器：统一处理请求/响应

```typescript
// 请求拦截器
request.interceptors.request.use((config) => {
  // 添加认证token
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器
request.interceptors.response.use(
  (response) => {
    // 统一处理成功响应
    return response.data;
  },
  (error) => {
    // 统一处理错误
    if (error.response?.status === 401) {
      // 跳转到登录页
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### 5. 缓存策略与性能优化

```typescript
// 传统方式：手动实现缓存
let cache = {};

async function fetchWithCache(url) {
  if (cache[url]) {
    return cache[url];
  }
  const data = await fetch(url);
  cache[url] = data;
  return data;
}

// umi/request：内置缓存
const { data, loading, error } = useRequest('/api/data', {
  cacheKey: 'userData', // 自动缓存
  cacheTime: 5 * 60 * 1000, // 缓存5分钟
  staleTime: 60 * 1000, // 数据保鲜时间
});
```

## 三、解决的实际问题

### 问题1：重复的请求封装

**传统方式**：
```javascript
// 每个API都要写一遍
export const getUser = async (id) => {
  try {
    const response = await fetch(`/api/users/${id}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('获取用户失败:', error);
    throw error;
  }
};

export const updateUser = async (id, data) => {
  // 重复的代码...
};
```

**umi/request解决方案**：
```typescript
// 统一配置，一处定义，处处使用
const request = createRequest({
  baseURL: '/api',
  timeout: 10000,
  interceptors: {
    request: (config) => {
      // 统一添加token
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    }
  }
});

// 所有请求都继承这个配置
export const getUser = (id) => request.get(`/users/${id}`);
export const updateUser = (id, data) => request.put(`/users/${id}`, data);
```

### 问题2：错误处理混乱

**传统方式**：
```javascript
// 每个请求都要写错误处理
try {
  const data = await fetchData();
} catch (error) {
  if (error.status === 401) {
    // 处理未授权
  } else if (error.status === 500) {
    // 处理服务器错误
  }
  // 每个请求都要写一遍
}
```

**umi/request解决方案**：
```typescript
// 统一错误处理
const request = createRequest({
  errorHandler: (error) => {
    // 统一错误处理
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 跳转到登录页
          window.location.href = '/login';
          break;
        case 500:
          message.error('服务器错误，请稍后重试');
          break;
        default:
          message.error('请求失败，请重试');
      }
    }
    return Promise.reject(error);
  }
});
```

### 问题3：类型安全缺失

**传统方式**：
```typescript
// 没有类型检查，容易出错
const user = await getUser(1);
console.log(user.nam); // 拼写错误，但不会报错
```

**umi/request解决方案**：
```typescript
interface User {
  id: number;
  name: string;
  email: string;
}

// 类型安全的请求
const getUser = async (id: number): Promise<User> => {
  return request.get<User>(`/users/${id}`);
};

// TypeScript会检查类型
const user = await getUser(1);
console.log(user.name); // 正确
console.log(user.nam); // TypeScript报错：属性'nam'不存在
```

## 四、高级特性

### 1. 请求取消
```typescript
import { useRequest } from 'umi';

const { data, loading, error, cancel } = useRequest('/api/data', {
  manual: true, // 手动触发
  onSuccess: (data) => {
    console.log('请求成功:', data);
  },
  onError: (error) => {
    console.error('请求失败:', error);
  }
});

// 取消请求
cancel();
```

### 2. 轮询请求
```typescript
const { data, loading } = useRequest('/api/data', {
  pollingInterval: 3000, // 每3秒轮询一次
  pollingWhenHidden: false, // 页面隐藏时停止轮询
});
```

### 3. 依赖请求
```typescript
// 依赖其他请求的结果
const { data: user } = useRequest('/api/user/1');
const { data: posts } = useRequest(
  () => `/api/users/${user?.id}/posts`,
  {
    ready: !!user, // 等待user数据加载完成
    refreshDeps: [user] // 依赖user变化
  }
);
```

### 4. 防抖与节流
```typescript
const { data, loading } = useRequest('/api/search', {
  debounceInterval: 300, // 防抖300ms
  throttleInterval: 1000, // 节流1秒
  manual: true,
  debounceOptions: {
    leading: true,
    trailing: true
  }
});
```

## 五、实际应用场景

### 场景1：表单提交
```typescript
const { loading, run } = useRequest(
  (formData) => request.post('/api/submit', formData),
  {
    manual: true,
    onSuccess: (result, params) => {
      message.success('提交成功');
    },
    onError: (error) => {
      message.error('提交失败');
    }
  }
);
```

### 场景2：分页加载
```typescript
const { data, loading, pagination } = useRequest(
  ({ current, pageSize }) => {
    return request.get('/api/list', {
      params: {
        page: current,
        pageSize,
      },
    });
  },
  {
    paginated: true,
    defaultPageSize: 10,
  }
);
```

### 场景3：文件上传
```typescript
const { loading, run } = useRequest(
  (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  {
    manual: true,
    onSuccess: (result) => {
      message.success('上传成功');
    },
  }
);
```

## 六、性能优化

### 1. 请求去重
```typescript
// 相同请求在pending时不会重复发送
const { data } = useRequest('/api/data', {
  cacheKey: 'userData', // 缓存key
  staleTime: 5 * 60 * 1000, // 5分钟缓存
});
```

### 2. 自动重试
```typescript
const { data, error, loading } = useRequest('/api/data', {
  retryCount: 3, // 失败重试3次
  retryInterval: 1000, // 重试间隔
  onErrorRetry: (error, key, config) => {
    // 自定义重试逻辑
    if (error.status === 500) {
      return;
    }
    // 重试
  }
});
```

### 3. 请求合并
```typescript
// 自动合并短时间内相同的请求
const { data: user } = useRequest('/api/user/1');
const { data: posts } = useRequest('/api/posts?userId=1');

// 会被合并为一次请求
const batchRequest = useRequest(['/api/user/1', '/api/posts?userId=1']);
```

## 七、总结

umi/request 通过以下方式解决了前端HTTP请求的核心痛点：

1. **统一配置**：一处配置，处处使用
2. **类型安全**：完整的TypeScript支持
3. **错误处理**：统一错误处理，避免重复代码
4. **性能优化**：自动缓存、请求合并、防抖节流
5. **开发体验**：完整的TypeScript支持，智能提示

通过umi/request，我们可以将更多的精力放在业务逻辑上，而不是重复的HTTP请求封装上，大大提升了开发效率和代码质量。

## 八、最佳实践

1. **统一错误处理**：在拦截器中统一处理错误
2. **类型安全**：为所有API定义TypeScript接口
3. **合理使用缓存**：根据业务场景设置合理的缓存策略
4. **监控与日志**：记录请求日志，便于问题排查
5. **性能监控**：监控请求耗时，优化慢请求

通过umi/request，我们可以构建更健壮、可维护的前端应用，让HTTP请求不再是开发的负担。