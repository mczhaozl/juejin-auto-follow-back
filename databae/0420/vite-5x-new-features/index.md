# Vite 5.x 新特性完全指南：性能、稳定性与新功能解析

Vite 5.x 是 Vite 生态系统的又一次重大升级，带来了性能提升、稳定性改进以及一系列新功能。本文将深入解析 Vite 5.x 的核心特性，帮助你充分利用这些新能力。

## 一、Vite 5.x 概述

Vite 5.x 于 2023 年 11 月发布，是 Vite 4.x 的后续版本。这个版本主要聚焦于：

1. **性能优化**：进一步提升开发服务器和构建速度
2. **稳定性改进**：修复大量问题，提升健壮性
3. **新功能**：引入有用的新特性
4. **依赖升级**：升级到最新的核心依赖

## 二、核心改进

### 1. 性能提升

Vite 5.x 在性能方面有显著提升：

#### 1.1 更快的依赖预构建

Vite 5.x 优化了依赖预构建的策略，减少了重复构建的情况。

```javascript
// vite.config.js
export default {
  optimizeDeps: {
    include: ['react', 'react-dom', 'lodash'],
    exclude: ['some-local-package'],
    force: false, // 强制重新构建
    esbuildOptions: {
      // esbuild 配置
    }
  }
}
```

#### 1.2 优化的热更新 (HMR)

Vite 5.x 改进了 HMR 的性能，特别是在大型项目中：

- 更智能的依赖追踪
- 减少不必要的模块重新加载
- 更快的边界模块处理

```javascript
// vite.config.js
export default {
  server: {
    hmr: {
      overlay: true, // 显示错误覆盖层
      port: 24678,
      clientPort: 24678
    }
  }
}
```

### 2. Rollup 4 集成

Vite 5.x 升级到 Rollup 4，带来了：

- 更好的 Tree Shaking
- 更快的构建速度
- 改进的错误报告

```javascript
// vite.config.js
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'utils': ['lodash', 'dayjs']
        }
      }
    }
  }
}
```

### 3. 改进的 CSS 处理

Vite 5.x 对 CSS 处理进行了多项改进：

#### 3.1 更好的 CSS 源映射

```javascript
// vite.config.js
export default {
  css: {
    devSourcemap: true, // 开发环境启用 CSS 源映射
    modules: {
      localsConvention: 'camelCaseOnly',
      scopeBehaviour: 'local'
    }
  }
}
```

#### 3.2 优化的 CSS 分割

```javascript
// vite.config.js
export default {
  build: {
    cssCodeSplit: true, // 启用 CSS 代码分割
    cssTarget: 'chrome80'
  }
}
```

## 三、新功能详解

### 1. 环境变量改进

Vite 5.x 改进了环境变量的处理：

```javascript
// .env.development
VITE_API_URL=http://localhost:3000
VITE_DEBUG=true

// .env.production
VITE_API_URL=https://api.example.com
VITE_DEBUG=false
```

```javascript
// 使用环境变量
console.log(import.meta.env.VITE_API_URL)
console.log(import.meta.env.DEV)
console.log(import.meta.env.PROD)
```

### 2. 新的 `define` 配置选项

Vite 5.x 改进了 `define` 选项，支持更复杂的替换：

```javascript
// vite.config.js
export default {
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    __DEBUG__: process.env.NODE_ENV === 'development'
  }
}
```

```javascript
// 在代码中使用
console.log('版本:', __APP_VERSION__)
console.log('构建时间:', __BUILD_TIME__)

if (__DEBUG__) {
  console.log('调试模式')
}
```

### 3. 改进的 TypeScript 支持

Vite 5.x 提供了更好的 TypeScript 支持：

```typescript
// vite-env.d.ts
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
  readonly VITE_DEBUG: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
```

### 4. 新的 `server.proxy` 配置

Vite 5.x 改进了代理配置：

```javascript
// vite.config.js
export default {
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
        configure: (proxy, options) => {
          proxy.on('proxyReq', (proxyReq, req, res) => {
            console.log('代理请求:', req.url)
          })
        }
      }
    }
  }
}
```

## 四、配置优化

### 1. 新的默认配置

Vite 5.x 更新了一些默认配置：

```javascript
// vite.config.js
export default {
  build: {
    target: 'es2020', // 默认目标
    minify: 'esbuild', // 默认压缩工具
    sourcemap: false, // 默认不生成源映射
    reportCompressedSize: true // 报告压缩大小
  }
}
```

### 2. 改进的插件 API

Vite 5.x 提供了更强大的插件 API：

```javascript
// my-plugin.js
export default function myPlugin() {
  return {
    name: 'my-plugin',
    config(config, env) {
      console.log('配置阶段:', env)
      return config
    },
    configResolved(config) {
      console.log('配置已解析')
    },
    configureServer(server) {
      server.middlewares.use((req, res, next) => {
        console.log('请求:', req.url)
        next()
      })
    },
    transform(code, id) {
      if (id.endsWith('.js')) {
        return code.replace('__PLACEHOLDER__', 'replaced')
      }
    }
  }
}
```

### 3. 新的 `build.assetsInlineLimit` 选项

```javascript
// vite.config.js
export default {
  build: {
    assetsInlineLimit: 4096, // 4kb 以下内联为 base64
    chunkSizeWarningLimit: 500 // 500kb 警告
  }
}
```

## 五、实战示例

### 1. 创建 Vite 5.x 项目

```bash
# 使用 npm
npm create vite@latest my-project -- --template react-ts

# 使用 yarn
yarn create vite my-project --template react-ts

# 使用 pnpm
pnpm create vite my-project --template react-ts
```

### 2. 完整的 Vite 配置示例

```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@utils': path.resolve(__dirname, './src/utils')
    }
  },
  
  css: {
    devSourcemap: true,
    modules: {
      localsConvention: 'camelCaseOnly'
    },
    preprocessorOptions: {
      scss: {
        additionalData: `@import "@/styles/variables.scss";`
      }
    }
  },
  
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  },
  
  build: {
    outDir: 'dist',
    sourcemap: true,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'router': ['react-router-dom'],
          'ui': ['antd']
        }
      }
    }
  },
  
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString())
  }
})
```

### 3. 使用环境变量

```javascript
// config.js
const config = {
  apiUrl: import.meta.env.VITE_API_URL || 'http://localhost:3000',
  debug: import.meta.env.VITE_DEBUG === 'true',
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD
}

export default config
```

## 六、迁移指南

### 从 Vite 4.x 迁移到 Vite 5.x

1. **更新依赖**

```bash
npm install vite@latest
```

2. **检查配置变更**

```javascript
// Vite 4.x
export default {
  build: {
    target: 'es2020'
  }
}

// Vite 5.x (相同，无需变更)
export default {
  build: {
    target: 'es2020'
  }
}
```

3. **测试构建**

```bash
npm run build
```

### 注意事项

- Rollup 4 可能有一些破坏性变更
- 检查自定义插件是否兼容
- 测试所有功能是否正常

## 七、性能最佳实践

### 1. 优化依赖预构建

```javascript
export default {
  optimizeDeps: {
    include: ['react', 'react-dom', 'antd'],
    exclude: ['your-local-package']
  }
}
```

### 2. 配置合理的代码分割

```javascript
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: (id) => {
          if (id.includes('node_modules')) {
            if (id.includes('react')) return 'react-vendor'
            if (id.includes('antd')) return 'ui-vendor'
            return 'vendor'
          }
        }
      }
    }
  }
}
```

### 3. 使用浏览器缓存

```javascript
export default {
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].js',
        chunkFileNames: 'assets/[name]-[hash].js',
        assetFileNames: 'assets/[name]-[hash].[ext]'
      }
    }
  }
}
```

## 八、总结

Vite 5.x 带来了显著的性能提升和稳定性改进，同时引入了一些有用的新功能。通过本文的介绍，你应该已经了解了：

1. Vite 5.x 的核心改进
2. 新功能的使用方法
3. 配置优化技巧
4. 迁移注意事项
5. 性能最佳实践

建议尽快升级到 Vite 5.x，享受更快的开发体验和更好的构建性能。

## 参考资料

- [Vite 官方文档](https://vitejs.dev/)
- [Vite 5.0 发布公告](https://vitejs.dev/blog/announcing-vite5)
- [Rollup 4 文档](https://rollupjs.org/)
