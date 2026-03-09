# 从贫血模型到 DDD：后端分层与领域建模实战

> 本文从常见的「贫血模型」痛点出发，说明 DDD 的分层、聚合根与值对象在业务代码里怎么落地方案，并给出可复用的分层示例与一段订单域示例代码，帮助你在现有项目里渐进式引入领域驱动设计。

## 一、背景 / 问题

很多后端项目会自然长成这样一种结构：Controller 调 Service，Service 调 Mapper/Repository，实体类只有 getter/setter，业务逻辑散落在各个 Service 方法里。这就是典型的**贫血模型**。

### 贫血模型带来的问题

- **逻辑分散**：同一业务规则（例如「订单能否取消」）可能出现在多个 Service，改一处容易漏另一处。
- **难以表达约束**：实体只是数据容器，不变量（invariant）无法在领域层集中保证，容易在边界处产生无效状态。
- **可测试性差**：要测一段业务逻辑，往往要 mock 一堆 Service 和 Repository，测试的是「流程」而不是「领域规则」。

当我们希望业务更清晰、变更更可控时，引入 **DDD（领域驱动设计）** 的分层与建模，可以把「业务规则」收拢到领域层，让应用层只做编排，数据库只做持久化。

---

## 二、思路 / 方案概览

### DDD 分层（从外到内）

| 层级 | 职责 | 典型内容 |
|------|------|----------|
| **用户接口层** | 协议适配、参数校验 | Controller、DTO、参数校验 |
| **应用层** | 用例编排、事务边界 | Application Service、事务、调用领域 + 基础设施 |
| **领域层** | 业务规则与领域模型 | 聚合根、实体、值对象、领域服务、领域事件 |
| **基础设施层** | 技术实现 | Repository 实现、MQ、外部 API、DB |

依赖方向：**用户接口 → 应用 → 领域 ← 基础设施**。领域层不依赖任何外层，只依赖自己。

### 核心概念速览

- **聚合根（Aggregate Root）**：一组相关实体的入口，外部只能通过聚合根修改内部状态，保证不变量在「一处」维护。
- **值对象（Value Object）**：无唯一标识、用属性相等比较的对象（如 Money、Address），不可变。
- **领域服务（Domain Service）**：当一段逻辑不属于单个实体/值对象时（如「转账」涉及两个账户），放在领域服务里。

下面用一个**订单取消**的小场景，把分层和领域建模串起来。

---

## 三、实现 / 步骤

### 3.1 领域层：订单聚合根与值对象

先定义**值对象**（不可变、无 ID）：

```typescript
// 值对象：金额（简化）
interface Money {
    amount: number;
    currency: string;
}

// 值对象：订单状态枚举
const OrderStatus = {
    CREATED: "CREATED",
    PAID: "PAID",
    SHIPPED: "SHIPPED",
    CANCELLED: "CANCELLED",
} as const;
type OrderStatus = (typeof OrderStatus)[keyof typeof OrderStatus];
```

再定义**聚合根**：订单。业务规则「只有未发货的订单可以取消」收拢在聚合内部。

```typescript
// 聚合根：订单
interface OrderItem {
    productId: string;
    quantity: number;
    price: Money;
}

interface OrderProps {
    id: string;
    status: OrderStatus;
    items: OrderItem[];
    createdAt: Date;
}

class Order {
    constructor(private readonly props: OrderProps) {}

    get id(): string {
        return this.props.id;
    }
    get status(): OrderStatus {
        return this.props.status;
    }

    /** 领域逻辑：是否允许取消 */
    canBeCancelled(): boolean {
        return this.props.status === OrderStatus.CREATED || this.props.status === OrderStatus.PAID;
    }

    /** 领域逻辑：执行取消（保持不变量的唯一入口） */
    cancel(): void {
        if (!this.canBeCancelled()) {
            throw new Error("当前状态不允许取消订单");
        }
        (this.props as { status: OrderStatus }).status = OrderStatus.CANCELLED;
    }
}
```

这里**不变量**是：只有 `CREATED` 或 `PAID` 才能变成 `CANCELLED`，所有修改都通过 `Order.cancel()`，避免在应用层或 Controller 里散落 if 判断。

### 3.2 领域层：Repository 接口（由基础设施实现）

领域层只定义「需要什么能力」，不关心数据库类型：

```typescript
// 领域层定义的接口
interface IOrderRepository {
    findById(id: string): Promise<Order | null>;
    save(order: Order): Promise<void>;
}
```

### 3.3 应用层：用例编排

应用层负责事务、取聚合、调领域方法、持久化，**不写业务规则**：

```typescript
// 应用服务
class CancelOrderApplicationService {
    constructor(private readonly orderRepository: IOrderRepository) {}

    async execute(command: { orderId: string }): Promise<void> {
        const order = await this.orderRepository.findById(command.orderId);
        if (!order) {
            throw new Error("订单不存在");
        }
        order.cancel(); // 领域逻辑
        await this.orderRepository.save(order);
    }
}
```

### 3.4 基础设施层：Repository 实现

用 TypeORM/Prisma/MyBatis 等把 `Order` 与数据库表做映射，实现 `IOrderRepository`，此处省略具体 SQL，仅示意：

```typescript
// 基础设施层
class OrderRepositoryImpl implements IOrderRepository {
    async findById(id: string): Promise<Order | null> {
        const row = await this.db.query("SELECT * FROM orders WHERE id = ?", [id]);
        return row ? this.toDomain(row) : null;
    }
    async save(order: Order): Promise<void> {
        await this.db.upsert("orders", this.toPersistence(order));
    }
    private toDomain(row: any): Order { /* ... */ }
    private toPersistence(order: Order): any { /* ... */ }
}
```

---

## 四、结果与注意点

### 效果对比

- **业务规则集中**：能否取消、状态怎么变，只看 `Order` 即可，方便单测（不依赖 DB）。
- **可读性**：应用层一眼能看出「取订单 → 取消 → 保存」，领域层表达「什么条件下能取消」。
- **扩展**：后续加「部分取消」「取消后发领域事件」等，只需在聚合根或领域服务里扩展，不影响 Controller。

### 常见坑与注意点

1. **聚合不要过大**：一个聚合内实体不宜过多，否则并发和一致性成本高；订单与订单项可以是一个聚合，订单与用户、库存建议通过 ID 引用，必要时用领域服务协调。
2. **避免在领域层依赖基础设施**：Repository 用接口，实现放在基础设施层；领域层不 import 具体 DB 或框架。
3. **渐进式引入**：不必一次性全项目 DDD，可以从一个核心子域（如订单、支付）先按分层 + 聚合根做起，其它模块保持原有写法，再逐步收敛。

### 何时适合上 DDD

- 业务规则多、变更频繁、多人协作子域多时，DDD 收益大。
- 简单 CRUD、一次性脚本或极小项目，可以先不引入，避免过度设计。

---

## 总结

- **贫血模型**的痛点是逻辑分散、约束难保证；DDD 通过**分层 + 聚合根 + 值对象**把业务规则收拢到领域层。
- **依赖方向**：用户接口 → 应用 → 领域 ← 基础设施；领域层不依赖外层。
- **落地时**：聚合根内封装不变量，应用层只做编排，Repository 接口在领域、实现在基础设施；可从一个子域渐进式引入。

如果这篇对你有帮助，欢迎点赞 / 收藏，后续可以再写「领域事件与最终一致性」「聚合划分实战」等主题。

---

**标签**：`DDD`、`领域驱动设计`、`后端`、`架构`、`最佳实践`
