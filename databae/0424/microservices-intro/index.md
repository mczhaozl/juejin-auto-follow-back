# 微服务架构完全入门指南：从单体到分布式系统

微服务架构是一种将应用程序构建为一组小型、独立服务的架构风格。本文将带你全面了解微服务架构。

## 一、微服务基础

### 1. 什么是微服务

```
单体架构:
┌─────────────────────────────────┐
│         单一应用程序              │
│  ┌──────┐ ┌──────┐ ┌──────┐  │
│  │ 用户 │ │ 订单 │ │ 支付 │  │
│  │ 服务 │ │ 服务 │ │ 服务 │  │
│  └──────┘ └──────┘ └──────┘  │
│         单一数据库               │
└─────────────────────────────────┘

微服务架构:
┌─────────┐  ┌─────────┐  ┌─────────┐
│ 用户服务 │  │ 订单服务 │  │ 支付服务 │
│ (独立)   │  │ (独立)   │  │ (独立)   │
└────┬────┘  └────┬────┘  └────┬────┘
     │             │             │
     └─────────────┼─────────────┘
                   │
            ┌──────┴──────┐
            │  API 网关    │
            └──────┬──────┘
                   │
                ┌──┴──┐
                │客户端 │
                └─────┘

每个服务:
- 独立部署
- 独立扩展
- 独立技术栈
- 独立数据库
```

### 2. 核心特征

- **单一职责**: 每个服务只做一件事
- **独立部署**: 可以独立部署和扩展
- **技术多样性**: 不同服务可以使用不同技术栈
- **去中心化**: 去中心化的数据管理和治理
- **容错设计**: 服务故障不影响整个系统
- **自动化**: 自动化部署、测试和监控

## 二、服务拆分策略

### 1. 按业务领域拆分

```
电商系统:
├── 用户服务 (User Service)
│   ├── 用户注册/登录
│   ├── 用户信息管理
│   └── 权限管理
├── 商品服务 (Product Service)
│   ├── 商品管理
│   ├── 分类管理
│   └── 库存管理
├── 订单服务 (Order Service)
│   ├── 订单创建
│   ├── 订单查询
│   └── 订单状态管理
├── 支付服务 (Payment Service)
│   ├── 支付处理
│   └── 支付记录
└── 通知服务 (Notification Service)
    ├── 邮件通知
    ├── 短信通知
    └── 推送通知
```

### 2. 按子域拆分（DDD）

```
限界上下文 (Bounded Context):
- 用户上下文
- 商品上下文
- 订单上下文
- 支付上下文
- 物流上下文

每个限界上下文 → 一个微服务
```

### 3. 拆分原则

```
1. 高内聚、低耦合
2. 单一职责
3. 独立部署
4. 合适的服务粒度
5. 考虑团队结构（康威定律）
6. 避免过度拆分
```

## 三、服务通信

### 1. 同步通信（REST/gRPC）

```javascript
// 用户服务调用订单服务 (REST)
const axios = require('axios');

class UserService {
  async getUserOrders(userId) {
    try {
      const response = await axios.get(
        `http://order-service/api/orders/user/${userId}`,
        { timeout: 5000 }
      );
      return response.data;
    } catch (error) {
      console.error('Failed to get user orders:', error);
      throw error;
    }
  }
}

// gRPC 示例
// proto/service.proto
syntax = "proto3";

service OrderService {
  rpc GetUserOrders(GetUserOrdersRequest) returns (GetUserOrdersResponse);
}

message GetUserOrdersRequest {
  string user_id = 1;
}

message Order {
  string id = 1;
  string user_id = 2;
  double total = 3;
  string status = 4;
}

message GetUserOrdersResponse {
  repeated Order orders = 1;
}
```

### 2. 异步通信（消息队列）

```javascript
// 使用 RabbitMQ
const amqp = require('amqplib');

// 订单服务 - 发布事件
class OrderService {
  async createOrder(order) {
    const savedOrder = await this.saveToDatabase(order);
    
    await this.publishOrderCreatedEvent(savedOrder);
    
    return savedOrder;
  }
  
  async publishOrderCreatedEvent(order) {
    const connection = await amqp.connect('amqp://localhost');
    const channel = await connection.createChannel();
    
    const exchange = 'order_events';
    await channel.assertExchange(exchange, 'topic', { durable: true });
    
    const message = JSON.stringify({
      type: 'ORDER_CREATED',
      data: order
    });
    
    channel.publish(exchange, 'order.created', Buffer.from(message));
    
    setTimeout(() => {
      connection.close();
    }, 500);
  }
}

// 通知服务 - 订阅事件
class NotificationService {
  async start() {
    const connection = await amqp.connect('amqp://localhost');
    const channel = await connection.createChannel();
    
    const exchange = 'order_events';
    await channel.assertExchange(exchange, 'topic', { durable: true });
    
    const q = await channel.assertQueue('', { exclusive: true });
    
    await channel.bindQueue(q.queue, exchange, 'order.created');
    
    console.log('Waiting for order events...');
    
    channel.consume(q.queue, (msg) => {
      if (msg.content) {
        const event = JSON.parse(msg.content.toString());
        this.handleOrderCreated(event.data);
        channel.ack(msg);
      }
    });
  }
  
  async handleOrderCreated(order) {
    console.log('Sending notification for order:', order.id);
    await this.sendEmailNotification(order);
    await this.sendSMSNotification(order);
  }
}
```

### 3. 服务发现

```javascript
// 使用 Consul
const consul = require('consul');

class ServiceRegistry {
  constructor() {
    this.client = consul({ host: 'consul', port: 8500 });
  }
  
  async register(serviceName, serviceId, host, port) {
    await this.client.agent.service.register({
      name: serviceName,
      id: serviceId,
      address: host,
      port: port,
      check: {
        http: `http://${host}:${port}/health`,
        interval: '10s',
        timeout: '5s'
      }
    });
  }
  
  async discover(serviceName) {
    const result = await this.client.health.service(serviceName, {
      passing: true
    });
    
    if (result.length === 0) {
      throw new Error(`No healthy instances of ${serviceName}`);
    }
    
    const instance = result[Math.floor(Math.random() * result.length)];
    return {
      host: instance.Service.Address,
      port: instance.Service.Port
    };
  }
}

// 使用
const registry = new ServiceRegistry();

// 注册服务
await registry.register('user-service', 'user-service-1', 'localhost', 3001);

// 发现服务
const orderService = await registry.discover('order-service');
const response = await axios.get(`http://${orderService.host}:${orderService.port}/api/orders`);
```

## 四、API 网关

### 1. 网关作用

```
客户端请求
    ↓
[API 网关]
    ↓
┌────┼────┐
↓    ↓    ↓
服务A 服务B 服务C
```

功能：
- 路由转发
- 负载均衡
- 认证授权
- 限流熔断
- 日志监控
- 协议转换

### 2. 使用 Kong 或 Express Gateway

```javascript
// 简单的 API 网关实现
const express = require('express');
const httpProxy = require('http-proxy');
const rateLimit = require('express-rate-limit');

const app = express();
const proxy = httpProxy.createProxyServer();

// 限流
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
});
app.use(limiter);

// 认证中间件
app.use((req, res, next) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'Unauthorized' });
  }
  next();
});

// 路由配置
const routes = {
  '/api/users': 'http://user-service:3001',
  '/api/orders': 'http://order-service:3002',
  '/api/products': 'http://product-service:3003'
};

app.use((req, res) => {
  for (const [path, target] of Object.entries(routes)) {
    if (req.path.startsWith(path)) {
      return proxy.web(req, res, { target });
    }
  }
  res.status(404).json({ error: 'Not found' });
});

proxy.on('error', (err, req, res) => {
  console.error('Proxy error:', err);
  res.status(503).json({ error: 'Service unavailable' });
});

app.listen(8080, () => {
  console.log('API Gateway listening on port 8080');
});
```

## 五、数据管理

### 1. 数据库 per 服务

```
用户服务 → PostgreSQL
订单服务 → PostgreSQL
商品服务 → MongoDB
搜索服务 → Elasticsearch
```

### 2. 分布式事务（Saga 模式）

```javascript
// Saga 模式 - 订单创建流程
class OrderSaga {
  async createOrder(order) {
    try {
      await this.step1ReserveInventory(order);
      await this.step2ProcessPayment(order);
      await this.step3CreateOrder(order);
      await this.step4SendNotification(order);
      
      return { success: true, order };
    } catch (error) {
      await this.compensate(error);
      return { success: false, error: error.message };
    }
  }
  
  async step1ReserveInventory(order) {
    try {
      await inventoryService.reserve(order.items);
    } catch (error) {
      throw new Error('Inventory reservation failed');
    }
  }
  
  async step2ProcessPayment(order) {
    try {
      await paymentService.process(order.payment);
    } catch (error) {
      await inventoryService.release(order.items);
      throw new Error('Payment processing failed');
    }
  }
  
  async step3CreateOrder(order) {
    try {
      return await orderService.create(order);
    } catch (error) {
      await paymentService.refund(order.payment);
      await inventoryService.release(order.items);
      throw new Error('Order creation failed');
    }
  }
  
  async compensate(error) {
    console.log('Saga compensation:', error);
  }
}
```

## 六、容错与弹性

### 1. 熔断器模式（Hystrix/Resilience4j）

```javascript
// 使用 opossum 熔断器
const CircuitBreaker = require('opossum');

const options = {
  timeout: 5000,
  errorThresholdPercentage: 50,
  resetTimeout: 30000
};

const breaker = new CircuitBreaker(asyncFunction, options);

breaker.fallback(() => {
  return 'Fallback response';
});

breaker.on('open', () => console.log('Circuit opened'));
breaker.on('halfOpen', () => console.log('Circuit half-open'));
breaker.on('close', () => console.log('Circuit closed'));

// 使用
const result = await breaker.fire();
```

### 2. 重试模式

```javascript
const pRetry = require('p-retry');

const fetchWithRetry = async (url, options = {}) => {
  return pRetry(
    async () => {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response.json();
    },
    {
      retries: 3,
      onFailedAttempt: error => {
        console.log(`Attempt ${error.attemptNumber} failed. Retrying...`);
      }
    }
  );
};
```

### 3. 舱壁模式

```javascript
// 限制并发数
const pLimit = require('p-limit');

const limit = pLimit(10); // 最多 10 个并发

const fetchUsers = async (userIds) => {
  const promises = userIds.map(id => 
    limit(() => fetchUser(id))
  );
  return Promise.all(promises);
};
```

## 七、监控与可观测性

### 1. 日志（ELK Stack）

```javascript
const winston = require('winston');
const { ElasticsearchTransport } = require('winston-elasticsearch');

const logger = winston.createLogger({
  level: 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new ElasticsearchTransport({
      node: 'http://elasticsearch:9200',
      index: 'logs-%Y%m%d'
    })
  ]
});

logger.info('Order created', { orderId: '123', userId: '456' });
```

### 2. 指标（Prometheus + Grafana）

```javascript
const promClient = require('prom-client');

const register = new promClient.Registry();
promClient.collectDefaultMetrics({ register });

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register]
});

const app = express();

app.use((req, res, next) => {
  const end = httpRequestDuration.startTimer();
  res.on('finish', () => {
    end({
      method: req.method,
      route: req.route?.path || req.path,
      status_code: res.statusCode
    });
  });
  next();
});

app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.send(await register.metrics());
});
```

### 3. 分布式追踪（Jaeger/Zipkin）

```javascript
const initTracer = require('jaeger-client').initTracer;

const config = {
  serviceName: 'order-service',
  sampler: { type: 'const', param: 1 },
  reporter: { logSpans: true }
};

const tracer = initTracer(config);

// 使用
const span = tracer.startSpan('create-order');
try {
  span.setTag('order.id', orderId);
  await createOrder(order);
  span.setTag('success', true);
} catch (error) {
  span.setTag('error', true);
  span.log({ event: 'error', error: error.message });
  throw error;
} finally {
  span.finish();
}
```

## 八、部署与运维

### 1. Docker 容器化

```dockerfile
# Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
EXPOSE 3000
CMD ["node", "server.js"]
```

### 2. Kubernetes 部署

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: my-registry/user-service:latest
        ports:
        - containerPort: 3001
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 3001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3001
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"

---
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3001
  type: ClusterIP
```

### 3. CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy to Kubernetes

on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: my-registry/user-service:${{ github.sha }}
      
      - name: Deploy to Kubernetes
        uses: steebchen/kubectl@v2
        with:
          config: ${{ secrets.KUBE_CONFIG }}
          command: set image deployment/user-service user-service=my-registry/user-service:${{ github.sha }}
```

## 九、最佳实践

1. 从单体开始，逐步拆分
2. 合理划分服务边界
3. 优先使用异步通信
4. 设计容错和弹性
5. 实现可观测性
6. 自动化一切
7. 安全第一
8. 文档化 API
9. 监控和告警
10. 持续改进

## 十、总结

微服务架构核心：
- 理解架构特点和优缺点
- 合理拆分服务
- 实现服务通信
- 使用 API 网关
- 管理分布式数据
- 设计容错弹性
- 实现可观测性
- 容器化部署
- 遵循最佳实践

根据实际情况选择架构，不要为了微服务而微服务！
