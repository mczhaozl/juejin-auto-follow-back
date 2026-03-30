# 负载均衡完全指南：算法与高可用方案

> 深入讲解负载均衡，包括轮询、哈希、加权等算法，Nginx/HAProxy 配置，以及实际项目中的高可用架构和故障转移策略。

## 一、负载均衡基础

### 1.1 什么是负载均衡

分发流量到多台服务器：

```
┌─────────────────────────────────────────────────────────────┐
│                    负载均衡                                  │
│                                                              │
│      ┌──────────────┐                                      │
│      │  负载均衡器   │                                      │
│      └──────┬───────┘                                      │
│             │                                               │
│    ┌────────┼────────┬────────┐                              │
│    ▼        ▼        ▼        ▼                            │
│ ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐                        │
│ │ S1  │  │ S2  │  │ S3  │  │ S4  │                        │
│ │请求1 │  │请求2 │  │请求3 │  │请求4 │                        │
│ └─────┘  └─────┘  └─────┘  └─────┘                        │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 负载均衡层级

| 层级 | 设备 | 协议 |
|------|------|------|
| L4 | F5/Nginx | TCP/UDP |
| L7 | HAProxy | HTTP |

## 二、负载均衡算法

### 2.1 轮询

```nginx
# Nginx
upstream backend {
    server 192.168.1.1:8080;
    server 192.168.1.2:8080;
    server 192.168.1.3:8080;
}
```

### 2.2 加权轮询

```nginx
upstream backend {
    server 192.168.1.1:8080 weight=3;
    server 192.168.1.2:8080 weight=2;
    server 192.168.1.3:8080 weight=1;
}
```

### 2.3 IP 哈希

```nginx
upstream backend {
    ip_hash;
    server 192.168.1.1:8080;
    server 192.168.1.2:8080;
}
```

### 2.4 最少连接

```nginx
upstream backend {
    least_conn;
    server 192.168.1.1:8080;
    server 192.168.1.2:8080;
}
```

## 三、Nginx 配置

### 3.1 基本配置

```nginx
http {
    upstream myapp {
        server 192.168.1.1:8080;
        server 192.168.1.2:8080;
        server 192.168.1.3:8080;
        
        keepalive 32;
    }
    
    server {
        listen 80;
        
        location / {
            proxy_pass http://myapp;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
    }
}
```

### 3.2 健康检查

```nginx
upstream backend {
    server 192.168.1.1:8080 max_fails=3 fail_timeout=30s;
    server 192.168.1.2:8080 max_fails=3 fail_timeout=30s;
}
```

### 3.3 SSL 终止

```nginx
server {
    listen 443 ssl;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    location / {
        proxy_pass http://backend;
    }
}
```

## 四、HAProxy

### 4.1 配置

```haproxy
global
    log /dev/log local0
    maxconn 4000
    user haproxy
    group haproxy

defaults
    mode http
    log global
    option httplog
    option dontlognull
    timeout connect 5000ms
    timeout client 50000ms
    timeout server 50000ms

frontend http_front
    bind *:80
    default_backend app_back

backend app_back
    balance roundrobin
    option httpchk GET /health
    server app1 192.168.1.1:8080 check inter 2000 rise 2 fall 3
    server app2 192.168.1.2:8080 check inter 2000 rise 2 fall 3
```

## 五、高可用

### 5.1 Keepalived

```
┌─────────────────────────────────────────────────────────────┐
│                    Keepalived                                │
│                                                              │
│   ┌──────────┐       ┌──────────┐                          │
│   │ Master   │◀─────▶│ Backup   │                          │
│   │ (主)    │  VRRP  │ (备)     │                          │
│   └────┬─────┘       └──────────┘                          │
│        │                                                     │
│        ▼                                                     │
│   虚拟 IP (VIP)                                             │
│        │                                                     │
│        ▼                                                     │
│   ┌──────────┐                                              │
│   │  用户请求 │                                              │
│   └──────────┘                                              │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 配置

```bash
# /etc/keepalived/keepalived.conf
vrrp_instance VI_1 {
    state MASTER
    interface eth0
    virtual_router_id 51
    priority 100
    virtual_ipaddress {
        192.168.1.100
    }
}
```

## 六、DNS 负载均衡

### 6.1 轮询 DNS

```bash
# DNS 配置
example.com.  IN A 192.168.1.1
example.com.  IN A 192.168.1.2
example.com.  IN A 192.168.1.3
```

### 6.2 地理 DNS

```json
{
  "region": {
    "cn-north": ["1.1.1.1", "1.1.1.2"],
    "us-west": ["2.2.2.1", "2.2.2.2"]
  }
}
```

## 七、实战案例

### 7.1 微服务负载均衡

```yaml
# Kubernetes Service
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

```yaml
# Kubernetes Ingress
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
spec:
  rules:
    - host: myapp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: myapp
                port:
                  number: 80
```

## 八、总结

负载均衡核心要点：

1. **算法**：轮询/加权/哈希
2. **Nginx**：L7 负载均衡
3. **HAProxy**：高性能
4. **Keepalived**：高可用
5. **健康检查**：故障转移
6. **DNS**：地理分布

掌握这些，高可用架构 so easy！

---

**推荐阅读**：
- [Nginx 负载均衡](https://nginx.org/en/docs/http/ngx_http_upstream_module.html)
- [HAProxy 文档](http://www.haproxy.org/)

**如果对你有帮助，欢迎点赞收藏！**
