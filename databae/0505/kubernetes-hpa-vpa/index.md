# Kubernetes HPA & VPA 自动扩缩容完全指南

## 一、Horizontal Pod Autoscaler (HPA)

### 1.1 基础配置

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: my-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: my-app
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

### 1.2 自定义指标

```yaml
metrics:
- type: Pods
  pods:
    metric:
      name: http_requests
    target:
      type: AverageValue
      averageValue: 1000m
```

## 二、部署 Resource Requests/Limits

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  template:
    spec:
      containers:
      - name: app
        resources:
          requests:
            cpu: "200m"
            memory: "256Mi"
          limits:
            cpu: "500m"
            memory: "512Mi"
```

## 三、Vertical Pod Autoscaler (VPA)

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app
spec:
  targetRef:
    apiVersion: "apps/v1"
    kind: Deployment
    name: my-app
  updatePolicy:
    updateMode: "Auto"  # Auto, Recreate, Initial, Off
  resourcePolicy:
    containerPolicies:
    - containerName: '*'
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 1000m
        memory: 1Gi
```

## 四、HPA & VPA 配合使用

```yaml
# VPA 推荐资源
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: my-app
spec:
  updatePolicy:
    updateMode: "Initial"
```

## 五、监控 HPA 状态

```bash
# 查看 HPA 状态
kubectl get hpa
kubectl describe hpa my-app

# 查看事件
kubectl get events
```

## 六、最佳实践

- 先设置合理的 requests 和 limits
- HPA 用于处理流量波动
- VPA 用于资源推荐和优化
- 考虑使用 Prometheus 自定义指标
- 测试扩缩容行为
- 避免频繁扩缩容
- 监控和调整参数
