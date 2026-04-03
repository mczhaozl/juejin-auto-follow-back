# 那个因为 API 设计混乱而导致线上事故的周一

这是一个关于 API 设计的职场故事，希望能给你一些启发。

## 一、背景

那是一个周一的早上，我刚到公司，正准备喝杯咖啡开始新的一周。

"不好了！支付功能出问题了！大量用户投诉！" 测试同学的声音从旁边传来。

我心里一紧，赶紧打开监控面板。果然，错误率飙升，支付成功率从 99.9% 跌到了 60%。

## 二、问题排查

我赶紧查看日志，发现大量这样的错误：

```
TypeError: Cannot read property 'id' of undefined
```

这是前端报错，说明某个预期的字段不存在。我赶紧找到负责这个功能的前端同学。

"昨天后端同学说 API 有调整，让我把 amount 改成 price，我就改了。" 前端同学说。

我赶紧去看后端代码。后端确实改了，但是...

```javascript
// 旧版本
{
  "orderId": "123",
  "amount": 99.99,
  "status": "pending"
}

// 新版本
{
  "orderId": "123",
  "price": 99.99,
  "payment": {
    "id": "pay_123",
    "status": "pending"
  }
}
```

不仅改了字段名，还把 status 移到了 payment 对象里！而且没有版本号，没有过渡期！

## 三、根本原因

事后复盘，我们发现了一堆 API 设计问题：

### 1. 没有版本管理

```javascript
// ❌ 不好
GET /api/orders

// ✅ 好
GET /api/v1/orders
GET /api/v2/orders
```

### 2. 破坏性变更没有过渡期

直接上线新版本，没有兼容旧版本。

### 3. 字段命名不一致

一会儿叫 amount，一会儿叫 price。

### 4. 没有 API 文档

接口变更只在群里说了一句，没有正式文档。

### 5. 错误处理不规范

```javascript
// ❌ 不好
{
  "error": "something wrong"
}

// ✅ 好
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid amount",
  "details": {
    "field": "amount",
    "reason": "must be positive"
  }
}
```

## 四、解决方案

痛定思痛，我们制定了 API 设计规范：

### 1. RESTful API 设计

```javascript
// GET    /api/v1/orders          - 获取列表
// GET    /api/v1/orders/:id      - 获取单个
// POST   /api/v1/orders          - 创建
// PUT    /api/v1/orders/:id      - 完全更新
// PATCH  /api/v1/orders/:id      - 部分更新
// DELETE /api/v1/orders/:id      - 删除
```

### 2. 统一响应格式

```javascript
// 成功响应
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": 1234567890,
    "version": "v1"
  }
}

// 失败响应
{
  "success": false,
  "error": {
    "code": "ORDER_NOT_FOUND",
    "message": "Order not found",
    "details": { "orderId": "123" }
  }
}
```

### 3. 分页设计

```javascript
GET /api/v1/orders?page=1&limit=20&sort=-createdAt

{
  "success": true,
  "data": [...],
  "meta": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

### 4. 版本管理策略

```javascript
// 同时支持 v1 和 v2
app.get('/api/v1/orders', handlerV1);
app.get('/api/v2/orders', handlerV2);

// 旧版本保留 3 个月
// 提前通知用户迁移
```

### 5. API 文档自动化

使用 Swagger/OpenAPI：

```yaml
openapi: 3.0.0
info:
  title: Order API
  version: 1.0.0
paths:
  /api/v1/orders:
    get:
      summary: Get orders
      responses:
        '200':
          description: Successful response
```

## 五、结果

实施这些规范后：
- 再也没有因为 API 变更导致的线上事故
- 前后端协作更顺畅
- 新同事上手更快
- API 文档自动更新

## 六、总结

API 设计不是小事，它直接影响：
- 系统稳定性
- 开发效率
- 用户体验
- 你的周末（能不能安心休息）

好的 API 设计+版本管理+文档=安心的周一！
