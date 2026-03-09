# ahooks useRequest 深度解析：一个 Hook 搞定所有请求

> 从手动请求到自动管理，掌握 useRequest 的缓存、轮询、防抖、重试等核心能力

---

## 一、为什么需要 useRequest

在 React 项目中，我们经常需要处理各种请求场景：

```javascript
// 传统写法：代码冗长且容易出错
function UserProfile() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    setLoading(true);
    fetchUser()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);
  
  if (loading) return <Spin />;
  if (error) return <Error />;
  return <div>{data.name}</div>;
}
```

使用 useRequest：

```javascript
import { useRequest } from 'ahooks';

function UserProfile() {
  const { data, loading, error } = useRequest(fetchUser);
  
  if (loading) return <Spin />;
  if (error) return <Error />;
  return <div>{data.name}</div>;
}
```

---

## 二、核心功能详解

### 1. 自动管理请求状态

```javascript
const { data, loading, error, run, refresh, cancel } = useRequest(
  fetchUserList,
  {
    manual: false,  // 自动执行
    defaultParams: [{ page: 1 }],  // 默认参数
  }
);

// run: 手动触发
// refresh: 使用上次参数重新请求
// cancel: 取消当前请求
```

### 2. 防抖与节流

```javascript
// 搜索场景：防抖
const { data, loading } = useRequest(searchAPI, {
  debounceWait: 300,  // 300ms 防抖
  manual: true,
});

// 滚动加载：节流
const { run } = useRequest(loadMore, {
  throttleWait: 1000,  // 1s 节流
  manual: true,
});
```

### 3. 轮询

```javascript
// 每 3 秒轮询一次
const { data } = useRequest(getStatus, {
  pollingInterval: 3000,
  pollingWhenHidden: false,  // 页面隐藏时停止轮询
});

// 条件轮询
const { data } = useRequest(getJobStatus, {
  pollingInterval: 2000,
  pollingErrorRetryCount: 3,  // 错误重试次数
  onSuccess: (result) => {
    if (result.status === 'completed') {
      // 完成后停止轮询
      return false;
    }
  }
});
```

### 4. 依赖刷新

```javascript
const [userId, setUserId] = useState('1');

const { data } = useRequest(
  () => fetchUser(userId),
  {
    refreshDeps: [userId],  // userId 变化时自动重新请求
  }
);
```

### 5. 缓存机制

```javascript
// SWR 模式：先返回缓存，后台更新
const { data, loading } = useRequest(fetchUser, {
  cacheKey: 'user-data',
  staleTime: 5000,  // 5s 内认为数据新鲜
  cacheTime: 300000,  // 缓存保留 5 分钟
});

// 清除缓存
import { clearCache } from 'ahooks';
clearCache('user-data');
```

### 6. 错误重试

```javascript
const { data, error, retry } = useRequest(unstableAPI, {
  retryCount: 3,  // 失败后重试 3 次
  retryInterval: 1000,  // 重试间隔 1s
  onError: (error, params) => {
    console.log('请求失败', error);
  }
});
```

---

## 三、进阶场景

### 并行请求

```javascript
const user = useRequest(fetchUser);
const posts = useRequest(fetchPosts);
const comments = useRequest(fetchComments);

const loading = user.loading || posts.loading || comments.loading;
```

### 串行请求

```javascript
const { data: user } = useRequest(fetchUser);

const { data: posts } = useRequest(
  () => fetchUserPosts(user.id),
  {
    ready: !!user,  // user 存在时才执行
    refreshDeps: [user],
  }
);
```

### 分页加载

```javascript
function UserList() {
  const { data, loading, loadMore, loadingMore, noMore } = useRequest(
    (d) => fetchList({ page: d?.nextPage || 1 }),
    {
      loadMore: true,
      isNoMore: (d) => !d?.hasMore,
    }
  );
  
  return (
    <>
      {data?.list.map(item => <Item key={item.id} {...item} />)}
      {!noMore && (
        <Button onClick={loadMore} loading={loadingMore}>
          加载更多
        </Button>
      )}
    </>
  );
}
```

### 乐观更新

```javascript
const { run: deleteItem } = useRequest(deleteAPI, {
  manual: true,
  onBefore: (params) => {
    // 立即更新 UI
    setList(list => list.filter(item => item.id !== params[0]));
  },
  onError: (error, params) => {
    // 失败时回滚
    message.error('删除失败');
    refresh();
  }
});
```

---

## 四、与其他方案对比

| 特性 | useRequest | React Query | SWR |
|------|-----------|-------------|-----|
| 学习成本 | 低 | 中 | 低 |
| 功能完整度 | 高 | 很高 | 中 |
| 包体积 | 小 | 较大 | 小 |
| 防抖节流 | 内置 | 需自己实现 | 需自己实现 |
| 轮询 | 内置 | 内置 | 需配置 |
| TypeScript | 良好 | 优秀 | 良好 |

---

## 五、最佳实践

1. **合理使用缓存**：列表、详情等读多写少的数据适合缓存
2. **设置合适的防抖时间**：搜索建议 300-500ms
3. **避免过度轮询**：根据业务需求设置合理的轮询间隔
4. **善用 ready 参数**：避免无效请求
5. **统一错误处理**：在全局配置中处理通用错误

```javascript
// 全局配置
import { configResponsive } from 'ahooks';

configResponsive({
  onError: (error) => {
    if (error.code === 401) {
      // 统一处理未登录
      redirectToLogin();
    }
  }
});
```

---

## 六、源码解析（简化版）

useRequest 的核心实现思路：

```javascript
function useRequest(service, options) {
  const [state, setState] = useState({
    data: undefined,
    loading: false,
    error: undefined,
  });
  
  const run = useCallback(async (...params) => {
    setState(s => ({ ...s, loading: true }));
    
    try {
      const data = await service(...params);
      setState({ data, loading: false, error: undefined });
    } catch (error) {
      setState(s => ({ ...s, loading: false, error }));
    }
  }, [service]);
  
  useEffect(() => {
    if (!options.manual) {
      run(...(options.defaultParams || []));
    }
  }, []);
  
  return { ...state, run };
}
```

实际实现还包括：
- 防抖节流的 debounce/throttle 包装
- 轮询的 setInterval 管理
- 缓存的 Map 存储
- 依赖追踪的 useEffect
- 请求取消的 AbortController

---

## 总结

useRequest 是一个功能强大且易用的请求管理 Hook，它封装了日常开发中 90% 的请求场景。通过合理使用其提供的能力，可以大幅减少样板代码，提升开发效率。

推荐在中小型项目中直接使用 useRequest，大型项目可以考虑 React Query 获得更强的数据管理能力。

如果这篇文章对你有帮助，欢迎点赞收藏！
