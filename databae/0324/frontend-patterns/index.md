# 前端架构设计模式：构建可维护大型应用的实践指南

> 系统梳理前端架构中的核心设计模式，从组件设计到状态管理，从代码组织到性能优化

---

## 一、前端架构的挑战

随着应用规模增长，前端代码复杂度呈指数级上升。我们经常遇到：

- **组件膨胀**：单个文件数千行，修改任何功能都胆战心惊
- **状态混乱**：数据流向不清晰，不知道什么时候该用 state、props 还是 context
- **重复代码**：类似的功能在不同模块复制粘贴，维护成本高昂
- **新人上手难**：代码结构混乱，新成员需要很长时间才能理解项目

本文系统介绍前端架构设计模式，帮你构建清晰、可维护的代码体系。

## 二、组件设计模式

### 2.1 展示组件与容器组件

将组件职责分离是最基本的设计原则：

```tsx
// 展示组件：只负责 UI 渲染，不关心数据来源
const UserCard = ({ user, onEdit, onDelete }) => (
  <div className="user-card">
    <img src={user.avatar} alt={user.name} />
    <h3>{user.name}</h3>
    <p>{user.email}</p>
    <div className="actions">
      <button onClick={() => onEdit(user)}>编辑</button>
      <button onClick={() => onDelete(user.id)}>删除</button>
    </div>
  </div>
);

// 容器组件：负责数据获取和业务逻辑
const UserCardContainer = ({ userId }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(data => {
      setUser(data);
      setLoading(false);
    });
  }, [userId]);

  const handleEdit = (user) => {
    // 编辑逻辑
  };

  const handleDelete = async (id) => {
    await deleteUser(id);
    // 更新状态
  };

  if (loading) return <Skeleton />;
  if (!user) return <NotFound />;

  return <UserCard user={user} onEdit={handleEdit} onDelete={handleDelete} />;
};
```

### 2.2 高阶组件（HOC）

用于逻辑复用和横切关注点：

```tsx
// withLoading 高阶组件
const withLoading = (WrappedComponent) => {
  return function WithLoading({ isLoading, ...props }) {
    if (isLoading) return <LoadingSpinner />;
    return <WrappedComponent {...props} />;
  };
};

// withError 高阶组件
const withError = (WrappedComponent) => {
  return function WithError({ error, ...props }) {
    if (error) return <ErrorMessage error={error} />;
    return <WrappedComponent {...props} />;
  };
};

// 组合使用
const UserProfile = withError(
  withLoading(({ user }) => (
    <div>
      <h1>{user.name}</h1>
      <p>{user.bio}</p>
    </div>
  ))
);

// 使用
<UserProfile userId="123" isLoading={loading} error={error} />;
```

### 2.3 自定义 Hook 模式

将逻辑提取为可复用的 Hook：

```tsx
// useUser Hook
const useUser = (userId) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!userId) return;

    setLoading(true);
    fetchUser(userId)
      .then(data => {
        setUser(data);
        setError(null);
      })
      .catch(err => {
        setError(err);
        setUser(null);
      })
      .finally(() => {
        setLoading(false);
      });
  }, [userId]);

  return { user, loading, error };
};

// useUserList Hook（带分页）
const useUserList = (initialPage = 1) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(initialPage);
  const [hasMore, setHasMore] = useState(true);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    const newUsers = await fetchUsers(page + 1);

    if (newUsers.length === 0) {
      setHasMore(false);
    } else {
      setUsers(prev => [...prev, ...newUsers]);
      setPage(prev => prev + 1);
    }

    setLoading(false);
  }, [page, loading, hasMore]);

  return { users, loading, hasMore, loadMore };
};
```

### 2.4 复合组件模式

适用于需要紧密协作的组件族：

```tsx
// Select 组件组
const Select = ({ children, value, onChange }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [selectedValue, setSelectedValue] = value;

  const contextValue = {
    isOpen,
    open: () => setIsOpen(true),
    close: () => setIsOpen(false),
    value: selectedValue,
    onChange: (value) => {
      setSelectedValue(value);
      onChange?.(value);
      setIsOpen(false);
    }
  };

  return (
    <SelectContext.Provider value={contextValue}>
      <div className="select">{children}</div>
    </SelectContext.Provider>
  );
};

Select.Option = ({ value, children }) => {
  const { onChange, value: selectedValue } = useContext(SelectContext);
  const isSelected = selectedValue === value;

  return (
    <div
      className={`select-option ${isSelected ? 'selected' : ''}`}
      onClick={() => onChange(value)}
    >
      {children}
    </div>
  );
};

Select.Placeholder = ({ children }) => {
  const { isOpen, open } = useContext(SelectContext);
  return (
    <div className="select-placeholder" onClick={open}>
      {children}
    </div>
  );
};

// 使用
<Select value={selectedValue} onChange={setSelectedValue}>
  <Select.Placeholder>请选择...</Select.Placeholder>
  <Select.Option value="a">选项 A</Select.Option>
  <Select.Option value="b">选项 B</Select.Option>
</Select>;
```

## 三、状态管理模式

### 3.1 状态提升

当多个组件需要共享状态时：

```tsx
// 状态提升示例
const Parent = () => {
  const [filter, setFilter] = useState('all');
  const [items, setItems] = useState([]);

  const filteredItems = items.filter(item => {
    if (filter === 'all') return true;
    return item.status === filter;
  });

  return (
    <div>
      <FilterBar filter={filter} onFilterChange={setFilter} />
      <ItemList items={filteredItems} />
    </div>
  );
};
```

### 3.2 Context 模式

用于深层组件传值：

```tsx
// Theme Context
const ThemeContext = createContext();

const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider');
  }
  return context;
};

const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState('light');

  const value = useMemo(() => ({
    theme,
    setTheme,
    isDark: theme === 'dark',
    toggleTheme: () => setTheme(t => t === 'light' ? 'dark' : 'light')
  }), [theme]);

  return (
    <ThemeContext.Provider value={value}>
      <div className={`app theme-${theme}`}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
};
```

### 3.3 状态机模式

使用状态机管理复杂状态：

```tsx
// 简单的状态机
const useAsyncState = (asyncFunction) => {
  const [state, setState] = useState({
    status: 'idle',
    data: null,
    error: null
  });

  const execute = useCallback(async (...args) => {
    setState({ status: 'pending', data: null, error: null });

    try {
      const data = await asyncFunction(...args);
      setState({ status: 'success', data, error: null });
      return data;
    } catch (error) {
      setState({ status: 'error', data: null, error });
      throw error;
    }
  }, [asyncFunction]);

  return { ...state, execute };
};

// 使用
const { status, data, error, execute } = useAsyncState(fetchUser);

<button onClick={() => execute(userId)} disabled={status === 'pending'}>
  {status === 'pending' ? '加载中...' : '获取用户'}
</button>
```

### 3.4 不可变数据模式

使用 Immer 简化不可变操作：

```tsx
import { produce } from 'immer';

// 传统方式
const updateUser = (users, userId, updates) => {
  return users.map(user =>
    user.id === userId ? { ...user, ...updates } : user
  );
};

// Immer 方式
const updateUser = (users, userId, updates) => {
  return produce(users, draft => {
    const user = draft.find(u => u.id === userId);
    if (user) {
      Object.assign(user, updates);
    }
  });
};

// 深层更新
const addAddress = (user, newAddress) => {
  return produce(user, draft => {
    if (!draft.addresses) draft.addresses = [];
    draft.addresses.push(newAddress);
  });
};
```

## 四、代码组织模式

### 4.1 功能切片模式

按功能组织代码：

```
src/
├── features/
│   ├── auth/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   └── index.ts
│   ├── users/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── store/
│   │   └── index.ts
│   └── products/
│       ├── components/
│       ├── hooks/
│       ├── services/
│       ├── store/
│       └── index.ts
├── shared/
│   ├── components/
│   ├── hooks/
│   ├── utils/
│   └── constants/
└── App.tsx
```

### 4.2 依赖注入模式

解耦组件与具体实现：

```tsx
// API 服务接口
interface UserService {
  fetchUser(id: string): Promise<User>;
  updateUser(user: User): Promise<User>;
  deleteUser(id: string): Promise<void>;
}

// 默认实现
class DefaultUserService implements UserService {
  async fetchUser(id: string) {
    const res = await fetch(`/api/users/${id}`);
    return res.json();
  }
  // ...
}

// 注入上下文
const UserServiceContext = createContext<UserService | null>(null);

// Provider
const UserServiceProvider = ({ children, service }: Props) => (
  <UserServiceContext.Provider value={service}>
    {children}
  </UserServiceContext.Provider>
);

// 使用 Hook
const useUserService = () => {
  const service = useContext(UserServiceContext);
  if (!service) {
    throw new Error('User service not provided');
  }
  return service;
};

// 组件中使用
const UserProfile = () => {
  const userService = useUserService();
  const { data: user } = useQuery(['user', id], () => userService.fetchUser(id));
  // ...
};
```

### 4.3 特性开关模式

控制功能发布：

```tsx
// 特性开关配置
const features = {
  newCheckout: {
    enabled: process.env.NEW_CHECKOUT === 'true',
    rolloutPercent: 30
  },
  darkMode: {
    enabled: true,
    rolloutPercent: 100
  }
};

// 特性开关 Hook
const useFeature = (featureName) => {
  const feature = features[featureName];
  if (!feature || !feature.enabled) return false;

  // 百分比 rollout
  if (feature.rolloutPercent < 100) {
    const userId = getUserId();
    return (userId % 100) < feature.rolloutPercent;
  }

  return true;
};

// 使用
const CheckoutButton = () => {
  const newCheckoutEnabled = useFeature('newCheckout');

  if (newCheckoutEnabled) {
    return <NewCheckoutButton />;
  }

  return <LegacyCheckoutButton />;
};
```

## 五、性能优化模式

### 5.1 虚拟列表模式

```tsx
const VirtualList = ({ items, itemHeight, containerHeight }) => {
  const [scrollTop, setScrollTop] = useState(0);

  const startIndex = Math.floor(scrollTop / itemHeight);
  const endIndex = Math.min(
    startIndex + Math.ceil(containerHeight / itemHeight) + 2,
    items.length
  );

  const visibleItems = items.slice(startIndex, endIndex);
  const offsetY = startIndex * itemHeight;

  return (
    <div
      className="virtual-list"
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={e => setScrollTop(e.target.scrollTop)}
    >
      <div style={{ height: items.length * itemHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map((item, index) => (
            <div key={item.id} style={{ height: itemHeight }}>
              <ListItem item={item} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
```

### 5.2 预加载模式

```tsx
// 路由预加载
const useRoutePreload = (routes) => {
  const preloadTimer = useRef(null);

  const preloadOnHover = (routePath) => {
    const route = routes.find(r => r.path === routePath);
    if (!route) return;

    preloadTimer.current = setTimeout(() => {
      route.component.preload();
    }, 100);
  };

  const cancelPreload = () => {
    if (preloadTimer.current) {
      clearTimeout(preloadTimer.current);
    }
  };

  return { preloadOnHover, cancelPreload };
};

// 图片预加载
const useImagePreload = (srcList) => {
  useEffect(() => {
    srcList.forEach(src => {
      const img = new Image();
      img.src = src;
    });
  }, [srcList]);
};
```

### 5.3 骨架屏模式

```tsx
const Skeleton = ({ width, height, borderRadius }) => (
  <div
    className="skeleton"
    style={{
      width,
      height,
      borderRadius,
      background: 'linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 1.5s infinite'
    }}
  />
);

// 使用
const UserCardSkeleton = () => (
  <div className="user-card-skeleton">
    <Skeleton width={60} height={60} borderRadius="50%" />
    <Skeleton width="60%" height={20} />
    <Skeleton width="80%" height={16} />
  </div>
);
```

## 六、API 设计模式

### 6.1 适配器模式

统一不同 API 的返回格式：

```tsx
// 适配器函数
const userAdapter = (apiUser) => ({
  id: apiUser.user_id,
  name: apiUser.full_name || apiUser.username,
  email: apiUser.contact_email,
  avatar: apiUser.profile_picture?.url,
  createdAt: new Date(apiUser.created_timestamp)
});

// 使用适配器
const fetchUser = async (id) => {
  const apiUser = await apiClient.get(`/users/${id}`);
  return userAdapter(apiUser);
};
```

### 6.2 统一错误处理

```tsx
// 错误处理中间件
const createApiClient = (baseUrl) => {
  const client = axios.create({ baseURL: baseUrl });

  client.interceptors.response.use(
    response => response.data,
    error => {
      if (error.response) {
        // 服务器返回错误
        const apiError = new Error(error.response.data.message);
        apiError.code = error.response.data.code;
        apiError.status = error.response.status;
        throw apiError;
      }

      if (error.request) {
        // 请求发送失败
        throw new Error('网络请求失败，请检查网络连接');
      }

      throw error;
    }
  );

  return client;
};

// 使用
const api = createApiClient('https://api.example.com');

try {
  const user = await api.get('/users/123');
} catch (error) {
  if (error.status === 401) {
    // 未授权，跳转登录
    navigate('/login');
  } else if (error.status === 404) {
    // 资源不存在
    showToast('用户不存在');
  } else {
    // 其他错误
    showToast(error.message);
  }
}
```

### 6.3 请求缓存模式

```tsx
const createCachedApi = (apiClient) => {
  const cache = new Map();
  const cacheTTL = 5 * 60 * 1000; // 5分钟

  const getCacheKey = (method, url, params) =>
    `${method}:${url}:${JSON.stringify(params)}`;

  const cachedFetch = async (method, url, params = {}) => {
    const key = getCacheKey(method, url, params);
    const cached = cache.get(key);

    if (cached && Date.now() - cached.time < cacheTTL) {
      return cached.data;
    }

    const data = await apiClient[method](url, params);

    cache.set(key, { data, time: Date.now() });
    return data;
  };

  return {
    get: (url, params) => cachedFetch('get', url, params),
    post: (url, data) => cachedFetch('post', url, data),
    clearCache: () => cache.clear()
  };
};
```

## 七、测试友好模式

### 7.1 依赖注入便于测试

```tsx
// 可测试的组件
const UserList = ({ fetchUsers, renderUser }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUsers().then(data => {
      setUsers(data);
      setLoading(false);
    });
  }, [fetchUsers]);

  if (loading) return <Loading />;

  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>{renderUser(user)}</li>
      ))}
    </ul>
  );
};

// 测试
test('renders users', async () => {
  const mockUsers = [{ id: 1, name: 'John' }];
  const mockFetchUsers = jest.fn().mockResolvedValue(mockUsers);

  render(<UserList fetchUsers={mockFetchUsers} renderUser={u => u.name} />);

  expect(mockFetchUsers).toHaveBeenCalled();
  expect(await screen.findByText('John')).toBeInTheDocument();
});
```

### 7.2 测试替身模式

```tsx
// Mock Service Worker
import { setupServer } from 'msw/node';
import { rest } from 'msw';

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(
      ctx.json([
        { id: 1, name: 'John' },
        { id: 2, name: 'Jane' }
      ])
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## 八、总结

前端架构设计模式的核心目标是：

- **可维护性**：代码结构清晰，易于理解和修改
- **可测试性**：组件职责单一，便于单元测试
- **可复用性**：逻辑抽象为通用模式，减少重复代码
- **可扩展性**：支持功能扩展，不破坏现有结构

掌握这些模式，并根据项目实际情况灵活运用，能显著提升代码质量和开发效率。

如果这篇文章对你有帮助，欢迎点赞收藏。
