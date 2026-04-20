# Kubernetes 服务与 Ingress 完全指南：从 ClusterIP 到流量管理

## 一、概述

Kubernetes Service 与 Ingress 是管理集群内外流量的核心资源，提供服务发现、负载均衡、路由等能力。

### 1.1 为什么需要 Service

Pod IP 是动态变化的，直接访问 Pod 不可靠：
- Pod 重启或调度会改变 IP
- 多个副本需要负载均衡
- 需要稳定的访问方式

### 1.2 核心概念

| 资源类型 | 用途 | 层级 |
|---------|------|------|
| ClusterIP | 集群内访问 | 四层 |
| NodePort | 节点端口暴露 | 四层 |
| LoadBalancer | 云厂商负载均衡 | 四层 |
| Ingress | 七层路由规则 | 七层 |

---

## 二、Service 详解

### 2.1 ClusterIP（默认）

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  type: ClusterIP
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
```

### 2.2 NodePort

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
      nodePort: 30080  # 可选，默认 30000-32767
```

### 2.3 LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-loadbalancer
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 3000
```

### 2.4 Headless Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-headless
spec:
  clusterIP: None
  selector:
    app: my-app
  ports:
    - port: 80
```

---

## 三、Ingress 详解

### 3.1 安装 Ingress Controller

```bash
# Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/cloud/deploy.yaml

# 或使用 Helm
helm upgrade --install ingress-nginx ingress-nginx \
  --repo https://kubernetes.github.io/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

### 3.2 基础 Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
spec:
  ingressClassName: nginx
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-service
                port:
                  number: 80
```

### 3.3 多个路径路由

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: multi-path-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /$1
spec:
  ingressClassName: nginx
  rules:
    - host: my-domain.com
      http:
        paths:
          - path: /app1(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: app1-service
                port:
                  number: 80
          - path: /app2(/|$)(.*)
            pathType: Prefix
            backend:
              service:
                name: app2-service
                port:
                  number: 80
```

---

## 四、Ingress 高级配置

### 4.1 TLS/HTTPS

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: tls-secret
type: kubernetes.io/tls
data:
  tls.crt: base64-encoded-cert
  tls.key: base64-encoded-key
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: tls-ingress
spec:
  ingressClassName: nginx
  tls:
    - hosts:
        - my-app.example.com
      secretName: tls-secret
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-service
                port:
                  number: 80
```

### 4.2 常用注解

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: annotated-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/affinity: "cookie"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
    nginx.ingress.kubernetes.io/rate-limit: |
      $binary_remote_addr: 10r/s
spec:
  ingressClassName: nginx
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            backend:
              service:
                name: my-app-service
                port:
                  number: 80
```

---

## 五、服务发现

### 5.1 DNS 解析

```yaml
# Pod 内可通过服务名访问
nslookup my-app-service.default.svc.cluster.local
```

### 5.2 环境变量

```bash
# 每个 Pod 会自动注入服务相关的环境变量
MY_APP_SERVICE_HOST=10.96.0.1
MY_APP_SERVICE_PORT=80
```

---

## 六、实战场景

### 6.1 蓝绿部署

```yaml
# v1 服务
apiVersion: v1
kind: Service
metadata:
  name: my-app-v1
spec:
  selector:
    app: my-app
    version: v1
  ports:
    - port: 80
---
# v2 服务
apiVersion: v1
kind: Service
metadata:
  name: my-app-v2
spec:
  selector:
    app: my-app
    version: v2
  ports:
    - port: 80
---
# 主服务，切换 selector 即可
apiVersion: v1
kind: Service
metadata:
  name: my-app-main
spec:
  selector:
    app: my-app
    version: v1  # 切换为 v2 即可切换流量
  ports:
    - port: 80
```

### 6.2 金丝雀发布

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: canary-ingress
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "20"
spec:
  ingressClassName: nginx
  rules:
    - host: my-app.example.com
      http:
        paths:
          - path: /
            backend:
              service:
                name: my-app-v2
                port:
                  number: 80
```

---

## 七、最佳实践

1. **使用 ClusterIP 为默认服务类型**
2. **合理使用 NodePort，注意端口冲突**
3. **优先使用 Ingress 管理七层流量**
4. **启用 TLS 保护**
5. **使用注解优化 Ingress 行为**

---

## 八、总结

Service 与 Ingress 是 Kubernetes 流量管理的核心组件，掌握它们是运维与开发必备技能。
