# 深入理解 ES 空值合并运算符??与可选链?.

掌握这两个语法糖，写出更优雅的 JavaScript 代码。

## 一、为什么需要??和?.

在日常开发中，我们经常需要处理变量可能为 `null` 或 `undefined` 的情况。传统的做法是使用逻辑或运算符 `||` 来提供默认值，但这种做法有一个隐蔽的陷阱。

```javascript
const count = 0;
const total = count || 10;
console.log(total); // 输出 10，而不是预期的 0
```

上面的代码中，`count` 的值是 `0`，这是一个有效的数值，但 `||` 会把它当作「假值」处理，返回默认值 10。这显然不是我们想要的结果。

空值合并运算符 `??` 和可选链 `?.` 的出现，正是为了解决这类问题。它们只会在值为 `null` 或 `undefined` 时才进行默认值的处理，而不会误伤 `0`、`false`、`''` 这样的「假值」。

## 二、空值合并运算符??

### 2.1 基本用法

空值合并运算符 `??` 会在左侧表达式值为 `null` 或 `undefined` 时返回右侧的默认值，否则返回左侧的值。

```javascript
const count = 0;
const total = count ?? 10;
console.log(total); // 输出 0，正确！

const name = null;
const displayName = name ?? 'Anonymous';
console.log(displayName); // 输出 'Anonymous'

const age = undefined;
const userAge = age ?? 18;
console.log(userAge); // 输出 18
```

### 2.2 与||的区别

让我们通过一个对比表格来清晰展示两者的区别：

| 左侧值 | `a ?? b` 结果 | `a || b` 结果 |
|--------|---------------|---------------|
| `null` | `b` | `b` |
| `undefined` | `b` | `b` |
| `0` | `0` | `b` |
| `false` | `false` | `b` |
| `''` | `''` | `b` |
| `'hello'` | `'hello'` | `'hello'` |

从表格可以看出，`??` 只会对 `null` 和 `undefined` 「过敏」，而 `||` 会对所有假值过敏。在需要保留 `0`、`false`、`''` 这样的有效值的场景下，`??` 是更安全的选择。

### 2.3 链式使用

`??` 可以链式使用，但需要注意优先级问题：

```javascript
const a = null;
const b = undefined;
const c = 0;
const d = '';

const result1 = a ?? b ?? c ?? 'default';
console.log(result1); // 输出 0

const result2 = a ?? b ?? d ?? 'default';
console.log(result2); // 输出 ''
```

链式使用时，`??` 会从左到右找到第一个非 null/undefined 的值就返回。

### 2.4 注意事项

`??` 不能与 `&&` 或 `||` 直接混用，需要使用括号明确优先级：

```javascript
// 错误写法 - 会抛出 SyntaxError
const invalid = null || undefined ?? 'default';

// 正确写法 - 使用括号明确优先级
const valid1 = (null || undefined) ?? 'default';
const valid2 = null || (undefined ?? 'default');
```

## 三、可选链?.

### 3.1 基本用法

可选链运算符 `?.` 允许你安全地访问嵌套对象的属性，即使中间某个属性不存在也不会报错。

```javascript
const user = {
  name: 'Alice',
  address: {
    city: 'Beijing'
  }
};

// 传统写法 - 需要先判断每一层
const city1 = user && user.address && user.address.city;

// 使用可选链 - 简洁安全
const city2 = user?.address?.city;
console.log(city2); // 输出 'Beijing'

// 访问不存在的属性
const country = user?.address?.country;
console.log(country); // 输出 undefined，不会报错
```

### 3.2 多种用法

可选链不仅可以用在属性访问上，还支持方法调用和数组索引：

```javascript
// 方法调用
const result = obj?.method?.();

// 数组索引
const firstItem = arr?.[0];

// 动态属性名
const value = obj?.[key];
```

### 3.3 实际应用场景

在实际开发中，可选链特别适合处理以下场景：

```javascript
// 1. 处理表单数据
const formData = {
  user: {
    profile: {
      name: 'Bob'
    }
  }
};

// 安全获取用户名，即使中间某层不存在
const userName = formData?.user?.profile?.name ?? 'Guest';

// 2. 处理 API 响应
async function fetchUser() {
  const response = await fetch('/api/user');
  const data = await response.json();
  
  // 安全访问嵌套数据
  const email = data?.user?.contact?.email ?? 'no-email';
  const avatar = data?.user?.profile?.avatar ?? '/default-avatar.png';
  
  return { email, avatar };
}

// 3. 处理可选的回调函数
function handleClick(event) {
  // 某些情况下 onClick 可能未定义
  event?.preventDefault?.();
  callback?.(event);
}
```

### 3.4 短路求值

可选链具有短路求值的特性：如果 `?.` 左侧的值为 `null` 或 `undefined`，右侧的表达式不会被执行。

```javascript
const obj = null;
let count = 0;

// 不会执行，因为 obj 为 null
const result = obj?.method(() => count++);

console.log(count); // 输出 0，callback 没有被执行
```

这个特性在包含副作用的表达式中特别有用，可以避免不必要的函数调用。

## 四、组合使用?.??

`?.` 和 `??` 可以组合使用，处理更复杂的场景：

```javascript
const config = {
  database: {
    host: null,
    port: 5432
  }
};

// 安全获取数据库配置，主机为空时使用默认值
const dbHost = config?.database?.host ?? 'localhost';
const dbPort = config?.database?.port ?? 3306;

console.log(dbHost); // 输出 'localhost'
console.log(dbPort); // 输出 5432

// 处理深层嵌套的配置对象
const settings = {
  ui: {
    theme: {
      colors: null
    }
  }
};

const primaryColor = settings?.ui?.theme?.colors?.primary ?? '#1890ff';
console.log(primaryColor); // 输出 '#1890ff'
```

## 五、TypeScript 中的使用

在 TypeScript 中使用 `??` 和 `?.` 时，类型系统能够正确推断出可能的类型：

```typescript
interface User {
  name: string;
  address?: {
    city: string;
    zipCode?: string;
  };
}

const user: User = {
  name: 'Alice'
};

// 可选链返回 undefined 或 string，类型为 string | undefined
const city = user.address?.city;

// 空值合并确保最终类型为 string
const zipCode = user.address?.zipCode ?? '000000';
```

## 六、浏览器兼容性

截至 2026 年，`??` 和 `?.` 已经在所有主流浏览器中得到支持，包括 Chrome、Firefox、Safari 和 Edge 的最新版本。对于需要兼容旧版浏览器的项目，可以使用 Babel 或 TypeScript 进行转译。

```json
// .babelrc 或 babel.config.js
{
  "plugins": [
    "@babel/plugin-proposal-optional-chaining",
    "@babel/plugin-proposal-nullish-coalescing-operator"
  ]
}
```

## 七、常见误区

第一个误区是认为 `??` 可以完全替代 `||`。实际上，`||` 在需要区分「未设置」和「设置了假值」的场景下仍然有用。比如表单验证中，空字符串可能是一个有效的输入值。

第二个误区是过度使用可选链。虽然可选链很方便，但在确定某属性一定存在的情况下，使用普通属性访问（`.`）性能更好，代码意图也更清晰。

第三个误区是在条件判断中混用 `??` 和 `&&`/`||`。由于运算符优先级不同，混用时必须使用括号来明确意图。

## 总结

`??` 和 `?.` 是 ES2020 引入的两个非常实用的语法糖。`??` 解决了 `||` 在处理假值时的误伤问题，`?.` 让深层嵌套对象的访问变得安全简洁。合理使用这两个特性，可以让你的 JavaScript 代码更加健壮和优雅。

如果这篇文章对你有帮助，欢迎点赞、收藏和关注。