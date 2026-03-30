# TypeScript 类型 narrowing 完全指南

> 深入讲解 TypeScript 类型 narrowing，包括 typeof、instanceof、in 操作符、类型守卫，以及 discriminated union 和自定义类型守卫。

## 一、类型收窄

### 1.1 什么是 narrowing

TypeScript 自动收窄类型：

```typescript
function print(value: string | number) {
  if (typeof value === 'string') {
    console.log(value.toUpperCase()); // string
  } else {
    console.log(value.toFixed(2)); // number
  }
}
```

### 1.2 typeof

```typescript
function process(value: string | number | boolean) {
  if (typeof value === 'string') {
    return value.toUpperCase();
  }
  if (typeof value === 'number') {
    return value * 2;
  }
  return value;
}
```

## 二、类型守卫

### 2.1 instanceof

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

### 2.2 in

```typescript
interface Fish { swim: () => void }
interface Bird { fly: () => void }

function move(animal: Fish | Bird) {
  if ('swim' in animal) {
    animal.swim();
  } else {
    animal.fly();
  }
}
```

## 三、Discriminated Union

### 3.1 标签联合

```typescript
type Action =
  | { type: 'increment'; delta: number }
  | { type: 'decrement'; delta: number }
  | { type: 'reset' };

function reducer(action: Action) {
  switch (action.type) {
    case 'increment':
      return action.delta;
    case 'decrement':
      return -action.delta;
    case 'reset':
      return 0;
  }
}
```

### 3.2 可辨识联合

```typescript
interface SuccessResponse<T> {
  status: 'success';
  data: T;
}

interface ErrorResponse {
  status: 'error';
  error: string;
}

type Response<T> = SuccessResponse<T> | ErrorResponse;

function handleResponse<T>(response: Response<T>) {
  if (response.status === 'success') {
    console.log(response.data);
  } else {
    console.error(response.error);
  }
}
```

## 四、自定义守卫

### 4.1 is 关键字

```typescript
function isString(value: unknown): value is string {
  return typeof value === 'string';
}

function process(value: unknown) {
  if (isString(value)) {
    console.log(value.toUpperCase());
  }
}
```

### 4.2 实践

```typescript
interface Admin { role: 'admin' }
interface User { role: 'user' }
type Person = Admin | User;

function isAdmin(person: Person): person is Admin {
  return person.role === 'admin';
}

function greet(person: Person) {
  if (isAdmin(person)) {
    console.log('管理员你好');
  } else {
    console.log('用户你好');
  }
}
```

## 五、总结

TypeScript narrowing 核心要点：

1. **typeof**：基础类型收窄
2. **instanceof**：类实例判断
3. **in**：属性存在判断
4. **Discriminated Union**：标签联合
5. **is 关键字**：自定义守卫

掌握这些，TypeScript 类型更精准！

---

**推荐阅读**：
- [TypeScript 官方文档](https://www.typescriptlang.org/docs/)

**如果对你有帮助，欢迎点赞收藏！**
