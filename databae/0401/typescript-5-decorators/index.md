# TypeScript 5.x 装饰器：从标准落地到生产实践

> 装饰器（Decorators）在 TypeScript 中已经存在多年，但一直处于「实验性阶段」。随着 ECMAScript 装饰器提案正式进入 Stage 3 并在 TS 5.0 中落地，我们终于迎来了符合标准的装饰器语法。本文将带你深入新版装饰器的核心，实战元数据驱动的业务逻辑封装。

---

## 目录 (Outline)
- [一、 装饰器的前世今生：从实验性语法到官方标准](#一-装饰器的前世今生从实验性语法到官方标准)
- [二、 TS 5.0 新版装饰器 vs 旧版实验性装饰器](#二-ts-50-新版装饰器-vs-旧版实验性装饰器)
- [三、 实战 1：方法装饰器实现全自动日志与性能分析](#三-实战-1方法装饰器实现全自动日志与性能分析)
- [四、 实战 2：类装饰器构建轻量级依赖注入 (DI)](#四-实战-2类装饰器构建轻量级依赖注入-di)
- [五、 总结与最佳实践](#五-总结与最佳实践)

---

## 一、 装饰器的前世今生：从实验性语法到官方标准

装饰器是典型的「先上车后补票」特性。

### 1. 历史背景
在 TS 5.0 之前，我们使用的是基于 Angular/Java 风格的实验性装饰器（`experimentalDecorators: true`）。它们主要操作的是类及其原型的属性描述符。

### 2. 标志性事件
- **2022 年**：ECMAScript 装饰器提案进入 Stage 3，确立了正式语法。
- **2023 年**：TypeScript 5.0 发布，完全支持该标准，并将其作为默认的装饰器实现。

### 3. 解决的问题 / 带来的变化
新版装饰器（TC39 提案）更加类型安全，且不再依赖复杂的 `Reflect Metadata`（虽然依然可以使用）。它能更好地被现代打包工具优化（Tree-shaking 友好）。

---

## 二、 TS 5.0 新版装饰器 vs 旧版实验性装饰器

新版装饰器在签名上有了重大变化：
- **旧版**：`(target, key, descriptor)`。
- **新版**：`(originalValue, context)`。

`context` 包含了丰富的元数据信息：
- `name`：装饰的属性/方法名。
- `kind`：装饰的类型（method, field, getter, setter, class）。
- `addInitializer`：允许在类初始化时执行额外逻辑。

---

## 三、 实战 1：方法装饰器实现全自动日志与性能分析

### 代码示例
```typescript
/**
 * @logged 装饰器：自动记录方法的入参、返回值及耗时
 */
function logged<This, Args extends any[], Return>(
  target: (this: This, ...args: Args) => Return,
  context: ClassMethodDecoratorContext<This, (this: This, ...args: Args) => Return>
) {
  const methodName = String(context.name);

  function replacementMethod(this: This, ...args: Args): Return {
    console.log(`🚀 开始执行方法 [${methodName}]，参数:`, args);
    const start = performance.now();
    const result = target.call(this, ...args);
    const end = performance.now();
    console.log(`✅ 方法 [${methodName}] 执行结束，耗时: ${(end - start).toFixed(2)}ms`);
    return result;
  }

  return replacementMethod;
}

class UserService {
  @logged
  getUser(id: string) {
    // 模拟重型计算
    for (let i = 0; i < 1e6; i++) {}
    return { id, name: 'Trae User' };
  }
}

const service = new UserService();
service.getUser('123');
```

---

## 四、 实战 2：类装饰器构建轻量级依赖注入 (DI)

利用新版装饰器的 `addInitializer`，我们可以非常方便地实现组件注册。

### 代码示例
```typescript
const registry = new Map<string, any>();

function component(name: string) {
  return function (value: any, context: ClassDecoratorContext) {
    context.addInitializer(() => {
      registry.set(name, value);
      console.log(`📦 组件 [${name}] 已注册到容器`);
    });
  };
}

@component('Database')
class MyDatabase {}

@component('Logger')
class MyLogger {}

// 在应用启动时，registry 已自动填满
console.log('当前容器中的组件:', [...registry.keys()]);
```

---

## 五、 总结与最佳实践

- **迁移建议**：如果你的项目重度依赖 NestJS 等旧版装饰器框架，暂时不要关闭 `experimentalDecorators`。
- **新项目**：优先采用 TS 5.x 的新版装饰器，它是未来的标准，且无需开启实验标志。
- **局限性**：新版装饰器目前不支持「属性装饰器」修改初始值（仅能监听或添加初始化逻辑）。

装饰器是 AOP（面向切面编程）在前端的最佳实践。通过装饰器，我们可以将「横切关注点」（如鉴权、日志、异常捕获）与「核心业务逻辑」彻底分离。

---

> **参考资料：**
> - *TypeScript 5.0 Release Notes: Decorators*
> - *TC39 Decorators Proposal*
> - *Modern TypeScript: Exploring the New Decorators*
