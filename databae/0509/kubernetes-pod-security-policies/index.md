# Kubernetes Pod Security Policies 完全指南

## 一、Pod Security Standards

```yaml
# namespace 配置
apiVersion: v1
kind: Namespace
metadata:
  labels:
    pod-security.kubernetes.io/enforce: baseline # restricted, privileged
    pod-security.kubernetes.io/audit: baseline
    pod-security.kubernetes.io/warn: baseline
```

## 二、安全上下文

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: security-context-demo
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    fsGroup: 2000
    seccompProfile:
      type: RuntimeDefault
  containers:
  - name: app
    image: myapp
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
```

## 三、受限 Pod 策略

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: restricted-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
  containers:
  - name: app
    image: myapp
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
```

## 四、资源限制

```yaml
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: app
    resources:
      limits:
        cpu: "1"
        memory: "512Mi"
      requests:
        cpu: "0.5"
        memory: "256Mi"
```

## 五、最佳实践

- 使用 pod-security.kubernetes.io 标签
- 从 baseline 开始逐步升级到 restricted
- 配置安全上下文（非 root, 只读 fs）
- 禁用特权容器
- 限制容器能力
- 配置 seccomp 和 AppArmor
- 使用网络策略隔离 Pod
