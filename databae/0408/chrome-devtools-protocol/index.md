# Chrome DevTools Protocol 实战：利用 CDP 实现页面自动化与性能分析

> 深入讲解 Chrome DevTools Protocol 的使用方法，通过 CDP 实现页面自动化、性能监控、截图等高级功能。

## 一、什么是 CDP

**Chrome DevTools Protocol (CDP)** 是 Chrome 浏览器提供的调试协议，允许开发者远程控制浏览器行为。

### 1.1 CDP 能做什么

- 页面自动化操作
- 性能监控与分析
- 网络请求拦截
- 页面截图
- DOM 操作
- JavaScript 调试

### 1.2 连接方式

```javascript
// 通过 Puppeteer/Playwright 连接
const browser = await puppeteer.launch();
const page = browser.newPage();

// 或直接连接 Chrome
const client = await CDP({ port: 9222 });
```

## 二、基础操作

### 2.1 启动 Chrome 远程调试

```bash
# macOS
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --no-first-run \
  --no-default-browser-check

# Windows
chrome.exe --remote-debugging-port=9222
```

### 2.2 Puppeteer 基础

```javascript
const puppeteer = require('puppeteer');

async function main() {
  const browser = await puppeteer.launch({
    headless: false
  });
  
  const page = await browser.newPage();
  await page.goto('https://juejin.cn');
  
  const title = await page.title();
  console.log('页面标题:', title);
  
  await browser.close();
}

main();
```

## 三、页面操作

### 3.1 导航控制

```javascript
async function navigate() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // 基本导航
  await page.goto('https://example.com', {
    waitUntil: 'networkidle0', // 等待网络空闲
    timeout: 30000
  });
  
  // 等待元素
  await page.waitForSelector('.content');
  
  // 点击导航
  await page.click('a.next-page');
  await page.waitForNavigation();
  
  await browser.close();
}
```

### 3.2 DOM 操作

```javascript
async function domOperations() {
  const page = await browser.newPage();
  
  // 获取元素属性
  const href = await page.$eval('a.logo', el => el.href);
  
  // 填写表单
  await page.type('#search-input', 'React 教程');
  
  // 点击按钮
  await page.click('#submit-btn');
  
  // 执行自定义 JS
  await page.evaluate(() => {
    document.body.style.backgroundColor = 'pink';
  });
  
  // 获取页面数据
  const data = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('.item'))
      .map(item => item.textContent);
  });
  
  console.log(data);
}
```

### 3.3 等待机制

```javascript
// 等待元素出现
await page.waitForSelector('.modal', { visible: true });

// 等待函数返回 true
await page.waitForFunction(() => document.readyState === 'complete');

// 等待超时
await page.waitForTimeout(2000);

// 等待网络请求
await page.waitForResponse(response => 
  response.url().includes('/api/data') && response.status() === 200
);
```

## 四、网络拦截

### 4.1 请求拦截

```javascript
async function interceptRequests() {
  const page = await browser.newPage();
  
  // 拦截请求
  await page.setRequestInterception(true);
  
  page.on('request', request => {
    if (request.url().includes('analytics')) {
      request.abort(); // 阻止分析请求
    } else if (request.url().endsWith('.json')) {
      request.continue(); // 继续请求
    }
  });
  
  await page.goto('https://example.com');
}
```

### 4.2 响应修改

```javascript
await page.setRequestInterception(true);

page.on('request', request => {
  request.continue();
});

page.on('response', response => {
  if (response.url().includes('/api/user')) {
    console.log('原始响应:', response.text());
  }
});
```

### 4.3 模拟慢网络

```javascript
const client = await page.target().createCDPSession();
await client.send('Network.emulateNetworkConditions', {
  offline: false,
  downloadThroughput: 50 * 1024, // 50KB/s
  uploadThroughput: 50 * 1024,
  latency: 100 // 100ms 延迟
});
```

## 五、性能分析

### 5.1 性能指标

```javascript
async function getPerformanceMetrics() {
  const client = await page.target().createCDPSession();
  
  // 启用性能收集
  await client.send('Performance.enable');
  
  // 导航
  await page.goto('https://example.com');
  
  // 获取指标
  const metrics = await client.send('Performance.getMetrics');
  
  console.log('性能指标:', metrics.metrics);
}
```

### 5.2 关键指标

```javascript
async function getCoreWebVitals() {
  const metrics = await page.evaluate(() => {
    return new Promise(resolve => {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const vitals = {};
        
        entries.forEach(entry => {
          vitals[entry.name] = entry.value;
        });
        
        resolve(vitals);
      }).observe({ entryTypes: ['lcp', 'fid', 'cls'] });
    });
  });
  
  console.log('Core Web Vitals:', metrics);
}
```

### 5.3 JavaScript 性能

```javascript
const client = await page.target().createCDPSession();

await client.send('Profiler.start');

// 执行代码
await page.goto('https://example.com');
await page.click('#button');

const profile = await client.send('Profiler.stop');
console.log('CPU Profile:', profile);
```

## 六、截图功能

### 6.1 页面截图

```javascript
// 整页截图
await page.screenshot({
  path: 'page.png',
  fullPage: true
});

// 视口截图
await page.screenshot({
  path: 'viewport.png'
});
```

### 6.2 元素截图

```javascript
const element = await page.$('.content');
await element.screenshot({
  path: 'element.png'
});
```

### 6.3 设备截图

```javascript
// 模拟移动设备
await page.setViewport({
  width: 375,
  height: 812,
  isMobile: true,
  deviceScaleFactor: 2
});

await page.screenshot({
  path: 'mobile.png',
  fullPage: true
});
```

## 七、调试功能

### 7.1 JavaScript 调试

```javascript
// 设置断点
const client = await page.target().createCDPSession();
await client.send('Debugger.enable');

await client.send('Debugger.setBreakpointByUrl', {
  url: 'https://example.com/app.js',
  lineNumber: 10
});

page.on('paused', () => console.log('Paused!'));

// 注入脚本
await page.evaluate(() => {
  debugger;
});
```

### 7.2 控制台监听

```javascript
page.on('console', msg => {
  console.log('Console:', msg.type(), msg.text());
});

page.on('pageerror', error => {
  console.error('Page Error:', error.message);
});
```

### 7.3 网络监控

```javascript
page.on('request', request => {
  console.log('Request:', request.url());
});

page.on('response', response => {
  console.log('Response:', response.url(), response.status());
});

page.on('requestfailed', request => {
  console.log('Failed:', request.url(), request.failure().errorText);
});
```

## 八、实战案例

### 8.1 自动化测试

```javascript
async function runTests() {
  const browser = await puppeteer.launch();
  const page = await browser.newPage();
  
  // 登录
  await page.goto('https://app.example.com/login');
  await page.type('#email', 'test@example.com');
  await page.type('#password', 'password');
  await page.click('#login');
  
  // 验证
  await page.waitForSelector('.dashboard');
  console.log('✓ 登录成功');
  
  // 验证数据
  const data = await page.$eval('.data-count', el => el.textContent);
  if (data !== '0') {
    console.log('✓ 数据加载成功');
  }
  
  await browser.close();
}
```

### 8.2 网页截图服务

```javascript
async function generateScreenshot(url, options = {}) {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  
  await page.setViewport({
    width: options.width || 1280,
    height: options.height || 800
  });
  
  await page.goto(url, { waitUntil: 'networkidle0' });
  
  const buffer = await page.screenshot({
    type: options.format || 'png',
    fullPage: options.fullPage || false
  });
  
  await browser.close();
  return buffer;
}
```

### 8.3 SEO 检测

```javascript
async function seoAnalysis(url) {
  const page = await browser.newPage();
  await page.goto(url);
  
  const seo = await page.evaluate(() => {
    return {
      title: document.title,
      meta: {
        description: document.querySelector('meta[name="description"]')?.content,
        keywords: document.querySelector('meta[name="keywords"]')?.content
      },
      h1: Array.from(document.querySelectorAll('h1')).map(h => h.textContent),
      images: Array.from(document.querySelectorAll('img')).map(img => ({
        src: img.src,
        alt: img.alt,
        hasAlt: !!img.alt
      })),
      links: document.querySelectorAll('a').length
    };
  });
  
  console.log('SEO 分析:', seo);
  return seo;
}
```

## 九、总结

CDP/Puppeteer 强大功能：

1. **页面自动化**：模拟用户操作
2. **网络拦截**：修改请求/响应
3. **性能分析**：获取各项指标
4. **截图功能**：生成页面快照
5. **调试能力**：断点、监控

掌握这些技能，可以构建自动化测试、性能监控、截图服务等应用！

---

**推荐阅读**：
- [Puppeteer 官方文档](https://pptr.dev)
- [CDP 协议文档](https://chromedevtools.github.io/devtools-protocol/)

**如果对你有帮助，欢迎点赞收藏！**
