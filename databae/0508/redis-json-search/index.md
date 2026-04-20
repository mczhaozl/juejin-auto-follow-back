# Redis JSON 与搜索完全指南

## 一、存储 JSON 数据

```javascript
// 存储完整 JSON
JSON.SET user:1 $ '{"name":"Alice","age":30,"address":{"city":"Beijing","street":"Main St"}}'

// 获取部分字段
JSON.GET user:1 $.name $.address.city
JSON.GET user:1 $

// 更新字段
JSON.NUMINCRBY user:1 $.age 1
JSON.SET user:1 $.address.street '"Wall St"'
```

## 二、创建搜索索引

```javascript
// 创建 RediSearch 索引
FT.CREATE users ON JSON PREFIX 1 user: SCHEMA 
  $.name AS name TEXT 
  $.age AS age NUMERIC 
  $.address.city AS city TEXT
  $.skills AS skills TAG SEPARATOR ","
```

## 三、全文搜索

```javascript
// 简单查询
FT.SEARCH users "@name:Alice @age:[25 35]"

// 复杂查询
FT.SEARCH users "@city:Beijing (@skills:Go,Redis | @skills:Python)"

// 分页和排序
FT.SEARCH users "@name:A*" SORTBY age DESC LIMIT 0 10
```

## 四、聚合查询

```javascript
// 分组聚合
FT.AGGREGATE users "*" GROUPBY 1 @city REDUCE COUNT 0 AS count

// 排序和分页
FT.AGGREGATE users "*" SORTBY 2 @age DESC LIMIT 0 20
```

## 五、实战：产品目录搜索

```javascript
// 产品数据模型
JSON.SET product:1 $ '{"name":"Wireless Headphones","price":299,"brand":"AudioTech","category":"Electronics","tags":["audio","wireless","headphones"]}'

// 索引
FT.CREATE products ON JSON PREFIX 1 product: SCHEMA 
  $.name AS name TEXT 
  $.price AS price NUMERIC 
  $.brand AS brand TAG 
  $.category AS category TAG 
  $.tags AS tags TAG SEPARATOR ","

// 查询：价格 100-500 的电子产品
FT.SEARCH products "@category:Electronics @price:[100 500]" SORTBY price ASC
```

## 六、最佳实践

- 合理设计索引字段
- 使用 TAG 类型优化过滤性能
- 监控搜索查询性能
- 考虑字段权重设置
- 定期优化索引
- 批量操作优化
