# Kubernetes StatefulSets 完全指南：从原理到持久化应用

## 一、StatefulSets 概述

### 1.1 vs Deployment

| 特性 | Deployment | StatefulSet |
|------|------------|-------------|
| Pod 标识 | 随机 | 稳定（name-0, name-1） |
| DNS | 临时 | 稳定 DNS |
| 存储 | 共享 | 独立 PVC |
| 伸缩顺序 | 无序 | 有序 |

### 1.2 适用场景

- 数据库（MySQL、PostgreSQL、MongoDB）
- 消息队列（Kafka、RabbitMQ）
- 分布式存储（Etcd、Zookeeper）

---

## 二、StatefulSet 配置

### 2.1 基本示例

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
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
        image: nginx
        ports:
        - containerPort: 80
          name: web
        volumeMounts:
        - name: www
          mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
  - metadata:
      name: www
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
```

### 2.2 Headless Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx
spec:
  selector:
    app: nginx
  clusterIP: None
  ports:
  - port: 80
    name: web
```

---

## 三、Pod 标识与 DNS

### 3.1 Pod 命名

```
web-0
web-1
web-2
```

### 3.2 DNS 解析

```
<Pod-Name>.<Service-Name>.<Namespace>.svc.cluster.local

web-0.nginx.default.svc.cluster.local
web-1.nginx.default.svc.cluster.local
```

---

## 四、持久化存储

### 4.1 Volume Claim Templates

```yaml
volumeClaimTemplates:
- metadata:
    name: data
  spec:
    accessModes: ["ReadWriteOnce"]
    storageClassName: "fast"
    resources:
      requests:
        storage: 10Gi
```

### 4.2 Storage Class

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/gce-pd
parameters:
  type: pd-ssd
```

---

## 五、MySQL 部署实战

### 5.1 StatefulSet

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: mysql
spec:
  serviceName: mysql
  replicas: 3
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        env:
        - name: MYSQL_ROOT_PASSWORD
          value: secret
        ports:
        - containerPort: 3306
        volumeMounts:
        - name: mysql-data
          mountPath: /var/lib/mysql
  volumeClaimTemplates:
  - metadata:
      name: mysql-data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 10Gi
```

### 5.2 Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: mysql
spec:
  selector:
    app: mysql
  clusterIP: None
  ports:
  - port: 3306
    name: mysql
```

### 5.3 连接 MySQL

```bash
# 连接到主节点
kubectl run mysql-client --rm -it --image=mysql:8.0 -- mysql -h mysql-0.mysql -uroot -psecret

# 连接到任意节点
kubectl run mysql-client --rm -it --image=mysql:8.0 -- mysql -h mysql -uroot -psecret
```

---

## 六、扩容与缩容

### 6.1 扩容

```bash
kubectl scale statefulset web --replicas=5

# 查看 Pod 创建顺序
kubectl get pods -w
```

### 6.2 缩容

```bash
kubectl scale statefulset web --replicas=3

# 注意：缩容不会删除 PVC
```

---

## 七、升级策略

### 7.1 RollingUpdate（默认）

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  updateStrategy:
    type: RollingUpdate
    rollingUpdate:
      partition: 1
```

### 7.2 OnDelete

```yaml
spec:
  updateStrategy:
    type: OnDelete
```

---

## 八、数据备份与恢复

### 8.1 备份 PVC

```bash
# 创建快照
kubectl apply -f snapshot.yaml

# 或者手动备份
kubectl cp <pod-name>:/data ./backup
```

### 8.2 从备份恢复

```bash
# 恢复数据到新 PVC
kubectl apply -f restore.yaml

# 或者手动恢复
kubectl cp ./backup <pod-name>:/data
```

---

## 九、最佳实践

### 9.1 配置建议

- 使用 Headless Service
- 配置 volumeClaimTemplates
- 设置合理的更新策略

### 9.2 数据安全

- 定期备份数据
- 使用 StorageClass
- 考虑使用 Operator

### 9.3 监控与运维

- 监控 Pod 状态
- 检查 PVC 使用情况
- 设置资源限制

---

## 总结

StatefulSets 为有状态应用提供了稳定的部署方式，通过稳定的网络标识和持久化存储，可以安全地运行数据库等有状态服务。
