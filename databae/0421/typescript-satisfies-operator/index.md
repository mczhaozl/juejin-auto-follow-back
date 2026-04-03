# TypeScript satisfies 操作符完全指南：类型安全与类型推断的完美平衡

TypeScript 4.9 引入了一个强大的新特性：`satisfies` 操作符。它解决了类型注解与类型推断之间的矛盾，让我们在保持类型安全的同时，还能获得完整的类型推断。

## 一、为什么需要 satisfies

### 1. 传统类型注解的问题

```typescript
type Config = {
  name: string;
  port: number;
  debug: boolean;
};

const config: Config = {
  name: 'my-app',
  port: 3000,
  debug: true,
};

// 问题：类型被拓宽了，失去了字面量类型
config.name; // string，而不是 'my-app'
config.port; // number，而不是 3000
```

### 2. 没有类型注解的问题

```typescript
const config = {
  name: 'my-app',
  port: 3000,
  debug: true,
};

// 问题：没有类型检查，可能写错属性
config.namee = 'test'; // 不会报错！
config.port = '3000'; // 也不会报错！
```

### 3. satisfies 来了！

```typescript
type Config = {
  name: string;
  port: number;
  debug: boolean;
};

const config = {
  name: 'my-app',
  port: 3000,
  debug: true,
} satisfies Config;

// 完美！既有类型检查，又保留了字面量类型
config.name; // 'my-app'（字面量类型）
config.port; // 3000（字面量类型）
config.debug; // true（字面量类型）

// config.namee = 'test'; // 会报错！
// config.port = '3000'; // 会报错！
```

## 二、satisfies 基本用法

### 1. 基础类型验证

```typescript
// 验证字符串
const name = 'Alice' satisfies string;
const name2 = 123 satisfies string; // 错误

// 验证数字
const age = 25 satisfies number;
const age2 = '25' satisfies number; // 错误

// 验证布尔值
const isActive = true satisfies boolean;
```

### 2. 对象类型验证

```typescript
type User = {
  id: number;
  name: string;
  email: string;
  isAdmin?: boolean;
};

const user = {
  id: 1,
  name: 'Alice',
  email: 'alice@example.com',
} satisfies User;

user.id; // 1（字面量类型）
user.name; // 'Alice'（字面量类型）

const user2 = {
  id: '1', // 错误！id 应该是 number
  name: 'Bob',
  email: 'bob@example.com',
} satisfies User; // 报错
```

### 3. 数组类型验证

```typescript
type Product = {
  id: number;
  name: string;
  price: number;
};

const products = [
  { id: 1, name: 'Apple', price: 5 },
  { id: 2, name: 'Banana', price: 3 },
  { id: 3, name: 'Orange', price: 4 },
] satisfies Product[];

products[0].name; // 'Apple'（字面量类型）
```

### 4. 联合类型验证

```typescript
type Status = 'pending' | 'approved' | 'rejected';

const status1 = 'pending' satisfies Status;
const status2 = 'approved' satisfies Status;
const status3 = 'unknown' satisfies Status; // 错误！

type Response = 
  | { success: true; data: string }
  | { success: false; error: string };

const response1 = {
  success: true,
  data: 'Hello',
} satisfies Response;

const response2 = {
  success: false,
  error: 'Something went wrong',
} satisfies Response;
```

## 三、高级用法

### 1. 保留字面量类型

```typescript
type RouteConfig = {
  path: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  handler: () => void;
};

const routes = {
  home: {
    path: '/',
    method: 'GET',
    handler: () => console.log('Home'),
  },
  user: {
    path: '/user',
    method: 'GET',
    handler: () => console.log('User'),
  },
  createUser: {
    path: '/user',
    method: 'POST',
    handler: () => console.log('Create User'),
  },
} satisfies Record<string, RouteConfig>;

// 完美的类型推断！
routes.home.method; // 'GET'（字面量类型）
routes.createUser.method; // 'POST'（字面量类型）

// 可以安全地使用这些字面量类型
function handleRoute(route: typeof routes[keyof typeof routes]) {
  if (route.method === 'GET') {
    // 这里 route.method 被正确收窄为 'GET'
  }
}
```

### 2. 与 as const 结合使用

```typescript
type Theme = {
  colors: {
    primary: string;
    secondary: string;
  };
  spacing: {
    small: number;
    large: number;
  };
};

const theme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
  },
  spacing: {
    small: 8,
    large: 16,
  },
} as const satisfies Theme;

// 完美！既有类型检查，又有完全的 readonly 字面量类型
theme.colors.primary; // '#007bff'（readonly 字面量类型）
theme.spacing.small; // 8（readonly 字面量类型）

// theme.colors.primary = '#ff0000'; // 错误！readonly
```

### 3. 验证函数返回值

```typescript
type ApiResponse<T> = {
  success: boolean;
  data: T;
  message?: string;
};

function fetchUser(): ApiResponse<{ id: number; name: string }> {
  return {
    success: true,
    data: { id: 1, name: 'Alice' },
  } satisfies ApiResponse<{ id: number; name: string }>;
}

function fetchUser2() {
  return {
    success: true,
    data: { id: 1, name: 'Alice' },
  } satisfies ApiResponse<{ id: number; name: string }>;
}

const result = fetchUser2();
result.data.name; // 'Alice'（字面量类型）
```

### 4. 复杂嵌套对象

```typescript
type AppConfig = {
  server: {
    host: string;
    port: number;
    ssl?: boolean;
  };
  database: {
    url: string;
    poolSize: number;
  };
  features: {
    enableCache: boolean;
    enableLog: boolean;
  };
};

const config = {
  server: {
    host: 'localhost',
    port: 5432,
    ssl: true,
  },
  database: {
    url: 'postgresql://localhost:5432/mydb',
    poolSize: 20,
  },
  features: {
    enableCache: true,
    enableLog: true,
  },
} satisfies AppConfig;

config.server.host; // 'localhost'（字面量类型）
config.features.enableCache; // true（字面量类型）
```

## 四、实际应用场景

### 1. 配置对象

```typescript
type FeatureFlags = {
  darkMode: boolean;
  notifications: boolean;
  analytics: boolean;
};

const featureFlags = {
  darkMode: true,
  notifications: true,
  analytics: false,
} satisfies FeatureFlags;

if (featureFlags.darkMode) {
  // 这里 featureFlags.darkMode 是 true，类型收窄完美
  document.documentElement.classList.add('dark');
}

if (featureFlags.analytics) {
  // 这里不会执行，类型系统知道 analytics 是 false
  initAnalytics();
}
```

### 2. API 路由定义

```typescript
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE';

type Route = {
  path: string;
  method: HttpMethod;
  handler: (req: Request) => Response | Promise<Response>;
};

const routes = {
  '/users': {
    path: '/users',
    method: 'GET',
    handler: async (req) => {
      return new Response(JSON.stringify({ users: [] }));
    },
  },
  '/users/:id': {
    path: '/users/:id',
    method: 'GET',
    handler: async (req) => {
      return new Response(JSON.stringify({ user: {} }));
    },
  },
  '/users': {
    path: '/users',
    method: 'POST',
    handler: async (req) => {
      return new Response('Created', { status: 201 });
    },
  },
} satisfies Record<string, Route>;

// 类型安全的路由注册
for (const [key, route] of Object.entries(routes)) {
  console.log(`Registering ${route.method} ${route.path}`);
}
```

### 3. 组件 Props

```typescript
type ButtonProps = {
  variant: 'primary' | 'secondary' | 'danger';
  size: 'small' | 'medium' | 'large';
  disabled?: boolean;
};

const buttonConfigs = {
  primary: {
    variant: 'primary',
    size: 'medium',
  },
  secondary: {
    variant: 'secondary',
    size: 'medium',
  },
  danger: {
    variant: 'danger',
    size: 'large',
    disabled: true,
  },
} satisfies Record<string, ButtonProps>;

function Button(props: ButtonProps) {
  const config = buttonConfigs[props.variant] || buttonConfigs.primary;
  // ...
}
```

### 4. 状态管理

```typescript
type AppState = {
  user: {
    id: number;
    name: string;
    email: string;
  } | null;
  theme: 'light' | 'dark';
  notifications: string[];
};

const initialState = {
  user: null,
  theme: 'light',
  notifications: [],
} satisfies AppState;

type Action =
  | { type: 'SET_USER'; payload: AppState['user'] }
  | { type: 'SET_THEME'; payload: AppState['theme'] }
  | { type: 'ADD_NOTIFICATION'; payload: string };

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case 'SET_USER':
      return { ...state, user: action.payload };
    case 'SET_THEME':
      return { ...state, theme: action.payload };
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [...state.notifications, action.payload],
      };
    default:
      return state;
  }
}
```

## 五、与其他 TypeScript 特性的对比

### 1. satisfies vs 类型注解

```typescript
type User = { id: number; name: string };

// 类型注解：失去字面量类型
const user1: User = { id: 1, name: 'Alice' };
user1.id; // number
user1.name; // string

// satisfies：保留字面量类型
const user2 = { id: 1, name: 'Alice' } satisfies User;
user2.id; // 1
user2.name; // 'Alice'
```

### 2. satisfies vs as const

```typescript
type User = { id: number; name: string };

// as const：只读，但没有类型检查
const user1 = { id: 1, name: 'Alice' } as const;
user1.id; // 1（readonly）
user1.name; // 'Alice'（readonly）
// user1.id = 2; // 错误！

// satisfies：有类型检查，但可变
const user2 = { id: 1, name: 'Alice' } satisfies User;
user2.id; // 1（可变）
user2.name; // 'Alice'（可变）
user2.id = 2; // 没问题！

// 两者结合：完美！
const user3 = { id: 1, name: 'Alice' } as const satisfies User;
user3.id; // 1（readonly，有类型检查）
```

### 3. satisfies vs 类型断言

```typescript
type User = { id: number; name: string };

// 类型断言：不安全，会跳过类型检查
const user1 = { id: '1', name: 'Alice' } as User; // 不会报错！

// satisfies：安全，会进行类型检查
const user2 = { id: '1', name: 'Alice' } satisfies User; // 会报错！
```

## 六、常见陷阱与最佳实践

### 1. 不要过度使用 satisfies

```typescript
// ❌ 没必要使用 satisfies
const name = 'Alice' satisfies string;
const age = 25 satisfies number;

// ✅ 直接赋值即可
const name = 'Alice';
const age = 25;
```

### 2. 配合类型收窄使用

```typescript
type Status = 'pending' | 'approved' | 'rejected';

const order = {
  status: 'pending' as Status,
  amount: 100,
};

// 问题：类型没有被收窄
if (order.status === 'pending') {
  // 这里 order.status 仍然是 Status，不是 'pending'
}

const order2 = {
  status: 'pending',
  amount: 100,
} satisfies { status: Status; amount: number };

// 完美！类型被收窄了
if (order2.status === 'pending') {
  // 这里 order2.status 是 'pending'
}
```

### 3. 可选属性的处理

```typescript
type Config = {
  name: string;
  debug?: boolean;
};

const config1 = {
  name: 'my-app',
} satisfies Config;

config1.debug; // undefined | boolean（因为 debug 是可选的）

const config2 = {
  name: 'my-app',
  debug: true,
} satisfies Config;

config2.debug; // true（字面量类型）
```

## 七、实战案例：类型安全的状态机

```typescript
type State = 'idle' | 'loading' | 'success' | 'error';

type StateMachine = {
  [K in State]: {
    on: {
      [event: string]: State;
    };
  };
};

const stateMachine = {
  idle: {
    on: {
      FETCH: 'loading',
    },
  },
  loading: {
    on: {
      SUCCESS: 'success',
      ERROR: 'error',
    },
  },
  success: {
    on: {
      FETCH: 'loading',
      RESET: 'idle',
    },
  },
  error: {
    on: {
      RETRY: 'loading',
      RESET: 'idle',
    },
  },
} satisfies StateMachine;

class Machine {
  private currentState: State = 'idle';

  transition(event: string) {
    const nextState = stateMachine[this.currentState].on[event];
    if (nextState) {
      this.currentState = nextState;
      console.log(`Transitioned to: ${this.currentState}`);
    } else {
      console.log(`Invalid event: ${event} in state: ${this.currentState}`);
    }
  }

  getState() {
    return this.currentState;
  }
}

const machine = new Machine();
machine.transition('FETCH'); // loading
machine.transition('SUCCESS'); // success
machine.transition('RESET'); // idle
```

## 八、总结

`satisfies` 操作符是 TypeScript 中一个非常强大的特性，它：

1. **保持类型安全**：验证值是否符合类型
2. **保留类型推断**：不丢失字面量类型信息
3. **灵活性强**：适用于对象、数组、函数等各种场景
4. **易于使用**：语法简单，易于理解和应用

最佳实践：
- 在需要类型检查但又想保留字面量类型时使用
- 可以与 `as const` 结合使用获得更强的类型安全
- 不要在简单类型上过度使用

掌握 `satisfies`，让你的 TypeScript 代码更加类型安全和灵活！

## 参考资料

- [TypeScript 4.9 Release Notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
- [TypeScript Handbook: satisfies Operator](https://www.typescriptlang.org/docs/handbook/2/everyday-types.html#the-satisfies-operator)
- [Understanding TypeScript's satisfies Operator](https://blog.logrocket.com/understanding-typescript-satisfies-operator/)
