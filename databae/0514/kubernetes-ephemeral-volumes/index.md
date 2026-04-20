# Kubernetes 临时卷完全指南

## 一、emptyDir

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-empty-dir
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - mountPath: /cache
      name: cache-volume
  volumes:
  - name: cache-volume
    emptyDir: {}
```

## 二、ConfigMap 作为卷

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: config
data:
  config.yaml: |
    key: value

---

apiVersion: v1
kind: Pod
metadata:
  name: pod-with-configmap
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - mountPath: /etc/config
      name: config
  volumes:
  - name: config
    configMap:
      name: config
```

## 三、Secret 作为卷

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-secret
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - mountPath: /etc/secret
      name: secret
  volumes:
  - name: secret
    secret:
      secretName: mysecret
```

## 四、CSI Ephemeral Volume

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-csi
spec:
  containers:
  - name: app
    image: nginx
    volumeMounts:
    - mountPath: /data
      name: data
  volumes:
  - name: data
    csi:
      driver: secrets-store.csi.k8s.io
```

## 最佳实践
- emptyDir 适合临时缓存
- ConfigMap/Secret 注入配置
- CSI Ephemeral 动态提供
- 注意临时卷的生命周期
- 设置大小限制
