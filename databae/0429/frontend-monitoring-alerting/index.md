# 前端监控与告警系统完全指南：从原理到实现

## 一、前端监控概述

### 1.1 监控指标
- **错误监控**：JS 异常、资源加载失败
- **性能监控**：FP、FCP、LCP、FID、CLS
- **行为监控**：用户操作、PV、UV
- **业务监控**：转化率、关键指标

---

## 二、错误监控

### 2.1 JS 错误捕获

```javascript
window.onerror = function(message, source, lineno, colno, error) {
  reportError({
    type: 'js_error',
    message,
    source,
    lineno,
    colno,
    stack: error?.stack,
    url: window.location.href
  });
  return true;
};

window.addEventListener('unhandledrejection', function(event) {
  reportError({
    type: 'unhandled_rejection',
    message: event.reason?.message || String(event.reason),
    stack: event.reason?.stack,
    url: window.location.href
  });
});
```

### 2.2 React 错误边界

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  
  componentDidCatch(error, info) {
    reportError({
      type: 'react_error',
      message: error.message,
      stack: error.stack,
      componentStack: info.componentStack
    });
  }
  
  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong</h1>;
    }
    return this.props.children;
  }
}
```

### 2.3 资源加载失败

```javascript
window.addEventListener('error', function(event) {
  const target = event.target;
  if (target instanceof HTMLScriptElement || 
      target instanceof HTMLLinkElement || 
      target instanceof HTMLImageElement) {
    
    reportError({
      type: 'resource_error',
      tagName: target.tagName,
      url: target.src || target.href,
      pageUrl: window.location.href
    });
  }
}, true);
```

---

## 三、性能监控

### 3.1 Web Vitals

```javascript
import { getCLS, getFID, getLCP, getFCP, getTTFB } from 'web-vitals';

function sendToAnalytics(metric) {
  reportPerformance({
    name: metric.name,
    value: metric.value,
    id: metric.id
  });
}

getCLS(sendToAnalytics);
getFID(sendToAnalytics);
getLCP(sendToAnalytics);
getFCP(sendToAnalytics);
getTTFB(sendToAnalytics);
```

### 3.2 Navigation Timing

```javascript
function getPerformanceData() {
  const timing = performance.timing;
  
  return {
    domReady: timing.domContentLoadedEventEnd - timing.navigationStart,
    loadComplete: timing.loadEventEnd - timing.navigationStart,
    ttfb: timing.responseStart - timing.navigationStart,
    dns: timing.domainLookupEnd - timing.domainLookupStart,
    tcp: timing.connectEnd - timing.connectStart,
    request: timing.responseEnd - timing.requestStart
  };
}

window.addEventListener('load', () => {
  const perfData = getPerformanceData();
  reportPerformance(perfData);
});
```

---

## 四、用户行为监控

### 4.1 PV/UV

```javascript
function reportPageView() {
  reportEvent({
    type: 'pageview',
    url: window.location.href,
    referrer: document.referrer,
    title: document.title,
    timestamp: Date.now()
  });
}

window.addEventListener('load', reportPageView);
```

### 4.2 用户点击

```javascript
document.addEventListener('click', function(event) {
  const target = event.target;
  reportEvent({
    type: 'click',
    tagName: target.tagName,
    id: target.id,
    className: target.className,
    text: target.textContent?.slice(0, 100),
    x: event.clientX,
    y: event.clientY
  });
});
```

---

## 五、数据上报

### 5.1 上报实现

```javascript
class Reporter {
  constructor(endpoint) {
    this.endpoint = endpoint;
    this.queue = [];
    this.flushTimer = null;
  }
  
  send(data) {
    this.queue.push(data);
    this.scheduleFlush();
  }
  
  scheduleFlush() {
    if (this.flushTimer) return;
    
    this.flushTimer = setTimeout(() => {
      this.flush();
      this.flushTimer = null;
    }, 1000);
  }
  
  flush() {
    if (this.queue.length === 0) return;
    
    const data = this.queue.splice(0);
    
    if (navigator.sendBeacon) {
      navigator.sendBeacon(this.endpoint, JSON.stringify(data));
    } else {
      fetch(this.endpoint, {
        method: 'POST',
        body: JSON.stringify(data),
        keepalive: true
      });
    }
  }
}

const reporter = new Reporter('https://api.example.com/report');
```

### 5.2 采样

```javascript
function shouldSample(rate = 0.1) {
  return Math.random() < rate;
}

if (shouldSample()) {
  reporter.send(data);
}
```

---

## 六、服务端接收

```javascript
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

app.post('/report', (req, res) => {
  const data = req.body;
  
  // 存储到数据库
  saveToDatabase(data);
  
  // 检查告警
  checkAlerts(data);
  
  res.sendStatus(204);
});

app.listen(3000);
```

---

## 七、告警系统

```javascript
const ALERT_RULES = [
  {
    type: 'js_error',
    threshold: 10,
    window: 60000 // 1分钟
  },
  {
    type: 'slow_page',
    threshold: 5000, // 5秒
    window: 60000
  }
];

function checkAlerts(data) {
  ALERT_RULES.forEach(rule => {
    if (matchesRule(data, rule)) {
      const count = getRecentCount(rule);
      if (count >= rule.threshold) {
        sendAlert(rule, count);
      }
    }
  });
}

function sendAlert(rule, count) {
  const message = `Alert: ${rule.type} count ${count} exceeds threshold ${rule.threshold}`;
  // 发送到 Slack、邮件等
  console.log(message);
}
```

---

## 八、可视化 Dashboard

```jsx
function Dashboard() {
  const [errors, setErrors] = useState([]);
  const [performance, setPerformance] = useState({});
  
  useEffect(() => {
    fetchErrors().then(setErrors);
    fetchPerformance().then(setPerformance);
  }, []);
  
  return (
    <div>
      <h1>Monitoring Dashboard</h1>
      
      <div className="charts">
        <ErrorChart data={errors} />
        <PerformanceChart data={performance} />
      </div>
    </div>
  );
}
```

---

## 九、Source Map 定位

```javascript
const sourceMap = require('source-map');

async function getOriginalPosition(stackLine) {
  const consumer = await new sourceMap.SourceMapConsumer(sourceMapContent);
  const result = consumer.originalPositionFor({
    line: stackLine.line,
    column: stackLine.column
  });
  return result;
}
```

---

## 十、最佳实践

1. 实现完整的错误捕获（JS、Promise、资源）
2. 监控 Web Vitals 性能指标
3. 合理使用采样率减少数据量
4. 使用 beacon 上报保证可靠性
5. 实现告警和可视化系统

---

## 十一、总结

前端监控能帮助我们及时发现和解决问题，提升用户体验和应用质量。
