# HTTP 协议基础：从小白到入门

> 全面介绍 HTTP 协议的核心知识点，包括请求方法、状态码、Headers、缓存机制，以及 HTTPS 的基本原理。

## 一、HTTP 简介

### 1.1 什么是 HTTP

HTTP（HyperText Transfer Protocol）是万维网的基础协议：

```
浏览器 → HTTP 请求 → 服务器 → HTTP 响应 → 浏览器
```

### 1.2 HTTP 工作流程

1. 浏览器建立 TCP 连接
2. 浏览器发送 HTTP 请求
3. 服务器处理请求并返回响应
4. 浏览器接收响应并渲染

## 二、请求方法

### 2.1 常用方法

| 方法 | 说明 | 幂等 |
|------|------|------|
| GET | 获取资源 | 是 |
| POST | 提交数据 | 否 |
| PUT | 更新资源 | 是 |
| DELETE | 删除资源 | 是 |
| PATCH | 部分更新 | 否 |

### 2.2 请求示例

```http
GET /api/users HTTP/1.1
Host: api.example.com
Accept: application/json
Authorization: Bearer token

POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name": "张三", "age": 25}
```

## 三、状态码

### 3.1 1xx - 信息

```http
100 Continue      # 继续请求
101 Switching    # 协议升级
```

### 3.2 2xx - 成功

```http
200 OK           # 成功
201 Created      # 已创建
204 No Content   # 成功，无返回
```

### 3.3 3xx - 重定向

```http
301 Moved        # 永久重定向
302 Found        # 临时重定向
304 Not Modified # 缓存可用
```

### 3.4 4xx - 客户端错误

```http
400 Bad Request      # 请求错误
401 Unauthorized    # 未认证
403 Forbidden       # 无权限
404 Not Found       # 不存在
422 Unprocessable   # 验证失败
429 Too Many        # 请求过多
```

### 3.5 5xx - 服务端错误

```http
500 Internal Error  # 服务器错误
502 Bad Gateway     # 网关错误
503 Unavailable     # 服务不可用
504 Gateway Timeout # 网关超时
```

## 四、Headers

### 4.1 请求 Headers

```http
Accept: application/json
Accept-Language: zh-CN,zh;q=0.9
Authorization: Bearer token
Content-Type: application/json
User-Agent: Mozilla/5.0
Cookie: session=xxx
```

### 4.2 响应 Headers

```http
Content-Type: application/json
Content-Length: 1234
Cache-Control: max-age=3600
Set-Cookie: session=xxx; HttpOnly
ETag: "abc123"
```

## 五、缓存机制

### 5.1 Cache-Control

```http
Cache-Control: max-age=3600          # 缓存1小时
Cache-Control: no-cache             # 需验证
Cache-Control: no-store             # 不缓存
Cache-Control: public               # 可被缓存
Cache-Control: private              # 仅浏览器缓存
```

### 5.2 ETag

```http
# 请求
If-None-Match: "abc123"

# 响应
ETag: "abc123"
```

## 六、Cookies

### 6.1 设置 Cookie

```http
Set-Cookie: session=abc123; Path=/; HttpOnly; Secure; Max-Age=3600
```

### 6.2 Cookie 属性

| 属性 | 说明 |
|------|------|
| Path | 生效路径 |
| Domain | 生效域名 |
| HttpOnly | 无法被 JS 读取 |
| Secure | 仅 HTTPS 发送 |
| SameSite | CSRF 防护 |

## 七、HTTPS 简介

### 7.1 什么是 HTTPS

HTTPS = HTTP + TLS/SSL，加密传输：

```http
https://api.example.com
```

### 7.2 握手过程

1. 客户端发送 ClientHello
2. 服务器发送证书
3. 协商加密算法
4. 建立安全连接

## 八、总结

HTTP 核心要点：

1. **请求方法**：GET/POST/PUT/DELETE
2. **状态码**：2xx/3xx/4xx/5xx
3. **Headers**：请求和响应头
4. **缓存**：Cache-Control、ETag
5. **Cookies**：会话管理
6. **HTTPS**：加密传输

掌握这些，HTTP 不再神秘！

---

**推荐阅读**：
- [MDN HTTP 文档](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- [HTTP 状态码](https://httpstatuses.com/)

**如果对你有帮助，欢迎点赞收藏！**
