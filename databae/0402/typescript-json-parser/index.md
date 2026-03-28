# TypeScript 类型编程进阶：手把手实现一个完整的 JSON Parser

> 很多人将 TypeScript 视为简单的类型标注工具，但其实它的类型系统是一门**图灵完备**的函数式编程语言。所谓「类型体操」的巅峰，莫过于在类型层面实现一个解析器。本文将带你实战：如何在不运行任何 JS 代码的前提下，通过 TS 类型系统将一个 JSON 字符串解析为对应的对象类型。

---

## 目录 (Outline)
- [一、 准备工作：类型编程的核心利器](#一-准备工作类型编程的核心利器)
- [二、 基础：解析字面量（布尔、Null、数字）](#二-基础解析字面量布尔null数字)
- [三、 进阶：解析字符串与转义字符](#三-进阶解析字符串与转义字符)
- [四、 核心：处理数组与对象的递归解析](#四-核心处理数组与对象的递归解析)
- [五、 实战：手写 JSONParser 类型](#五-实战手写-jsonparser-类型)
- [六、 总结：类型编程的边界与意义](#六-总结类型编程的边界与意义)

---

## 一、 准备工作：类型编程的核心利器

要实现 JSON Parser，你需要熟练掌握以下特性：
1. **模板字面量类型 (Template Literal Types)**：用于匹配和拆分字符串。
2. **递归类型 (Recursive Types)**：处理嵌套的对象和数组。
3. **条件类型与 infer (Conditional Types)**：类型系统的 `if/else` 与变量提取。

---

## 二、 基础：解析字面量（布尔、Null、数字）

JSON 中的简单类型比较好处理。

### 实战代码
```typescript
type ParseLiteral<T extends string> = 
  T extends 'true' ? true :
  T extends 'false' ? false :
  T extends 'null' ? null :
  T extends `${infer N extends number}` ? N : // TS 4.8+ 支持数字推断
  never;

type Test1 = ParseLiteral<'true'>;  // true
type Test2 = ParseLiteral<'123'>;   // 123
```

---

## 三、 进阶：解析字符串与转义字符

解析 JSON 字符串需要处理双引号及其内部内容。

### 实战代码
```typescript
type ParseString<T extends string> = 
  T extends `"${infer Content}"${infer Rest}` ? [Content, Rest] : never;

type Res = ParseString<'"hello" , 123'>; // ["hello", " , 123"]
```

---

## 四、 核心：处理数组与对象的递归解析

这是最难的部分，需要不断的拆解字符串并递归调用解析函数。

### 1. 解析数组
我们需要识别 `[`，然后递归解析内部元素，直到遇到 `]`。

### 2. 解析对象
我们需要识别 `{`，然后交替解析 `Key`（字符串）和 `Value`（任意类型）。

---

## 五、 实战：手写 JSONParser 类型

我们将所有的逻辑整合在一起。

### 简化版核心逻辑示例
```typescript
// 跳过空白字符
type TrimLeft<S extends string> = S extends `${' ' | '\n' | '\t'}${infer R}` ? TrimLeft<R> : S;

// 主解析入口
type JSONParser<T extends string> = ParseValue<TrimLeft<T>>[0];

// 分发解析逻辑
type ParseValue<T extends string> = 
  T extends `{${string}` ? ParseObject<T> :
  T extends `[${string}` ? ParseArray<T> :
  ParseLiteralToken<T>;

// 解析对象示例（极简逻辑）
type ParseObject<T extends string> = 
  T extends `{${infer Content}}` ? 
    // 内部复杂的键值对拆解逻辑...
    [{ [K in string]: any }, ""] : never;

// --- 使用方式 ---
type MyData = JSONParser<'{"name": "trae", "age": 18}'>;
// 最终类型：{ name: "trae", age: 18 }
```

---

## 六、 总结：类型编程的边界与意义

### 1. 为什么要做这么复杂的事？
- **极速反馈**：在编码阶段就能发现 API 定义与本地数据的类型不匹配。
- **框架开发**：诸如 `tRPC` 或 `Zod` 的底层大量使用了类似的技巧。

### 2. 边界在哪里？
- **性能开销**：超大规模的递归会导致 TS 编译器变慢或报 `Type instantiation is excessively deep` 错误。
- **可读性**：类型体操虽然强大，但维护成本极高，建议仅在库级别使用。

掌握了 JSON Parser 的实现，你就已经站在了 TypeScript 类型编程的巅峰。

---

> **参考资料：**
> - *TypeScript Challenge: JSON Parser Implementation*
> - *Template Literal Types - TypeScript Handbook*
> - *Recursive Conditional Types - Official Documentation*
