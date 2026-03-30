# RESTful API 完全指南：设计与最佳实践

> 深入讲解 RESTful API 设计，包括资源命名、HTTP 方法、状态码、版本控制，以及实际项目中的 API 安全和文档编写。

## 一、REST 原则

### 1.1 核心原则

- **资源**：所有内容都是资源
- **URI**：资源用 URI 标识
- **无状态**：请求包含所有信息
- **统一接口**：标准 HTTP 方法

### 1.2 URL 设计

```
# 资源集合
GET    /users          # 获取用户列表
POST   /users          # 创建用户

# 单个资源
GET    /users/:id      # 获取用户
PUT    /users/:id      # 更新用户
DELETE /users/:id      # 删除用户

# 子资源
GET    /users/:id/posts    # 用户文章
POST   /users/:id/posts    # 用户创建文章
```

## 二、HTTP 方法

### 2.1 方法含义

| 方法 | 说明 | 幂等 |
|------|------|------|
| GET | 获取资源 | 是 |
| POST | 创建资源 | 否 |
| PUT | 完整更新 | 是 |
| PATCH | 部分更新 | 否 |
| DELETE | 删除资源 | 是 |

### 2.2 例子

```http
# 获取列表
GET /users

# 获取单个
GET /users/123

# 创建
POST /users
Content-Type: application/json
{"name": "张三", "email": "zhangsan@example.com"}

# 完整更新
PUT /users/123
Content-Type: application/json
{"name": "李四", "email": "lisi@example.com"}

# 部分更新
PATCH /users/123
Content-Type: application/json
{"name": "王五"}

# 删除
DELETE /users/123
```

## 三、状态码

### 3.1 成功

```http
200 OK                  # 成功
201 Created            # 创建成功
204 No Content         # 删除成功
```

### 3.2 客户端错误

```http
400 Bad Request        # 请求错误
401 Unauthorized       # 未认证
403 Forbidden          # 无权限
404 Not Found          # 资源不存在
422 Unprocessable      # 验证失败
429 Too Many Requests  # 请求过多
```

### 3.3 服务端错误

```http
500 Internal Server Error
502 Bad Gateway
503 Service Unavailable
```

## 四、版本控制

### 4.1 URL 版本

```
/api/v1/users
/api/v2/users
```

### 4.2 Header 版本

```http
Accept: application/vnd.myapp.v2+json
```

## 五、响应格式

### 5.1 标准格式

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "name": "张三"
  }
}
```

### 5.2 列表响应

```json
{
  "data": [
    {"id": 1, "name": "张三"},
    {"id": 2, "name": "李四"}
  ],
  "pagination": {
    "page": 1,
    "pageSize": 10,
    "total": 100
  }
}
```

### 5.3 错误响应

```json
{
  "code": 400,
  "message": "Validation failed",
  "errors": [
    {"field": "email", "message": "Invalid email format"}
  ]
}
```

## 六、安全

### 6.1 认证

```http
Authorization: Bearer <token>
```

### 6.2 限流

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640000000
```

## 七、总结

RESTful API 核心要点：

1. **资源**：URI 设计
2. **方法**：GET/POST/PUT/DELETE
3. **状态码**：语义化返回
4. **版本**：API 版本控制
5. **安全**：认证限流

掌握这些，API 设计更规范！

---

**推荐阅读**：
- [RESTful API 设计最佳实践](https://restfulapi.net/)

**如果对你有帮助，欢迎点赞收藏！**
