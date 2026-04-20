# Kubernetes CRD 完全指南

## 一、定义 CRD

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: myresources.example.com
spec:
  group: example.com
  versions:
    - name: v1
      served: true
      storage: true
      schema:
        openAPIV3Schema:
          type: object
          properties:
            spec:
              type: object
              properties:
                replicas:
                  type: integer
  scope: Namespaced
  names:
    plural: myresources
    singular: myresource
    kind: MyResource
    shortNames:
    - mr
```

## 二、创建自定义资源

```yaml
apiVersion: example.com/v1
kind: MyResource
metadata:
  name: example
spec:
  replicas: 3
```

```bash
# 应用 CRD
kubectl apply -f crd.yaml

# 查看 CRD
kubectl get crd

# 创建自定义资源
kubectl apply -f myresource.yaml

# 查看自定义资源
kubectl get myresource
kubectl describe myresource example
```

## 三、简单的 Operator

```go
// main.go - 简单的控制器
package main

import (
  "k8s.io/client-go/kubernetes"
  "k8s.io/client-go/tools/clientcmd"
)

func main() {
  // 连接到 Kubernetes
  config, _ := clientcmd.BuildConfigFromFlags("", "/.kube/config")
  clientset, _ := kubernetes.NewForConfig(config)
  
  // ... 逻辑
}
```

## 四、使用 Kubebuilder/Operator SDK

```bash
# 初始化项目
operator-sdk init --domain example.com --repo github.com/example/myoperator

# 创建 API
operator-sdk create api --group apps --version v1 --kind MyApp --resource --controller
```

## 最佳实践
- 使用 OpenAPI schema 验证
- 考虑升级和转换策略
- 使用 Finalizers 清理资源
- 合理设置 status 子资源
- 使用成熟的 Operator 框架
