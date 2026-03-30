# Nginx 高级配置：负载均衡、缓存与 HTTPS 优化

> 深入讲解 Nginx 高级特性，包括负载均衡策略、静态资源缓存、SSL/TLS 配置优化，以及高可用架构设计。

## 一、负载均衡

### 1.1 upstream

```nginx
upstream backend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

server {
    location / {
        proxy_pass http://backend;
    }
}
```

### 1.2 负载均衡策略

```nginx
# 轮询（默认）
upstream backend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
}

# 权重
upstream backend {
    server 127.0.0.1:3001 weight=3;
    server 127.0.0.1:3002 weight=1;
}

# IP 哈希（会话保持）
upstream backend {
    ip_hash;
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
}

# 最少连接
upstream backend {
    least_conn;
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
}
```

### 1.3 健康检查

```nginx
upstream backend {
    server 127.0.0.1:3001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3002 max_fails=3 fail_timeout=30s;
}
```

## 二、缓存配置

### 2.1 代理缓存

```nginx
proxy_cache_path /tmp/nginx_cache levels=1:2 
    keys_zone=my_cache:10m 
    max_size=1g 
    inactive=60m;

server {
    location / {
        proxy_cache my_cache;
        proxy_cache_valid 200 10m;
        proxy_cache_key $uri;
        add_header X-Cache-Status $upstream_cache_status;
        
        proxy_pass http://backend;
    }
}
```

### 2.2 静态资源缓存

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
    expires 30d;
    add_header Cache-Control "public, no-transform";
    access_log off;
}
```

## 三、HTTPS 优化

### 3.1 SSL 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    # SSL 版本
    ssl_protocols TLSv1.2 TLSv1.3;
    
    # 加密套件
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
}
```

### 3.2 会话复用

```nginx
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 1d;
```

## 四、安全配置

### 4.1 隐藏版本号

```nginx
server_tokens off;

# 隐藏 Server
more_clear_headers Server;
```

### 4.2 限流

```nginx
http {
    limit_req_zone $binary_remote_addr zone=req_limit:10m rate=10r/s;
    
    server {
        location /api/ {
            limit_req zone=req_limit burst=20 nodelay;
        }
    }
}
```

## 五、性能优化

### 5.1 Gzip 压缩

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml application/json 
    application/javascript application/xml;
gzip_min_length 1000;
```

### 5.2 连接复用

```nginx
upstream backend {
    server 127.0.0.1:3001;
    keepalive 32;
}

location / {
    proxy_http_version 1.1;
    proxy_set_header Connection "";
    proxy_pass http://backend;
}
```

## 六、总结

Nginx 高级核心要点：

1. **负载均衡**：轮询、权重、IP 哈希
2. **缓存**：代理缓存、静态缓存
3. **HTTPS**：SSL 配置、HSTS
4. **安全**：限流、隐藏信息
5. **性能**：Gzip、连接复用

掌握这些，Nginx 不再是简单的 Web 服务器！

---

**推荐阅读**：
- [Nginx 官方文档](https://nginx.org/en/docs/)

**如果对你有帮助，欢迎点赞收藏！**
