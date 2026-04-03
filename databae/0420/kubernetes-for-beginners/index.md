# Kubernetes 入门完全指南：从概念到实践

Kubernetes（K8s）是一个开源的容器编排平台，用于自动化部署、扩展和管理容器化应用。本文将带你从零开始学习 Kubernetes。

## 一、Kubernetes 简介

### 1. 什么是 Kubernetes

Kubernetes 是 Google 开源的容器编排系统，用于管理云平台中多个主机上的容器化应用。

### 2. 为什么使用 Kubernetes

- **自动化部署和扩展**
- **服务发现和负载均衡**
- **自我修复**
- **存储编排**
- **自动回滚和发布**
- **密钥和配置管理**

### 3. Kubernetes vs Docker Swarm

| 特性 | Kubernetes | Docker Swarm |
|------|------------|--------------|
| 复杂度 | 高 | 低 |
| 功能 | 丰富 | 基础 |
| 生态 | 强大 | 较小 |
| 学习曲线 | 陡峭 | 平缓 |

## 二、Kubernetes 核心概念

### 1. Pod

Pod 是 Kubernetes 中最小的可部署单元。

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: my-app
spec:
  containers:
  - name: web
    image: nginx:alpine
    ports:
    - containerPort: 80
```

### 2. Deployment

Deployment 用于管理 Pod 的部署和更新。

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-deployment
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
      - name: web
        image: nginx:alpine
        ports:
        - containerPort: 80
```

### 3. Service

Service 用于定义访问 Pod 的策略。

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-service
spec:
  selector:
    app: my-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: LoadBalancer
```

### 4. Namespace

Namespace 用于资源隔离。

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
```

### 5. ConfigMap

ConfigMap 用于存储配置数据。

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  database_url: postgres://localhost:5432/mydb
  log_level: info
```

### 6. Secret

Secret 用于存储敏感数据。

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-secret
type: Opaque
stringData:
  username: admin
  password: secret
```

## 三、安装 Kubernetes

### 1. 本地安装 - Minikube

```bash
# 安装 Minikube
# 下载地址：https://minikube.sigs.k8s.io/docs/start/

# 启动 Minikube
minikube start

# 查看状态
minikube status

# 访问 dashboard
minikube dashboard
```

### 2. 本地安装 - Kind

```bash
# 安装 Kind
# 下载地址：https://kind.sigs.k8s.io/

# 创建集群
kind create cluster

# 查看集群
kubectl cluster-info --context kind-kind
```

### 3. 安装 kubectl

```bash
# 下载 kubectl
# https://kubernetes.io/docs/tasks/tools/

# 验证安装
kubectl version --client
```

## 四、常用 kubectl 命令

### 1. 集群管理

```bash
# 查看集群信息
kubectl cluster-info

# 查看节点
kubectl get nodes

# 查看命名空间
kubectl get namespaces

# 创建命名空间
kubectl create namespace my-namespace

# 切换命名空间
kubectl config set-context --current --namespace=my-namespace
```

### 2. Pod 管理

```bash
# 查看 Pod
kubectl get pods
kubectl get pods -n my-namespace
kubectl get pods -o wide

# 查看 Pod 详情
kubectl describe pod my-pod

# 查看 Pod 日志
kubectl logs my-pod
kubectl logs -f my-pod
kubectl logs my-pod -c container-name

# 进入 Pod
kubectl exec -it my-pod -- /bin/bash
kubectl exec -it my-pod -c container-name -- /bin/sh

# 删除 Pod
kubectl delete pod my-pod
```

### 3. Deployment 管理

```bash
# 创建 Deployment
kubectl apply -f deployment.yaml

# 查看 Deployment
kubectl get deployments
kubectl get deployments -o wide

# 查看 Deployment 详情
kubectl describe deployment my-deployment

# 扩展 Deployment
kubectl scale deployment my-deployment --replicas=5

# 更新 Deployment
kubectl set image deployment/my-deployment web=nginx:1.25.0

# 回滚 Deployment
kubectl rollout undo deployment/my-deployment

# 查看回滚历史
kubectl rollout history deployment/my-deployment

# 删除 Deployment
kubectl delete deployment my-deployment
```

### 4. Service 管理

```bash
# 创建 Service
kubectl apply -f service.yaml

# 查看 Service
kubectl get services
kubectl get svc

# 查看 Service 详情
kubectl describe service my-service

# 删除 Service
kubectl delete service my-service
```

### 5. 其他常用命令

```bash
# 查看所有资源
kubectl get all

# 查看资源详情
kubectl describe <resource> <name>

# 查看资源 YAML
kubectl get <resource> <name> -o yaml

# 导出资源
kubectl get <resource> <name> -o yaml --export

# 应用配置
kubectl apply -f file.yaml
kubectl apply -f directory/

# 删除资源
kubectl delete -f file.yaml
kubectl delete <resource> <name>

# 查看事件
kubectl get events
kubectl get events -w
```

## 五、实战案例

### 1. 部署 Nginx

```yaml
# nginx-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:alpine
        ports:
        - containerPort: 80
        resources:
          limits:
            cpu: "100m"
            memory: "128Mi"
          requests:
            cpu: "50m"
            memory: "64Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
  type: NodePort
```

```bash
# 部署
kubectl apply -f nginx-deployment.yaml

# 查看
kubectl get deployments
kubectl get pods
kubectl get services

# 访问（Minikube）
minikube service nginx-service
```

### 2. 部署 Node.js + MongoDB

```yaml
# app-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: demo
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mongodb
  namespace: demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mongodb
  template:
    metadata:
      labels:
        app: mongodb
    spec:
      containers:
      - name: mongodb
        image: mongo:6
        ports:
        - containerPort: 27017
        env:
        - name: MONGO_INITDB_ROOT_USERNAME
          value: admin
        - name: MONGO_INITDB_ROOT_PASSWORD
          value: secret
        volumeMounts:
        - name: mongo-data
          mountPath: /data/db
      volumes:
      - name: mongo-data
        persistentVolumeClaim:
          claimName: mongo-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: mongodb
  namespace: demo
spec:
  selector:
    app: mongodb
  ports:
  - port: 27017
    targetPort: 27017
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongo-pvc
  namespace: demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-app
  namespace: demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: node-app
  template:
    metadata:
      labels:
        app: node-app
    spec:
      containers:
      - name: node-app
        image: my-node-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: MONGODB_URI
          value: mongodb://admin:secret@mongodb:27017/mydb?authSource=admin
        resources:
          limits:
            cpu: "200m"
            memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: node-app
  namespace: demo
spec:
  selector:
    app: node-app
  ports:
  - port: 80
    targetPort: 3000
  type: LoadBalancer
```

```bash
# 部署
kubectl apply -f app-deployment.yaml

# 查看
kubectl get all -n demo

# 查看日志
kubectl logs -f deployment/node-app -n demo
```

## 六、健康检查和探针

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
      - name: my-app
        image: my-app:latest
        ports:
        - containerPort: 3000
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        startupProbe:
          httpGet:
            path: /health
            port: 3000
          failureThreshold: 30
          periodSeconds: 10
```

## 七、水平自动扩缩（HPA）

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 八、总结

Kubernetes 是云原生应用的基石。通过本文的学习，你应该已经掌握了：

1. Kubernetes 的核心概念
2. kubectl 常用命令
3. 部署应用的基本流程
4. 健康检查和探针
5. 水平自动扩缩

继续深入学习 Kubernetes，成为云原生专家！

## 参考资料

- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [Minikube](https://minikube.sigs.k8s.io/)
- [Kind](https://kind.sigs.k8s.io/)
- [Awesome Kubernetes](https://github.com/ramitsurana/awesome-kubernetes)
