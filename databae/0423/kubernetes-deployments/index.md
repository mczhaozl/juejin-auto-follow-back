# Kubernetes 部署完全指南：从入门到生产环境

Kubernetes (K8s) 是容器编排的事实标准。本文将带你从零掌握 Kubernetes 部署。

## 一、Kubernetes 基础

### 1. 什么是 Kubernetes

Kubernetes 是一个开源的容器编排平台，用于自动化部署、扩展和管理容器化应用。

### 2. 核心概念

```
Pod: 最小部署单元，包含一个或多个容器
Deployment: 管理 Pod 的部署和更新
Service: 服务发现和负载均衡
ConfigMap: 配置管理
Secret: 敏感数据管理
Volume: 数据持久化
Namespace: 资源隔离
```

### 3. 安装 kubectl

```bash
# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"

# macOS
brew install kubectl

# Windows
choco install kubectl

# 验证安装
kubectl version --client
```

### 4. 本地集群

```bash
# Minikube
minikube start

# Kind
kind create cluster

# K3s
curl -sfL https://get.k3s.io | sh -
```

## 二、Pod

### 1. Pod 定义

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
  labels:
    app: my-app
    environment: dev
spec:
  containers:
  - name: web
    image: nginx:alpine
    ports:
    - containerPort: 80
    resources:
      requests:
        memory: "64Mi"
        cpu: "250m"
      limits:
        memory: "128Mi"
        cpu: "500m"
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5
```

### 2. 操作 Pod

```bash
# 创建 Pod
kubectl apply -f pod.yaml

# 查看 Pod
kubectl get pods
kubectl get pods -o wide
kubectl get pods -o yaml

# 查看 Pod 详情
kubectl describe pod my-pod

# 查看日志
kubectl logs my-pod
kubectl logs my-pod -f

# 进入容器
kubectl exec -it my-pod -- /bin/sh

# 删除 Pod
kubectl delete pod my-pod
```

## 三、Deployment

### 1. Deployment 定义

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  labels:
    app: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: nginx:1.21
        ports:
        - containerPort: 80
  strategy:
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
    type: RollingUpdate
```

### 2. 操作 Deployment

```bash
# 创建 Deployment
kubectl apply -f deployment.yaml

# 查看 Deployment
kubectl get deployments
kubectl get deployments -o wide

# 查看 ReplicaSet
kubectl get rs

# 扩容
kubectl scale deployment web-deployment --replicas=5

# 更新镜像
kubectl set image deployment/web-deployment web=nginx:1.22

# 查看更新状态
kubectl rollout status deployment/web-deployment

# 回滚
kubectl rollout undo deployment/web-deployment
kubectl rollout undo deployment/web-deployment --to-revision=2

# 查看历史
kubectl rollout history deployment/web-deployment

# 暂停/恢复
kubectl rollout pause deployment/web-deployment
kubectl rollout resume deployment/web-deployment
```

## 四、Service

### 1. ClusterIP

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

### 2. NodePort

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: NodePort
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
    nodePort: 30080
```

### 3. LoadBalancer

```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-service
spec:
  type: LoadBalancer
  selector:
    app: web
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

### 4. 操作 Service

```bash
# 创建 Service
kubectl apply -f service.yaml

# 查看 Service
kubectl get services
kubectl get svc

# 查看 Service 详情
kubectl describe service web-service

# 端口转发
kubectl port-forward service/web-service 8080:80
```

## 五、ConfigMap

### 1. ConfigMap 定义

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database: postgres
  cache: redis
  log_level: info
  
  # 文件形式
  config.json: |
    {
      "database": {
        "host": "db",
        "port": 5432
      }
    }
```

### 2. 使用 ConfigMap

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: app
    image: my-app
    env:
    - name: DATABASE
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database
    - name: LOG_LEVEL
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: log_level
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

## 六、Secret

### 1. Secret 定义

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  username: YWRtaW4=  # base64 编码的 admin
  password: cGFzc3dvcmQ=  # base64 编码的 password
```

### 2. 使用 Secret

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: app
    image: my-app
    env:
    - name: DB_USERNAME
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: username
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: password
    volumeMounts:
    - name: secret-volume
      mountPath: /etc/secret
      readOnly: true
  volumes:
  - name: secret-volume
    secret:
      secretName: app-secret
```

## 七、Volume

### 1. EmptyDir

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: app
    image: my-app
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir: {}
```

### 2. PersistentVolumeClaim

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: app
    image: my-app
    volumeMounts:
    - mountPath: /data
      name: my-volume
  volumes:
  - name: my-volume
    persistentVolumeClaim:
      claimName: my-pvc
```

## 八、Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: development
---
apiVersion: v1
kind: Namespace
metadata:
  name: production
```

```bash
# 创建 Namespace
kubectl apply -f namespace.yaml

# 查看 Namespace
kubectl get namespaces
kubectl get ns

# 切换 Namespace
kubectl config set-context --current --namespace=development

# 在指定 Namespace 操作
kubectl get pods -n production
```

## 九、Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web-service
            port:
              number: 80
      - path: /api
        pathType: Prefix
        backend:
          service:
            name: api-service
            port:
              number: 3000
```

## 十、完整应用示例

```yaml
# config.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  DATABASE_URL: postgres://user:pass@db:5432/mydb
  REDIS_URL: redis://redis:6379

---
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  DB_PASSWORD: cGFzc3dvcmQ=

---
# db-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: db
spec:
  replicas: 1
  selector:
    matchLabels:
      app: db
  template:
    metadata:
      labels:
        app: db
    spec:
      containers:
      - name: db
        image: postgres:15
        env:
        - name: POSTGRES_USER
          value: user
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: app-secret
              key: DB_PASSWORD
        - name: POSTGRES_DB
          value: mydb
        ports:
        - containerPort: 5432
        volumeMounts:
        - mountPath: /var/lib/postgresql/data
          name: db-data
      volumes:
      - name: db-data
        persistentVolumeClaim:
          claimName: db-pvc

---
# db-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: db
spec:
  type: ClusterIP
  selector:
    app: db
  ports:
  - port: 5432

---
# db-pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: db-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
# redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        ports:
        - containerPort: 6379

---
# redis-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: redis
spec:
  type: ClusterIP
  selector:
    app: redis
  ports:
  - port: 6379

---
# web-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
      - name: web
        image: my-web-app:latest
        envFrom:
        - configMapRef:
            name: app-config
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

---
# web-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  type: ClusterIP
  selector:
    app: web
  ports:
  - port: 80
    targetPort: 3000

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: web-ingress
spec:
  ingressClassName: nginx
  rules:
  - host: myapp.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: web
            port:
              number: 80
```

## 十一、常用命令

```bash
# 查看资源
kubectl get all
kubectl get pods,svc,deploy

# 查看节点
kubectl get nodes
kubectl describe node <node-name>

# 查看事件
kubectl get events
kubectl get events -w

# 导出资源
kubectl get deployment web -o yaml > web.yaml

# 调试
kubectl debug -it my-pod --image=busybox
kubectl run -it --rm debug --image=busybox -- sh
```

## 十二、最佳实践

1. 使用声明式配置（YAML）
2. 合理设置资源限制
3. 配置健康检查
4. 使用 ConfigMap 和 Secret
5. 合理使用 Namespace
6. 设置滚动更新策略
7. 使用标签和选择器
8. 监控和日志

## 十三、总结

Kubernetes 部署核心：
- Pod 是最小部署单元
- Deployment 管理部署和更新
- Service 提供服务发现
- ConfigMap 和 Secret 管理配置
- Volume 处理数据持久化
- Ingress 处理外部访问

开始在 Kubernetes 上部署你的应用吧！
