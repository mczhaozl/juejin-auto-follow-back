# RedisTimeSeries 完全指南

## 一、创建时间序列

```javascript
// 创建时间序列，保留 1 天数据，保留重复策略 LAST
TS.CREATE temperature:1 RETENTION 86400000 DUPLICATE_POLICY LAST LABELS sensorId 1 location office

// 添加数据
TS.ADD temperature:1 * 24.5 // * 表示当前时间戳
TS.ADD temperature:1 1609459200000 22.0
```

## 二、查询范围数据

```javascript
// 查询范围
TS.RANGE temperature:1 1609459200000 1609545600000

// 查询聚合
TS.RANGE temperature:1 1609459200000 1609545600000 AGGREGATION avg 3600000 // 1小时平均值
```

## 三、标签和多序列

```javascript
// 带标签的序列
TS.ADD temperature:2 * 23.0 LABELS sensorId 2 location warehouse

// 查询多个序列
TS.MRANGE 1609459200000 1609545600000 FILTER location=office
```

## 四、向下采样（downsampling）

```javascript
// 创建聚合规则
TS.CREATERULE temperature:1 temp_hourly AGGREGATION avg 3600000

// 查询聚合数据
TS.RANGE temp_hourly 1609459200000 1609545600000
```

## 五、最佳实践

- 合理配置 retention（数据保留）
- 使用聚合规则优化查询
- 标签用于组织和筛选序列
- 监控内存使用
- 适合实时数据流处理
