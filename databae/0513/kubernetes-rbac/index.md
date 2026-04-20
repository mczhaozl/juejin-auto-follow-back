# Kubernetes RBAC 完全指南

## 一、Role 与 RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

---

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

## 二、ClusterRole 与 ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "watch", "list"]

---

apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-nodes
subjects:
- kind: User
  name: bob
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

## 三、ServiceAccount

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-app

---

apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-app-role
subjects:
- kind: ServiceAccount
  name: my-app
roleRef:
  kind: ClusterRole
  name: view
  apiGroup: rbac.authorization.k8s.io
```

## 四、验证权限

```bash
# 检查权限
kubectl auth can-i get pods --as alice -n default

# 查看角色
kubectl describe role pod-reader

# 查看角色绑定
kubectl describe rolebinding read-pods
```

## 最佳实践
- 最小权限原则
- 优先使用内置 ClusterRole
- 使用 ServiceAccount 管理应用权限
- 使用 Aggregated ClusterRole 组合权限
- 定期审计 RBAC 策略
