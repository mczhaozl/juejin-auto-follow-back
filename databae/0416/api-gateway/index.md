# API Gateway 完全指南：统一网关实践

> 深入讲解 API Gateway，包括路由转发、认证授权、限流熔断、日志监控，以及 Kong、Zuul 的使用和微服务网关架构设计。

## 一、API Gateway 基础

### 1.1 什么是 API Gateway

统一入口：

```
┌─────────────────────────────────────────────────────────┐
│                     API Gateway                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ • 路由转发                                        │   │
│  │ • 认证授权                                        │   │
│  │ • 限流熔断                                        │   │
│  │ • 日志监控                                        │   │
│  │ • 协议转换                                        │   │
│  └─────────────────────────────────────────────────┘   │
└──────┬──────────────────────────────────────────────────┘
       │
       ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  用户服务    │  │  订单服务    │  │  商品服务    │
└──────────────┘  └──────────────┘  └──────────────┘
```

### 1.2 核心功能

| 功能 | 说明 |
|------|------|
| 路由 | 请求转发到后端服务 |
| 认证 | JWT、OAuth2 |
| 限流 | 防止流量洪峰 |
| 熔断 | 保护后端服务 |
| 监控 | 日志、指标 |

## 二、Kong

### 2.1 安装

```bash
# Docker 安装
docker run -d --name kong \
  -e "KONG_DATABASE=off" \
  -e "KONG_DECLARATIVE_CONFIG=/usr/local/kong/kong.yml" \
  -p 8000:8000 \
  kong:latest
```

### 2.2 路由配置

```bash
# 添加服务
curl -X POST http://localhost:8001/services/ \
  --data name=user-service \
  --data url=http://user-service:8080

# 添加路由
curl -X POST http://localhost:8001/services/user-service/routes/ \
  --data paths[]=/users \
  --data strip_path=true

# 测试
curl http://localhost:8000/users
```

### 2.3 插件配置

```bash
# 限流
curl -X POST http://localhost:8001/services/user-service/plugins/ \
  --data name=rate-limiting \
  --data config.minute=100

# JWT 认证
curl -X POST http://localhost:8001/services/user-service/plugins/ \
  --data name=jwt

# 日志
curl -X POST http://localhost:8001/services/user-service/plugins/ \
  --data name=logging \
  --data config.http_endpoint=http://logging-service:8080
```

## 三、Zuul

### 3.1 Spring Cloud Zuul

```yaml
# application.yml
zuul:
  routes:
    user-service:
      path: /users/**
      url: http://user-service:8080
    order-service:
      path: /orders/**
      serviceId: order-service
  prefix: /api
  strip-prefix: true
```

### 3.2 过滤器

```java
@Component
public class AuthFilter extends ZuulFilter {
    
    @Override
    public String filterType() {
        return "pre";
    }
    
    @Override
    public int filterOrder() {
        return 0;
    }
    
    @Override
    public boolean shouldFilter() {
        return true;
    }
    
    @Override
    public Object run() {
        RequestContext ctx = RequestContext.getCurrentContext();
        String token = ctx.getRequest().getHeader("Authorization");
        
        if (token == null) {
            ctx.setSendZuulResponse(false);
            ctx.setResponseStatusCode(401);
        }
        
        return null;
    }
}
```

## 四、认证授权

### 4.1 JWT 验证

```javascript
// 网关验证 JWT
const jwt = require('jsonwebtoken');

app.use(async (ctx, next) => {
  const token = ctx.headers.authorization?.replace('Bearer ', '');
  
  if (!token) {
    ctx.status = 401;
    ctx.body = { error: 'No token provided' };
    return;
  }
  
  try {
    const decoded = jwt.verify(token, 'secret');
    ctx.user = decoded;
    await next();
  } catch (err) {
    ctx.status = 401;
    ctx.body = { error: 'Invalid token' };
  }
});
```

### 4.2 OAuth2

```yaml
# OAuth2 资源配置
security:
  oauth2:
    resourceserver:
      jwt:
        issuer-uri: https://auth.example.com
```

## 五、限流与熔断

### 5.1 限流策略

```yaml
# Kong 限流
plugins:
  - name: rate-limiting
    config:
      minute: 100
      hour: 1000
      policy: local
      fault_tolerant: true

# 分布式限流
# Redis 实现
plugins:
  - name: rate-limiting
    config:
      minute: 100
      policy: redis
      redis_host: redis-host
      redis_port: 6379
```

### 5.2 熔断配置

```yaml
# Spring Cloud Hystrix
hystrix:
  command:
    user-service:
      execution:
        isolation:
          thread:
            timeoutInMilliseconds: 5000
      circuitBreaker:
        requestVolumeThreshold: 20
        sleepWindowInMilliseconds: 10000
        errorThresholdPercentage: 50
```

## 六、日志与监控

### 6.1 日志收集

```javascript
// Kong 日志
curl -X POST http://localhost:8001/plugins \
  --data name=http-log \
  --data config.http_endpoint=http://logstash:8080 \
  --data config.method=POST
```

### 6.2 监控指标

```yaml
# Prometheus + Grafana
- name: prometheus
  config:
    per_consumer: false
```

### 6.3 链路追踪

```java
// Spring Cloud Sleuth
spring:
  sleuth:
    sampler:
      probability: 1.0
    zipkin:
      base-url: http://zipkin:9411
```

## 七、实战配置

### 7.1 完整 Kong 配置

```yaml
_format_version: "2.1"

services:
  - name: user-service
    url: http://user-service:8080
    routes:
      - name: user-route
        paths:
          - /api/users
        strip_path: true
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 100
      - name: correlation-id
      - name: http-log
        config:
          http_endpoint: http://logging:8080

  - name: order-service
    url: http://order-service:8080
    routes:
      - name: order-route
        paths:
          - /api/orders
        strip_path: true
    plugins:
      - name: jwt
      - name: rate-limiting
        config:
          minute: 50
      - name: http-log
        config:
          http_endpoint: http://logging:8080
```

## 八、总结

API Gateway 核心要点：

1. **路由**：请求转发
2. **认证**：JWT/OAuth2
3. **限流**：防止洪峰
4. **熔断**：保护服务
5. **监控**：日志链路
6. **Kong**：Nginx + Lua
7. **Zuul**：Spring Cloud

掌握这些，统一网关 so easy！

---

**推荐阅读**：
- [Kong 官方文档](https://docs.konghq.com/)
- [Spring Cloud Zuul](https://spring.io/projects/spring-cloud-netflix)

**如果对你有帮助，欢迎点赞收藏！**
