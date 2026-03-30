# Nginx 反向代理与负载均衡实战配置指南

> 深入讲解 Nginx 反向代理、负载均衡、SSL 配置与性能优化，提供完整配置示例帮助快速部署生产环境。

## 一、Nginx 基础

### 1.1 安装

```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS
sudo yum install nginx

# 启动
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 1.2 目录结构

```
/etc/nginx/          # 配置目录
  nginx.conf         # 主配置
  sites-available/   # 可用站点
  sites-enabled/    # 启用站点
/var/log/nginx/     # 日志目录
/usr/share/nginx/   # 网页目录
```

## 二、反向代理

### 2.1 基本配置

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 2.2 传递真实 IP

```nginx
location / {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 2.3 WebSocket 支持

```nginx
location /ws/ {
    proxy_pass http://ws_backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

## 三、负载均衡

### 3.1 upstream 配置

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

### 3.2 负载均衡算法

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

### 3.3 健康检查

```nginx
upstream backend {
    server 127.0.0.1:3001 max_fails=3 fail_timeout=30s;
    server 127.0.0.1:3002 max_fails=3 fail_timeout=30s;
}
```

## 四、SSL/TLS 配置

### 4.1 HTTPS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/server.crt;
    ssl_certificate_key /etc/nginx/ssl/server.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
}
```

### 4.2 HTTP 重定向 HTTPS

```nginx
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

### 4.3 HSTS

```nginx
add_header Strict-Transport-Security "max-age=63072000" always;
```

## 五、性能优化

### 5.1 Gzip 压缩

```nginx
gzip on;
gzip_vary on;
gzip_proxied any;
gzip_comp_level 6;
gzip_types text/plain text/css text/xml application/json application/javascript application/xml;
```

### 5.2 缓存配置

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 30d;
    add_header Cache-Control "public, no-transform";
}
```

### 5.3 连接数限制

```nginx
http {
    limit_conn_zone $binary_remote_addr zone=addr:10m;
    
    server {
        limit_conn addr 100;
    }
}
```

## 六、静态文件服务

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

## 七、总结

Nginx 核心配置：

1. **反向代理**：转发请求到后端
2. **负载均衡**：分发流量到多台服务器
3. **SSL/TLS**：HTTPS 配置
4. **性能优化**：压缩、缓存、限流
5. **静态服务**：高效服务静态资源

掌握这些，生产环境部署不再难！

---

**推荐阅读**：
- [Nginx 官方文档](https://nginx.org/en/docs/)
- [Nginx 入门教程](https://www.nginx.com/resources/wiki/start/)

**如果对你有帮助，欢迎点赞收藏！**
