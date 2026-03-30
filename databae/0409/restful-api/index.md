# RESTful API 设计最佳实践：从入门到规范

> 深入讲解 RESTful API 设计原则、URL 规范、HTTP 状态码使用，以及错误处理、版本控制和安全性设计。

## 一、RESTful 基础

### 1.1 什么是 REST

REST（Representational State Transfer）是架构风格，不是标准：

```http
GET    /api/users        # 获取用户列表
GET    /api/users/123    # 获取单个用户
POST   /api/users        # 创建用户
PUT    /api/users/123    # 更新用户
DELETE /api/users/123    # 删除用户
```

### 1.2 核心原则

- **资源**：URL 代表资源，不是动作
- **表示**：资源可以有多种表示（JSON、XML）
- **无状态**：每个请求包含所有信息

## 二、URL 设计

### 2.1 资源命名

```http
# 复数形式
GET /users
GET /orders

# 嵌套关系
GET /users/123/orders
GET /orders?status=pending

# 避免
GET /getUsers      # 错误
GET /user_get     # 错误
```

### 2.2 查询参数

```http
# 过滤
GET /users?status=active&age>=18

# 排序
GET /users?sort=name&order=asc

# 分页
GET /users?page=2&limit=20
```

### 2.3 HTTP 方法

| 方法 | 用途 | 幂等 |
|------|------|------|
| GET | 获取资源 | 是 |
| POST | 创建资源 | 否 |
| PUT | 完整更新 | 是 |
| PATCH | 部分更新 | 否 |
| DELETE | 删除资源 | 是 |

## 三、状态码

### 3.1 成功状态码

```http
200 OK                    # 成功
201 Created               # 创建成功
204 No Content            # 删除成功，无返回

# 示例
POST /users
201 Created
Location: /users/123
```

### 3.2 客户端错误

```http
400 Bad Request           # 请求参数错误
401 Unauthorized          # 未认证
403 Forbidden             # 无权限
404 Not Found             # 资源不存在
422 Unprocessable Entity  # 验证失败
429 Too Many Requests    # 请求过多
```

### 3.3 服务端错误

```http
500 Internal Server Error  # 服务器错误
502 Bad Gateway            # 网关错误
503 Service Unavailable    # 服务不可用
```

## 四、响应格式

### 4.1 成功响应

```json
{
  "data": {
    "id": "123",
    "name": "张三",
    "email": "zhangsan@example.com"
  },
  "meta": {
    "total": 100,
    "page": 1,
    "limit": 20
  }
}
```

### 4.2 列表响应

```json
{
  "data": [
    { "id": "1", "name": "张三" },
    { "id": "2", "name": "李四" }
  ],
  "meta": {
    "total": 2,
    "page": 1,
    "limit": 20
  }
}
```

### 4.3 错误响应

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "用户不存在",
    "details": [
      { "field": "id", "message": "用户ID无效" }
    ]
  }
}
```

## 五、版本控制

### 5.1 URL 版本

```http
GET /api/v1/users
GET /api/v2/users
```

### 5.2 Header 版本

```http
Accept: application/vnd.myapp.v2+json
```

## 六、安全性

### 6.1 认证

```http
# Token 认证
Authorization: Bearer <token>

# API Key
X-API-Key: <api_key>
```

### 6.2 HTTPS

```http
# 强制 HTTPS
Strict-Transport-Security: max-age=31536000
```

### 6.3 CORS

```http
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

## 七、实战建议

### 7.1 分页

```http
GET /users?page=2&limit=20
```

响应：
```json
{
  "data": [...],
  "pagination": {
    "page": 2,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

### 7.2 字段过滤

```http
GET /users?fields=id,name,email
```

### 7.3 搜索

```http
GET /users?q=张三&fields=name,email
```

## 八、总结

RESTful API 设计要点：

1. **URL 规范**：资源命名、嵌套关系
2. **HTTP 方法**：正确使用 GET/POST/PUT/DELETE
3. **状态码**：准确返回 2xx/4xx/5xx
4. **响应格式**：统一 data/meta/error 结构
5. **版本控制**：URL 或 Header
6. **安全性**：认证、HTTPS、CORS

遵循这些原则，你的 API 会更专业、更易用！

---

**推荐阅读**：
- [RESTful API 设计指南](https://restfulapi.net/)
- [HTTP 状态码](https://httpstatuses.com/)

**如果对你有帮助，欢迎点赞收藏！**
