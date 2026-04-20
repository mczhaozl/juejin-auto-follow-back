# Kubernetes Helm 完全指南

## 一、安装 Helm

```bash
# 安装 Helm
brew install helm

# 初始化
helm repo add stable https://charts.helm.sh/stable
helm repo update
```

## 二、安装 Chart

```bash
# 安装 nginx
helm install my-nginx bitnami/nginx

# 查看 release
helm list

# 升级
helm upgrade my-nginx bitnami/nginx

# 删除
helm uninstall my-nginx
```

## 三、创建 Chart

```bash
helm create mychart
```

```
mychart/
├── Chart.yaml   # 元数据
├── values.yaml  # 默认值
├── templates/   # 模板
└── ...
```

## 四、模板语法

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}
spec:
  replicas: {{ .Values.replicaCount }}
```

## 五、最佳实践

- 使用官方和社区 Chart
- 合理配置 values
- 自定义 Chart 组织资源
- 使用子 Chart（subcharts）拆分
- 测试和验证 Chart
- 安全扫描 Chart
