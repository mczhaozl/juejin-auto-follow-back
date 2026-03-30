# 监控与告警完全指南：Prometheus 与 Grafana 实战

> 深入讲解监控体系，包括 Prometheus 指标收集、Grafana 可视化、告警规则配置，以及实际项目中的全链路监控和性能优化实践。

## 一、监控体系基础

### 1.1 监控重要性

监控四大黄金指标：

```
┌─────────────────────────────────────────────────────────────────┐
│                     四大黄金指标                                 │
│                                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │   延迟   │  │  流量    │  │  错误    │  │  饱和度  │     │
│  │ Latency  │  │ Traffic  │  │ Errors   │  │ Saturation│     │
│  │          │  │          │  │          │  │          │     │
│  │ 请求耗时  │  │  QPS    │  │  错误率  │  │ CPU/内存  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 监控层级

| 层级 | 监控内容 |
|------|----------|
| 基础设施 | CPU、内存、磁盘、网络 |
| 中间件 | 数据库、缓存、消息队列 |
| 应用 | 接口性能、业务指标 |
| 业务 | DAU、订单量、转化率 |

## 二、Prometheus

### 2.1 安装

```bash
# Docker 安装
docker run -d --name prometheus \
  -p 9090:9090 \
  -v /path/to/prometheus.yml:/etc/prometheus/prometheus.yml \
  prom/prometheus
```

### 2.2 配置

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']

  - job_name: 'myapp'
    static_configs:
      - targets: ['myapp:8080']
```

### 2.3 查询 PromQL

```promql
# CPU 使用率
100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用率
100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))

# 请求延迟
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# QPS
rate(http_requests_total[5m])

# 错误率
rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])
```

## 三、Node Exporter

### 3.1 安装

```bash
# 启动
docker run -d --name node-exporter \
  -p 9100:9100 \
  prom/node-exporter
```

### 3.2 关键指标

```promql
# CPU
rate(node_cpu_seconds_total[5m])

# 内存
node_memory_MemTotal_bytes
node_memory_MemAvailable_bytes

# 磁盘
node_filesystem_size_bytes
node_filesystem_avail_bytes

# 网络
rate(node_network_receive_bytes_total[5m])
rate(node_network_transmit_bytes_total[5m])
```

## 四、Grafana

### 4.1 安装

```bash
# Docker 安装
docker run -d --name grafana \
  -p 3000:3000 \
  -e GF_SECURITY_ADMIN_PASSWORD=admin \
  grafana/grafana
```

### 4.2 数据源配置

```
┌─────────────────────────────────────────────┐
│  Configuration → Data Sources → Add        │
│                                             │
│  Name: Prometheus                          │
│  Type: Prometheus                          │
│  URL: http://prometheus:9090              │
│  Access: Server (default)                  │
│                                             │
│  [Save & Test]                            │
└─────────────────────────────────────────────┘
```

### 4.3 Dashboard

```json
{
  "dashboard": {
    "title": "Node Exporter",
    "panels": [
      {
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by (mode) (rate(node_cpu_seconds_total{mode='idle'}[1m])) * 100)"
          }
        ]
      },
      {
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes"
          }
        ]
      }
    ]
  }
}
```

### 4.4 常用图表

| 图表 | 用途 |
|------|------|
| Graph | 时序数据 |
| Stat | 单值显示 |
| Gauge | 仪表盘 |
| Table | 表格 |
| Heatmap | 热力图 |

## 五、告警配置

### 5.1 Alertmanager

```yaml
# alertmanager.yml
route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h
  receiver: 'email'
receivers:
  - name: 'email'
    email_configs:
      - to: 'alerts@example.com'
        send_resolved: true
```

### 5.2 告警规则

```yaml
# rules.yml
groups:
  - name: myapp
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value | humanizePercentage }}"

      - alert: HighLatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
```

### 5.3 告警模板

```yaml
annotations:
  summary: "服务 {{ $labels.instance }} CPU 使用率过高"
  description: |
    CPU 使用率: {{ $value | humanizePercentage }}
    持续时间: {{ $duration }}
    服务: {{ $labels.job }}
    实例: {{ $labels.instance }}
```

## 六、应用监控

### 6.1 业务指标

```javascript
// Node.js 指标暴露
const promClient = require('prom-client');

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const httpRequestTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

// 使用
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    httpRequestDuration.labels(req.method, req.route, res.statusCode).observe(duration);
    httpRequestTotal.labels(req.method, req.route, res.statusCode).inc();
  });
  next();
});
```

### 6.2 业务埋点

```javascript
// 订单创建
const orderTotal = new promClient.Counter({
  name: 'orders_created_total',
  help: 'Total number of orders created',
  labelNames: ['status']
});

const orderAmount = new promClient.Histogram({
  name: 'order_amount',
  help: 'Order amount histogram',
  buckets: [10, 50, 100, 500, 1000, 5000]
});

// 创建订单时
orderTotal.labels('success').inc();
orderAmount.observe(order.amount);
```

## 七、全链路监控

### 7.1 架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      全链路监控                                  │
│                                                                  │
│  ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐      │
│  │ Gateway │──▶│ Service1│──▶│ Service2│──▶│ Database│      │
│  └─────────┘   └─────────┘   └─────────┘   └─────────┘      │
│       │              │              │                          │
│       ▼              ▼              ▼                          │
│  ┌─────────────────────────────────────────┐                  │
│  │           Trace ID 串联                   │                  │
│  │  trace-id: abc123                        │                  │
│  │  span-id: s1 → s2 → s3 → s4            │                  │
│  └─────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 分布式追踪

```yaml
# Jaeger 配置
jaeger:
  collector:
    zipkin:
      host: localhost
  agent:
    host: localhost
    port: 6831
```

## 八、总结

监控告警核心要点：

1. **Prometheus**：指标收集
2. **Grafana**：可视化
3. **Alertmanager**：告警管理
4. **PromQL**：查询语言
5. **黄金指标**：延迟/流量/错误/饱和
6. **全链路**：分布式追踪

掌握这些，监控体系 so easy！

---

**推荐阅读**：
- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)

**如果对你有帮助，欢迎点赞收藏！**
