# HTTP 协议完全指南：请求响应与状态码

> 深入讲解 HTTP 协议，包括请求方法、响应状态码、Headers、缓存机制，以及 HTTPS、TLS 和实际项目中的性能优化。

## 一、HTTP 基础

### 1.1 什么是 HTTP

超文本传输协议：

```
┌─────────────────────────────────────────────────────────────┐
│                      HTTP 请求-响应                         │
│                                                              │
│  浏览器                      服务器                         │
│    │                           │                           │
│    │──── GET /index.html ────▶│                           │
│    │                           │                           │
│    │◀─── 200 OK + HTML ───────│                           │
│    │                           │                           │
└─────────────────────────────────────────────────────────────┘

版本历史：
HTTP/1.0 - 1996
HTTP/1.1 - 1999（持久连接）
HTTP/2 - 2015（多路复用）
HTTP/3 - 2022（QUIC）
```

### 1.2 URL 结构

```
https://username:password@example.com:443/path/name?query=1#section
└─┬──┘ └───┬──┘ └────────┬────────┘ ├─┬──┘└─────┬─────┘└───┬───┘└┬┘
  │        │             │           │         │         │    │
协议     认证信息       主机名      端口      路径      查询  片段
```

## 二、请求方法

### 2.1 方法列表

| 方法 | 说明 | 幂等 |
|------|------|------|
| GET | 获取资源 | ✓ |
| POST | 创建资源 | ✗ |
| PUT | 替换资源 | ✓ |
| PATCH | 部分更新 | ✗ |
| DELETE | 删除资源 | ✓ |
| HEAD | 获取头部 | ✓ |
| OPTIONS | 获取能力 | ✓ |

### 2.2 示例

```http
GET /api/users HTTP/1.1
Host: api.example.com
Accept: application/json

---

POST /api/users HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name": "张三", "age": 25}

---

PUT /api/users/123 HTTP/1.1
Host: api.example.com
Content-Type: application/json

{"name": "李四", "age": 30}

---

DELETE /api/users/123 HTTP/1.1
Host: api.example.com
```

## 三、状态码

### 3.1 状态码分类

```
1xx - 信息响应
2xx - 成功响应
3xx - 重定向
4xx - 客户端错误
5xx - 服务器错误
```

### 3.2 常见状态码

```http
200 OK                    // 成功
201 Created               // 创建成功
204 No Content            // 无内容

301 Moved Permanently     // 永久重定向
302 Found                 // 临时重定向
304 Not Modified          // 缓存

400 Bad Request           // 请求错误
401 Unauthorized          // 未认证
403 Forbidden             // 无权限
404 Not Found             // 不存在
405 Method Not Allowed    // 方法不允许
429 Too Many Requests     // 请求过多

500 Internal Server Error // 服务器错误
502 Bad Gateway          // 网关错误
503 Service Unavailable  // 服务不可用
504 Gateway Timeout       // 网关超时
```

## 四、Headers

### 4.1 请求头

```http
Accept: application/json
Accept-Encoding: gzip, deflate
Accept-Language: zh-CN,zh;q=0.9
Authorization: Bearer token
Cache-Control: no-cache
Content-Type: application/json
Cookie: session=abc123
User-Agent: Mozilla/5.0
```

### 4.2 响应头

```http
Content-Type: application/json
Content-Length: 1234
Content-Encoding: gzip
Cache-Control: max-age=3600
Set-Cookie: session=abc123; HttpOnly; Secure
ETag: "abc123"
Last-Modified: Mon, 01 Jan 2024 00:00:00 GMT
```

## 五、缓存

### 5.1 缓存机制

```
┌─────────────────────────────────────────────────────────────┐
│                      缓存流程                                │
│                                                              │
│  浏览器 ──▶ 请求 ──▶ 有缓存? ──是──▶ 检查新鲜度 ──▶ 新鲜? │
│                │               │               │            │
│                │              否               │            │
│                ▼               ▼               ▼            │
│           服务器           返回缓存        返回新内容       │
│                                      (200 + 新内容)         │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 缓存控制

```http
# 请求
Cache-Control: no-cache          # 每次验证
Cache-Control: no-store          # 不缓存
Cache-Control: max-age=3600     # 缓存1小时

# 响应
Cache-Control: public, max-age=3600
Cache-Control: private, max-age=3600
Cache-Control: no-cache         # 每次验证
Cache-Control: no-store         # 不缓存
```

### 5.3 条件请求

```http
# 请求
If-None-Match: "abc123"
If-Modified-Since: Mon, 01 Jan 2024 00:00:00 GMT

# 响应（未修改）
HTTP/1.1 304 Not Modified
ETag: "abc123"
```

## 六、HTTPS

### 6.1 TLS/SSL

```
┌─────────────────────────────────────────────────────────────┐
│                    HTTPS 握手                               │
│                                                              │
│  浏览器 ──────── ClientHello ─────────▶ 服务器             │
│                  ◀────── ServerHello ──────                │
│                  ◀────── 证书 + 公钥 ──────                │
│  ───────── 预主密钥（加密） ─────────▶                       │
│                  ◀────── 确认 ──────                        │
│                                                              │
│  后续请求使用对称加密                                        │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 证书

```bash
# Let's Encrypt 免费证书
certbot certonly --webroot -w /var/www/html -d example.com
```

### 6.3 HTTPS 优化

```http
# 启用 HTTP/2
Alt-Svc: h2=":443"

# 启用 HTTP/3
Alt-Svc: h3=":443"

# HSTS（强制 HTTPS）
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## 七、实战案例

### 7.1 cURL

```bash
# GET 请求
curl https://api.example.com/users

# POST 请求
curl -X POST https://api.example.com/users \
  -H "Content-Type: application/json" \
  -d '{"name": "张三"}'

# 带认证
curl -H "Authorization: Bearer token" \
  https://api.example.com/profile

# 下载文件
curl -O https://example.com/file.zip

# 发送表单
curl -F "file=@/path/to/file" https://api.example.com/upload
```

### 7.2 调试工具

```bash
# 查看完整请求
curl -v https://api.example.com

# 查看响应头
curl -I https://api.example.com

# 忽略证书
curl -k https://example.com
```

## 八、总结

HTTP 协议核心要点：

1. **方法**：GET/POST/PUT/DELETE
2. **状态码**：2xx/3xx/4xx/5xx
3. **Headers**：请求/响应头
4. **缓存**：Cache-Control/ETag
5. **HTTPS**：TLS 加密
6. **HTTP/2**：多路复用

掌握这些，Web 通信 so easy！

---

**推荐阅读**：
- [MDN HTTP 文档](https://developer.mozilla.org/en-US/docs/Web/HTTP)
- [HTTP 状态码](https://httpstatuses.com/)

**如果对你有帮助，欢迎点赞收藏！**
