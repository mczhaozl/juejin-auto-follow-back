# 微服务架构模式完全指南：设计模式与实战

> 深入讲解微服务架构模式，包括服务拆分、通信机制、服务发现、容错处理、分布式事务，以及实际项目中的架构设计和最佳实践。

## 一、微服务基础

### 1.1 什么是微服务

服务拆分：

```
┌─────────────────────────────────────────────────────────────┐
│                    微服务架构                                │
│                                                              │
│   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐          │
│   │ 用户   │  │ 订单   │  │ 支付   │  │ 物流   │          │
│   │ 服务   │  │ 服务   │  │ 服务   │  │ 服务   │          │
│   └────────┘  └────────┘  └────────┘  └────────┘          │
│        │         │         │         │                      │
│        └─────────┴─────────┴─────────┘                      │
│                      │                                       │
│              API Gateway                                     │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 优势

| 优势 | 说明 |
|------|------|
| 独立部署 | 各自独立迭代 |
| 技术异构 | 选型灵活 |
| 故障隔离 | 单点不影响全局 |
| 扩展方便 | 按需扩展 |

## 二、拆分策略

### 2.1 拆分维度

```
┌─────────────────────────────────────────────────────────────┐
│                    拆分策略                                  │
│                                                              │
│  按业务能力   │  按子业务       │  按团队                │
│  ────────────┼───────────────┼─────────────               │
│  用户        │  订单子业务     │  前端团队               │
│  订单        │  支付子业务     │  后端团队               │
│  支付        │  物流子业务     │  支付团队               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 拆分原则

```markdown
1. 单一职责
2. 高内聚低耦合
3. 业务边界清晰
4. 团队自主
5. 渐进式拆分
```

## 三、服务通信

### 3.1 同步通信

```yaml
# HTTP/REST
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  selector:
    app: order
  ports:
    - port: 80
      targetPort: 8080
---
# gRPC
syntax = "proto3";

service OrderService {
  rpc CreateOrder(CreateOrderRequest) returns (Order);
  rpc GetOrder(GetOrderRequest) returns (Order);
}

message Order {
  string id = 1;
  string user_id = 2;
  repeated OrderItem items = 3;
}
```

### 3.2 异步通信

```yaml
# RabbitMQ 消息
# order.created
{
  "event": "order.created",
  "orderId": "123",
  "userId": "456",
  "total": 100.00,
  "timestamp": "2024-01-01T10:00:00Z"
}
```

## 四、服务发现

### 4.1 Consul

```yaml
# docker-compose.yml
services:
  consul:
    image: consul
    ports:
      - "8500:8500"
    command: agent -server -ui -bootstrap-expect=1 -client=0.0.0.0
```

### 4.2 Spring Cloud Netflix

```yaml
# application.yml
eureka:
  client:
    service-url:
      defaultZone: http://localhost:8761/eureka/
  instance:
    prefer-ip-address: true
```

## 五、容错处理

### 5.1 熔断器

```
┌─────────────────────────────────────────────────────────────┐
│                    熔断器状态                                │
│                                                              │
│  Closed (关闭) ──▶ 故障 ──▶ Open (打开)                   │
│      ▲                              │                       │
│      │                              ▼                       │
│      └─────── 恢复 ────────── Half-Open (半开)            │
│                                                              │
│  关闭: 正常请求                                              │
│  打开: 快速失败                                              │
│  半开: 探测恢复                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Resilience4j

```java
// 熔断器
CircuitBreakerConfig config = CircuitBreakerConfig.custom()
    .failureRateThreshold(50)
    .waitDurationInOpenState(Duration.ofSeconds(10))
    .slidingWindowSize(10)
    .build();

CircuitBreaker circuitBreaker = CircuitBreaker.of("backendService", config);

// 使用
Decorator.decorateSupplier(supplier, circuitBreaker)
    .get();
```

### 5.3 重试

```java
RetryConfig config = RetryConfig.custom()
    .maxAttempts(3)
    .waitDuration(Duration.ofMillis(100))
    .build();

Retry retry = Retry.of("backendService", config);
```

## 六、分布式事务

### 6.1 CAP 定理

```
┌─────────────────────────────────────────────────────────────┐
│                    CAP 定理                                  │
│                                                              │
│  Consistency (一致性)                                        │
│       │                                                     │
│       ├───────────────────┐                                  │
│       │                   │                                  │
│   Availability       Partition                              │
│   (可用性)           Tolerance                              │
│   (分区容错)         (必须满足两个)                         │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 TCC 模式

```java
// Try: 预留资源
@Compensable(confirmMethod = "confirmOrder", cancelMethod = "cancelOrder")
public void createOrder(Order order) {
    // 冻结库存
    inventoryService.freezeStock(order.getItems());
    // 冻结余额
    accountService.freezeBalance(order.getUserId(), order.getTotal());
}

// Confirm: 确认执行
public void confirmOrder(Order order) {
    inventoryService.deductStock(order.getItems());
    accountService.deductBalance(order.getUserId(), order.getTotal());
}

// Cancel: 取消回滚
public void cancelOrder(Order order) {
    inventoryService.unfreezeStock(order.getItems());
    accountService.unfreezeBalance(order.getUserId(), order.getTotal());
}
```

### 6.3 Saga 模式

```yaml
# 订单服务 → 支付服务 → 物流服务
# 每个服务有正向操作和补偿操作

order_service:
  create_order:       # 创建订单
    compensate: cancel_order
  
payment_service:
  process_payment:    # 处理支付
    compensate: refund_payment

shipping_service:
  ship_order:         # 发货
    compensate: cancel_ship
```

## 七、API 网关

### 7.1 Kong 配置

```yaml
# 服务
curl -X POST http://localhost:8001/services \
  -d '{"name":"user-service","url":"http://user-service:8080"}'

# 路由
curl -X POST http://localhost:8001/services/user-service/routes \
  -d '{"paths":["/users"],"methods":["GET","POST"]}'

# 认证插件
curl -X POST http://localhost:8001/services/user-service/plugins \
  -d '{"name":"jwt","config":{"key_claim":"user_id"}}'
```

### 7.2 Spring Cloud Gateway

```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: user-service
          uri: lb://user-service
          predicates:
            - Path=/users/**
          filters:
            - StripPrefix=1
            - AddRequestHeader=X-Gateway, SpringCloud
```

## 八、总结

微服务架构核心要点：

1. **拆分**：业务边界
2. **通信**：同步/异步
3. **发现**：Consul/Eureka
4. **容错**：熔断/重试
5. **事务**：TCC/Saga
6. **网关**：统一入口

掌握这些，微服务架构 so easy！

---

**推荐阅读**：
- [微服务设计](https://book.douban.com/subject/26772677/)

**如果对你有帮助，欢迎点赞收藏！**
