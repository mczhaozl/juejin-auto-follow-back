# Redis Stack 完全指南

## 一、Redis Stack 简介

Redis Stack 是一个包含多个高级模块的包，包括：
- RedisJSON
- RediSearch
- RedisTimeSeries
- RedisBloom

## 二、RedisJSON

```javascript
// 存储 JSON
JSON.SET user:1 $ '{"name":"Alice","age":30}'

// 读取
JSON.GET user:1
JSON.GET user:1 $.name

// 操作
JSON.NUMINCRBY user:1 $.age 1
```

## 三、RediSearch

```javascript
// 创建索引
FT.CREATE users ON JSON PREFIX 1 user: SCHEMA $.name AS name TEXT $.age AS age NUMERIC

// 搜索
FT.SEARCH users '@name:Alice @age:[20 40]'

// 聚合
FT.AGGREGATE users '*' GROUPBY 1 @name COUNT
```

## 四、RedisTimeSeries

```javascript
// 创建时间序列
TS.CREATE temp:room1 RETENTION 86400000 DUPLICATE_POLICY LAST

// 添加数据
TS.ADD temp:room1 1609459200 25.5
TS.ADD temp:room1 1609459300 26.0

// 查询
TS.RANGE temp:room1 1609459200 1609459999
TS.MRANGE 1609459200 1609459999 FILTER area=room1

// 聚合
TS.RANGE temp:room1 1609459200 1609459999 AGGREGATION avg 3600
```

## 五、RedisBloom

```javascript
// 布隆过滤器
BF.REGISTER bf 0.01 1000000
BF.ADD bf item1
BF.EXISTS bf item1

// 布谷鸟过滤器
CF.CREATE cf 1000000
CF.ADD cf item1
CF.EXISTS cf item1

// Count-Min Sketch
CMS.INITBYDIM cms 1000 5
CMS.INCRBY cms item1 10
CMS.QUERY cms item1

// Top-K
TOPK.RESERVE topk 50 2000 7 0.925
TOPK.ADD topk item1 item2 item3
TOPK.LIST topk
```

## 六、最佳实践

- 使用 RedisJSON 处理复杂数据
- RediSearch 提供强大的检索能力
- RedisTimeSeries 处理时序数据
- 布隆过滤器节省空间
- 考虑使用 Redis Stack Server
