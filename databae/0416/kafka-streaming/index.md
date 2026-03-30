# Kafka 与流处理完全指南：消息队列实战

> 深入讲解 Kafka 和流处理，包括 Topic、Partition、Consumer Group、Offset 管理，以及 Streams API 和实际项目中的消息队列架构。

## 一、Kafka 基础

### 1.1 什么是 Kafka

分布式流平台：

```
┌─────────────────────────────────────────────────────┐
│                    Kafka Cluster                     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ Broker1 │  │ Broker2 │  │ Broker3 │            │
│  │  :9092  │  │  :9092  │  │  :9092  │            │
│  └─────────┘  └─────────┘  └─────────┘            │
└─────────────────────────────────────────────────────┘
        ↑               ↑               ↑
Producer          Consumer         Consumer
```

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| Broker | Kafka 服务节点 |
| Topic | 消息主题 |
| Partition | 分区 |
| Producer | 生产者 |
| Consumer | 消费者 |
| Consumer Group | 消费者组 |

## 二、Topic 与 Partition

### 2.1 创建 Topic

```bash
# 创建
kafka-topics.sh --create \
  --topic user-events \
  --partitions 3 \
  --replication-factor 1 \
  --bootstrap-server localhost:9092

# 列表
kafka-topics.sh --list \
  --bootstrap-server localhost:9092

# 详情
kafka-topics.sh --describe \
  --topic user-events \
  --bootstrap-server localhost:9092
```

### 2.2 分区原理

```
Topic: user-events (3 partitions)

┌────────────────────────────────────────┐
│            user-events                 │
├──────────┬──────────┬─────────────────┤
│    P0    │    P1    │       P2        │
│ [0,100)  │ [100,200)│ [200,...]       │
└──────────┴──────────┴─────────────────┘
     ↑           ↑            ↑
  Leader      Leader       Leader
```

## 三、生产者

### 3.1 Java 生产者

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("key.serializer", "org.apache.kafka.common.serialization.StringSerializer");
props.put("value.serializer", "org.apache.kafka.common.serialization.StringSerializer");

KafkaProducer<String, String> producer = new KafkaProducer<>(props);

ProducerRecord<String, String> record = new ProducerRecord<>(
    "user-events",
    "user-id-123",
    "{\"event\": \"login\", \"userId\": 123}"
);

producer.send(record);
producer.close();
```

### 3.2 分区策略

```java
// 指定分区
new ProducerRecord<>("topic", partition, key, value);

// 键哈希
// partition = hash(key) % numPartitions
```

## 四、消费者

### 4.1 Java 消费者

```java
Properties props = new Properties();
props.put("bootstrap.servers", "localhost:9092");
props.put("group.id", "my-group");
props.put("key.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");
props.put("value.deserializer", "org.apache.kafka.common.serialization.StringDeserializer");

KafkaConsumer<String, String> consumer = new KafkaConsumer<>(props);
consumer.subscribe(Collections.singletonList("user-events"));

while (true) {
    ConsumerRecords<String, String> records = consumer.poll(Duration.ofMillis(100));
    for (ConsumerRecord<String, String> record : records) {
        System.out.println(record.value());
    }
}
```

### 4.2 Consumer Group

```
Topic: user-events

Group A: ┌─────────┐
         │Consumer1│ → P0, P1
         │Consumer2│ → P2
         └─────────┘

Group B: ┌─────────┐
         │Consumer1│ → P0, P1, P2 (全部)
         └─────────┘
```

## 五、Offset 管理

### 5.1 提交 Offset

```java
// 自动提交（默认）
props.put("enable.auto.commit", "true");
props.put("auto.commit.interval.ms", "5000");

// 手动提交
consumer.commitSync();  // 同步
consumer.commitAsync(); // 异步
```

### 5.2 读取策略

```java
// 从头开始
consumer.seekToBeginning(Collections.emptyList());

// 从最新
consumer.seekToEnd(Collections.emptyList());

// 从指定 offset
consumer.seek(new TopicPartition("user-events", 0), 100);
```

## 六、Kafka Streams

### 6.1 简单流处理

```java
KStreamBuilder builder = new KStreamBuilder();

KStream<String, String> source = builder.stream("user-events");

KStream<String, String> transformed = source
    .filter((key, value) -> value.contains("login"))
    .map((key, value) -> KeyValue.pair(key, value.toUpperCase()));

transformed.to("user-events-upper");
```

### 6.2 聚合操作

```java
KTable<String, Long> counts = source
    .map((key, value) -> KeyValue.pair(extractUser(value), 1L))
    .groupByKey(Serialized.with(Serdes.String(), Serdes.Long()))
    .count("user-counts");

counts.to(Serdes.String(), Serdes.Long(), "user-counts-topic");
```

## 七、实战案例

### 7.1 日志收集

```
┌─────────┐    ┌─────────┐    ┌─────────┐
│  App    │───►│  Kafka  │───►│  Logstash │
│  Logs   │    │  Topic  │    │          │
└─────────┘    └─────────┘    └─────┬────┘
                                    │
                              ┌─────▼────┐
                              │ Elastic  │
                              │ search   │
                              └──────────┘
```

### 7.2 实时统计

```java
// 实时统计每分钟登录次数
KTable<Windowed<String>, Long> loginCounts = source
    .filter((k, v) -> v.contains("login"))
    .map((k, v) -> KeyValue.pair(v.getTimestamp(), 1L))
    .groupByKey()
    .windowedBy(TimeWindows.of(Duration.ofMinutes(1)))
    .count();
```

## 八、总结

Kafka 核心要点：

1. **Topic**：消息主题
2. **Partition**：分区并行
3. **Producer**：消息生产
4. **Consumer**：消息消费
5. **Consumer Group**：消费组
6. **Offset**：消费位置
7. **Streams**：流处理

掌握这些，消息队列 so easy！

---

**推荐阅读**：
- [Kafka 官方文档](https://kafka.apache.org/documentation/)

**如果对你有帮助，欢迎点赞收藏！**
