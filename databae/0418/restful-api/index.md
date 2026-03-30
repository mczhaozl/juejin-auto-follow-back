# RESTful API 完全指南：设计与最佳实践

> 深入讲解 RESTful API 设计，包括 REST 约束、资源命名、状态码、版本控制、认证授权，以及实际项目中的 API 网关和性能优化。

## 一、REST 基础

### 1.1 什么是 REST

表述性状态转移：

```
┌─────────────────────────────────────────────────────────────┐
│                      REST 原则                               │
│                                                              │
│  1. 客户端-服务器                                            │
│  2. 无状态                                                   │
│  3. 可缓存                                                   │
│  4. 分层系统                                                 │
│  5. 统一接口                                                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 资源导向

```
资源: /users
    │
    ├── GET    /users        # 获取用户列表
    ├── POST   /users        # 创建用户
    │
    └── /users/:id
        ├── GET    /users/1    # 获取用户
        ├── PUT    /users/1    # 更新用户
        ├── PATCH  /users/1    # 部分更新
        └── DELETE /users/1    # 删除用户
```

## 二、URL 设计

### 2.1 命名规范

```http
# 推荐
GET    /api/v1/users
GET    /api/v1/users/123
GET    /api/v1/users/123/posts
POST   /api/v1/users/123/orders

# 不推荐
GET    /getUsers
POST   /createUser
GET    /user/123
```

### 2.2 过滤与分页

```http
# 分页
GET /users?page=1&limit=20

# 排序
GET /users?sort=name&order=asc

# 过滤
GET /users?status=active&age_gt=18

# 搜索
GET /users?q=张三
```

## 三、状态码

### 3.1 响应状态码

```http
# 2xx 成功
200 OK                    # 请求成功
201 Created               # 资源创建成功
204 No Content            # 无返回内容

# 3xx 重定向
301 Moved Permanently     # 永久重定向
302 Found                 # 临时重定向
304 Not Modified          # 缓存

# 4xx 客户端错误
400 Bad Request           # 请求错误
401 Unauthorized         # 未认证
403 Forbidden            # 无权限
404 Not Found            # 不存在
422 Unprocessable Entity # 验证错误
429 Too Many Requests    # 请求过多

# 5xx 服务器错误
500 Internal Server Error
502 Bad Gateway
503 Service Unavailable
504 Gateway Timeout
```

### 3.2 错误响应

```json
{
  "error": {
    "code": "USER_NOT_FOUND",
    "message": "用户不存在",
    "details": [
      { "field": "userId", "message": "无效的用户ID" }
    ]
  }
}
```

## 四、版本控制

### 4.1 URL 版本

```http
# 路径版本（推荐）
GET /api/v1/users
GET /api/v2/users

# Header 版本
GET /users
Accept: application/vnd.myapp.v2+json
```

### 4.2 兼容性

```json
// v1
{
  "id": 1,
  "name": "张三"
}

// v2
{
  "id": 1,
  "firstName": "张",
  "lastName": "三"
}
```

## 五、认证授权

### 5.1 JWT

```javascript
// 生成 Token
const jwt = require('jsonwebtoken')
const token = jwt.sign(
  { userId: user.id },
  process.env.JWT_SECRET,
  { expiresIn: '7d' }
)

// 验证 Token
const decoded = jwt.verify(token, process.env.JWT_SECRET)
```

### 5.2 请求头

```http
# 认证请求
GET /api/v1/users
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

# 无权限响应
HTTP/1.1 403 Forbidden
{
  "error": {
    "code": "FORBIDDEN",
    "message": "无权访问此资源"
  }
}
```

## 六、实战案例

### 6.1 Express 实现

```javascript
const express = require('express')
const app = express()

app.use(express.json())

// 路由
app.get('/api/v1/users', async (req, res) => {
  const { page = 1, limit = 20 } = req.query
  const users = await User.find()
    .skip((page - 1) * limit)
    .limit(Number(limit))
  
  res.json({
    data: users,
    pagination: {
      page: Number(page),
      limit: Number(limit),
      total: await User.countDocuments()
    }
  })
})

app.get('/api/v1/users/:id', async (req, res) => {
  try {
    const user = await User.findById(req.params.id)
    if (!user) {
      return res.status(404).json({
        error: { code: 'NOT_FOUND', message: '用户不存在' }
      })
    }
    res.json(user)
  } catch (error) {
    res.status(500).json({
      error: { code: 'INTERNAL_ERROR', message: '服务器错误' }
    })
  }
})

app.post('/api/v1/users', async (req, res) => {
  const { name, email } = req.body
  
  // 验证
  if (!name) {
    return res.status(400).json({
      error: { code: 'VALIDATION_ERROR', message: '姓名必填' }
    })
  }
  
  const user = await User.create({ name, email })
  res.status(201).json(user)
})
```

### 6.2 中间件

```javascript
// 认证中间件
const auth = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '')
    if (!token) {
      return res.status(401).json({
        error: { code: 'UNAUTHORIZED', message: '未登录' }
      })
    }
    
    const decoded = jwt.verify(token, process.env.JWT_SECRET)
    req.user = decoded
    next()
  } catch (error) {
    res.status(401).json({
      error: { code: 'INVALID_TOKEN', message: 'Token 无效' }
    })
  }
}

// 限流中间件
const rateLimit = require('express-rate-limit')
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100
})

app.use('/api', limiter)
app.use('/api/v1/users', auth)
```

## 七、总结

RESTful API 核心要点：

1. **资源**：URL 即资源
2. **方法**：GET/POST/PUT/DELETE
3. **状态码**：正确使用
4. **版本**：URL 路径
5. **认证**：JWT
6. **错误**：统一格式
7. **限流**：保护接口

掌握这些，API 设计 so easy！

---

**推荐阅读**：
- [REST API 设计指南](https://restfulapi.net/)

**如果对你有帮助，欢迎点赞收藏！**
