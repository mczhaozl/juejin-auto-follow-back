# ELK 完全指南：日志收集与分析实战

> 深入讲解 ELK Stack，包括 Elasticsearch、Logstash、Kibana 的安装配置，以及日志收集、搜索分析、可视化仪表盘的实际应用。

## 一、ELK 概述

### 1.1 什么是 ELK

日志分析三剑客：

```
┌─────────────────────────────────────────────────────────────┐
│                        ELK Stack                            │
│  ┌─────────┐    ┌────────────┐    ┌─────────────┐         │
│  │ Logstash│───▶│Elasticsearch│◀───│  Kibana     │         │
│  │ (收集)  │    │  (存储/搜索) │    │  (可视化)   │         │
│  └─────────┘    └─────────────┘    └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 组件介绍

| 组件 | 功能 |
|------|------|
| Logstash | 日志收集、过滤、转换 |
| Elasticsearch | 分布式搜索和分析引擎 |
| Kibana | 数据可视化 |
| Beats | 轻量级日志收集器 |

## 二、Elasticsearch

### 2.1 安装

```bash
# Docker 安装
docker run -d --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  elasticsearch:8.11.0
```

### 2.2 核心概念

| 概念 | 说明 |
|------|------|
| Index | 索引（类似数据库） |
| Document | 文档（类似记录） |
| Shard | 分片 |
| Replica | 副本 |

### 2.3 API 操作

```bash
# 创建索引
curl -X PUT "localhost:9200/logs" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  }
}
'

# 索引文档
curl -X POST "localhost:9200/logs/_doc" -H 'Content-Type: application/json' -d'
{
  "timestamp": "2024-01-01T10:00:00",
  "level": "INFO",
  "message": "User logged in",
  "user_id": 123
}
'

# 搜索
curl -X GET "localhost:9200/logs/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "level": "ERROR"
    }
  }
}
'
```

### 2.4 DSL 查询

```json
{
  "query": {
    "bool": {
      "must": [
        { "match": { "level": "ERROR" } }
      ],
      "filter": {
        "range": {
          "timestamp": {
            "gte": "now-1h"
          }
        }
      }
    }
  }
}
```

## 三、Logstash

### 3.1 安装

```bash
# Docker 安装
docker run -d --name logstash \
  -p 5044:5044 \
  -v /path/to/logstash.conf:/usr/share/logstash/pipeline/logstash.conf \
  logstash:8.11.0
```

### 3.2 配置

```conf
input {
  beats {
    port => 5044
  }
  
  file {
    path => "/var/log/syslog"
    type => "syslog"
  }
}

filter {
  # JSON 解析
  json {
    source => "message"
  }
  
  # Grok 解析
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
  }
  
  # 日期解析
  date {
    match => [ "timestamp", "ISO8601" ]
    target => "@timestamp"
  }
  
  # 字段处理
  mutate {
    remove_field => [ "host" ]
    lowercase => [ "level" ]
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
  
  stdout {
    codec => rubydebug
  }
}
```

### 3.3 管道配置

```conf
# input -> filter -> output
input { stdin {} }

filter {
  mutate { add_field => { "source" => "stdin" } }
}

output {
  elasticsearch { hosts => ["localhost:9200"] }
}
```

## 四、Kibana

### 4.1 安装

```bash
# Docker 安装
docker run -d --name kibana \
  -p 5601:5601 \
  -e ELASTICSEARCH_HOSTS=http://elasticsearch:9200 \
  kibana:8.11.0
```

### 4.2 Discover

```
┌─────────────────────────────────────────────────────────────┐
│  Kibana - Discover                                          │
├─────────────────────────────────────────────────────────────┤
│  [搜索框] level:ERROR                                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ @timestamp    │ level │ message                    │    │
│  ├─────────────────────────────────────────────────────┤    │
│  │ 10:00:00     │ INFO  │ User login                  │    │
│  │ 10:01:00     │ ERROR │ Connection failed           │    │
│  │ 10:02:00     │ DEBUG │ Processing request          │    │
│  └─────────────────────────────────────────────────────┘    │
│  [时间选择器] [刷新] [保存]                                  │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 可视化

```javascript
// 1. 创建柱状图
//    - 选择索引: logs-*
//    - X轴: terms level
//    - Y轴: count

// 2. 创建折线图
//    - X轴: date histogram @timestamp
//    - Y轴: count

// 3. 创建饼图
//    - Slice: terms status_code
```

### 4.4 Dashboard

```json
{
  "title": "应用日志仪表盘",
  "panels": [
    {
      "type": "visualization",
      "title": "错误趋势",
      "id": "error-trend"
    },
    {
      "type": "visualization", 
      "title": "日志级别分布",
      "id": "level-distribution"
    },
    {
      "type": "visualization",
      "title": "Top 10 错误",
      "id": "top-errors"
    }
  ]
}
```

## 五、Filebeat

### 5.1 安装

```bash
# 安装
curl -L -O https://artifacts.elastic.co/downloads/beats/filebeat/filebeat-8.11.0-linux-x86_64.tar.gz
tar -xzf filebeat-8.11.0-linux-x86_64.tar.gz
```

### 5.2 配置

```yaml
# filebeat.yml
filebeat.inputs:
  - type: log
    enabled: true
    paths:
      - /var/log/*.log
      - /var/log/syslog
    
  - type: json
    enabled: true
    paths:
      - /var/log/app/*.json
    json.keys_under_root: true
    json.add_error_key: true

output.logstash:
  hosts: ["logstash:5044"]

logging.json: true
```

### 5.3 模块

```bash
# 启用 Nginx 模块
filebeat modules enable nginx

# 配置
filebeat modules list
```

## 六、实战案例

### 6.1 微服务日志收集

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Service 1   │    │  Service 2   │    │  Service 3   │
│  Filebeat    │    │  Filebeat    │    │  Filebeat    │
└──────┬───────┘    └──────┬───────┘    └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ▼
                    ┌──────────────┐
                    │   Logstash   │
                    │  (处理/过滤) │
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │Elasticsearch │
                    │ (存储/索引)  │
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │   Kibana    │
                    │  (可视化)    │
                    └──────────────┘
```

### 6.2 日志分析场景

```json
// 1. 错误日志分析
{
  "query": {
    "bool": {
      "must": [
        { "term": { "level": "ERROR" } }
      ],
      "filter": {
        "range": {
          "@timestamp": { "gte": "now-24h" }
        }
      }
    }
  },
  "aggs": {
    "error_types": {
      "terms": { "field": "error_type" }
    },
    "error_trend": {
      "date_histogram": {
        "field": "@timestamp",
        "calendar_interval": "hour"
      }
    }
  }
}
```

## 七、总结

ELK Stack 核心要点：

1. **Elasticsearch**：分布式搜索引擎
2. **Logstash**：日志收集处理
3. **Kibana**：可视化分析
4. **Filebeat**：轻量收集
5. **DSL**：查询语法
6. **Dashboard**：仪表盘

掌握这些，日志分析 so easy！

---

**推荐阅读**：
- [Elastic 官方文档](https://www.elastic.co/guide/index.html)

**如果对你有帮助，欢迎点赞收藏！**
