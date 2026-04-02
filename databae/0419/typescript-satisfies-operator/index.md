# TypeScript `satisfies` 操作符完全指南

> 一句话摘要：深入解析 TypeScript 4.9 引入的 `satisfies` 操作符，掌握如何同时获得类型推断和类型验证，提升你的 TypeScript 代码质量。

## 一、背景与问题

### 1.1 传统类型声明的困境

在 TypeScript 中，我们经常面临一个两难选择：是使用类型注解牺牲类型推断，还是保持推断却失去类型检查？

```typescript
// 方案 1：类型注解 —— 失去类型推断
const config1: Record<string, string | number> = {
    port: 8080,
    host: "localhost",
    debug: true  // ❌ 错误：debug 是 boolean，不是 string | number
};
// TypeScript 会报错，但我们失去了具体的类型信息

// 方案 2：类型推断 —— 失去类型验证
const config2 = {
    port: 8080,
    host: "localhost",
    debug: true  // ✅ 推断为 { port: number; host: string; debug: boolean }
};
// TypeScript 没有报错，但我们无法确保 config2 符合预期格式

// 方案 3：双重标注 —— 代码冗余
const config3: { port: number; host: string } = {
    port: 8080,
    host: "localhost"
};
// 既保证类型，又保留推断，但写起来麻烦
```

### 1.2 `satisfies` 的诞生

TypeScript 4.9 引入了 `satisfies` 操作符来解决这个困境：

```typescript
// 使用 satisfies —— 鱼与熊掌兼得
const config = {
    port: 8080,
    host: "localhost",
    debug: true
} satisfies ConfigType;

// ✅ 类型被验证是否符合 ConfigType
// ✅ 同时保留了 config 的具体类型推断（{ port: number; host: string; debug: boolean }）
```

### 1.3 本文目标

1. 理解 `satisfies` 的核心概念
2. 掌握各种使用场景
3. 学会配合其他 TypeScript 特性使用
4. 了解最佳实践和注意事项

## 二、核心概念

### 2.1 基本语法

```typescript
// 语法结构
expression satisfies Type

// 实际示例
type RGB = [red: number, green: number, blue: number];
const palette = {
    red: [255, 0, 0],
    green: "#00ff00",
    blue: [0, 0, 255]
} satisfies Record<string, RGB | string>;

// palette 的类型是：
// {
//     red: RGB;
//     green: string;
//     blue: RGB;
// }
// 而不是 Record<string, RGB | string>
```

### 2.2 类型推断 vs 类型验证

```typescript
// 场景：定义一个配置对象
type Config = {
    port: number;
    host: string;
    protocol: "http" | "https";
};

// 传统方式 1：类型注解
const config1: Config = {
    port: 8080,
    host: "localhost",
    protocol: "http"
};
// ✅ 类型检查通过
// ❌ config1.port 被推断为 number，但 Config 允许任意 number
//    如果 Config 变成 { port: 80 | 8080 }，config1 仍然有效（因为 number 兼容）

// satisfies 方式
const config2 = {
    port: 8080,
    host: "localhost",
    protocol: "http"
} satisfies Config;
// ✅ 类型检查通过
// ✅ config2.port 是具体的字面量类型 8080，而不是 number
```

### 2.3 关键特性

#### 特性 1：保留字面量类型

```typescript
type Direction = "north" | "south" | "east" | "west";

const directions1: Direction[] = ["north", "south"];  // string[] 被推断
const directions2 = ["north", "south"] satisfies Direction[];  // ("north" | "south")[] 被推断

// 差异：
directions1.push("任意字符串");  // ✅ 允许（类型为 string[]）
directions2.push("任意字符串");  // ❌ 错误（类型为 ("north" | "south")[]）
```

#### 特性 2：联合类型成员验证

```typescript
type StringOrNumber = string | number;

const mixed = {
    a: "hello",
    b: 42,
    c: true  // ❌ 这里会报错，因为 c: boolean 不在 StringOrNumber 中
} satisfies Record<string, StringOrNumber>;
```

#### 特性 3：嵌套对象验证

```typescript
type Nested = {
    user: {
        name: string;
        age: number;
    };
    settings: {
        theme: "light" | "dark";
        notifications: boolean;
    };
};

const data = {
    user: {
        name: "张三",
        age: 25
    },
    settings: {
        theme: "dark",
        notifications: true
    }
} satisfies Nested;

// data.user.name 是 string 类型
// data.settings.theme 是 "light" | "dark" 类型
```

## 三、实战应用场景

### 3.1 配置对象验证

```typescript
// 场景 1：应用配置
type AppConfig = {
    server: {
        port: number;
        host: string;
    };
    database: {
        url: string;
        poolSize: number;
    };
    features: string[];
};

const appConfig = {
    server: {
        port: 3000,
        host: "localhost"
    },
    database: {
        url: "postgresql://localhost/mydb",
        poolSize: 10
    },
    features: ["auth", "logging", "analytics"]
} satisfies AppConfig;

// ✅ 验证通过
// ✅ appConfig.server.port 是 number 类型（具体值 3000）
// ✅ appConfig.features 是 string[] 类型

// 访问时获得完整类型提示
appConfig.server.port  // number
appConfig.features[0]  // string
```

### 3.2 路由配置

```typescript
// 场景 2：路由表定义
type Route = {
    path: string;
    component: string;
    meta?: {
        title?: string;
        requiresAuth?: boolean;
    };
};

const routes = {
    home: {
        path: "/",
        component: "HomePage"
    },
    about: {
        path: "/about",
        component: "AboutPage",
        meta: {
            title: "关于我们"
        }
    },
    login: {
        path: "/login",
        component: "LoginPage",
        meta: {
            requiresAuth: false
        }
    },
    profile: {
        path: "/profile",
        component: "ProfilePage",
        meta: {
            title: "个人中心",
            requiresAuth: true
        }
    }
} satisfies Record<string, Route>;

// ✅ 类型安全
// ✅ 可以用 routes.home.path 访问
// ✅ meta 的可选属性都被正确处理

// 类型推断示例
type RouteKey = keyof typeof routes;
// type RouteKey = "home" | "about" | "login" | "profile"

routes.home.meta?.requiresAuth  // boolean | undefined
```

### 3.3 主题与样式系统

```typescript
// 场景 3：设计令牌系统
type DesignToken = string | number;

type Theme = {
    colors: Record<string, DesignToken>;
    spacing: Record<string, number>;
    fonts: Record<string, string>;
};

const theme = {
    colors: {
        primary: "#007bff",
        secondary: "#6c757d",
        success: "#28a745",
        error: "#dc3545",
        white: "#ffffff"
    },
    spacing: {
        xs: 4,
        sm: 8,
        md: 16,
        lg: 24,
        xl: 32
    },
    fonts: {
        sans: "system-ui, sans-serif",
        mono: "Monaco, monospace"
    }
} satisfies Theme;

// 使用示例
function createStyles(colorKey: keyof typeof theme.colors) {
    return { color: theme.colors[colorKey] };
}

createStyles("primary");  // ✅ 正确
createStyles("unknown");  // ❌ 类型错误
```

### 3.4 状态机定义

```typescript
// 场景 4：有限状态机
type State = "idle" | "loading" | "success" | "error";

type Transition = {
    from: State;
    to: State;
    guard?: (ctx: Context) => boolean;
};

type StateMachine = {
    initial: State;
    transitions: Transition[];
    context: Context;
};

const machine = {
    initial: "idle" as const,
    transitions: [
        { from: "idle", to: "loading" },
        { from: "loading", to: "success" },
        { from: "loading", to: "error" },
        { from: "error", to: "loading" }
    ],
    context: {
        retryCount: 0,
        lastError: null as Error | null
    }
} satisfies StateMachine;

// 类型安全的状态机
type StateKey = typeof machine.initial;
// type StateKey = "idle"
```

### 3.5 API 响应结构

```typescript
// 场景 5：API 响应类型
type ApiResponse<T> = {
    data: T;
    status: number;
    message?: string;
};

type UserResponse = {
    data: {
        id: string;
        name: string;
        email: string;
    };
    status: 200;
};

const userResponse = {
    data: {
        id: "user_123",
        name: "张三",
        email: "zhangsan@example.com"
    },
    status: 200
} satisfies ApiResponse<{ id: string; name: string; email: string }>;

// userResponse.data.name 是 string
// userResponse.status 是字面量 200
```

### 3.6 插件/扩展系统

```typescript
// 场景 6：插件注册表
type Plugin = {
    name: string;
    version: string;
    init: (app: App) => void;
    dependencies?: string[];
};

type PluginRegistry = Record<string, Plugin>;

const registry = {
    auth: {
        name: "Auth Plugin",
        version: "1.0.0",
        init: (app) => {
            console.log("Initializing auth...");
        }
    },
    logger: {
        name: "Logger Plugin",
        version: "2.0.0",
        init: (app) => {
            console.log("Initializing logger...");
        },
        dependencies: ["auth"]  // 依赖 auth 插件
    },
    analytics: {
        name: "Analytics Plugin",
        version: "1.5.0",
        init: (app) => {
            console.log("Initializing analytics...");
        }
    }
} satisfies PluginRegistry;

// registry 是 Record<string, Plugin>
// 同时保留了每个插件的具体类型

function loadPlugin(name: keyof typeof registry) {
    const plugin = registry[name];
    plugin.init(app);  // 完整类型提示
}
```

## 四、高级用法

### 4.1 结合类型推断

```typescript
// 使用 infer 推断 satisfies 的结果类型
type InferSatisfies<T, U> = T extends satisfies U ? T : never;

// 示例
type Colors = "red" | "green" | "blue";

const myColors = ["red", "green"] satisfies Colors[];
// myColors 的类型是 ("red" | "green")[]

// 结合 typeof
const baseColors = ["red", "green", "blue"] as const;
type BaseColors = typeof baseColors;
// type BaseColors = readonly ["red", "green", "blue"]

const userColors = ["red", "green"] satisfies typeof baseColors;
// userColors 的类型是 ("red" | "green")[]
```

### 4.2 条件类型中的 satisfies

```typescript
// 根据 satisfies 结果改变类型
type ValidateConfig<T> = T satisfies Record<string, unknown>
    ? { [K in keyof T]: T[K] }
    : never;

// 使用
type Result = ValidateConfig<{ port: number; host: string }>;
// Result = { port: number; host: string }

type InvalidResult = ValidateConfig<"not an object">;
// InvalidResult = never
```

### 4.3 多层嵌套验证

```typescript
// 复杂的嵌套类型
type DeepConfig = {
    level1: {
        level2: {
            level3: {
                value: number;
                label: string;
            }[];
        };
    };
};

const deepConfig = {
    level1: {
        level2: {
            level3: [
                { value: 1, label: "One" },
                { value: 2, label: "Two" }
            ]
        }
    }
} satisfies DeepConfig;

// deepConfig.level1.level2.level3[0].value 是 number
// deepConfig.level1.level2.level3[0].label 是 string
```

### 4.4 与 readonly 配合

```typescript
// 不可变配置
type ImmutableConfig = {
    readonly [key: string]: string | number;
};

const immutableConfig = {
    apiUrl: "https://api.example.com",
    timeout: 5000
} satisfies ImmutableConfig;

// 如果尝试修改会报错
immutableConfig.apiUrl = "other";  // ❌ 错误（假设 ApiUrl 不在类型中）
```

### 4.5 与 as const 配合

```typescript
// 结合 as const 实现完全字面量类型
const strictRoutes = {
    home: "/",
    about: "/about",
    contact: "/contact"
} as const satisfies Record<string, string>;

// 所有值都是字面量类型
type RoutePath = typeof strictRoutes[keyof typeof strictRoutes];
// type RoutePath = "/" | "/about" | "/contact"
```

## 五、与 typeof 的区别

### 5.1 基本对比

```typescript
const obj = {
    x: 1,
    y: "hello"
};

// typeof 获取类型
type ObjType = typeof obj;
// type ObjType = { x: number; y: string; }

// satisfies 验证并保留推断
const validated = {
    x: 1,
    y: "hello"
} satisfies { x: number; y: string };
// validated 的类型仍然是 { x: number; y: string }

// 关键区别：typeof 不验证，satisfies 验证
```

### 5.2 实际差异

```typescript
// 示例 1：超出类型的字段
const obj1 = {
    x: 1,
    y: 2,
    z: 3  // 额外的字段
};

type Obj1Type = typeof obj1;
// type Obj1Type = { x: number; y: number; z: number; }
// ✅ 没有错误，额外字段被保留

const obj2 = {
    x: 1,
    y: 2
} satisfies { x: number; y: string };
// ❌ 错误：y: number 不能赋值给 string | number
```

### 5.3 组合使用

```typescript
// 最佳实践：先 satisfies 验证，再 typeof 提取类型
const validatedConfig = {
    port: 8080,
    host: "localhost",
    debug: false
} satisfies {
    port: number;
    host: string;
    debug?: boolean;
};

// 用 typeof 提取新类型
type Config = typeof validatedConfig;
// type Config = {
//     port: number;
//     host: string;
//     debug: boolean | undefined;
// }

// 两者结合的优势：
// 1. 验证初始对象符合预期结构
// 2. 提取出带完整推断的新类型供其他地方使用
```

## 六、常见问题与解决方案

### 6.1 问题 1：可选属性处理

```typescript
// 问题
type Config = {
    required: string;
    optional?: number;
};

const config = {
    required: "value"
} satisfies Config;
// ✅ 正确，可选属性可以省略

// 但如果想访问 optional，需要处理 undefined
const opt: number | undefined = config.optional;
```

### 6.2 问题 2：联合类型验证

```typescript
// 问题：如何验证值属于联合类型
type Color = "red" | "green" | "blue";

const colors = ["red", "green", "purple"] satisfies Color[];
// ❌ 错误：purple 不在 Color 中

// 解决方案：使用类型谓词
function isColor(val: string): val is Color {
    return ["red", "green", "blue"].includes(val);
}

function filterColors(arr: string[]): Color[] {
    return arr.filter(isColor);
}
```

### 6.3 问题 3：类属性验证

```typescript
// satisfies 不能用于类
class Config {
    port = 8080;
}

const config = new Config() satisfies { port: number };
// ❌ 错误：satisfies 不能用于类实例

// 解决方案：使用类型断言或 separate 类型检查
const config = new Config();
const checked: { port: number } = config as { port: number };
```

### 6.4 问题 4：泛型中的 satisfies

```typescript
// 问题：泛型约束
function processConfig<T extends { port: number }>(
    config: T satisfies T
) {
    // 这个语法不对
}

// 正确用法
function processConfig<T>(
    config: T satisfies { port: number }
) {
    // config 是 T 类型，同时满足 { port: number }
}
```

## 七、性能考虑

### 7.1 类型检查开销

```typescript
// satisfies 在编译时进行类型检查
// 对运行时性能没有影响

// 但复杂的多层嵌套 satisfies 可能增加编译时间
const veryComplex = {
    // 100+ 嵌套层
} satisfies VeryDeepNestedType;
// 编译时间可能增加
```

### 7.2 最佳实践

```typescript
// ✅ 推荐：明确的类型定义
type KnownShape = {
    a: string;
    b: number;
};

const good = { a: "x", b: 1 } satisfies KnownShape;

// ❌ 不推荐：过度嵌套
const bad = {
    level1: {
        level2: {
            // 更多层...
        }
    }
} satisfies DeepType;
```

## 八、迁移指南

### 8.1 从类型断言迁移

```typescript
// 旧代码（使用类型断言）
const config = {
    port: 8080
} as {
    port: number;
};

// 新代码（使用 satisfies）
const config = {
    port: 8080
} satisfies {
    port: number;
};

// 差异：
// as：不验证类型，可能导致意外的类型宽化
// satisfies：验证类型，同时保留字面量推断
```

### 8.2 从类型注解迁移

```typescript
// 旧代码（使用类型注解）
const config: {
    port: number;
    host: string;
} = {
    port: 8080,
    host: "localhost"
};

// 新代码（使用 satisfies）
const config = {
    port: 8080,
    host: "localhost"
} satisfies {
    port: number;
    host: string;
};

// 优势：
// 1. 错误信息更明确（如果类型不匹配，指向具体字段）
// 2. 保留字面量类型推断
```

## 九、与其他 TypeScript 特性的对比

### 9.1 vs 类型别名

```typescript
type A = string | number;
type B = "a" | "b";

// satisfies 验证值是否符合类型
const val = "a" satisfies B;
```

### 9.2 vs 类型守卫

```typescript
// 类型守卫需要在运行时检查
function isConfig(val: unknown): val is Config {
    return typeof val === "object" && val !== null && "port" in val;
}

// satisfies 在编译时验证
const config = {} satisfies Config;
```

### 9.3 vs 类型断言

```typescript
// 类型断言（as）不验证
const a = "hello" as number;  // ❌ 没有错误，但类型是错的

// satisfies 验证
const b = "hello" satisfies number;  // ✅ 错误：string 不能赋值给 number
```

## 十、总结

### 10.1 关键要点

1. **`satisfies` 在编译时验证类型，同时保留类型推断**
2. **它解决了类型注解和类型推断的两难困境**
3. **适用于配置对象、路由表、主题系统等场景**
4. **可以与 `typeof`、泛型、条件类型等配合使用**

### 10.2 使用建议

- ✅ 使用 `satisfies` 验证配置对象和常量
- ✅ 使用 `satisfies` 替代 `as` 类型断言
- ✅ 使用 `satisfies` 保留字面量类型推断
- ❌ 不要在简单场景过度使用
- ❌ 不要用 `satisfies` 替代运行时验证

### 10.3 资源推荐

- [TypeScript 4.9 Release Notes](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)
- [TypeScript satisfies Operator](https://www.typescriptlang.org/docs/handbook/2/typeof-types.html#the-satisfies-operator)

> 如果对你有帮助，欢迎点赞、收藏！
