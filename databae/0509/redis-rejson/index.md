# Redis ReJSON 完全指南

## 一、JSON 操作

```javascript
// 设置完整 JSON
JSON.SET user:1 $ '{"name":"Alice","age":30,"address":{"city":"Beijing"}}'

// 获取字段
JSON.GET user:1
JSON.GET user:1 $.name
JSON.GET user:1 $.address.city

// 更新字段
JSON.SET user:1 $.name '"Alice Smith"'
JSON.NUMINCRBY user:1 $.age 1
```

## 二、数组操作

```javascript
// 数组追加
JSON.ARRAPPEND user:1 $.hobbies '"reading"'

// 数组索引
JSON.GET user:1 $.hobbies[0]

// 数组长度
JSON.ARRLEN user:1 $.hobbies
```

## 三、路径表达式

```javascript
// 通配符
JSON.GET user:1 $.address.*
JSON.GET user:1 $.hobbies[*]

// 条件筛选
JSON.GET user:1 $.orders[?(@.total>100)]
```

## 四、与搜索集成

```javascript
// 索引 JSON 字段
FT.CREATE users ON JSON PREFIX 1 user: SCHEMA 
  $.name AS name TEXT 
  $.age AS age NUMERIC 
  $.address.city AS city TAG

// 查询
FT.SEARCH users "@name:A* @age:[20 40] @city:Beijing"
```

## 五、最佳实践

- 使用 RediSearch 与 ReJSON 组合
- 合理设计 JSON schema
- 部分更新优化性能
- 监控内存使用
- 考虑持久化策略
- 批量操作优化
