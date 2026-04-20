# Vite 性能优化完全指南：从开发到生产优化

## 一、开发环境优化

### 1.1 依赖预构建优化

```javascript
// vite.config.js
export default {
  optimizeDeps: {
    include: ['react', 'react-dom'],
    exclude: ['heavy-lib'],
    force: true
  }
};
```

### 1.2 优化服务器启动

```javascript
export default {
  server: {
    watch: {
      ignored: ['**/node_modules/**', '**/.git/**']
    }
  }
};
```

---

## 二、生产环境优化

### 2.1 代码分割

```javascript
export default {
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['lodash-es']
        }
      }
    }
  }
};
```

### 2.2 Tree Shaking

```javascript
// 确保使用 ES Modules
export function util1() {}
export function util2() {}

// 只导入使用的
import { util1 } from './utils';
```

---

## 三、压缩优化

```javascript
export default {
  build: {
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  }
};
```

---

## 四、静态资源优化

```javascript
export default {
  assetsInlineLimit: 4096, // 4KB 以下内联
  build: {
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]',
        chunkFileNames: 'assets/[name]-[hash].js'
      }
    }
  }
};
```

---

## 五、依赖优化

```bash
# 使用 ES Module 版本的依赖
npm install lodash-es

# 或使用 CDN
export default {
  plugins: [
    importToCDN({
      modules: [
        { name: 'react', var: 'React', path: 'umd/react.production.min.js' }
      ]
    })
  ]
};
```

---

## 六、预加载与预获取

```javascript
// vite.config.js
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [
    {
      name: 'preload-assets',
      transformIndexHtml(html) {
        return html.replace(
          '</head>',
          '<link rel="preload" href="/logo.png" as="image"></head>'
        );
      }
    }
  ]
});
```

---

## 七、分析包大小

```bash
npm install rollup-plugin-visualizer --save-dev
```

```javascript
import { defineConfig } from 'vite';
import { visualizer } from 'rollup-plugin-visualizer';

export default defineConfig({
  plugins: [visualizer({ open: true })]
});
```

---

## 八、环境变量优化

```bash
# .env.production
VITE_APP_TITLE=My App
```

```javascript
// vite.config.js
import { defineConfig, loadEnv } from 'vite';

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd());
  return {
    define: {
      __APP_TITLE__: JSON.stringify(env.VITE_APP_TITLE)
    }
  };
});
```

---

## 九、缓存优化

```javascript
export default {
  build: {
    rollupOptions: {
      output: {
        entryFileNames: 'assets/[name]-[hash].js'
      }
    }
  }
};
```

```html
<!-- nginx -->
location ~* \.(js|css)$ {
  expires 1y;
  add_header Cache-Control "public, immutable";
}
```

---

## 十、最佳实践

1. 合理配置依赖预构建
2. 优化代码分割
3. 使用 Tree Shaking
4. 压缩生产资源
5. 分析并优化包大小

---

## 十一、总结

Vite 优化需要从开发体验和生产性能两方面入手，全面提升项目效率。
