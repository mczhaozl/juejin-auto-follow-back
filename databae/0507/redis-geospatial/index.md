# Redis Geospatial 地理位置完全指南

## 一、添加地理位置

```javascript
GEOADD cities 116.4074 39.9042 "Beijing"
GEOADD cities 121.4737 31.2304 "Shanghai"
GEOADD cities 113.2644 23.1291 "Guangzhou"
```

## 二、计算距离

```javascript
GEODIST cities "Beijing" "Shanghai" km
```

## 三、查找附近的位置

```javascript
GEOSEARCH cities FROMLONLAT 116.40 39.91 BYRADIUS 100 km WITHCOORD WITHDIST
```

```javascript
GEOSEARCH cities BYMEMBER "Beijing" BYRADIUS 200 km WITHCOORD
```

## 四、获取 Geohash

```javascript
GEOHASH cities "Beijing" "Shanghai"
```

## 五、应用场景

```javascript
// 附近的餐厅
GEOADD restaurants 116.4 39.9 "KFC"
GEOSEARCH restaurants FROMLONLAT 116.39 39.91 BYRADIUS 1 km

// 出租车实时位置
GEOADD taxis 116.4 39.9 "taxi_001"
GEOADD taxis 116.41 39.905 "taxi_002"
```

## 六、最佳实践

- 合理选择精度
- 定期更新位置
- 使用 Radius 查询
- 考虑索引和性能
- 分布式情况下分片
- 监控内存使用
