# Kubernetes 完全指南：容器编排实战

> 深入讲解 Kubernetes，包括 Pod、Deployment、Service、ConfigMap、Secret、Ingress，以及 Helm、Dashboard 和实际项目中的集群管理。

## 一、Kubernetes 基础

### 1.1 什么是 Kubernetes

容器编排平台：

```
┌─────────────────────────────────────────────────────────────────┐
│                      Kubernetes Cluster                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                    Control Plane                         │    │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐ │    │
│  │  │  API    │  │Scheduler│  │Controller│  │   Etcd  │ │    │
│  │  │ Server  │  │         │  │ Manager  │  │         │ │    │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘ │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌───────────────────────────┼───────────────────────────┐      │
│  │                    Worker Nodes                       │      │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐             │      │
│  │  │ Node 1  │  │ Node 2  │  │ Node 3  │             │      │
│  │  │ ┌─────┐ │  │ ┌─────┐ │  │ ┌─────┐ │             │      │
│  │  │ │ Pod │ │  │ │ Pod │ │  │ │ Pod │ │             │      │
│  │  │ └─────┘ │  │ └─────┘ │  │ └─────┘ │             │      │
│  │  │ ┌─────┐ │  │ ┌─────┐ │  │         │             │      │
│  │  │ │ Pod │ │  │ │ Pod │ │  │         │             │      │
│  │  │ └─────┘ │  │ └─────┘ │  │         │             │      │
│  │  └─────────┘  └─────────┘  └─────────┘             │      │
│  └───────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| Pod | K8s 最小调度单元 |
| Deployment | Pod 管理 |
| Service | 服务发现与负载均衡 |
| Ingress | HTTP 路由 |
| ConfigMap | 配置 |
| Secret | 敏感信息 |

## 二、Pod

### 2.1 Pod 定义

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp
  labels:
    app: myapp
spec:
  containers:
    - name: myapp
      image: myapp:latest
      ports:
        - containerPort: 8080
      resources:
        requests:
          memory: "64Mi"
          cpu: "250m"
        limits:
          memory: "128Mi"
          cpu: "500m"
```

### 2.2 多容器 Pod

```yaml
spec:
  containers:
    - name: web
      image: nginx
      ports:
        - containerPort: 80
    - name: sidecar
      image: sidecar:latest
```

## 三、Deployment

### 3.1 基本 Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
        - name: myapp
          image: myapp:latest
          ports:
            - containerPort: 8080
```

### 3.2 滚动更新

```yaml
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### 3.3 操作命令

```bash
# 查看
kubectl get pods
kubectl get deployments

# 扩缩容
kubectl scale deployment myapp --replicas=5

# 更新
kubectl set image deployment/myapp myapp=myapp:v2

# 回滚
kubectl rollout undo deployment/myapp
kubectl rollout status deployment/myapp
```

## 四、Service

### 4.1 Service 类型

```yaml
# ClusterIP（默认）
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

# NodePort
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  type: NodePort
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
      nodePort: 30080

# LoadBalancer
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  type: LoadBalancer
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
```

### 4.2 Headless Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp
spec:
  clusterIP: None
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8080
```

## 五、ConfigMap 与 Secret

### 5.1 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: myapp-config
data:
  database_url: "postgres://db:5432/myapp"
  config.yaml: |
    log_level: info
    timeout: 30
```

### 5.2 Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: myapp-secret
type: Opaque
stringData:
  username: admin
  password: secret123
```

### 5.3 使用

```yaml
env:
  - name: DATABASE_URL
    valueFrom:
      configMapKeyRef:
        name: myapp-config
        key: database_url

env:
  - name: PASSWORD
    valueFrom:
      secretKeyRef:
        name: myapp-secret
        key: password
```

## 六、Ingress

### 6.1 Ingress 定义

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: myapp
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
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

### 6.2 TLS

```yaml
spec:
  tls:
    - hosts:
        - myapp.example.com
      secretName: myapp-tls
```

## 七、Helm

### 7.1 Helm 基础

```bash
# 安装
brew install helm

# 添加仓库
helm repo add stable https://charts.helm.sh/stable

# 搜索
helm search repo nginx

# 安装
helm install my-release stable/nginx-ingress
```

### 7.2 Chart

```yaml
# Chart.yaml
apiVersion: v2
name: myapp
description: My Application
version: 1.0.0

# values.yaml
replicas: 3
image:
  repository: myapp
  tag: latest

# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicas }}
  template:
    spec:
      containers:
        - name: myapp
          image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
```

## 八、总结

Kubernetes 核心要点：

1. **Pod**：最小调度单元
2. **Deployment**：应用管理
3. **Service**：服务发现
4. **ConfigMap**：配置
5. **Secret**：敏感信息
6. **Ingress**：HTTP 路由
7. **Helm**：包管理

掌握这些，容器编排 so easy！

---

**推荐阅读**：
- [Kubernetes 官方文档](https://kubernetes.io/docs/)

**如果对你有帮助，欢迎点赞收藏！**
