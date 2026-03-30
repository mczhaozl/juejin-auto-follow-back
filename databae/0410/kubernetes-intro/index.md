# Kubernetes 入门指南：从零搭建容器编排平台

> 手把手教你掌握 Kubernetes 核心概念，包括 Pod、Deployment、Service、ConfigMap 等，以及实际部署案例。

## 一、Kubernetes 简介

### 1.1 什么是 K8s

Kubernetes（K8s）是容器编排平台：

- 自动部署、扩展和管理容器化应用
- 支持多容器运行
- 自我修复、负载均衡

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| Pod | 最小部署单元 |
| Deployment | 管理 Pod |
| Service | 网络服务 |
| ConfigMap | 配置管理 |

## 二、Pod

### 2.1 基本定义

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
  - name: nginx
    image: nginx:1.21
    ports:
    - containerPort: 80
```

### 2.2 运行

```bash
kubectl apply -f pod.yaml
kubectl get pods
kubectl describe pod my-app
kubectl delete pod my-app
```

## 三、Deployment

### 3.1 基本定义

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
```

### 3.2 扩缩容

```bash
# 扩缩容
kubectl scale deployment my-app --replicas=5

# 自动扩缩容
kubectl autoscale deployment my-app --min=2 --max=10
```

### 3.3 更新回滚

```bash
# 更新镜像
kubectl set image deployment/my-app nginx=nginx:1.22

# 查看状态
kubectl rollout status deployment/my-app

# 回滚
kubectl rollout undo deployment/my-app
```

## 四、Service

### 4.1 ClusterIP

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

### 4.2 NodePort

```yaml
spec:
  type: NodePort
  ports:
  - port: 80
    targetPort: 80
    nodePort: 30080
```

### 4.3 LoadBalancer

```yaml
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 80
```

## 五、ConfigMap 和 Secret

### 5.1 ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  DATABASE_URL: postgres://db:5432
  CACHE_ENABLED: "true"
```

使用：

```yaml
env:
- name: DATABASE_URL
  valueFrom:
    configMapKeyRef:
      name: my-config
      key: DATABASE_URL
```

### 5.2 Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
data:
  username: YWRtaW4=
  password: cGFzc3dvcmQ=
```

## 六、实战案例

### 6.1 完整部署

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web-app
  template:
    metadata:
      labels:
        app: web-app
    spec:
      containers:
      - name: web
        image: myapp:latest
        ports:
        - containerPort: 8080
        env:
        - name: NODE_ENV
          value: "production"
        resources:
          limits:
            memory: "256Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: web-app
spec:
  selector:
    app: web-app
  ports:
  - port: 80
    targetPort: 8080
  type: LoadBalancer
```

### 6.2 健康检查

```yaml
spec:
  containers:
  - name: web
    image: myapp:latest
    livenessProbe:
      httpGet:
        path: /health
        port: 8080
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /ready
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
```

## 七、常用命令

```bash
# 部署
kubectl apply -f deployment.yaml

# 查看
kubectl get pods,svc,deployments

# 日志
kubectl logs -f pod-name
kubectl logs deployment/my-app

# 进入容器
kubectl exec -it pod-name -- /bin/sh

# 删除
kubectl delete -f deployment.yaml
```

## 八、总结

Kubernetes 核心要点：

1. **Pod**：最小部署单元
2. **Deployment**：管理 Pod 副本
3. **Service**：服务发现和负载均衡
4. **ConfigMap/Secret**：配置管理
5. **健康检查**：存活探针、就绪探针
6. **扩缩容**：手动和自动

掌握这些，K8s 部署不再难！

---

**推荐阅读**：
- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Kubectl  cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)

**如果对你有帮助，欢迎点赞收藏！**
