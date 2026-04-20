# Kubernetes Helm 包管理完全指南

## 一、Helm 概述

### 1.1 什么是 Helm

Kubernetes 的包管理工具，类似 apt/yum/npm。

### 1.2 核心概念

- **Chart**：包，包含 Kubernetes 资源定义
- **Release**：Chart 的运行实例
- **Repository**：Chart 仓库

---

## 二、基本使用

### 2.1 安装 Helm

```bash
# macOS
brew install helm

# Linux
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

### 2.2 添加仓库

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update
```

### 2.3 安装 Chart

```bash
helm install my-release bitnami/nginx

# 使用自定义 values
helm install my-release bitnami/nginx -f values.yaml

# 设置参数
helm install my-release bitnami/nginx --set service.type=NodePort
```

### 2.4 管理 Release

```bash
# 查看
helm list

# 升级
helm upgrade my-release bitnami/nginx

# 回滚
helm rollback my-release 1

# 卸载
helm uninstall my-release
```

---

## 三、创建 Chart

### 3.1 初始化

```bash
helm create mychart
```

### 3.2 Chart 结构

```
mychart/
├── Chart.yaml          # Chart 元信息
├── values.yaml         # 默认值
├── templates/          # 模板
│   ├── deployment.yaml
│   ├── service.yaml
│   └── ingress.yaml
└── charts/             # 依赖
```

### 3.3 Chart.yaml

```yaml
apiVersion: v2
name: myapp
description: A Helm chart for My App
type: application
version: 0.1.0
appVersion: "1.0.0"
```

### 3.4 values.yaml

```yaml
replicaCount: 1
image:
  repository: nginx
  tag: latest
  pullPolicy: IfNotPresent
service:
  type: ClusterIP
  port: 80
```

---

## 四、模板语法

### 4.1 基本模板

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
      - name: {{ .Release.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
```

### 4.2 函数与管道

```yaml
# 默认值
port: {{ .Values.port | default 80 }}

# 引用
{{ include "mychart.fullname" . }}

# 条件
{{- if .Values.ingress.enabled }}
...
{{- end }}

# 循环
{{- range .Values.env }}
- name: {{ .name }}
  value: {{ .value }}
{{- end }}
```

### 4.3 命名模板

```yaml
{{/* _helpers.tpl */}}
{{- define "mychart.fullname" -}}
{{- .Release.Name }}
{{- end }}
```

---

## 五、模板调试

```bash
# 渲染模板
helm template mychart ./mychart

# 检查语法
helm lint ./mychart

# 安装前预览
helm install my-release --dry-run --debug ./mychart
```

---

## 六、依赖管理

### 6.1 Chart.yaml

```yaml
dependencies:
- name: redis
  version: "17.x.x"
  repository: "https://charts.bitnami.com/bitnami"
  condition: redis.enabled
```

### 6.2 更新依赖

```bash
helm dependency build
helm dependency update
```

---

## 七、实战：应用 Chart

### 7.1 部署应用

```yaml
# values.yaml
replicaCount: 3
image:
  repository: myapp
  tag: v1.0.0
service:
  type: LoadBalancer
ingress:
  enabled: true
  hosts:
    - host: myapp.example.com
      paths:
        - path: /
```

```bash
helm install myapp ./mychart -f values.yaml
```

---

## 八、最佳实践

- 使用命名模板
- 合理组织 values.yaml
- 使用 chart-testing 测试
- 版本化 Chart
- 文档化 values

---

## 总结

Helm 简化了 Kubernetes 应用的部署和管理，通过模板和 values 的分离实现灵活配置。
