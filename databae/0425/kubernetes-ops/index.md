# Kubernetes 运维完全实战指南：从部署到监控

Kubernetes 是容器编排的事实标准。本文将带你从基础部署到生产运维，全面掌握 Kubernetes。

## 一、Kubernetes 基础

### 1. 核心概念

```
Pod: 最小调度单元，包含一个或多个容器
Deployment: 声明式更新 Pod 和 ReplicaSet
Service: 定义访问 Pod 的策略
Namespace: 资源隔离
ConfigMap/Secret: 配置管理
Volume: 存储
Ingress: 外部访问入口
```

### 2. 安装 Minikube

```bash
# 安装 kubectl
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# 安装 Minikube
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube

# 启动 Minikube
minikube start --driver=docker
```

### 3. 第一个应用

```yaml
# deployment.yaml
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
        image: nginx:1.21
        ports:
        - containerPort: 80

# service.yaml
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
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

kubectl get deployments
kubectl get pods
kubectl get services

minikube service nginx-service
```

## 二、运维操作

### 1. 扩容和缩容

```bash
# 手动扩容
kubectl scale deployment nginx-deployment --replicas=5

# 自动扩缩容（HPA）
kubectl autoscale deployment nginx-deployment --min=2 --max=10 --cpu-percent=80
```

```yaml
# hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: nginx-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: nginx-deployment
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 80
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 70
```

### 2. 滚动更新和回滚

```bash
# 更新镜像
kubectl set image deployment/nginx-deployment nginx=nginx:1.22

# 查看更新状态
kubectl rollout status deployment/nginx-deployment

# 查看更新历史
kubectl rollout history deployment/nginx-deployment

# 回滚到上一个版本
kubectl rollout undo deployment/nginx-deployment

# 回滚到特定版本
kubectl rollout undo deployment/nginx-deployment --to-revision=2
```

### 3. 健康检查

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
      - name: web-app
        image: my-web-app:latest
        ports:
        - containerPort: 3000
        livenessProbe:
          httpGet:
            path: /healthz
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /readyz
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

### 4. 配置管理

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  database.host: "postgres"
  database.port: "5432"
  log.level: "info"
  app.conf: |
    [server]
    port=3000
    [database]
    host=postgres

# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  database.password: cGFzc3dvcmQxMjM=  # base64 编码
  api.key: YXBpa2V5MTIz
```

```yaml
# 使用 ConfigMap 和 Secret
apiVersion: v1
kind: Pod
metadata:
  name: config-demo
spec:
  containers:
  - name: app
    image: my-app:latest
    env:
    - name: DB_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.host
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: database.password
    volumeMounts:
    - name: config-volume
      mountPath: /etc/config
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```

## 三、存储

### 1. PV 和 PVC

```yaml
# pv.yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: pv-demo
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: manual
  hostPath:
    path: /data/pv-demo

# pvc.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: pvc-demo
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 5Gi
  storageClassName: manual
```

```yaml
# 使用 PVC
apiVersion: v1
kind: Pod
metadata:
  name: pv-pod
spec:
  containers:
    - name: app
      image: nginx
      volumeMounts:
      - mountPath: "/usr/share/nginx/html"
        name: pv-storage
  volumes:
    - name: pv-storage
      persistentVolumeClaim:
        claimName: pvc-demo
```

### 2. StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
  fsType: ext4
reclaimPolicy: Retain
allowVolumeExpansion: true
volumeBindingMode: WaitForFirstConsumer
```

## 四、网络

### 1. Service 类型

```yaml
# ClusterIP (默认)
apiVersion: v1
kind: Service
metadata:
  name: clusterip-service
spec:
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080

# NodePort
apiVersion: v1
kind: Service
metadata:
  name: nodeport-service
spec:
  type: NodePort
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
    nodePort: 30080

# LoadBalancer
apiVersion: v1
kind: Service
metadata:
  name: loadbalancer-service
spec:
  type: LoadBalancer
  selector:
    app: my-app
  ports:
  - port: 80
    targetPort: 8080
```

### 2. Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ingress-demo
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx
  rules:
  - host: example.com
    http:
      paths:
      - path: /app1
        pathType: Prefix
        backend:
          service:
            name: app1-service
            port:
              number: 80
      - path: /app2
        pathType: Prefix
        backend:
          service:
            name: app2-service
            port:
              number: 80
  tls:
  - hosts:
    - example.com
    secretName: example-tls
```

## 五、监控和日志

### 1. Prometheus 和 Grafana

```yaml
# prometheus-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
      volumes:
      - name: config
        configMap:
          name: prometheus-config
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'kubernetes'
      kubernetes_sd_configs:
      - role: pod
```

```bash
# 安装 Prometheus Stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack
```

### 2. ELK Stack

```yaml
# filebeat.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: filebeat-config
data:
  filebeat.yml: |
    filebeat.inputs:
    - type: container
      paths:
        - /var/log/containers/*.log
    output.elasticsearch:
      hosts: ["elasticsearch:9200"]
```

```bash
# 安装 ELK
helm repo add elastic https://helm.elastic.co
helm install elasticsearch elastic/elasticsearch
helm install kibana elastic/kibana
helm install filebeat elastic/filebeat
```

## 六、安全

### 1. RBAC

```yaml
# role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

---
# rolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### 2. 网络策略

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  policyTypes:
  - Ingress
---
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-web
spec:
  podSelector:
    matchLabels:
      app: web
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 80
```

## 七、最佳实践

1. 使用声明式配置（YAML）
2. 配置资源限制（requests/limits）
3. 实现健康检查（liveness/readiness）
4. 使用 ConfigMap 和 Secret 管理配置
5. 配置滚动更新策略
6. 实施 RBAC
7. 配置网络策略
8. 监控和日志
9. 定期备份
10. 使用 Helm 管理 Chart

## 八、总结

Kubernetes 运维核心要点：
- 理解核心概念（Pod、Deployment、Service）
- 掌握常用运维操作（扩容、更新、回滚）
- 配置管理（ConfigMap、Secret）
- 存储（PV、PVC、StorageClass）
- 网络（Service、Ingress）
- 监控和日志（Prometheus、Grafana、ELK）
- 安全（RBAC、网络策略）
- 遵循最佳实践

开始用 Kubernetes 运维你的容器化应用吧！
