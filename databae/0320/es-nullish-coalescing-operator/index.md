# 告别 Try-Catch：ES 新运算符让错误处理变得如此优雅

> 深入理解 ?= 赋值运算符与逻辑空赋值，简化代码提升可读性

---

## 一、从繁琐的错误处理说起

我们在日常开发中，经常会遇到这样的代码：

```javascript
// 传统写法：需要手动检查 null/undefined
let config = null;
if (options !== null && options !== undefined) {
  config = options;
} else {
  config = defaultConfig;
}

// 或者使用三元运算符
const config = options !== null && options !== undefined ? options : defaultConfig;

// 或者使用 || 运算符（但有陷阱）
const config = options || defaultConfig; // ❌ 如果 options 是空字符串或 0，会被错误覆盖
```

这种写法不仅冗长，而且容易出错。当 `options` 是 `0`、`false` 或空字符串时，`||` 运算符会错误地使用默认值。

## 二、?= 逻辑空赋值运算符

### 2.1 基本用法

ES2021 引入的 `??=` 运算符（逻辑空赋值）完美解决了这个问题：

```javascript
let config = null;
config ??= defaultConfig; // 只有当 config 是 null 或 undefined 时才赋值
console.log(config); // defaultConfig

config = 'custom';
config ??= defaultConfig; // config 已有值，不会被覆盖
console.log(config); // custom
```

### 2.2 与 || 的对比

```javascript
// 使用 || 的问题
let count = 0;
count = count || 10; // ❌ 结果是 10，不是 0
console.log(count); // 10

// 使用 ??= 的正确做法
let count = 0;
count ??= 10; // ✅ 结果是 0，正确
console.log(count); // 0

// 实际场景
function processValue(value) {
  value ??= 'default';
  return value.toUpperCase();
}

processValue(null);      // 'DEFAULT'
processValue(undefined); // 'DEFAULT'
processValue('hello');   // 'HELLO'
processValue(0);         // '0' ✅ 正确保留 0
processValue(false);     // false ✅ 正确保留 false
```

### 2.3 实际应用场景

**场景一：配置对象合并**

```javascript
function createAppConfig(userConfig) {
  const defaultConfig = {
    theme: 'light',
    language: 'zh-CN',
    apiUrl: 'https://api.example.com',
    timeout: 5000
  };

  const config = { ...defaultConfig };
  
  // 使用 ??= 合并用户配置
  config.theme ??= userConfig.theme;
  config.language ??= userConfig.language;
  config.apiUrl ??= userConfig.apiUrl;
  config.timeout ??= userConfig.timeout;
  
  return config;
}

const userConfig = { theme: 'dark' };
const config = createAppConfig(userConfig);
console.log(config);
// { theme: 'dark', language: 'zh-CN', apiUrl: 'https://api.example.com', timeout: 5000 }
```

**场景二：表单默认值**

```javascript
function createUserProfile(formData) {
  const profile = {
    name: formData.name ?? '匿名用户',
    age: formData.age ?? 18,
    bio: formData.bio ?? '这个人很懒，什么都没写',
    avatar: formData.avatar ?? '/default-avatar.png'
  };
  
  return profile;
}

console.log(createUserProfile({ name: '张三' }));
// { name: '张三', age: 18, bio: '这个人很懒，什么都没写', avatar: '/default-avatar.png' }
```

**场景三：缓存数据初始化**

```javascript
class DataCache {
  constructor() {
    this.cache = new Map();
  }
  
  getOrCompute(key, computeFn) {
    if (!this.cache.has(key)) {
      this.cache.set(key, computeFn());
    }
    return this.cache.get(key);
  }
  
  // 使用 ??= 简化
  getOrCompute2(key, computeFn) {
    this.cache.get(key) ??= computeFn();
    return this.cache.get(key);
  }
}

const cache = new DataCache();
const expensiveResult = cache.getOrCompute2('expensive-key', () => {
  console.log('Computing...');
  return heavyComputation();
});
```

## 三、完整的空值处理运算符家族

### 3.1 逻辑或赋值 ||=

```javascript
let value = 0;
value ||= 10; // 0 是 falsy 值，会被覆盖
console.log(value); // 10
```

### 3.2 逻辑与赋值 &&=

```javascript
let obj = { enabled: true };
obj.enabled &&= false; // 只有为 truthy 时才赋值
console.log(obj.enabled); // false

obj = { enabled: false };
obj.enabled &&= true; // 已经是 false，不会被覆盖
console.log(obj.enabled); // false
```

### 3.3 可选链 ?. 与空值合并 ??

```javascript
const user = {
  name: '张三',
  address: {
    city: '北京'
  }
};

// 可选链访问深层属性
const city = user.address?.city; // '北京'
const country = user.address?.country; // undefined
const zip = user.address?.zip?.code; // undefined

// 组合使用
const zipCode = user.address?.zip?.code ?? '000000';
console.log(zipCode); // '000000'
```

### 3.4 运算符优先级

```javascript
// 运算符优先级：??= 与 ||=、&&= 相同
let a = null, b = null, c = null;

a ??= b || c; // 先执行 b || c，再 ??= a
console.log(a); // null（因为 b || c 是 null）

a = null;
(a ??= b) || c; // 先执行 a ??= b，再 || c
console.log(a); // null

// 实际使用建议：使用括号明确意图
let config = null;
let options = null;

(config ??= {}) || options; // 明确：先赋值 config，再逻辑或
```

## 四、实战：构建健壮的数据处理函数

### 4.1 配置解析器

```javascript
function parseConfig(rawConfig) {
  const config = {
    // 基础配置
    debug: rawConfig.debug ?? false,
    verbose: rawConfig.verbose ?? false,
    
    // 服务器配置
    host: rawConfig.host ?? 'localhost',
    port: rawConfig.port ?? 8080,
    
    // 功能开关
    enableCache: rawConfig.enableCache ?? true,
    enableCompression: rawConfig.enableCompression ?? true,
    
    // 限制配置
    maxConnections: rawConfig.maxConnections ?? 100,
    timeout: rawConfig.timeout ?? 30000,
    
    // 白名单
    allowedOrigins: rawConfig.allowedOrigins ?? ['http://localhost:3000']
  };
  
  return config;
}

// 测试
console.log(parseConfig({ port: 9000, enableCache: false }));
/*
{
  debug: false,
  verbose: false,
  host: 'localhost',
  port: 9000,
  enableCache: false,
  enableCompression: true,
  maxConnections: 100,
  timeout: 30000,
  allowedOrigins: ['http://localhost:3000']
}
*/
```

### 4.2 API 响应处理

```javascript
class ApiResponse {
  constructor(data, error) {
    this.data = data ?? null;
    this.error = error ?? null;
    this.success = data !== null && error === null;
  }
  
  static ok(data) {
    return new ApiResponse(data, null);
  }
  
  static fail(error) {
    return new ApiResponse(null, error);
  }
  
  getOrDefault(defaultValue) {
    return this.data ?? defaultValue;
  }
}

const response = ApiResponse.ok({ user: '张三' });
console.log(response.getOrDefault({ user: '默认用户' })); // { user: '张三' }

const errorResponse = ApiResponse.fail('Network error');
console.log(errorResponse.getOrDefault({ user: '默认用户' })); // { user: '默认用户' }
```

### 4.3 状态管理器

```javascript
class StateManager {
  constructor(initialState) {
    this.state = initialState ?? {};
    this.listeners = [];
  }
  
  setState(updates) {
    const newState = { ...this.state };
    
    for (const [key, value] of Object.entries(updates)) {
      // 只更新非 undefined 的值
      if (value !== undefined) {
        newState[key] = value;
      }
    }
    
    this.state = newState;
    this.notify();
  }
  
  // 使用 ??= 简化
  setState2(updates) {
    const newState = { ...this.state };
    
    for (const [key, value] of Object.entries(updates)) {
      newState[key] ??= value; // 只���原值为 undefined 时更新
    }
    
    this.state = newState;
    this.notify();
  }
  
  get(key) {
    return this.state[key];
  }
  
  getOr(key, defaultValue) {
    return this.state[key] ?? defaultValue;
  }
  
  notify() {
    this.listeners.forEach(fn => fn(this.state));
  }
}

// 使用示例
const store = new StateManager({ count: 0, theme: 'light' });
store.setState2({ count: null, theme: undefined, language: 'zh' });
console.log(store.state); // { count: 0, theme: 'light', language: 'zh' }
```

## 五、常见陷阱与解决方案

### 5.1 与 || 混用的陷阱

```javascript
// ❌ 错误示例
let value = 0;
value = value || 10; // 0 被覆盖为 10

// ✅ 正确示例
let value = 0;
value = value ?? 10; // 0 被保留
```

### 5.2 链式赋值的注意事项

```javascript
// ❌ 错误示例
let a = null, b = null, c = null;
a ??= b ??= c ??= 10;
console.log(a, b, c); // 10, 10, 10 - 所有变量都被赋值

// ✅ 正确示例：明确意图
let a = null, b = null, c = null;
a ??= 10;
b ??= 10;
c ??= 10;
console.log(a, b, c); // 10, 10, 10
```

### 5.3 对象属性的空值赋值

```javascript
const user = { name: '张三' };

// ❌ 错误：会覆盖整个对象
user.settings ??= { theme: 'dark' };

// ✅ 正确：使用解构赋值
user.settings = user.settings ?? { theme: 'dark' };

// ✅ 更优雅：使用可选链和空值合并
user.settings ??= { theme: 'dark' }; // 实际上这是正确的！
// 因为 ??= 只会修改 undefined 的属性，不会覆盖已有对象
```

## 六、性能与最佳实践

### 6.1 性能对比

```javascript
// Benchmark: ??= vs traditional approach
function benchmark() {
  const iterations = 1000000;
  
  // 方式一：三元运算符
  console.time('ternary');
  for (let i = 0; i < iterations; i++) {
    const value = i % 2 === 0 ? null : i;
    const result = value !== null && value !== undefined ? value : 0;
  }
  console.timeEnd('ternary');
  
  // 方式二：??= 运算符
  console.time('nullish-assignment');
  for (let i = 0; i < iterations; i++) {
    const value = i % 2 === 0 ? null : i;
    let result = 0;
    result ??= value;
  }
  console.timeEnd('nullish-assignment');
}
```

### 6.2 代码规范建议

```javascript
// ✅ 推荐：使用 ??= 处理默认值
function createUser(options) {
  const user = {
    name: options.name ?? '匿名',
    age: options.age ?? 18,
    role: options.role ?? 'user'
  };
  return user;
}

// ✅ 推荐：使用 &&= 处理开关
function toggleFeature(config, feature) {
  config.features[feature] &&= !config.features[feature];
  return config;
}

// ✅ 推荐：组合使用多种运算符
function processConfig(input) {
  const config = {
    debug: input.debug ?? false,
    verbose: input.verbose ?? false,
    maxRetries: input.maxRetries ?? 3
  };
  
  config.cacheEnabled &&= config.debug;
  config.logLevel ??= config.verbose ? 'debug' : 'info';
  
  return config;
}
```

## 七、浏览器与 Node.js 兼容性

### 7.1 支持情况

| 浏览器 | 版本 |
|--------|------|
| Chrome | 85+ |
| Firefox | 79+ |
| Safari | 14+ |
| Edge | 85+ |

| Node.js | 版本 |
|---------|------|
| Node.js | 15.0.0+ |

### 7.2 降级方案

```javascript
// 使用 Babel 插件转换
// babel.config.js
module.exports = {
  plugins: [
    '@babel/plugin-proposal-logical-assignment-operators'
  ]
};

// 转换后的代码
// a ??= b 转换为 a ?? (a = b)
```

## 八、总结

?= 逻辑空赋值运算符是 ES2021 引入的重要特性，它让代码更加简洁和健壮：

- **?=**：只在值为 null/undefined 时赋值
- **||=**：只在值为 falsy 时赋值
- **&&=**：只在值为 truthy 时赋值

这些运算符特别适合以下场景：

- 配置对象合并
- 表单默认值处理
- 缓存初始化
- 状态管理

掌握这些运算符，可以让你的代码更加优雅，减少样板代码，同时避免传统写法中的陷阱。

如果这篇文章对你有帮助，欢迎点赞收藏。
