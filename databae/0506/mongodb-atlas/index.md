# MongoDB Atlas 完全指南

## 一、MongoDB Atlas 简介

MongoDB 官方提供的云托管数据库服务，提供安全、高可用的数据库部署。

## 二、创建集群

### 2.1 选择部署类型

- **Shared**: 适合开发测试
- **Dedicated**: 适合生产环境
- **Serverless**: 按使用量付费

### 2.2 配置连接

```javascript
// 连接字符串
const uri = "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority";
const client = new MongoClient(uri);
```

## 三、安全配置

### 3.1 IP 白名单

```javascript
// 配置特定 IP 访问
```

### 3.2 数据库用户

```javascript
// 创建只读用户
db.createUser({
  user: "reader",
  pwd: "password",
  roles: [{ role: "read", db: "myDatabase" }]
});
```

## 四、备份和恢复

```javascript
// Atlas 提供自动备份
// 可以按需恢复到特定时间点
```

## 五、性能监控

```javascript
// Performance Advisor
// 自动发现性能问题
// 提供索引建议
```

## 六、Atlas Search

```javascript
// 全文搜索
db.collection.aggregate([
  {
    $search: {
      "text": {
        "query": "search term",
        "path": "field"
      }
    }
  }
]);
```

## 七、最佳实践

- 使用 VPC Peering 实现网络隔离
- 定期备份和测试恢复
- 配置合适的高可用级别
- 使用 Atlas Search 增强检索能力
- 监控 Performance Advisor 建议
- 合理配置连接池大小
