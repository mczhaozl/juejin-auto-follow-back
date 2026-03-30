# TypeScript 泛型完全指南：从入门到高级应用

> 深入讲解 TypeScript 泛型，包括泛型函数、泛型类、泛型约束、泛型工具类型，以及在实际项目中的最佳实践。

## 一、泛型基础

### 1.1 什么是泛型

泛型允许创建可复用的组件，支持多种类型：

```typescript
// 泛型函数
function identity<T>(value: T): T {
  return value;
}

const str = identity('hello');  // string
const num = identity(123);      // number
```

### 1.2 泛型变量

```typescript
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}

const firstNum = first([1, 2, 3]);  // number
const firstStr = first(['a', 'b']);  // string
```

## 二、泛型函数

### 2.1 函数类型

```typescript
type Fn = <T>(x: T) => T;

const fn: Fn = (x) => x;
```

### 2.2 多个类型参数

```typescript
function pair<K, V>(key: K, value: V): [K, V] {
  return [key, value];
}

const p = pair('name', '张三');  // [string, string]
```

## 三、泛型接口

### 3.1 接口泛型

```typescript
interface Container<T> {
  value: T;
  getValue(): T;
}

const container: Container<string> = {
  value: 'hello',
  getValue() { return this.value; }
};
```

### 3.2 接口方法泛型

```typescript
interface Api {
  get<T>(url: string): Promise<T>;
  post<T, D>(url: string, data: D): Promise<T>;
}

const api: Api = {
  async get(url) { return fetch(url).then(r => r.json()); },
  async post(url, data) { return fetch(url, { method: 'POST', body: JSON.stringify(data) }).then(r => r.json()); }
};
```

## 四、泛型类

### 4.1 基本用法

```typescript
class Box<T> {
  private content: T;
  
  constructor(content: T) {
    this.content = content;
  }
  
  getContent(): T {
    return this.content;
  }
}

const box = new Box<string>('hello');
const numBox = new Box<number>(123);
```

### 4.2 约束

```typescript
class Storage<T extends { id: number }> {
  private items: T[] = [];
  
  add(item: T) {
    this.items.push(item);
  }
  
  getById(id: number): T | undefined {
    return this.items.find(item => item.id === id);
  }
}
```

## 五、泛型约束

### 5.1 extends 约束

```typescript
interface Lengthwise {
  length: number;
}

function logLength<T extends Lengthwise>(arg: T): number {
  return arg.length;
}

logLength('hello');  // 5
logLength([1, 2, 3]);  // 3
```

### 5.2 键约束

```typescript
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: '张三', age: 25 };
const name = getProperty(user, 'name');  // string
```

## 六、实战应用

### 6.1 API 类型

```typescript
interface ApiResponse<T> {
  code: number;
  data: T;
  message: string;
}

async function fetchApi<T>(url: string): Promise<ApiResponse<T>> {
  const res = await fetch(url);
  return res.json();
}

interface User {
  name: string;
}

const result = await fetchApi<User>('/api/user');
```

### 6.2 工具函数

```typescript
function pick<T, K extends keyof T>(obj: T, keys: K[]): Pick<T, K> {
  const result = {} as Pick<T, K>;
  keys.forEach(key => {
    result[key] = obj[key];
  });
  return result;
}

const user = { name: '张三', age: 25, email: 'test@example.com' };
const picked = pick(user, ['name', 'email']);
```

### 6.3 事件系统

```typescript
type EventHandler<T = any> = (data: T) => void;

class EventEmitter<Events extends Record<string, any>> {
  private handlers: { [K in keyof Events]?: EventHandler<Events[K]>[] } = {};
  
  on<K extends keyof Events>(event: K, handler: EventHandler<Events[K]>) {
    this.handlers[event] = (this.handlers[event] || []).concat(handler);
  }
  
  emit<K extends keyof Events>(event: K, data: Events[K]) {
    this.handlers[event]?.forEach(h => h(data));
  }
}

const emitter = new EventEmitter<{ userLogin: { id: number }; logout: void }>();
emitter.on('userLogin', (data) => console.log(data.id));
emitter.emit('userLogin', { id: 123 });
```

## 七、总结

TypeScript 泛型核心要点：

1. **泛型函数**：`<T>` 参数化类型
2. **泛型接口**：接口中的类型参数
3. **泛型类**：类的类型参数
4. **约束**：extends 限制类型
5. **泛型工具**：Pick、Partial 等
6. **实际应用**：API、工具函数

掌握这些，TypeScript 更精通！

---

**推荐阅读**：
- [TypeScript 泛型文档](https://www.typescriptlang.org/docs/handbook/2/generics.html)

**如果对你有帮助，欢迎点赞收藏！**
