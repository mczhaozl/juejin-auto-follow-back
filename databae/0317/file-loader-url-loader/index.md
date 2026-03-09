# file-loader 与 url-loader：静态资源处理的演进史

> 从传统 loader 到 webpack 5 Asset Modules 的迁移指南

---

## 一、静态资源处理的演进

### webpack 4 及之前

需要 file-loader 和 url-loader 处理图片、字体等资源。

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.(png|jpg|gif)$/,
        use: ['file-loader']
      }
    ]
  }
};
```

### webpack 5

内置 Asset Modules，无需额外 loader。

```javascript
module.exports = {
  module: {
    rules: [
      {
        test: /\.(png|jpg|gif)$/,
        type: 'asset/resource'
      }
    ]
  }
};
```

---

## 二、file-loader

将文件复制到输出目录，返回文件路径。

### 基础用法

```javascript
{
  test: /\.(png|jpg|gif)$/,
  use: {
    loader: 'file-loader',
    options: {
      name: '[name].[hash:8].[ext]',
      outputPath: 'images/'
    }
  }
}
```

### 配置选项

```javascript
{
  loader: 'file-loader',
  options: {
    // 文件名模板
    name: '[path][name].[ext]',
    
    // 输出目录
    outputPath: 'assets/',
    
    // 公共路径
    publicPath: '/static/',
    
    // 自定义文件名
    name(file) {
      if (process.env.NODE_ENV === 'development') {
        return '[path][name].[ext]';
      }
      return '[contenthash].[ext]';
    }
  }
}
```

---

## 三、url-loader

小文件转 base64，大文件用 file-loader。

### 基础用法

```javascript
{
  test: /\.(png|jpg|gif)$/,
  use: {
    loader: 'url-loader',
    options: {
      limit: 8192,  // 8KB 以下转 base64
      fallback: 'file-loader'
    }
  }
}
```

### 优势

- 减少 HTTP 请求
- 小图标直接内联

### 劣势

- 增加 JS/CSS 体积
- 无法利用浏览器缓存

---

## 四、webpack 5 Asset Modules

### 四种类型

```javascript
module.exports = {
  module: {
    rules: [
      // asset/resource：替代 file-loader
      {
        test: /\.(png|jpg|gif)$/,
        type: 'asset/resource'
      },
      
      // asset/inline：替代 url-loader（强制 base64）
      {
        test: /\.svg$/,
        type: 'asset/inline'
      },
      
      // asset/source：替代 raw-loader
      {
        test: /\.txt$/,
        type: 'asset/source'
      },
      
      // asset：自动选择（替代 url-loader）
      {
        test: /\.(png|jpg|gif)$/,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 8 * 1024  // 8KB
          }
        }
      }
    ]
  }
};
```

---

## 五、迁移指南

### file-loader → asset/resource

```javascript
// 旧配置
{
  test: /\.(png|jpg)$/,
  use: {
    loader: 'file-loader',
    options: {
      name: 'images/[name].[hash:8].[ext]'
    }
  }
}

// 新配置
{
  test: /\.(png|jpg)$/,
  type: 'asset/resource',
  generator: {
    filename: 'images/[name].[hash:8][ext]'
  }
}
```

### url-loader → asset

```javascript
// 旧配置
{
  test: /\.(png|jpg)$/,
  use: {
    loader: 'url-loader',
    options: {
      limit: 8192,
      name: 'images/[name].[hash:8].[ext]'
    }
  }
}

// 新配置
{
  test: /\.(png|jpg)$/,
  type: 'asset',
  parser: {
    dataUrlCondition: {
      maxSize: 8 * 1024
    }
  },
  generator: {
    filename: 'images/[name].[hash:8][ext]'
  }
}
```

---

## 六、完整配置示例

```javascript
module.exports = {
  module: {
    rules: [
      // 图片
      {
        test: /\.(png|jpg|jpeg|gif)$/,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 10 * 1024  // 10KB
          }
        },
        generator: {
          filename: 'images/[name].[hash:8][ext]'
        }
      },
      
      // SVG
      {
        test: /\.svg$/,
        type: 'asset/inline'
      },
      
      // 字体
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[name][ext]'
        }
      },
      
      // 视频
      {
        test: /\.(mp4|webm)$/,
        type: 'asset/resource',
        generator: {
          filename: 'videos/[name].[hash:8][ext]'
        }
      }
    ]
  }
};
```

---

## 总结

webpack 5 的 Asset Modules 是更现代的方案：

- 无需额外安装 loader
- 配置更简洁
- 性能更好
- 功能更强大

建议新项目直接使用 Asset Modules，旧项目逐步迁移。

如果这篇文章对你有帮助，欢迎点赞收藏！
