# Go Kubernetes Operator 完全指南

## 一、Operator SDK

```bash
operator-sdk init --domain example.com --repo github.com/example/my-operator
operator-sdk create api --group apps --version v1 --kind MyApp --resource --controller
```

## 二、定义 CRD

```go
// api/v1/myapp_types.go
type MyAppSpec struct {
  Replicas int32 `json:"replicas"`
  Image string `json:"image"`
}

type MyAppStatus struct {
  ReadyReplicas int32 `json:"readyReplicas,omitempty"`
}
```

## 三、Controller 逻辑

```go
func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
  log := log.FromContext(ctx)
  
  // 获取对象
  myapp := &appsv1.MyApp{}
  if err := r.Get(ctx, req.NamespacedName, myapp); err != nil {
    return ctrl.Result{}, client.IgnoreNotFound(err)
  }
  
  // 管理 Deployment
  dep := &appsv1.Deployment{}
  // ... 创建和更新
  
  return ctrl.Result{}, nil
}
```

## 四、部署 CRD

```yaml
apiVersion: apps.example.com/v1
kind: MyApp
metadata:
  name: myapp-sample
spec:
  replicas: 3
  image: nginx:1.19
```

## 五、最佳实践

- 设计清晰的 CRD
- 使用 Finalizer 清理
- 状态更新正确
- 错误处理和重试
- 测试控制器逻辑
- 文档化 API
