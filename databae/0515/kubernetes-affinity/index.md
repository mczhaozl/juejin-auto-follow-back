# Kubernetes Affinity 完全指南

## 一、Node Affinity

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-node-affinity
spec:
  containers:
  - name: app
    image: nginx
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: disktype
            operator: In
            values:
            - ssd
```

## 二、Pod Affinity

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-pod-affinity
spec:
  containers:
  - name: app
    image: nginx
  affinity:
    podAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
      - labelSelector:
          matchExpressions:
          - key: app
            operator: In
            values:
            - backend
        topologyKey: topology.kubernetes.io/zone
```

## 三、Toleration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-toleration
spec:
  containers:
  - name: app
    image: nginx
  tolerations:
  - key: "dedicated"
    operator: "Equal"
    value: "special"
    effect: "NoSchedule"
```

## 四、Node Selector

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: pod-with-node-selector
spec:
  containers:
  - name: app
    image: nginx
  nodeSelector:
    disktype: ssd
```

## 最佳实践
- Affinity 灵活放置
- Toleration 调度特殊节点
- 平衡可用性和性能
- topologyKey 控制 AZ 分布
- 测试调度行为
