# Node.js 微服务架构完全指南：从原理到实战

## 一、微服务架构概述

### 1.1 什么是微服务
微服务是一种架构风格，将应用构建为一组小型、独立部署的服务。

### 1.2 微服务特点
- 独立部署与扩展
- 专注单一功能
- 独立技术栈
- 独立数据存储
- 通过网络通信

---

## 二、项目初始化

```bash
mkdir nodejs-microservices
cd nodejs-microservices
npm init -y
npm install express axios mongoose amqplib
```

---

## 三、API Gateway

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
const PORT = 3000;

const SERVICES = {
  users: 'http://localhost:3001',
  products: 'http://localhost:3002',
  orders: 'http://localhost:3003'
};

app.use(express.json());

app.get('/api/users', async (req, res) => {
  try {
    const response = await axios.get(`${SERVICES.users}/users`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.get('/api/products', async (req, res) => {
  try {
    const response = await axios.get(`${SERVICES.products}/products`);
    res.json(response.data);
  } catch (error) {
    res.status(500).json({ error: 'Service unavailable' });
  }
});

app.listen(PORT, () => {
  console.log(`API Gateway running on port ${PORT}`);
});
```

---

## 四、用户服务

```javascript
const express = require('express');
const mongoose = require('mongoose');

const app = express();
const PORT = 3001;

mongoose.connect('mongodb://localhost:27017/users')
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error(err));

const userSchema = new mongoose.Schema({
  name: String,
  email: String,
  createdAt: { type: Date, default: Date.now }
});

const User = mongoose.model('User', userSchema);

app.use(express.json());

app.get('/users', async (req, res) => {
  const users = await User.find();
  res.json(users);
});

app.post('/users', async (req, res) => {
  const user = new User(req.body);
  await user.save();
  res.status(201).json(user);
});

app.listen(PORT, () => {
  console.log(`User service running on port ${PORT}`);
});
```

---

## 五、产品服务

```javascript
const express = require('express');
const mongoose = require('mongoose');

const app = express();
const PORT = 3002;

mongoose.connect('mongodb://localhost:27017/products')
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error(err));

const productSchema = new mongoose.Schema({
  name: String,
  price: Number,
  stock: Number
});

const Product = mongoose.model('Product', productSchema);

app.use(express.json());

app.get('/products', async (req, res) => {
  const products = await Product.find();
  res.json(products);
});

app.post('/products', async (req, res) => {
  const product = new Product(req.body);
  await product.save();
  res.status(201).json(product);
});

app.listen(PORT, () => {
  console.log(`Product service running on port ${PORT}`);
});
```

---

## 六、订单服务

```javascript
const express = require('express');
const mongoose = require('mongoose');
const amqplib = require('amqplib');

const app = express();
const PORT = 3003;

mongoose.connect('mongodb://localhost:27017/orders')
  .then(() => console.log('Connected to MongoDB'))
  .catch(err => console.error(err));

let channel;
async function connectRabbitMQ() {
  const connection = await amqplib.connect('amqp://localhost');
  channel = await connection.createChannel();
  await channel.assertQueue('order-events');
}
connectRabbitMQ();

const orderSchema = new mongoose.Schema({
  userId: mongoose.Schema.Types.ObjectId,
  productId: mongoose.Schema.Types.ObjectId,
  quantity: Number,
  status: { type: String, default: 'pending' }
});

const Order = mongoose.model('Order', orderSchema);

app.use(express.json());

app.get('/orders', async (req, res) => {
  const orders = await Order.find();
  res.json(orders);
});

app.post('/orders', async (req, res) => {
  const order = new Order(req.body);
  await order.save();
  channel.sendToQueue('order-events', Buffer.from(JSON.stringify(order)));
  res.status(201).json(order);
});

app.listen(PORT, () => {
  console.log(`Order service running on port ${PORT}`);
});
```

---

## 七、服务发现

```javascript
const serviceRegistry = new Map();

function registerService(name, url) {
  serviceRegistry.set(name, { url, healthy: true, lastHeartbeat: Date.now() });
}

function getService(name) {
  return serviceRegistry.get(name);
}

function heartbeat(name) {
  const service = serviceRegistry.get(name);
  if (service) {
    service.lastHeartbeat = Date.now();
    service.healthy = true;
  }
}

setInterval(() => {
  const now = Date.now();
  for (const [name, service] of serviceRegistry) {
    if (now - service.lastHeartbeat > 30000) {
      service.healthy = false;
    }
  }
}, 10000);
```

---

## 八、熔断器模式

```javascript
class CircuitBreaker {
  constructor(request, failureThreshold = 3, recoveryTimeout = 30000) {
    this.request = request;
    this.failureThreshold = failureThreshold;
    this.recoveryTimeout = recoveryTimeout;
    this.state = 'CLOSED';
    this.failureCount = 0;
    this.lastFailureTime = 0;
  }

  async fire() {
    if (this.state === 'OPEN') {
      if (Date.now() - this.lastFailureTime > this.recoveryTimeout) {
        this.state = 'HALF-OPEN';
      } else {
        throw new Error('Circuit breaker is open');
      }
    }

    try {
      const result = await this.request();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  onSuccess() {
    this.failureCount = 0;
    this.state = 'CLOSED';
  }

  onFailure() {
    this.failureCount++;
    this.lastFailureTime = Date.now();
    if (this.failureCount >= this.failureThreshold) {
      this.state = 'OPEN';
    }
  }
}
```

---

## 九、限流与降级

```javascript
class RateLimiter {
  constructor(maxRequests, windowMs) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
    this.requests = new Map();
  }

  isAllowed(key) {
    const now = Date.now();
    const windowStart = now - this.windowMs;
    
    if (!this.requests.has(key)) {
      this.requests.set(key, []);
    }
    
    const timestamps = this.requests.get(key);
    const filtered = timestamps.filter(t => t > windowStart);
    this.requests.set(key, filtered);
    
    if (filtered.length < this.maxRequests) {
      filtered.push(now);
      return true;
    }
    return false;
  }
}
```

---

## 十、Docker Compose 部署

```yaml
version: '3.8'
services:
  mongodb:
    image: mongo:5
    ports:
      - "27017:27017"
  
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
  
  gateway:
    build: ./gateway
    ports:
      - "3000:3000"
    depends_on:
      - users
      - products
      - orders
  
  users:
    build: ./users
    ports:
      - "3001:3001"
    depends_on:
      - mongodb
  
  products:
    build: ./products
    ports:
      - "3002:3002"
    depends_on:
      - mongodb
  
  orders:
    build: ./orders
    ports:
      - "3003:3003"
    depends_on:
      - mongodb
      - rabbitmq
```

---

## 十一、最佳实践

1. 每个服务有独立数据库
2. 使用异步通信处理跨服务调用
3. 实现熔断器与降级策略
4. 完善的监控与日志
5. 容器化部署与自动化 CI/CD

---

## 十二、总结

微服务架构提供了更好的可扩展性和可维护性，但也带来了复杂性的增加。
