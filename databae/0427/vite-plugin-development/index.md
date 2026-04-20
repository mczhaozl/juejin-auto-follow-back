# Vite Plugin 开发完全指南

> 从零开始学习 Vite Plugin 开发，掌握核心概念和开发技巧。

## 一、Vite Plugin 概述

Vite Plugin 基于 Rollup Plugin 设计，提供了更强大的开发时能力。

### 1.1 Vite Plugin 的特点

- 兼容 Rollup Plugin
- 提供 Vite 特有钩子
- 开发与生产环境一致
- 支持热更新

### 1.2 Plugin 结构

```javascript
// my-plugin.js
export default function myPlugin(options = {}) {
  return {
    name: 'my-plugin', // 必须，唯一标识
    
    // Vite 特有钩子
    config(config, env) {},
    configResolved(config) {},
    configureServer(server) {},
    transformIndexHtml(html) {},
    handleHotUpdate(ctx) {},
    
    // Rollup 钩子
    options(options) {},
    buildStart(options) {},
    resolveId(source, importer) {},
    load(id) {},
    transform(code, id) {},
    buildEnd(error) {},
    generateBundle(outputOptions, bundle) {},
    writeBundle(outputOptions, bundle) {},
    closeBundle() {}
  };
}
```

---

## 二、第一个 Vite Plugin

### 2.1 创建基础 Plugin

```javascript
// plugins/vite-plugin-example.js
export default function examplePlugin() {
  return {
    name: 'vite-plugin-example',
    
    config(config) {
      console.log('config hook');
      return {
        define: {
          __PLUGIN_VERSION__: '"1.0.0"'
        }
      };
    },
    
    configResolved(config) {
      console.log('configResolved hook');
    },
    
    transform(code, id) {
      console.log('transform:', id);
      return code;
    }
  };
}
```

### 2.2 在 Vite 配置中使用

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import examplePlugin from './plugins/vite-plugin-example';

export default defineConfig({
  plugins: [
    examplePlugin()
  ]
});
```

---

## 三、核心钩子详解

### 3.1 config 和 configResolved

```javascript
export default function configPlugin() {
  return {
    name: 'config-plugin',
    
    config(config, { command, mode }) {
      console.log('Command:', command); // 'serve' or 'build'
      console.log('Mode:', mode); // 'development' or 'production'
      
      // 修改配置
      return {
        server: {
          port: 3000
        },
        build: {
          outDir: 'dist'
        }
      };
    },
    
    configResolved(config) {
      // 读取最终配置
      console.log('Final config:', config);
    }
  };
}
```

### 3.2 configureServer 开发服务器

```javascript
export default function devServerPlugin() {
  return {
    name: 'dev-server-plugin',
    
    configureServer(server) {
      // 添加中间件
      server.middlewares.use((req, res, next) => {
        console.log('Request:', req.url);
        next();
      });
      
      // 自定义路由
      server.middlewares.use('/api/hello', (req, res) => {
        res.end('Hello from Vite Plugin!');
      });
      
      // 监听 WebSocket 事件
      server.ws.on('connection', (ws) => {
        ws.send('Welcome!');
      });
    }
  };
}
```

### 3.3 transformIndexHtml 转换 HTML

```javascript
export default function htmlPlugin() {
  return {
    name: 'html-plugin',
    
    transformIndexHtml(html) {
      return html.replace(
        '<head>',
        `<head>
          <meta name="plugin-version" content="1.0.0">
        `
      );
    }
    
    // 或者返回对象
    transformIndexHtml(html) {
      return {
        html,
        tags: [
          {
            tag: 'script',
            attrs: { src: '/custom-script.js' },
            injectTo: 'head'
          }
        ]
      };
    }
  };
}
```

---

## 四、Rollup 钩子在 Vite 中的应用

### 4.1 resolveId 解析模块

```javascript
export default function resolvePlugin() {
  return {
    name: 'resolve-plugin',
    
    resolveId(source, importer) {
      if (source === 'virtual:my-module') {
        // 标记为虚拟模块
        return '\0virtual:my-module';
      }
      return null; // 让其他插件处理
    }
  };
}
```

### 4.2 load 加载模块

```javascript
export default function loadPlugin() {
  return {
    name: 'load-plugin',
    
    load(id) {
      if (id === '\0virtual:my-module') {
        return `
          export const message = 'Hello from virtual module!';
          export const version = '1.0.0';
        `;
      }
      return null;
    }
  };
}
```

### 4.3 transform 转换代码

```javascript
export default function transformPlugin() {
  return {
    name: 'transform-plugin',
    
    transform(code, id) {
      // 只处理 .js 文件
      if (!id.endsWith('.js')) return;
      
      // 简单的代码转换
      const transformedCode = code.replace(
        /console\.log\(/g,
        'console.log("[Plugin] "'
      );
      
      return {
        code: transformedCode,
        map: null // sourcemap
      };
    }
  };
}
```

---

## 五、实战案例一：虚拟模块

### 5.1 创建虚拟模块 Plugin

```javascript
// plugins/vite-plugin-virtual.js
export default function virtualModulePlugin() {
  const virtualModuleId = 'virtual:env-info';
  const resolvedVirtualModuleId = '\0' + virtualModuleId;

  return {
    name: 'vite-plugin-virtual',

    resolveId(id) {
      if (id === virtualModuleId) {
        return resolvedVirtualModuleId;
      }
    },

    load(id) {
      if (id === resolvedVirtualModuleId) {
        return `
          export const NODE_ENV = '${process.env.NODE_ENV || 'development'}';
          export const VERSION = '${process.env.npm_package_version || '1.0.0'}';
          export const BUILD_TIME = '${new Date().toISOString()}';
        `;
      }
    }
  };
}
```

### 5.2 使用虚拟模块

```javascript
// src/main.js
import { NODE_ENV, VERSION, BUILD_TIME } from 'virtual:env-info';

console.log('Environment:', NODE_ENV);
console.log('Version:', VERSION);
console.log('Build Time:', BUILD_TIME);
```

---

## 六、实战案例二：处理自定义文件

### 6.1 处理 .yaml 文件

```javascript
// plugins/vite-plugin-yaml.js
import yaml from 'js-yaml';

export default function yamlPlugin() {
  return {
    name: 'vite-plugin-yaml',
    
    transform(code, id) {
      if (id.endsWith('.yaml') || id.endsWith('.yml')) {
        try {
          const data = yaml.load(code);
          return {
            code: `export default ${JSON.stringify(data)};`
          };
        } catch (e) {
          this.error(e.message);
        }
      }
    }
  };
}
```

### 6.2 使用 YAML 文件

```yaml
# config.yaml
app:
  name: My App
  version: 1.0.0
database:
  host: localhost
  port: 5432
```

```javascript
import config from './config.yaml';

console.log(config.app.name);
console.log(config.database.port);
```

---

## 七、实战案例三：热更新处理

### 7.1 自定义 HMR

```javascript
// plugins/vite-plugin-hmr.js
export default function hmrPlugin() {
  return {
    name: 'vite-plugin-hmr',
    
    handleHotUpdate({ file, server, modules }) {
      console.log('File changed:', file);
      
      // 自定义更新逻辑
      if (file.endsWith('.special')) {
        server.ws.send({
          type: 'custom',
          event: 'special-update',
          data: { file }
        });
        return []; // 不触发默认更新
      }
      
      return modules; // 默认行为
    }
  };
}
```

### 7.2 客户端接收 HMR

```javascript
// src/hmr-client.js
if (import.meta.hot) {
  import.meta.hot.on('special-update', (data) => {
    console.log('Special update:', data);
    // 自定义更新处理
  });
}
```

---

## 八、插件开发技巧

### 8.1 区分开发与生产环境

```javascript
export default function envPlugin() {
  let isDev;

  return {
    name: 'env-plugin',
    
    configResolved(config) {
      isDev = config.command === 'serve';
    },
    
    transform(code, id) {
      if (isDev) {
        // 开发环境逻辑
        return code + '\nconsole.log("Dev only");';
      } else {
        // 生产环境逻辑
        return code;
      }
    }
  };
}
```

### 8.2 插件排序

```javascript
// vite.config.js
export default defineConfig({
  plugins: [
    pluginA(), // 先执行
    pluginB(), // 后执行
  ]
});

// 使用 enforce
export default function plugin() {
  return {
    name: 'my-plugin',
    enforce: 'pre', // 'pre' | 'post' | undefined
  };
}
```

---

## 九、调试与测试

### 9.1 调试 Plugin

```javascript
// 使用 debug
import createDebug from 'debug';
const debug = createDebug('vite-plugin-example');

export default function debugPlugin() {
  return {
    name: 'debug-plugin',
    
    transform(code, id) {
      debug('Transforming:', id);
      return code;
    }
  };
}
```

### 9.2 测试 Plugin

```javascript
// test/plugin.test.js
import { createServer } from 'vite';
import myPlugin from '../index.js';

test('plugin works', async () => {
  const server = await createServer({
    plugins: [myPlugin()]
  });
  
  // 测试逻辑
  
  await server.close();
});
```

---

## 十、最佳实践

1. **命名规范**：使用 `vite-plugin-` 前缀
2. **TypeScript**：使用 TS 开发，提供类型
3. **文档**：完善的 README
4. **测试**：提供单元测试
5. **兼容性**：考虑不同 Vite 版本

---

## 十一、总结

Vite Plugin 开发是 Vite 生态的重要部分。掌握 Plugin 开发，可以定制化 Vite，满足项目需求。

希望这篇文章对你有帮助！
