# TypeScript 品牌类型完全指南

## 一、基础品牌类型

```typescript
// 定义品牌类型
type Brand<T, BrandName extends string> = T & { __brand: BrandName };

// 用户 ID
type UserId = Brand<string, 'UserId'>;
type ProductId = Brand<string, 'ProductId'>;

// 创建品牌类型的安全方式
function createUserId(id: string): UserId {
  return id as UserId;
}

function createProductId(id: string): ProductId {
  return id as ProductId;
}

// 使用 - 不能混淆
const userId = createUserId('123');
const productId = createProductId('abc');

function fetchUser(id: UserId) { /* ... */ }
function fetchProduct(id: ProductId) { /* ... */ }

fetchUser(userId); // OK
fetchUser(productId); // 错误！类型不匹配
```

## 二、数值品牌类型

```typescript
type USD = Brand<number, 'USD'>;
type EUR = Brand<number, 'EUR'>;

function createUSD(amount: number): USD {
  return amount as USD;
}

function createEUR(amount: number): EUR {
  return amount as EUR;
}

function totalPrice(usd: USD, quantity: number): USD {
  return (usd * quantity) as USD;
}
```

## 三、品牌类型工具

```typescript
// 1. 通用创建函数
function brand<T, B extends string>(value: T): Brand<T, B> {
  return value as Brand<T, B>;
}

// 2. 使用类（更安全）
class UUID {
  private readonly __brand!: void;
  constructor(public readonly value: string) {}
}

// 使用
const uuid = new UUID('550e8400...');
```

## 四、品牌类型与验证

```typescript
type Email = Brand<string, 'Email'>;

function isEmail(str: string): str is Email {
  return /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(str);
}

function createEmail(str: string): Email {
  if (!isEmail(str)) {
    throw new Error('Invalid email');
  }
  return str as Email;
}

function sendEmail(to: Email) {
  console.log('Sending to', to);
}
```

## 最佳实践
- 使用品牌类型防止类型混淆
- 添加验证逻辑
- 合理设计品牌系统
- 不要过度使用品牌类型
- 考虑使用 Opaque 类型库
