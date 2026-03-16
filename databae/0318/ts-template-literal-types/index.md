# TypeScript 模板字面量类型高级用法

> 掌握类型体操技巧，让类型推导更精确。

## 一、模板字面量类型是什么

模板字面量类型是 TypeScript 4.1 引入的强大特性，它允许你在类型层面使用类似 JavaScript 模板字符串的语法。通过这个特性，你可以基于已有的字符串类型构造出新的字符串类型，实现精确的类型推导和约束。

在介绍具体用法之前，让我们先理解模板字面量类型的基本语法：

```typescript
type Greeting = `Hello, ${string}`;
const greeting1: Greeting = 'Hello, World';  // ✓ 正确
const greeting2: Greeting = 'Hi, there';     // ✗ 错误，不匹配模式
```

`Greeting` 类型表示所有以「Hello, 」开头的字符串。只有符合这个模式的字符串才能赋值给 `Greeting` 类型的变量。

## 二、模板字面量类型的基本用法

### 2.1 字符串拼接类型

模板字面量类型最基础的用法是拼接字符串：

```typescript
type Part1 = 'Hello';
type Part2 = 'World';
type Greeting = `${Part1} ${Part2}`;
// Greeting 类型为 "Hello World"
```

### 2.2 使用联合类型

模板字面量类型可以与联合类型配合使用，生成所有可能的组合：

```typescript
type Direction = 'top' | 'bottom' | 'left' | 'right';
type MarginProperty = `margin${Capitalize<Direction>}`;
// MarginProperty 类型为 "marginTop" | "marginBottom" | "marginLeft" | "marginRight"

type BorderProperty = `border${Capitalize<Direction>}-width`;
// BorderProperty 类型为 "borderTop-width" | "borderBottom-width" | ...
```

注意这里使用了 TypeScript 内置的 `Capitalize` 工具类型，它可以将字符串类型的首字母转为大写。

### 2.3 内置工具类型

TypeScript 提供了几个与模板字面量类型配合使用的内置工具类型：

- `Uppercase<StringType>`：将字符串转为大写
- `Lowercase<StringType>`：将字符串转为小写
- `Capitalize<StringType>`：将首字母转为大写
- `Uncapitalize<StringType>`：将首字母转为小写

```typescript
type EventName = 'click' | 'hover' | 'focus';
type UpperEventName = `${Uppercase<EventName>}`;
// "CLICK" | "HOVER" | "FOCUS"

type HandlerName = `on${Capitalize<EventName>}`;
// "onClick" | "onHover" | "onFocus"
```

## 三、实战：CSS 属性类型生成

让我们通过一个实际场景来深入理解模板字面量类型的用法。假设我们需要为 CSS 属性生成对应的类型定义：

```typescript
// 定义所有可能的 CSS 属性前缀
type CssPropertyPrefix = '' | 'webkit' | 'moz' | 'ms' | 'o';

// 定义属性名
type CssPropertyName = 
  | 'transform' | 'transition' | 'animation'
  | 'flex' | 'grid';

// 生成完整的 CSS 属性名
type CssProperty = `${CssPropertyPrefix}${Capitalize<CssPropertyName>}`;
// 结果："" | "WebkitTransform" | "MozTransform" | "MsTransform" | "OTransform" | ...
```

更复杂的例子，生成带值的 CSS 属性类型：

```typescript
type CssValue = 'auto' | '0' | '100%' | '1px' | '2px';
type CssPropertyWithValue = `${CssProperty} ${CssValue}`;
// 例如："transform auto" | "transform 0" | "WebkitTransform 100%" | ...
```

## 四、模板字面量类型与infer

模板字面量类型最强大的用法是配合 `infer` 关键字进行模式匹配和类型提取：

### 4.1 提取字符串中的特定部分

```typescript
// 提取事件名称
type ExtractEventName<T> = T extends `on${infer Name}` ? Name : never;

type ClickEvent = ExtractEventName<'onClick'>;      // "Click"
type HoverEvent = ExtractEventName<'onHover'>;      // "Hover"
type CustomEvent = ExtractEventName<'onCustom'>;    // "Custom"
```

### 4.2 提取路径中的文件名

```typescript
type ExtractFileName<T> = T extends `${string}/${infer Name}` ? Name : T;

type FileName1 = ExtractFileName<'/src/components/Button.tsx'>;  // "Button.tsx"
type FileName2 = ExtractFileName<'index.ts'>;                    // "index.ts"
```

### 4.3 提取驼峰命名并转换

```typescript
type CamelToKebab<T extends string> = 
  T extends `${infer First}${infer Rest}`
    ? First extends Uppercase<First>
      ? `-${Lowercase<First>}${CamelToKebab<Rest>}`
      : `${First}${CamelToKebab<Rest>}`
    : T;

type KebabCase = CamelToKebab<'backgroundColor'>;  // "background-color"
type KebabCase2 = CamelToKebab<'borderRadius'>;    // "border-radius"
```

### 4.4 提取并转换 URL 参数

```typescript
type ExtractQueryParams<T extends string> = 
  T extends `${string}?${infer Query}`
    ? Query extends `${infer Key}=${infer Value}&${infer Rest}`
      ? { [K in Key]: Value } & ExtractQueryParams<`?${Rest}`>
      : Query extends `${infer Key}=${infer Value}`
        ? { [K in Key]: Value }
        : {}
    : {};

type Params = ExtractQueryParams<'/api/users?id=1&name=jack&age=25'>;
// { id: "1" } & { name: "jack" } & { age: "25" }
```

## 五、模板字面量类型在React中的应用

### 5.1 组件 Props 类型推导

```typescript
type Size = 'small' | 'medium' | 'large';
type Color = 'primary' | 'secondary' | 'danger';

type ButtonVariant = `${Size}-${Color}`;
// "small-primary" | "small-secondary" | "small-danger" | ...

interface ButtonProps {
  variant: ButtonVariant;
  onClick: `handle${Capitalize<ButtonVariant>}`;
// 例如：handleSmallPrimary | handleSmallSecondary | ...
}

function createHandler(variant: ButtonVariant): ButtonProps['onClick'] {
  return `handle${variant}` as ButtonProps['onClick'];
}
```

### 5.2 状态更新函数类型

```typescript
type Setter<T extends string> = `set${Capitalize<T>}`;

interface State {
  name: string;
  age: number;
  email: string;
}

type StateSetters = {
  [K in keyof State as Setter<string & K>]: (value: State[K]) => void
};

// Setter<"name"> = "setName"
// 结果类型：{ setName: (value: string) => void; setAge: (value: number) => void; ... }
```

### 5.3 路由参数类型

```typescript
type RouteParams<T extends string> = 
  T extends `${string}:${infer Param}/${infer Rest}`
    ? { [K in Param]: string } & RouteParams<`/${Rest}`>
    : T extends `${string}:${infer Param}`
      ? { [K in Param]: string }
      : {};

type BlogRoute = RouteParams<'/blog/:id/:slug'>;
// { id: string } & { slug: string }

type UserRoute = RouteParams<'/users/:id'>;
// { id: string }
```

## 六、模板字面量类型与映射类型

模板字面量类型可以与映射类型结合，批量生成相关的类型：

```typescript
type APIResponse = {
  code: number;
  message: string;
  data: unknown;
};

type APIAction = 'login' | 'register' | 'logout' | 'profile';

type APIEndpoint = `/${APIAction}`;

type APIResponses = {
  [K in APIAction as `${K}${string}`]: APIResponse;
};

// 结果：
// {
//   login: APIResponse;
//   loginSuccess: APIResponse;
//   loginFailed: APIResponse;
//   register: APIResponse;
//   ...
// }
```

更实用的例子，生成表单验证规则类型：

```typescript
type ValidationRule = 'required' | 'minLength' | 'maxLength' | 'pattern';
type FieldName = 'email' | 'password' | 'username' | 'phone';

type ValidationConfig = {
  [F in FieldName as `${F}${Capitalize<ValidationRule>}`]: 
    F extends 'email' 
      ? { pattern: RegExp } | { required: true }
      : F extends 'password'
        ? { minLength: number } | { required: true }
        : { required: true } | { minLength: number; maxLength: number }
};

// emailRequired: { pattern: RegExp } | { required: true }
// passwordMinLength: { minLength: number } | { required: true }
// usernameRequired: { required: true } | { minLength: number; maxLength: number }
```

## 七、模板字面量类型的性能考虑

模板字面量类型在编译时计算，过度复杂的类型推导可能会影响 TypeScript 的编译性能。以下是一些优化建议：

首先，避免在模板字面量类型中使用过深的递归。深度递归的类型推导会显著增加类型检查的时间。

```typescript
// 不推荐：深层递归
type DeepCamelToKebab<T extends string, Acc extends string = ''> = 
  T extends `${infer First}${infer Rest}`
    ? First extends Uppercase<First>
      ? DeepCamelToKebab<Rest, `${Acc}-${Lowercase<First>}`>
      : DeepCamelToKebab<Rest, `${Acc}${First}`>
    : Acc;

// 推荐：限制递归深度或使用条件类型简化
type SimpleCamelToKebab<T extends string> = 
  T extends `${infer A}${infer B}`
    ? A extends Uppercase<A>
      ? `-${Lowercase<A>}${SimpleCamelToKebab<B>}`
      : `${A}${SimpleCamelToKebab<B>}`
    : T;
```

其次，使用 `extends` 约束来缩小类型范围，减少类型计算量：

```typescript
// 不推荐：无约束的类型推导
type ExtractFromString<T> = T extends `${string}${infer Rest}` ? Rest : T;

// 推荐：添加约束
type ExtractFromString<T extends string> = 
  T extends `${string}${infer Rest}` ? Rest : T;
```

第三，对于复杂的类型计算，考虑使用类型别名缓存结果：

```typescript
// 缓存计算结果
type CachedKebabCase<T extends string> = KebabCaseMap[T];

// 预先计算映射
type KebabCaseMap = {
  backgroundColor: 'background-color';
  borderRadius: 'border-radius';
  color: 'color';
  // ... 更多预计算的类型
};
```

## 八、模板字面量类型的调试技巧

复杂的模板字面量类型往往难以调试。以下是几个实用的调试技巧：

第一个技巧是使用中间类型别名来分解复杂类型：

```typescript
// 原始复杂类型
type ComplexType = `${Prefix}${Capitalize<Name>}${Suffix}`;

// 分解为多个中间类型
type Step1 = Capitalize<Name>;
type Step2 = `${Prefix}${Step1}`;
type Step3 = `${Step2}${Suffix}`;
```

第二个技巧是使用条件类型产生错误信息：

```typescript
// 通过错误信息查看实际类型
type Debug<T> = T extends string ? never : T;
type Result = Debug<YourComplexType>;  // 错误信息会显示实际类型
```

第三个技巧是使用 `typeof` 和模板字面量类型结合：

```typescript
const config = {
  apiUrl: 'https://api.example.com',
  version: 'v1',
} as const;

type Endpoint = `${typeof config.apiUrl}/${typeof config.version}/${string}`;
// "https://api.example.com/v1/${string}"
```

## 九、常见问题与解决方案

### 9.1 模板字面量类型不生效

确保你使用的是 TypeScript 4.1 或更高版本。在较旧的 TypeScript 版本中，模板字面量类型可能不被支持。

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020"],
    "typescriptVersion": ">=4.1.0"
  }
}
```

### 9.2 联合类型在模板字面量中的行为

当模板字面量类型中的某部分是一个联合类型时，结果会是所有可能组合的联合：

```typescript
type A = 'x' | 'y';
type B = '1' | '2';
type C = `${A}${B}`;
// "x1" | "x2" | "y1" | "y2"
```

### 9.3 大小写转换工具类型

TypeScript 的内置大小写转换工具类型只对 ASCII 字符有效。如果你需要处理其他语言的字符，可能需要自定义实现：

```typescript
type UppercaseFirst<T extends string> = 
  T extends `${infer First}${infer Rest}`
    ? `${Uppercase<First>}${Rest}`
    : T;

type LowercaseFirst<T extends string> = 
  T extends `${infer First}${infer Rest}`
    ? `${Lowercase<First>}${Rest}`
    : T;
```

## 十、总结

模板字面量类型是 TypeScript 类型系统中最强大的特性之一。它不仅可以让你的类型定义更加精确和类型安全，还能在编译时捕获许多潜在的类型错误。通过掌握模板字面量类型，你可以写出更加健壮、可维护的 TypeScript 代码。

如果这篇文章对你有帮助，欢迎点赞、收藏和关注。