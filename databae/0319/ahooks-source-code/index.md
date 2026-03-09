# ahooks 源码解析：useRequest 是如何实现的

> 深入 ahooks 源码，揭秘 useRequest 的缓存、轮询、重试等核心机制

---

## 一、为什么要读源码

useRequest 是 ahooks 最核心的 Hook，它封装了：
- 自动管理 loading/error/data
- 防抖节流
- 轮询
- 缓存
- 错误重试
- 依赖刷新

理解它的实现，能让你：
- 更好地使用 useRequest
- 学习优秀的 Hook 设计模式
- 自己封装类似的工具

---

## 二、核心架构

useRequest 采用插件化架构，核心代码非常简洁。

### 目录结构

```
useRequest/
├── index.ts          # 入口
├── useRequestImplement.ts  # 核心实现
├── Fetch.ts          # 请求管理类
└── plugins/          # 插件目录
    ├── useDebouncePlugin.ts
    ├── useThrottlePlugin.ts
    ├── usePollingPlugin.ts
    ├── useCachePlugin.ts
    └── useRetryPlugin.ts
```

---

## 三、核心实现：Fetch 类

Fetch 类负责管理单个请求的生命周期。

```typescript
class Fetch<TData, TParams extends any[]> {
  // 请求状态
  state: FetchState<TData, TParams> = {
    loading: false,
    data: undefined,
    error: undefined,
    params: undefined,
  };

  // 插件列表
  pluginImpls: PluginReturn<TData, TParams>[];

  constructor(
    serviceRef: MutableRefObject<Service<TData, TParams>>,
    options: Options<TData, TParams>,
    subscribe: () => void,
  ) {
    this.serviceRef = serviceRef;
    this.options = options;
    this.subscribe = subscribe;

    // 初始化插件
    this.pluginImpls = this.initPlugins();
  }

  // 执行请求
  async runAsync(...params: TParams): Promise<TData> {
    this.setState({ loading: true, params });

    // 执行 onBefore 插件钩子
    this.runPluginHandler('onBefore', params);

    try {
      // 调用 service
      const servicePromise = this.serviceRef.current(...params);
      const res = await servicePromise;

      // 执行 onSuccess 插件钩子
      this.runPluginHandler('onSuccess', res, params);

      this.setState({
        data: res,
        error: undefined,
        loading: false,
      });

      return res;
    } catch (error) {
      // 执行 onError 插件钩子
      this.runPluginHandler('onError', error, params);

      this.setState({
        error,
        loading: false,
      });

      throw error;
    }
  }

  // 运行插件钩子
  runPluginHandler(event: keyof PluginReturn, ...rest: any[]) {
    const r = this.pluginImpls.map(i => i[event]?.(...rest)).filter(Boolean);
    return Object.assign({}, ...r);
  }
}
```

---

## 四、插件系统

每个插件都是一个函数，返回生命周期钩子。

### 插件接口

```typescript
export interface PluginReturn<TData, TParams extends any[]> {
  onBefore?: (params: TParams) => void;
  onRequest?: (service: Service<TData, TParams>, params: TParams) => {
    servicePromise?: Promise<TData>;
  };
  onSuccess?: (data: TData, params: TParams) => void;
  onError?: (e: Error, params: TParams) => void;
  onFinally?: (params: TParams, data?: TData, e?: Error) => void;
  onCancel?: () => void;
  onMutate?: (data: TData) => void;
}
```

---

## 五、防抖插件实现

```typescript
const useDebouncePlugin: Plugin<any, any[]> = (
  fetchInstance,
  { debounceWait, debounceLeading, debounceTrailing, debounceMaxWait },
) => {
  const debouncedRef = useRef<DebouncedFunc<any>>();

  useEffect(() => {
    if (debounceWait) {
      const originRunAsync = fetchInstance.runAsync.bind(fetchInstance);

      // 用 lodash.debounce 包装 runAsync
      debouncedRef.current = debounce(
        (callback) => {
          callback();
        },
        debounceWait,
        {
          leading: debounceLeading,
          trailing: debounceTrailing,
          maxWait: debounceMaxWait,
        },
      );

      // 替换 runAsync
      fetchInstance.runAsync = (...args) => {
        return new Promise((resolve, reject) => {
          debouncedRef.current?.(() => {
            originRunAsync(...args)
              .then(resolve)
              .catch(reject);
          });
        });
      };

      return () => {
        debouncedRef.current?.cancel();
      };
    }
  }, [debounceWait, debounceLeading, debounceTrailing, debounceMaxWait]);

  return {};
};
```

---

## 六、缓存插件实现

```typescript
const cache = new Map<string, CachedData>();

const useCachePlugin: Plugin<any, any[]> = (
  fetchInstance,
  { cacheKey, cacheTime = 5 * 60 * 1000, staleTime = 0 },
) => {
  const unSubscribeRef = useRef<() => void>();

  useEffect(() => {
    if (!cacheKey) return;

    // 从缓存读取
    const cacheData = cache.get(cacheKey);
    if (cacheData && Date.now() - cacheData.time <= staleTime) {
      fetchInstance.state.data = cacheData.data;
      fetchInstance.state.params = cacheData.params;
    }
  }, [cacheKey]);

  return {
    onBefore: (params) => {
      if (!cacheKey) return {};

      const cacheData = cache.get(cacheKey);
      if (!cacheData || Date.now() - cacheData.time > staleTime) {
        return {};
      }

      // 返回缓存数据
      return {
        loading: false,
        data: cacheData?.data,
        error: undefined,
        returnNow: true,
      };
    },

    onSuccess: (data, params) => {
      if (!cacheKey) return;

      // 写入缓存
      cache.set(cacheKey, {
        data,
        params,
        time: Date.now(),
      });

      // 设置过期时间
      setTimeout(() => {
        cache.delete(cacheKey);
      }, cacheTime);
    },
  };
};
```

---

## 七、轮询插件实现

```typescript
const usePollingPlugin: Plugin<any, any[]> = (
  fetchInstance,
  { pollingInterval, pollingWhenHidden = true },
) => {
  const timerRef = useRef<NodeJS.Timeout>();
  const unsubscribeRef = useRef<() => void>();

  const stopPolling = () => {
    if (timerRef.current) {
      clearTimeout(timerRef.current);
    }
  };

  useEffect(() => {
    if (!pollingWhenHidden) {
      const visibilitychange = () => {
        if (document.hidden) {
          stopPolling();
        } else {
          // 页面可见时重新开始轮询
          fetchInstance.refresh();
        }
      };
      document.addEventListener('visibilitychange', visibilitychange);
      return () => {
        document.removeEventListener('visibilitychange', visibilitychange);
      };
    }
  }, [pollingWhenHidden]);

  return {
    onBefore: () => {
      stopPolling();
    },

    onFinally: () => {
      if (!pollingInterval) return;

      // 请求完成后，设置下次轮询
      timerRef.current = setTimeout(() => {
        fetchInstance.refresh();
      }, pollingInterval);
    },

    onCancel: () => {
      stopPolling();
    },
  };
};
```

---

## 八、重试插件实现

```typescript
const useRetryPlugin: Plugin<any, any[]> = (
  fetchInstance,
  { retryCount, retryInterval },
) => {
  const timerRef = useRef<NodeJS.Timeout>();
  const countRef = useRef(0);

  return {
    onBefore: () => {
      if (!retryCount) return {};

      countRef.current = 0;
    },

    onError: () => {
      if (!retryCount) return;

      countRef.current += 1;

      if (countRef.current <= retryCount) {
        const timeout = retryInterval ?? Math.min(1000 * 2 ** countRef.current, 30000);
        
        timerRef.current = setTimeout(() => {
          fetchInstance.refresh();
        }, timeout);
      }
    },

    onCancel: () => {
      if (timerRef.current) {
        clearTimeout(timerRef.current);
      }
    },
  };
};
```

---

## 九、useRequestImplement 核心

```typescript
function useRequestImplement<TData, TParams extends any[]>(
  service: Service<TData, TParams>,
  options: Options<TData, TParams> = {},
  plugins: Plugin<TData, TParams>[] = [],
) {
  const { manual = false, ...rest } = options;

  const fetchOptions = {
    manual,
    ...rest,
  };

  const serviceRef = useLatest(service);

  const [state, setState] = useState<Result<TData, TParams>>({
    loading: !manual,
    data: undefined,
    error: undefined,
  });

  const fetchInstance = useCreation(() => {
    return new Fetch<TData, TParams>(
      serviceRef,
      fetchOptions,
      () => {
        setState(fetchInstance.state);
      },
    );
  }, []);

  // 初始化插件
  fetchInstance.pluginImpls = plugins.map((p) =>
    p(fetchInstance, fetchOptions),
  );

  // 自动执行
  useEffect(() => {
    if (!manual) {
      fetchInstance.run(...(fetchOptions.defaultParams || []));
    }
  }, []);

  return {
    loading: state.loading,
    data: state.data,
    error: state.error,
    run: fetchInstance.run.bind(fetchInstance),
    runAsync: fetchInstance.runAsync.bind(fetchInstance),
    refresh: fetchInstance.refresh.bind(fetchInstance),
    cancel: fetchInstance.cancel.bind(fetchInstance),
    mutate: fetchInstance.mutate.bind(fetchInstance),
  };
}
```

---

## 十、设计亮点

### 1. 插件化架构

- 核心功能最小化
- 功能通过插件扩展
- 插件之间解耦

### 2. 生命周期钩子

- onBefore：请求前
- onRequest：请求中
- onSuccess：成功后
- onError：失败后
- onFinally：完成后
- onCancel：取消时

### 3. Ref 管理

- 用 useLatest 保持最新引用
- 避免闭包陷阱

### 4. 状态管理

- 单一 Fetch 实例管理状态
- 通过 subscribe 通知更新

---

## 总结

ahooks useRequest 的核心设计思想：

1. **插件化**：核心简洁，功能可扩展
2. **生命周期**：清晰的钩子机制
3. **状态管理**：单一实例管理
4. **Ref 优化**：避免闭包问题

这种设计模式值得在自己的项目中借鉴。

如果这篇文章对你有帮助，欢迎点赞收藏！
