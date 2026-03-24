# TypeScript 进阶：如何优雅地处理深层嵌套对象的类型定义？

> 在处理大型 JSON 响应或复杂状态树时，深层嵌套对象的类型定义往往让人头疼。本文将分享几种高级技巧，教你如何利用 TypeScript 的模板字符串、映射类型和递归类型来优雅地搞定它们。

## 一、场景：痛点在哪里？

假设你正在处理一个配置对象，结构非常深：

```typescript
const config = {
  api: {
    endpoint: "https://api.example.com",
    auth: {
      type: "bearer",
      token: "secret"
    }
  },
  theme: {
    colors: {
      primary: "#ff0000",
      secondary: "#00ff00"
    }
  }
};
```

如果你需要实现一个 `get` 函数来通过路径获取属性，该如何定义类型呢？

```typescript
// 传统的写法，类型丢失严重
function get(obj: any, path: string): any {
  return path.split('.').reduce((o, key) => o?.[key], obj);
}
```

## 二、方案一：利用递归类型和模板字符串

我们可以定义一个 `Path<T>` 类型，它可以自动推导出对象的所有合法路径字符串（如 `"api.endpoint"`、`"theme.colors.primary"`）。

```typescript
type Path<T> = T extends object
  ? {
      [K in keyof T]: K extends string
        ? T[K] extends object
          ? `${K}` | `${K}.${Path<T[K]>}`
          : `${K}`
        : never;
    }[keyof T]
  : never;

// 使用示例
type ConfigPath = Path<typeof config>;
// ConfigPath 会是 "api" | "api.endpoint" | "api.auth" | "api.auth.type" ...
```

## 三、方案二：路径值推导 PathValue<T, P>

有了路径 `P`，我们如何拿到对应位置的类型呢？这需要另一个递归工具类型。

```typescript
type PathValue<T, P extends string> = P extends `${infer Key}.${infer Rest}`
  ? Key extends keyof T
    ? PathValue<T[Key], Rest>
    : never
  : P extends keyof T
  ? T[P]
  : never;

// 使用示例
type TokenValue = PathValue<typeof config, "api.auth.token">; // string
```

## 四、实战：类型安全的 get 函数

现在，我们可以把这两个工具结合起来，打造一个完美的 `get` 函数：

```typescript
function safeGet<T extends object, P extends Path<T>>(obj: T, path: P): PathValue<T, P> {
  return path.split('.').reduce((o, key) => (o as any)?.[key], obj) as any;
}

// 完美推导
const token = safeGet(config, "api.auth.token"); // 类型推导为 string
const primaryColor = safeGet(config, "theme.colors.primary"); // 类型推导为 string
```

## 五、总结

通过本文，我们学习了：
1. **递归类型**：处理无限深度的结构。
2. **模板字符串类型**：动态生成路径字符串。
3. **映射类型**：遍历并修改对象的 key。

掌握这些技巧，能让你的 TypeScript 代码从「勉强能跑」变成「工业级标准」。

**如果你觉得这些高级技巧对你有帮助，别忘了点赞关注哦！**
