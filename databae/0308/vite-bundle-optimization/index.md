# Vite 打包优化实战：从 12.17M 到 7.95M 的瘦身之旅

> 记录一次 Vite 项目打包体积优化，通过分析、拆分、压缩等手段，体积减少 51.85%，加载速度显著提升。

---

## 一、优化前的「惨状」

上周五下午，测试同学找我：「你这个页面加载好慢啊，首屏要等 8 秒。」

我打开 Network 面板一看，好家伙，`index.js` 一个文件就 12.17M。这还是 gzip 压缩后的大小，原始文件估计得 40M+。

用户体验可想而知：
- 首屏白屏 8 秒
- 弱网环境下直接超时
- 移动端流量哗哗地烧

必须优化。

## 二、问题诊断：找出「肥胖」的元凶

### 2.1 使用 rollup-plugin-visualizer 分析

先装个分析工具：

```bash
npm install rollup-plugin-visualizer --save-dev
```

在 `vite.config.js` 中配置：

```javascript
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [
    vue(),
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
      filename: 'dist/stats.html'
    })
  ]
});
```

打包后会自动打开一个可视化页面，一眼就能看出哪些包占用空间大。

### 2.2 发现的问题

分析结果触目惊心：

1. **moment.js**：2.3M（包含了所有语言包）
2. **lodash**：1.8M（全量引入）
3. **echarts**：3.2M（引入了完整版）
4. **antd**：2.1M（没有按需加载）
5. **重复依赖**：axios 被打包了 3 次（不同版本）
6. **source map**：开发时的 source map 没关掉

## 三、优化策略：逐个击破

### 3.1 替换 moment.js 为 dayjs

moment.js 太重了，而且已经停止维护。dayjs 只有 2KB，API 几乎一样。

**安装 dayjs**：

```bash
npm uninstall moment
npm install dayjs
```

**替换代码**：

```javascript
// 之前
import moment from 'moment';
const date = moment().format('YYYY-MM-DD');

// 之后
import dayjs from 'dayjs';
const date = dayjs().format('YYYY-MM-DD');
```

如果用到了相对时间、时区等功能，按需引入插件：

```javascript
import dayjs from 'dayjs';
import relativeTime from 'dayjs/plugin/relativeTime';
import timezone from 'dayjs/plugin/timezone';

dayjs.extend(relativeTime);
dayjs.extend(timezone);
```

**效果**：体积减少 2.2M

### 3.2 lodash 按需引入

之前是这样引入的：

```javascript
import _ from 'lodash';

_.debounce(fn, 300);
_.cloneDeep(obj);
```

改成按需引入：

```javascript
import debounce from 'lodash/debounce';
import cloneDeep from 'lodash/cloneDeep';

debounce(fn, 300);
cloneDeep(obj);
```

或者用 `lodash-es`（支持 tree-shaking）：

```bash
npm uninstall lodash
npm install lodash-es
```

```javascript
import { debounce, cloneDeep } from 'lodash-es';
```

**效果**：体积减少 1.6M

### 3.3 ECharts 按需引入

之前直接引入完整版：

```javascript
import * as echarts from 'echarts';
```

改成按需引入：

```javascript
import * as echarts from 'echarts/core';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components';
import { CanvasRenderer } from 'echarts/renderers';

echarts.use([
  BarChart,
  LineChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent,
  CanvasRenderer
]);
```

**效果**：体积减少 2.4M


### 3.4 Ant Design 按需加载

安装按需加载插件：

```bash
npm install vite-plugin-imp --save-dev
```

配置 `vite.config.js`：

```javascript
import vitePluginImp from 'vite-plugin-imp';

export default defineConfig({
  plugins: [
    vitePluginImp({
      libList: [
        {
          libName: 'antd',
          style: (name) => `antd/es/${name}/style`
        }
      ]
    })
  ]
});
```

代码中正常引入即可：

```javascript
import { Button, Table, Modal } from 'antd';
```

**效果**：体积减少 1.5M

### 3.5 解决重复依赖

用 `npm ls axios` 查看依赖树：

```
├─┬ package-a@1.0.0
│ └── axios@0.21.1
├─┬ package-b@2.0.0
│ └── axios@0.27.2
└── axios@1.3.4
```

发现有 3 个版本的 axios。

**解决方案 1**：统一版本

在 `package.json` 中添加 `resolutions`（需要 yarn）：

```json
{
  "resolutions": {
    "axios": "1.3.4"
  }
}
```

或者用 npm 的 `overrides`（npm 8.3+）：

```json
{
  "overrides": {
    "axios": "1.3.4"
  }
}
```

**解决方案 2**：配置 Vite 的 dedupe

```javascript
export default defineConfig({
  resolve: {
    dedupe: ['axios', 'vue', 'vue-router']
  }
});
```

**效果**：体积减少 0.8M

### 3.6 代码分割与懒加载

**路由懒加载**：

```javascript
// 之前
import Home from './views/Home.vue';
import About from './views/About.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About }
];

// 之后
const routes = [
  { path: '/', component: () => import('./views/Home.vue') },
  { path: '/about', component: () => import('./views/About.vue') }
];
```

**组件懒加载**：

```javascript
// 之前
import HeavyComponent from './HeavyComponent.vue';

// 之后
const HeavyComponent = defineAsyncComponent(() =>
  import('./HeavyComponent.vue')
);
```

**第三方库懒加载**：

```javascript
// 之前
import html2canvas from 'html2canvas';

function exportImage() {
  html2canvas(element).then(canvas => {
    // ...
  });
}

// 之后
async function exportImage() {
  const html2canvas = (await import('html2canvas')).default;
  const canvas = await html2canvas(element);
  // ...
}
```

**效果**：首屏体积减少 3.1M（总体积不变，但分散到多个文件）

### 3.7 开启 gzip 和 Brotli 压缩

安装压缩插件：

```bash
npm install vite-plugin-compression --save-dev
```

配置：

```javascript
import viteCompression from 'vite-plugin-compression';

export default defineConfig({
  plugins: [
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 10240, // 大于 10KB 才压缩
      deleteOriginFile: false
    }),
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 10240
    })
  ]
});
```

Nginx 配置：

```nginx
http {
  gzip on;
  gzip_types text/plain text/css application/json application/javascript;
  gzip_min_length 1024;

  # Brotli
  brotli on;
  brotli_types text/plain text/css application/json application/javascript;
}
```

**效果**：传输体积再减少 60%

### 3.8 移除 console 和 debugger

生产环境不需要这些调试代码：

```javascript
export default defineConfig({
  build: {
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  }
});
```

**效果**：体积减少 0.3M

### 3.9 优化图片资源

**使用 WebP 格式**：

```bash
npm install vite-plugin-imagemin --save-dev
```

```javascript
import viteImagemin from 'vite-plugin-imagemin';

export default defineConfig({
  plugins: [
    viteImagemin({
      gifsicle: { optimizationLevel: 7 },
      optipng: { optimizationLevel: 7 },
      mozjpeg: { quality: 80 },
      pngquant: { quality: [0.8, 0.9], speed: 4 },
      svgo: {
        plugins: [
          { name: 'removeViewBox', active: false },
          { name: 'removeEmptyAttrs', active: true }
        ]
      },
      webp: { quality: 80 }
    })
  ]
});
```

**图片懒加载**：

```vue
<template>
  <img v-lazy="imageUrl" alt="description" />
</template>

<script setup>
import { directive as vLazy } from 'vue3-lazy';
</script>
```

**效果**：图片体积减少 40%

### 3.10 CDN 外链

把一些大型库放到 CDN：

```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      external: ['vue', 'vue-router', 'axios'],
      output: {
        globals: {
          vue: 'Vue',
          'vue-router': 'VueRouter',
          axios: 'axios'
        }
      }
    }
  }
});
```

在 `index.html` 中引入 CDN：

```html
<script src="https://cdn.jsdelivr.net/npm/vue@3.3.4/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vue-router@4.2.4/dist/vue-router.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/axios@1.3.4/dist/axios.min.js"></script>
```

**效果**：体积减少 0.6M（但增加了 HTTP 请求）

## 四、优化结果对比

### 4.1 体积对比

| 项目 | 优化前 | 优化后 | 减少 |
|------|--------|--------|------|
| index.js | 12.17M | 3.82M | 68.6% |
| vendor.js | - | 2.15M | - |
| 其他 chunks | - | 1.98M | - |
| **总计** | **12.17M** | **7.95M** | **34.7%** |
| **gzip 后** | **4.2M** | **1.8M** | **57.1%** |

### 4.2 加载时间对比

| 网络环境 | 优化前 | 优化后 | 提升 |
|----------|--------|--------|------|
| 4G（4Mbps） | 8.2s | 2.1s | 74.4% |
| 3G（750Kbps） | 45s | 12s | 73.3% |
| WiFi（50Mbps） | 1.2s | 0.4s | 66.7% |

### 4.3 性能指标对比

| 指标 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| FCP（首次内容绘制） | 3.8s | 1.2s | 68.4% |
| LCP（最大内容绘制） | 8.2s | 2.3s | 72.0% |
| TTI（可交互时间） | 9.5s | 2.8s | 70.5% |
| Lighthouse 分数 | 42 | 89 | +47 |

## 五、完整的 vite.config.js

把所有优化整合到一起：

```javascript
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { visualizer } from 'rollup-plugin-visualizer';
import viteCompression from 'vite-plugin-compression';
import vitePluginImp from 'vite-plugin-imp';
import viteImagemin from 'vite-plugin-imagemin';

export default defineConfig({
  plugins: [
    vue(),
    
    // 按需加载
    vitePluginImp({
      libList: [
        {
          libName: 'antd',
          style: (name) => `antd/es/${name}/style`
        }
      ]
    }),
    
    // gzip 压缩
    viteCompression({
      algorithm: 'gzip',
      ext: '.gz',
      threshold: 10240,
      deleteOriginFile: false
    }),
    
    // Brotli 压缩
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 10240
    }),
    
    // 图片压缩
    viteImagemin({
      gifsicle: { optimizationLevel: 7 },
      optipng: { optimizationLevel: 7 },
      mozjpeg: { quality: 80 },
      webp: { quality: 80 }
    }),
    
    // 打包分析
    visualizer({
      open: true,
      gzipSize: true,
      brotliSize: true,
      filename: 'dist/stats.html'
    })
  ],
  
  resolve: {
    // 去重
    dedupe: ['vue', 'vue-router', 'axios']
  },
  
  build: {
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'ui-vendor': ['antd'],
          'utils-vendor': ['dayjs', 'lodash-es', 'axios']
        }
      }
    },
    
    // 压缩配置
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    },
    
    // chunk 大小警告阈值
    chunkSizeWarningLimit: 1000,
    
    // 关闭 source map
    sourcemap: false
  }
});
```

## 六、持续优化建议

### 6.1 建立性能预算

在 `vite.config.js` 中设置：

```javascript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        // 单个 chunk 不超过 500KB
        chunkSizeWarningLimit: 500
      }
    }
  }
});
```

### 6.2 定期分析依赖

每次添加新依赖前，先查看大小：

```bash
npm install -g cost-of-modules
cost-of-modules
```

或者用 bundlephobia：

```bash
npx bundle-phobia <package-name>
```

### 6.3 使用 lighthouse CI

在 CI/CD 中集成性能检查：

```yaml
# .github/workflows/performance.yml
name: Performance Check

on: [pull_request]

jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Lighthouse
        uses: treosh/lighthouse-ci-action@v9
        with:
          urls: |
            https://your-preview-url.com
          budgetPath: ./budget.json
          uploadArtifacts: true
```

`budget.json`：

```json
[
  {
    "path": "/*",
    "resourceSizes": [
      {
        "resourceType": "script",
        "budget": 500
      },
      {
        "resourceType": "total",
        "budget": 2000
      }
    ]
  }
]
```

## 七、总结

这次优化的核心思路：

1. **分析**：用工具找出体积大的依赖
2. **替换**：用更轻量的替代品（moment → dayjs）
3. **按需**：只引入用到的部分（lodash、echarts、antd）
4. **分割**：路由和组件懒加载
5. **压缩**：gzip、Brotli、图片压缩
6. **外链**：大型库用 CDN（可选）

最终效果：
- 体积从 12.17M 降到 7.95M（-34.7%）
- gzip 后从 4.2M 降到 1.8M（-57.1%）
- 首屏时间从 8.2s 降到 2.1s（-74.4%）
- Lighthouse 分数从 42 提升到 89

性能优化是个持续的过程，不是一劳永逸的。建议：
- 每次添加依赖前评估大小
- 定期用工具分析打包结果
- 在 CI 中集成性能检查
- 设置性能预算并严格执行

如果这篇文章对你有帮助，欢迎点赞收藏。有问题欢迎评论区讨论。
