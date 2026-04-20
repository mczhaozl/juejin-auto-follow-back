# TypeScript Zod 数据验证完全指南

## 一、Zod 基础

```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.string(),
  name: z.string().min(2),
  age: z.number().int().min(0).max(150),
  email: z.string().email(),
  isActive: z.boolean()
});

// 验证数据
const data = { id: '1', name: 'Alice', age: 30, email: 'a@a.com', isActive: true };
UserSchema.parse(data);
```

## 二、常见类型

```typescript
// 基础类型
z.string()
z.number()
z.boolean()
z.date()

// 可选和可选
z.string().optional()
z.string().nullable()

// 数组
z.array(z.string())

// 联合类型
z.union([z.string(), z.number()])

// 枚举
z.enum(['Admin', 'User', 'Guest'])
```

## 三、对象验证

```typescript
const OrderSchema = z.object({
  id: z.string(),
  items: z.array(z.object({
    product: z.string(),
    quantity: z.number().min(1)
  })),
  total: z.number()
}).strict();
```

## 四、自定义验证

```typescript
const PasswordSchema = z.string()
  .min(8)
  .max(32)
  .refine(val => /[A-Z]/.test(val), {
    message: '需要包含大写字母'
  })
  .refine(val => /[0-9]/.test(val), {
    message: '需要包含数字'
  });
```

## 五、类型推断

```typescript
type User = z.infer<typeof UserSchema>;
// { id: string; name: string; ... }

const user: User = {
  id: '1',
  name: 'Alice',
  age: 30,
  email: 'alice@example.com',
  isActive: true
};
```

## 六、异步验证

```typescript
const EmailSchema = z.string()
  .email()
  .refine(async (email) => {
    const exists = await checkEmailExists(email);
    return !exists;
  }, { message: '邮箱已存在' });

await EmailSchema.parseAsync(email);
```

## 七、错误处理

```typescript
try {
  UserSchema.parse(data);
} catch (err) {
  if (err instanceof z.ZodError) {
    console.log(err.issues);
  }
}
```

## 八、实战场景

```typescript
// API 验证
app.post('/api/users', (req, res) => {
  try {
    const user = UserSchema.parse(req.body);
    // 保存用户
    res.json({ success: true, user });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// 表单验证
function validateForm(formData) {
  const result = FormSchema.safeParse(formData);
  if (!result.success) {
    return { errors: result.error.flatten() };
  }
  return { data: result.data };
}
```

## 九、最佳实践

- 在应用入口处验证外部数据
- 使用 strict() 防止多余字段
- 利用类型推断避免重复定义
- 提供友好的错误消息
- 合理使用 refine 自定义验证
