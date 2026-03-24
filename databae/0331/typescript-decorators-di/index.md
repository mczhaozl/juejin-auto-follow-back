# TypeScript 装饰器进阶：实现自动化的依赖注入容器

在现代 Web 开发中，随着应用规模的扩大，模块间的耦合度往往会迅速上升。如何优雅地管理模块之间的依赖关系，成为了架构设计的核心命题。TypeScript 的装饰器（Decorators）和依赖注入（Dependency Injection, DI）模式，为我们提供了一套从「手动解耦」到「自动装配」的完美进化路径。

本文将带你领略装饰器的前世今生，并手把手实现一个轻量级的 DI 容器。

---

## 目录 (Outline)
- [一、 混沌时期：手动实例化的痛苦（1990s - 2000s）](#一-混沌时期手动实例化的痛苦1990s---2000s)
- [二、 启蒙时期：构造器注入与 Reflect Metadata（2012 - 2015）](#二-启蒙时期构造器注入与-reflect-metadata2012---2015)
- [三、 现代时期：装饰器驱动的自动装配（2016 - 至今）](#三-现代时期装饰器驱动的自动装配2016---至今)
- [四、 进阶话题：单例与生命周期管理](#四-进阶话题单例与生命周期管理)
- [五、 总结](#五-总结)

---

## 一、 混沌时期：手动实例化的痛苦（1990s - 2000s）

在早期的面向对象编程（OOP）中，我们通常直接在类内部实例化它的依赖项。

### 1. 历史背景
在那个年代，模块化还处于萌芽阶段。虽然类与类之间有依赖，但开发者习惯于「谁用谁建」。这种做法虽然直观，但带来了巨大的测试挑战：一旦你想测试 `UserService`，你就必须同时启动真实的 `Database` 连接。

### 2. 标志性事件
- **1994 年**：GoF 出版《设计模式》，提出了「创建型模式」，但尚未普及解耦容器。
- **2004 年**：Martin Fowler 发布了著名博文《Inversion of Control Containers and the Dependency Injection pattern》，正式定义了 DI 模式。

### 3. 解决的问题 / 带来的变化
这一阶段解决了「如何实例化对象」的问题，但留下了「代码难以测试、难以维护」的痛点。

### 4. 代码示例：那个年代的手动依赖
```typescript
// 1990 年代典型的硬编码依赖
class Database {
    query(sql: string) { console.log('Executing:', sql); }
}

class UserService {
    private db: Database;
    constructor() {
        // ❌ 痛点：UserService 强耦合了具体的 Database 类
        this.db = new Database();
    }

    getUser() { return this.db.query('SELECT * FROM users'); }
}
```

---

## 二、 启蒙时期：构造器注入与 Reflect Metadata（2012 - 2015）

随着 Java 领域的 Spring 框架大获成功，前端社区开始思考：能不能在 JavaScript/TypeScript 中也实现类似的自动注入？

### 1. 历史背景
2012 年 TypeScript 发布，为 JavaScript 带来了静态类型。2014 年左右，Angular 2（现在的 Angular）开始在内部大规模使用依赖注入。为了支持装饰器，社区引入了 `reflect-metadata` 库，允许我们在运行时读取类的元数据。

### 2. 标志性事件
- **2012 年**：TypeScript 0.8 发布。
- **2014 年**：Google 发布 Angular 2 Alpha，展示了强大的 DI 机制。
- **2015 年**：ES6 规范发布，类（Class）成为正式语法。同时，Reflect Metadata 提案进入 TC39 视野。

### 3. 解决的问题 / 带来的变化
开发者不再在类内部 `new` 对象，而是通过构造器参数声明自己「需要什么」。

### 4. 代码示例：初步的依赖注入
```typescript
// 2014 年左右典型的 DI 模式
class Database {}

class UserService {
    // ✅ 改进：通过构造函数传入依赖（DI 的萌芽）
    constructor(private db: Database) {}
}

// 容器手动装配（痛点：当依赖链很长时，手动 new 非常累）
const db = new Database();
const service = new UserService(db);
```

---

## 三、 现代时期：装饰器驱动的自动装配（2016 - 至今）

现代框架（如 NestJS、InversifyJS）利用装饰器和元数据，实现了完全自动化的 DI 容器。

### 1. 历史背景
装饰器提案虽然在 TC39 历经坎坷（从第一版重构到第三版），但 TypeScript 始终支持实验性的装饰器。这使得开发者可以像 Java 注解一样，优雅地标记一个类为「可注入的」。

### 2. 标志性事件
- **2017 年**：NestJS 诞生，将 Spring 的设计理念彻底带入 Node.js 社区。
- **2019 年**：InversifyJS 成为前端最流行的轻量级 DI 框架。
- **2023 年**：TypeScript 5.0 正式支持符合 ECMAScript 标准的装饰器。

### 3. 核心原理解析：如何实现一个 DI 容器？

一个自动化的 DI 容器主要由三部分组成：
1. **装饰器**：用于标记哪些类需要被管理。
2. **注册表（Registry）**：存储类与其实例（或工厂函数）的映射。
3. **递归实例化器**：根据构造函数的参数类型，递归地从注册表中取出并注入依赖。

### 4. 实战示例：手写一个轻量级 DI 容器

首先，我们需要引入 `reflect-metadata` 并开启 TS 实验配置。

```typescript
import 'reflect-metadata';

// 定义一个映射，存储已注册的类
const container = new Map<any, any>();

/**
 * @Injectable 装饰器：标记一个类可以被注入
 */
function Injectable() {
  return function(target: any) {
    // 简单起见，我们将类注册到全局容器
    container.set(target, null);
  };
}

/**
 * 工厂函数：从容器中获取实例，如果不存在则创建
 */
function get<T>(target: any): T {
  // 如果已经有单例，直接返回
  if (container.get(target)) {
    return container.get(target);
  }

  // 获取构造函数参数的元数据（由 TS 编译器生成）
  const paramTypes: any[] = Reflect.getMetadata('design:paramtypes', target) || [];

  // 递归地实例化所有依赖项
  const injections = paramTypes.map((token: any) => get(token));

  // 创建并存储实例
  const instance = new target(...injections);
  container.set(target, instance);
  
  return instance;
}

// --- 使用方式 ---

@Injectable()
class Logger {
  log(msg: string) { console.log(`[LOG]: ${msg}`); }
}

@Injectable()
class ApiService {
  constructor(private logger: Logger) {}
  fetchData() {
    this.logger.log('Fetching data...');
    return { data: 'Hello DI' };
  }
}

// 魔法发生的地方：我们只需要获取顶层服务，底层依赖自动装配！
const api = get<ApiService>(ApiService);
console.log(api.fetchData());
```

---

## 四、 进阶话题：单例与生命周期管理

真实的 DI 容器通常支持更复杂的配置：
1. **Singleton（单例）**：全局只有一个实例。
2. **Transient（瞬时）**：每次请求都创建一个新实例。
3. **Request（请求作用域）**：在一次 HTTP 请求内共享实例。

### 最佳实践建议：
- **接口注入优于类注入**：尽量针对 Interface 编程，虽然 TS 运行时无法获取 Interface 类型，但可以通过「字符串 Token」解决。
- **避免循环依赖**：如果 A 依赖 B，B 也依赖 A，DI 容器会进入死循环。
- **利用 TypeScript 5.0 装饰器**：随着标准装饰器的落地，未来元数据的处理可能会更加原生化。

---

## 五、 总结

从硬编码到构造器注入，再到基于装饰器的自动装配，依赖注入的进化史就是一部「模块化与解耦」的抗争史。

虽然手动 `new` 在小型项目中更简单，但一旦涉及到复杂的业务逻辑和单元测试，DI 容器带来的好处（可维护性、代码整洁度）将不可估量。作为开发者，掌握装饰器这一利器，你将能写出更具架构美感的代码。

---

> **参考资料：**
> - *TypeScript Documentation: Decorators*
> - *Martin Fowler: Inversion of Control Containers and the Dependency Injection pattern*
> - *NestJS Documentation: Dependency Injection*
