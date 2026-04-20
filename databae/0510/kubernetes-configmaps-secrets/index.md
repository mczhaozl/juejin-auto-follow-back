# Kubernetes ConfigMaps 和 Secrets 完全指南

## 一、ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
data:
  app.config: |
    debug=true
    log.level=info
  database.host: "mysql"
  database.port: "3306"
```

## 二、使用 ConfigMap

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: myapp
    env:
    - name: DATABASE_HOST
      valueFrom:
        configMapKeyRef:
          name: app-config
          key: database.host
    volumeMounts:
    - name: config
      mountPath: /etc/app
  volumes:
  - name: config
    configMap:
      name: app-config
```

## 三、Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: app-secret
type: Opaque
data:
  username: YWRtaW4=
  password: cGFzc3dvcmQ=
```

## 四、使用 Secret

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    image: myapp
    env:
    - name: DB_PASSWORD
      valueFrom:
        secretKeyRef:
          name: app-secret
          key: password
    volumeMounts:
    - name: secret
      mountPath: /var/secret
  volumes:
  - name: secret
    secret:
      secretName: app-secret
```

## 五、最佳实践

- 使用 ConfigMap 存储配置
- 使用 Secret 存储敏感信息
- 使用 Sealed Secrets 或 SOPS 加密 Secrets
- 通过 volume 挂载配置
- 环境变量方式便于使用
- 使用 Kustomize 或 Helm 管理配置
