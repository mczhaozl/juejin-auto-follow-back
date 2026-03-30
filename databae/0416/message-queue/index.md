# 消息队列完全指南：RabbitMQ 与应用场景

> 深入讲解消息队列，包括 RabbitMQ 核心概念、Exchange、Queue、Binding，以及死信队列、延迟队列和实际项目中的异步处理架构。

## 一、消息队列基础

### 1.1 为什么需要消息队列

异步处理：

```
同步:  请求 → 处理 → 响应  (串行，阻塞)

异步:  请求 → 队列 ← 消费者处理  (并行，非阻塞)
```

### 1.2 核心优势

| 优势 | 说明 |
|------|------|
| 解耦 | 生产者与消费者分离 |
| 削峰 | 流量高峰期缓冲 |
| 异步 | 非核心流程异步处理 |
| 可靠 | 消息持久化 |

## 二、RabbitMQ 基础

### 2.1 核心概念

```
┌─────────────────────────────────────────────────────────────┐
│                      RabbitMQ                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   Exchange                           │   │
│  │    ┌──────────┐    ┌──────────┐    ┌──────────┐   │   │
│  │    │  Direct  │    │   Fanout │    │   Topic  │   │   │
│  │    └────┬─────┘    └────┬─────┘    └────┬─────┘   │   │
│  └─────────┼───────────────┼───────────────┼───────────┘   │
│            │               │               │                 │
│  ┌─────────┼───────────────┼───────────────┼─────────────┐ │
│  │         ▼               ▼               ▼             │ │
│  │    ┌───────┐       ┌───────┐       ┌───────┐        │ │
│  │    │Queue 1│       │Queue 2│       │Queue 3│        │ │
│  │    └───────┘       └───────┘       └───────┘        │ │
│  │        ▲               ▲               ▲             │ │
│  └────────┼───────────────┼───────────────┼────────────┘ │
│           └───────────────┴───────────────┘               │
│                      Consumer                               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 安装

```bash
# Docker 安装
docker run -d --name rabbitmq \
  -p 5672:5672 \
  -p 15672:15672 \
  -e RABBITMQ_DEFAULT_USER=guest \
  -e RABBITMQ_DEFAULT_PASS=guest \
  rabbitmq:management
```

## 三、Exchange 类型

### 3.1 Direct

完全匹配：

```javascript
// 生产者
channel.assertExchange('direct_logs', 'direct', { durable: false });

channel.publish(
  'direct_logs',
  'error',  // routing key
  Buffer.from('Error message')
);

// 消费者
channel.assertQueue('error_queue', { durable: false });
channel.bindQueue('error_queue', 'direct_logs', 'error');
```

### 3.2 Fanout

广播：

```javascript
// 生产者
channel.assertExchange('logs', 'fanout', { durable: false });
channel.publish('logs', '', Buffer.from('Broadcast message'));

// 消费者 1
channel.assertQueue('queue1', { durable: false });
channel.bindQueue('queue1', 'logs', '');

// 消费者 2
channel.assertQueue('queue2', { durable: false });
channel.bindQueue('queue2', 'logs', '');
```

### 3.3 Topic

模式匹配：

```javascript
// routing key 格式: user.*.order
// * 匹配一个词
// # 匹配零个或多个词

// 生产者
channel.publish('topic_exchange', 'user.created.order', Buffer.from('msg'));

// 消费者
channel.bindQueue('queue1', 'topic_exchange', 'user.*.order');
channel.bindQueue('queue2', 'topic_exchange', 'user.#');
```

## 四、消息确认

### 4.1 手动确认

```javascript
// 消费者
channel.consume('queue', (msg) => {
  const content = msg.content.toString();
  
  try {
    // 处理消息
    processMessage(content);
    
    // 确认消息
    channel.ack(msg);
  } catch (error) {
    // 拒绝消息，重新入队
    channel.nack(msg, false, true);
  }
}, { noAck: false });
```

### 4.2 自动确认

```javascript
channel.consume('queue', (msg) => {
  console.log(msg.content.toString());
}, { noAck: true });
```

## 五、死信队列

### 5.1 配置

```javascript
// 声明死信交换机和队列
channel.assertExchange('dlx.exchange', 'direct', { durable: true });
channel.assertQueue('dlx.queue', { durable: true });
channel.bindQueue('dlx.queue', 'dlx.exchange', 'dlx.routing.key');

// 主队列配置死信
channel.assertQueue('main.queue', {
  durable: true,
  arguments: {
    'x-dead-letter-exchange': 'dlx.exchange',
    'x-dead-letter-routing-key': 'dlx.routing.key'
  }
});
```

### 5.2 消息过期

```javascript
// 设置消息过期时间
channel.sendToQueue('main.queue', Buffer.from('msg'), {
  expiration: '10000'  // 10秒
});
```

## 六、延迟队列

### 6.1 TTL + 死信

```javascript
// 生产延迟消息
channel.assertQueue('delay.queue', {
  durable: true,
  arguments: {
    'x-message-ttl': 5000,  // 5秒后过期
    'x-dead-letter-exchange': 'real.exchange'
  }
});

channel.sendToQueue('delay.queue', Buffer.from('delayed message'));
```

### 6.2 延迟插件

```bash
# 安装延迟插件
rabbitmq-plugins enable rabbitmq_delayed_message_exchange
```

```javascript
// 使用延迟交换机
channel.assertExchange('delayed.exchange', 'x-delayed-message', {
  durable: true,
  arguments: { 'x-delayed-type': 'direct' }
});
```

## 七、实战案例

### 7.1 订单处理

```
┌─────────┐    ┌─────────────┐    ┌──────────────┐
│  用户   │───►│  订单服务   │───►│  消息队列    │
│  下单   │    │  创建订单   │    │  order.created │
└─────────┘    └─────────────┘    └──────┬───────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
            ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
            │  库存服务    │    │  通知服务    │    │  积分服务    │
            │  扣减库存    │    │  发送通知    │    │  增加积分    │
            └──────────────┘    └──────────────┘    └──────────────┘
```

### 7.2 代码实现

```javascript
// 订单服务 - 生产消息
async function createOrder(order) {
  const orderId = await saveOrder(order);
  
  // 发送消息
  channel.publish(
    'order.events',
    'order.created',
    Buffer.from(JSON.stringify({ orderId, order })),
    { persistent: true }
  );
  
  return orderId;
}

// 库存服务 - 消费消息
channel.consume('inventory.queue', async (msg) => {
  const { orderId, items } = JSON.parse(msg.content.toString());
  
  try {
    await deductInventory(items);
    channel.ack(msg);
  } catch (error) {
    channel.nack(msg, false, false); // 不重新入队
    // 发送库存不足事件
  }
});
```

## 八、总结

消息队列核心要点：

1. **消息队列**：异步解耦
2. **RabbitMQ**：AMQP 实现
3. **Exchange**：路由规则
4. **Queue**：消息存储
5. **消息确认**：可靠性
6. **死信队列**：异常处理
7. **延迟队列**：定时任务

掌握这些，消息队列 so easy！

---

**推荐阅读**：
- [RabbitMQ 官方文档](https://www.rabbitmq.com/documentation.html)

**如果对你有帮助，欢迎点赞收藏！**
