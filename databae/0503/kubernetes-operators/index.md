# Kubernetes Operators 完全指南

## 一、Operators 概述

### 1.1 什么是 Operator

打包、部署和管理 Kubernetes 应用的方法。

### 1.2 核心概念

- **Custom Resource (CR)**：自定义资源
- **Custom Controller**：自定义控制器
- **CRD**：自定义资源定义

---

## 二、Operator SDK

### 2.1 安装 Operator SDK

```bash
# 安装
brew install operator-sdk

# 验证
operator-sdk version
```

### 2.2 创建项目

```bash
operator-sdk init --domain example.com --repo github.com/example/myoperator
cd myoperator
```

### 2.3 创建 API

```bash
operator-sdk create api --group app --version v1 --kind MyApp --resource --controller
```

---

## 三、定义 CRD

```go
// api/v1/myapp_types.go
type MyAppSpec struct {
	Size    int32  `json:"size"`
	Image   string `json:"image"`
}

type MyAppStatus struct {
	Nodes []string `json:"nodes"`
}
```

---

## 四、Controller 实现

```go
// controllers/myapp_controller.go
func (r *MyAppReconciler) Reconcile(ctx context.Context, req ctrl.Request) (ctrl.Result, error) {
	log := log.FromContext(ctx)
	
	app := &appv1.MyApp{}
	if err := r.Get(ctx, req.NamespacedName, app); err != nil {
		return ctrl.Result{}, client.IgnoreNotFound(err)
	}
	
	deployment := r.desiredDeployment(app)
	if err := r.CreateOrUpdate(ctx, deployment); err != nil {
		return ctrl.Result{}, err
	}
	
	return ctrl.Result{}, nil
}
```

---

## 五、部署

```bash
# 安装 CRD
make install

# 本地运行
make run

# 构建镜像
make docker-build docker-push IMG=myoperator:v0.0.1

# 部署
make deploy IMG=myoperator:v0.0.1
```

---

## 六、使用 CR

```yaml
# myapp.yaml
apiVersion: app.example.com/v1
kind: MyApp
metadata:
  name: myapp-sample
spec:
  size: 3
  image: nginx:latest
```

```bash
kubectl apply -f myapp.yaml
kubectl get myapp
kubectl get pods
```

---

## 七、常用 Operators

- **Prometheus Operator**
- **Strimzi**：Kafka Operator
- **Etcd Operator**
- **Flux**：GitOps
- **Argo CD**

---

## 八、最佳实践

- 从小开始
- 利用现有工具
- 正确处理错误
- 添加状态管理
- 编写文档

---

## 总结

Operators 让 Kubernetes 应用管理自动化，通过自定义资源和控制器实现运维知识的编码化。
