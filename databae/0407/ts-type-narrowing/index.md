# TypeScript类型收窄完全指南：从原理到实战

> 深入解析TypeScript类型收窄机制，包括类型守卫、可辨识联合、typeof与instanceof的实用技巧。

## 一、什么是类型收窄

类型收窄（Narrowing）是 TypeScript 根据条件判断，自动缩小变量类型范围的过程：

```typescript
function printId(id: string | number) {
  if (typeof id === 'string') {
    // TypeScript 知道这里是 string 类型
    console.log(id.toUpperCase());
  } else {
    // TypeScript 知道这里是 number 类型
    console.log(id.toFixed(2));
  }
}
```

## 二、typeof 类型守卫

### 2.1 基本用法

```typescript
function processValue(value: string | number | boolean) {
  if (typeof value === 'string') {
    console.log(value.toUpperCase());
    console.log(value.length);
  }
  
  if (typeof value === 'number') {
    console.log(value.toFixed(2));
    console.log(value * 2);
  }
  
  if (typeof value === 'boolean') {
    console.log(value ? '是' : '否');
  }
}
```

### 2.2 typeof 支持的类型

| typeof 返回值 | 类型 |
|--------------|------|
| "string" | string |
| "number" | number |
| "boolean" | boolean |
| "undefined" | undefined |
| "function" | Function |
| "object" | object (除null) |

### 2.3 局限性

```typescript
// typeof 无法区分对象的具体类型
function process(obj: Date | Array<any> | object) {
  if (typeof obj === 'object') {
    // Date 和 Array 都会被识别为 object
    // 但它们有不同的方法
    obj.getTime(); // 错误！object 类型没有 getTime
  }
}
```

## 三、可辨识联合（Discriminated Unions）

### 3.1 基本概念

通过一个公共的「标签」属性来区分联合类型中的不同成员：

```typescript
type Shape = 
  | { kind: 'circle'; radius: number }
  | { kind: 'rectangle'; width: number; height: number }
  | { kind: 'triangle'; base: number; height: number };

function getArea(shape: Shape): number {
  switch (shape.kind) {
    case 'circle':
      return Math.PI * shape.radius ** 2;
    case 'rectangle':
      return shape.width * shape.height;
    case 'triangle':
      return 0.5 * shape.base * shape.height;
  }
}
```

### 3.2 实战：状态管理

```typescript
type AsyncState<T> = 
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: Error };

function render<T>(state: AsyncState<T>) {
  switch (state.status) {
    case 'idle':
      return <div>点击加载</div>;
    case 'loading':
      return <div>加载中...</div>;
    case 'success':
      return <div>数据: {state.data}</div>;
    case 'error':
      return <div>错误: {state.error.message}</div>;
  }
}
```

## 四、instanceof 守卫

### 4.1 基本用法

```typescript
function logValue(value: Date | string | number) {
  if (value instanceof Date) {
    console.log(value.getFullYear());
  } else if (value instanceof String) {
    console.log(value.toUpperCase());
  } else if (typeof value === 'number') {
    console.log(value.toFixed(2));
  }
}
```

### 4.2 自定义类

```typescript
class Dog {
  bark() { console.log('汪汪'); }
}

class Cat {
  meow() { console.log('喵喵'); }
}

function makeSound(animal: Dog | Cat) {
  if (animal instanceof Dog) {
    animal.bark();
  } else {
    animal.meow();
  }
}
```

## 五、in 操作符

### 5.1 对象属性检查

```typescript
type Config = 
  | { mode: 'dev'; debug: boolean }
  | { mode: 'prod'; secrets: string[] };

function initConfig(config: Config) {
  if ('debug' in config) {
    console.log('调试模式:', config.debug);
  } else {
    console.log('生产模式，共', config.secrets.length, '个密钥');
  }
}
```

### 5.2 可选属性

```typescript
type User = {
  name: string;
  email?: string;
  phone?: string;
};

function contact(user: User) {
  if ('email' in user) {
    sendEmail(user.email); // TypeScript 知道 email 存在
  }
  
  if ('phone' in user && user.phone) {
    sendSMS(user.phone);
  }
}
```

## 六、类型谓词（Type Predicates）

### 6.1 自定义类型守卫

```typescript
interface Fish {
  swim(): void;
}

interface Bird {
  fly(): void;
}

function isFish(pet: Fish | Bird): pet is Fish {
  return (pet as Fish).swim !== undefined;
}

function move(pet: Fish | Bird) {
  if (isFish(pet)) {
    pet.swim();
  } else {
    pet.fly();
  }
}
```

### 6.2 复杂场景

```typescript
type APIResponse = 
  | { status: 200; data: string }
  | { status: 400; error: string }
  | { status: 500; message: string };

function isSuccess(response: APIResponse): response is { status: 200; data: string } {
  return response.status === 200;
}

function handleResponse(response: APIResponse) {
  if (isSuccess(response)) {
    console.log('成功:', response.data);
  }
}
```

## 七、never 类型与穷尽性检查

### 7.1 穷尽检查

```typescript
type Color = 'red' | 'green' | 'blue';

function getColorName(color: Color): string {
  switch (color) {
    case 'red':
      return '红色';
    case 'green':
      return '绿色';
    case 'blue':
      return '蓝色';
    default:
      // 穷尽性检查：如果漏掉某个 case，TS 会报错
      const _exhaustive: never = color;
      return _exhaustive;
  }
}
```

### 7.2 联合类型的收窄

```typescript
type Result<T> = 
  | { ok: true; value: T }
  | { ok: false; error: Error };

function unwrap<T>(result: Result<T>): T {
  if (result.ok) {
    return result.value;
  } else {
    throw result.error;
  }
}
```

## 八、实用技巧

### 8.1 null 检查

```typescript
function greet(name: string | null) {
  if (name !== null) {
    // TypeScript 自动推断 name 为 string
    console.log(`Hello, ${name}!`);
  }
}
```

### 8.2 数组非空检查

```typescript
function firstElement<T>(arr: T[]): T | undefined {
  if (arr.length > 0) {
    // TypeScript 知道数组非空
    return arr[0];
  }
  return undefined;
}
```

### 8.3 布尔断言

```typescript
function process(input: string | null) {
  const trimmed = input?.trim();
  if (trimmed) {
    // 排除 null 和空字符串
    console.log(trimmed.toUpperCase());
  }
}
```

## 九、实战案例

### 9.1 表单验证

```typescript
type ValidationError = {
  field: string;
  message: string;
};

type FormState = 
  | { status: 'idle' }
  | { status: 'validating' }
  | { status: 'errors'; errors: ValidationError[] }
  | { status: 'success'; data: any };

function Form() {
  const [state, setState] = useState<FormState>({ status: 'idle' });
  
  switch (state.status) {
    case 'idle':
      return <FormInputs />;
    case 'validating':
      return <Spinner />;
    case 'errors':
      return <ErrorList errors={state.errors} />;
    case 'success':
      return <SuccessView data={state.data} />;
  }
}
```

### 9.2 API 请求处理

```typescript
type ApiResult<T> = 
  | { success: true; data: T }
  | { success: false; error: string };

async function fetchData<T>(url: string): Promise<ApiResult<T>> {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      return { success: false, error: response.statusText };
    }
    const data = await response.json();
    return { success: true, data };
  } catch (e) {
    return { success: false, error: e.message };
  }
}

// 使用
const result = await fetchData<User>('/api/user');
if (result.success) {
  console.log(result.data.name); // TypeScript 知道 data 存在
} else {
  console.error(result.error); // TypeScript 知道 error 存在
}
```

## 十、总结

类型收窄是 TypeScript 类型系统的核心能力：

1. **typeof**：基础类型检查
2. **可辨识联合**：区分对象类型
3. **instanceof**：类实例检查
4. **类型谓词**：自定义守卫
5. **never**：穷尽性检查

熟练掌握这些技巧，能让你写出更安全、更可维护的 TypeScript 代码。

---

**推荐阅读**：
- [TypeScript 官方文档 - Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [TypeScript Deep Dive - Narrowing](https://basarat.gitbook.io/typescript/type-system/narrowing)

**如果对你有帮助，欢迎点赞收藏！**
