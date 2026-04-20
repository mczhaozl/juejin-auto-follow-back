# RedisBloom 完全指南

## 一、布隆过滤器

```javascript
// 创建布隆过滤器
BF.RESERVE bf 0.01 100000 // 误差率0.01，容量100k

// 添加元素
BF.ADD bf item1
BF.MADD bf item2 item3 item4

// 检查元素
BF.EXISTS bf item1
BF.MEXISTS bf item1 item2 item3
```

## 二、Cuckoo 过滤器

```javascript
// 创建 cuckoo 过滤器（支持删除）
CF.RESERVE cf 100000

// 添加
CF.ADD cf item
CF.ADDNX cf item // 仅当不存在时

// 删除
CF.DEL cf item

// 检查
CF.EXISTS cf item
```

## 三、Count-Min Sketch

```javascript
// 统计元素频率
CMS.INITBYDIM cms 1000 5

// 增加计数
CMS.INCRBY cms item1 10
CMS.INCRBY cms item2 20

// 查询
CMS.QUERY cms item1
```

## 四、Top-K

```javascript
// 追踪 Top K 元素
TOPK.RESERVE topk 50 2000 7 0.925

// 添加
TOPK.ADD topk a b c d e f g

// 查询 Top K
TOPK.LIST topk
```

## 五、最佳实践

- 布隆过滤器用于存在性判断（不支持删除）
- Cuckoo 支持删除操作
- Count-Min Sketch 用于频率统计
- Top-K 用于热门元素追踪
- 合理配置容量和误差率
