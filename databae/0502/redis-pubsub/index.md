# Redis Pub/Sub 发布订阅与消息队列完全指南

## 一、Pub/Sub 概述

### 1.1 什么是 Pub/Sub

发布订阅模式，生产者发布消息，消费者订阅接收。

### 1.2 基本概念

- **Publisher（发布者）**：发送消息
- **Subscriber（订阅者）**：接收消息
- **Channel（频道）**：消息通道

---

## 二、基本用法

### 2.1 订阅频道

```javascript
const redis = require('redis');
const subscriber = redis.createClient();

subscriber.on('message', (channel, message) => {
  console.log(`收到频道 ${channel} 的消息: ${message}`);
});

subscriber.subscribe('news', 'sports');
```

### 2.2 发布消息

```javascript
const publisher = redis.createClient();

publisher.publish('news', '重大新闻！');
publisher.publish('sports', '比赛结果...');
```

### 2.3 取消订阅

```javascript
subscriber.unsubscribe('news');
subscriber.unsubscribe(); // 取消所有
```

---

## 三、模式匹配订阅

### 3.1 订阅模式

```javascript
subscriber.psubscribe('news.*', 'sports.*');

subscriber.on('pmessage', (pattern, channel, message) => {
  console.log(`模式 ${pattern}，频道 ${channel}: ${message}`);
});
```

### 3.2 使用示例

```javascript
// 订阅所有 news 开头的频道
subscriber.psubscribe('news:*');

// 发布
publisher.publish('news:tech', '技术新闻');
publisher.publish('news:business', '商业新闻');
```

---

## 四、查看订阅信息

### 4.1 查看频道

```bash
# 活跃频道
PUBSUB CHANNELS

# 匹配模式
PUBSUB CHANNELS news:*
```

### 4.2 查看订阅数

```bash
# 频道订阅数
PUBSUB NUMSUB news sports

# 模式订阅数
PUBSUB NUMPAT
```

---

## 五、实战场景

### 5.1 实时通知

```javascript
// 发布者
function sendNotification(userId, message) {
  publisher.publish(`notifications:${userId}`, JSON.stringify(message));
}

// 订阅者
subscriber.subscribe('notifications:123');
subscriber.on('message', (channel, message) => {
  const notification = JSON.parse(message);
  console.log('收到通知:', notification);
  // 推送给用户...
});
```

### 5.2 聊天系统

```javascript
// 用户订阅聊天频道
function joinRoom(userId, roomId) {
  subscriber.subscribe(`chat:${roomId}`);
}

// 发送消息
function sendMessage(userId, roomId, content) {
  const message = { userId, content, time: Date.now() };
  publisher.publish(`chat:${roomId}`, JSON.stringify(message));
}

// 接收消息
subscriber.on('message', (channel, message) => {
  if (channel.startsWith('chat:')) {
    const chatMessage = JSON.parse(message);
    console.log('收到聊天消息:', chatMessage);
    // 广播给房间用户...
  }
});
```

### 5.3 任务队列（使用 List）

```javascript
// 生产者
function addTask(queueName, task) {
  publisher.lPush(queueName, JSON.stringify(task));
  publisher.publish(`queue:${queueName}`, 'new-task');
}

// 消费者
async function processTasks(queueName) {
  while (true) {
    const result = await subscriber.brPop(0, queueName);
    const task = JSON.parse(result.element);
    console.log('处理任务:', task);
    // 处理任务...
  }
}
```

---

## 六、消息队列高级模式

### 6.1 可靠队列（Stream）

```javascript
// 生产者
function addToStream(streamName, data) {
  publisher.xAdd(streamName, '*', data);
}

// 消费者
async function consumeStream(streamName, groupName, consumerName) {
  // 创建消费者组
  try {
    await subscriber.xGroupCreate(streamName, groupName, '0', { MKSTREAM: true });
  } catch (err) {
    // 组已存在
  }
  
  while (true) {
    const result = await subscriber.xReadGroup(
      groupName,
      consumerName,
      { key: streamName, id: '>' },
      { COUNT: 1, BLOCK: 0 }
    );
    
    if (result) {
      const [stream, messages] = result[0];
      for (const [id, message] of messages) {
        console.log('处理消息:', id, message);
        // 确认处理
        await subscriber.xAck(streamName, groupName, id);
      }
    }
  }
}
```

### 6.2 延迟队列

```javascript
// 生产者
function addDelayedTask(task, delaySeconds) {
  const executeAt = Date.now() + delaySeconds * 1000;
  publisher.zAdd('delayed-tasks', { score: executeAt, value: JSON.stringify(task) });
}

// 消费者
async function processDelayedTasks() {
  while (true) {
    const now = Date.now();
    const tasks = await subscriber.zRangeByScore('delayed-tasks', 0, now, {
      WITHSCORES: true,
      LIMIT: { offset: 0, count: 1 }
    });
    
    if (tasks.length > 0) {
      const task = JSON.parse(tasks[0].value);
      console.log('处理延迟任务:', task);
      // 删除已处理
      await subscriber.zRem('delayed-tasks', tasks[0].value);
      // 处理任务...
    } else {
      // 等待
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
}
```

### 6.3 广播系统

```javascript
class EventBus {
  constructor() {
    this.publisher = redis.createClient();
    this.subscriber = redis.createClient();
  }
  
  publish(eventName, data) {
    this.publisher.publish(`events:${eventName}`, JSON.stringify(data));
  }
  
  subscribe(eventName, handler) {
    this.subscriber.subscribe(`events:${eventName}`);
    this.subscriber.on('message', (channel, message) => {
      if (channel === `events:${eventName}`) {
        handler(JSON.parse(message));
      }
    });
  }
  
  unsubscribe(eventName) {
    this.subscriber.unsubscribe(`events:${eventName}`);
  }
}

// 使用
const bus = new EventBus();
bus.subscribe('user:created', user => console.log('新用户:', user));
bus.publish('user:created', { id: 1, name: 'John' });
```

---

## 七、注意事项

### 7.1 Pub/Sub 限制

- 消息不持久化
- 断线会丢失消息
- 没有确认机制

### 7.2 解决方案

- 使用 Stream 替代（持久化）
- 使用 List + BRPOP
- 结合持久化存储

---

## 八、性能优化

### 8.1 消息批量处理

```javascript
// 批量发送
const pipeline = publisher.pipeline();
for (const message of messages) {
  pipeline.publish('channel', message);
}
await pipeline.exec();
```

### 8.2 连接复用

```javascript
// 复用连接，不要频繁创建/关闭
```

---

## 总结

Redis Pub/Sub 适合实时通信、通知系统，结合 List 或 Stream 可以构建可靠的消息队列。根据场景选择合适的模式。
