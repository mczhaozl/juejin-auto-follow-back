# Webpack 打包优化实战：从 10s 到 2s 的极致优化

> 代码分割、缓存、多线程、Tree Shaking 等实战技巧全解析

---

## 一、优化前的问题

项目打包时间 10 秒，每次改动都要等很久，开发体验极差。

---

## 二、优化策略

### 1. 代码分割

```javascript
optimization: {
  splitChunks: {
    chunks: 'all',
    cacheGroups: {
      vendor: {
        test: /[\\/]node_modules[\\/]/,
        name: 'vendors',
        priority: 10
      }
    }
  }
}
```

### 2. 持久化缓存

```javascript
cache: {
  type: 'filesystem',
  buildDependencies: {
    config: [__filename]
  }
}
```

### 3. 多线程编译

```javascript
use: [
  'thread-loader',
  'babel-loader'
]
```

### 4. Tree Shaking

```javascript
optimization: {
  usedExports: true,
  minimize: true
}
```

---

## 三、优化结果

- 首次构建：10s → 8s
- 二次构建：10s → 2s
- 开发体验大幅提升

---

## 总结

通过缓存、代码分割、多线程等手段，可以将打包时间降低 80%。

如果这篇文章对你有帮助，欢迎点赞收藏！
