# Kubernetes 存储完全指南

## 一、PV、PVC 基础

### 1.1 PersistentVolume

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: my-pv
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /data
```

### 1.2 PersistentVolumeClaim

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
      storage: 5Gi
```

## 二、StorageClass

```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/aws-ebs
parameters:
  type: gp2
```

```yaml
# 使用 StorageClass
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  storageClassName: fast
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

## 三、在 Pod 中使用

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
    - name: app
      image: myapp
      volumeMounts:
        - name: my-storage
          mountPath: /app/data
  volumes:
    - name: my-storage
      persistentVolumeClaim:
        claimName: my-pvc
```

## 四、访问模式

- ReadWriteOnce (RWO): 单节点读写
- ReadWriteMany (RWX): 多节点读写
- ReadOnlyMany (ROX): 多节点只读

## 五、存储类型

### 5.1 HostPath (开发用)
```yaml
hostPath:
  path: /data
```

### 5.2 NFS
```yaml
nfs:
  path: /export
  server: nfs-server.example.com
```

### 5.3 EBS (AWS)
```yaml
awsElasticBlockStore:
  volumeID: <volume-id>
```

## 六、StatefulSet 存储

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: web
spec:
  serviceName: "nginx"
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    spec:
      containers:
        - name: nginx
          image: k8s.gcr.io/nginx
          volumeMounts:
            - name: www
              mountPath: /usr/share/nginx/html
  volumeClaimTemplates:
    - metadata:
        name: www
      spec:
        accessModes: ["ReadWriteOnce"]
        resources:
          requests:
            storage: 1Gi
```

## 七、最佳实践

- 使用 StorageClass 动态供给
- 选择合适的访问模式
- 设置合理的 reclaim 策略
- StatefulSet 使用 volumeClaimTemplates
- 监控存储使用
- 定期备份重要数据
