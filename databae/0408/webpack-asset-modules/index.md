# Webpack Asset Modules 完全指南：从 file-loader 到 Asset Modules 的演进

> 深入讲解 Webpack 5 的 Asset Modules 特性，对比旧版 loader，帮你平滑迁移并优化资源处理。

## 一、为什么需要 Asset Modules

在 Webpack 5 之前，处理静态资源需要使用各种 loader：

```javascript
// webpack 4 配置
module.exports = {
  module: {
    rules: [
      {
        test: /\.(png|jpg|gif)$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: 'images/[name].[hash:8].[ext]'
            }
          }
        ]
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: 'fonts/[name].[hash:8].[ext]'
            }
          }
        ]
      },
      {
        test: /\.svg$/,
        use: [
          {
            loader: 'svg-inline-loader',
            options: {
              removeSVGTagAttrs: false
            }
          }
        ]
      }
    ]
  }
};
```

Webpack 5 引入了 **Asset Modules**，统一了资源处理方式。

## 二、Asset Modules 基本用法

### 2.1 四种资源类型

| 类型 | 描述 | 相当于旧版 |
|------|------|-----------|
| asset/resource | 导出单独文件 | file-loader |
| asset/inline | 导出 data URI | url-loader |
| asset/source | 导出原始内容 | raw-loader |
| asset | 自动选择 | url-loader (有 limit) |

### 2.2 基本配置

```javascript
// webpack 5 配置
module.exports = {
  module: {
    rules: [
      {
        test: /\.(png|jpg|gif|svg)$/,
        type: 'asset/resource'
      },
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[name].[hash:8][ext]'
        }
      },
      {
        test: /\.ico$/,
        type: 'asset/inline'
      }
    ]
  }
};
```

## 三、asset/resource

### 3.1 图片资源

```javascript
{
  test: /\.(png|jpg|gif)$/,
  type: 'asset/resource',
  generator: {
    filename: 'images/[name].[hash:8][ext]'
  }
}
```

**使用**：

```javascript
import img from './logo.png';

console.log(img); // 输出: /static/images/logo.a1b2c3d4.png
```

### 3.2 字体资源

```javascript
{
  test: /\.(woff|woff2|eot|ttf|otf)$/,
  type: 'asset/resource',
  generator: {
    filename: 'fonts/[name].[hash:8][ext]'
  }
}
```

## 四、asset/inline

### 4.1 小图片转 Base64

```javascript
{
  test: /\.svg$/,
  type: 'asset/inline'
}
```

**使用**：

```javascript
import svg from './icon.svg';

console.log(svg); // 输出: data:image/svg+xml;base64,...
```

### 4.2 Data URI 优势

- 减少 HTTP 请求
- 适合小文件
- 增加 JS bundle 大小

## 五、asset/source

### 5.1 读取原始内容

```javascript
{
  test: /\.txt$/,
  type: 'asset/source'
}
```

**使用**：

```javascript
import content from './file.txt';

console.log(content); // 输出: 文件原始内容
```

### 5.2 适用场景

- 加载模板文件
- 加载原始文本
- 需要自行处理的资源

## 六、asset（自动选择）

### 6.1 自动选择 resource 或 inline

```javascript
{
  test: /\.(png|jpg|gif)$/,
  type: 'asset',
  parser: {
    dataUrlCondition: {
      maxSize: 8 * 1024 // 8KB
    }
  }
}
```

**逻辑**：

- 文件 > 8KB → `asset/resource`（单独文件）
- 文件 ≤ 8KB → `asset/inline`（Base64）

### 6.2 配置对比

```javascript
// webpack 4: url-loader
{
  test: /\.(png|jpg|gif)$/,
  use: [
    {
      loader: 'url-loader',
      options: {
        limit: 8192,
        name: 'images/[name].[hash:8].[ext]'
      }
    }
  ]
}

// webpack 5: asset
{
  test: /\.(png|jpg|gif)$/,
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

## 七、Generator 配置

### 7.1 全局配置

```javascript
module.exports = {
  output: {
    assetModuleFilename: 'assets/[name].[hash:8][ext]'
  },
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

### 7.2 规则级配置

```javascript
{
  test: /\.(png|jpg)$/,
  type: 'asset/resource',
  generator: {
    filename: 'images/[name].[hash:8][ext]'
  }
},
{
  test: /\.(woff|woff2)$/,
  type: 'asset/resource',
  generator: {
    filename: 'fonts/[name].[hash:8][ext]'
  }
}
```

## 八、迁移指南

### 8.1 从 file-loader 迁移

```javascript
// webpack 4
{
  test: /\.png$/,
  use: [
    {
      loader: 'file-loader',
      options: {
        name: 'images/[name].[hash:8].[ext]',
        publicPath: 'assets/'
      }
    }
  ]
}

// webpack 5
{
  test: /\.png$/,
  type: 'asset/resource',
  generator: {
    filename: 'images/[name].[hash:8][ext]',
    publicPath: 'assets/'
  }
}
```

### 8.2 从 url-loader 迁移

```javascript
// webpack 4
{
  test: /\.png$/,
  use: [
    {
      loader: 'url-loader',
      options: {
        limit: 8192,
        name: 'images/[name].[hash:8].[ext]'
      }
    }
  ]
}

// webpack 5
{
  test: /\.png$/,
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

### 8.3 从 raw-loader 迁移

```javascript
// webpack 4
{
  test: /\.txt$/,
  use: 'raw-loader'
}

// webpack 5
{
  test: /\.txt$/,
  type: 'asset/source'
}
```

## 九、完整配置示例

```javascript
const path = require('path');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: '[name].js',
    assetModuleFilename: 'assets/[name].[hash:8][ext]'
  },
  module: {
    rules: [
      // 图片: 超过 8KB 单独文件，否则 Base64
      {
        test: /\.(png|jpg|gif|webp)$/,
        type: 'asset',
        parser: {
          dataUrlCondition: {
            maxSize: 8 * 1024
          }
        },
        generator: {
          filename: 'images/[name].[hash:8][ext]'
        }
      },
      // SVG: 始终作为单独文件
      {
        test: /\.svg$/,
        type: 'asset/resource',
        generator: {
          filename: 'icons/[name].[hash:8][ext]'
        }
      },
      // 字体: 单独文件
      {
        test: /\.(woff|woff2|eot|ttf|otf)$/,
        type: 'asset/resource',
        generator: {
          filename: 'fonts/[name].[hash:8][ext]'
        }
      },
      // 音频/视频: 单独文件
      {
        test: /\.(mp3|mp4|webm|ogg)$/,
        type: 'asset/resource',
        generator: {
          filename: 'media/[name].[hash:8][ext]'
        }
      },
      // Markdown: 原始内容
      {
        test: /\.md$/,
        type: 'asset/source',
        generator: {
          filename: 'docs/[name][ext]'
        }
      }
    ]
  }
};
```

## 十、总结

Asset Modules 是 Webpack 5 的重要改进：

1. **统一 API**：用 `type` 替代多种 loader
2. **内置支持**：无需安装额外包
3. **更细粒度**：灵活控制资源处理方式
4. **平滑迁移**：兼容旧配置

迁移建议：

- 优先使用 `asset/resource` 或 `asset`
- 合理设置 `maxSize` 阈值
- 注意 `generator.filename` 路径

---

**推荐阅读**：
- [Webpack 5 Asset Modules 文档](https://webpack.js.org/guides/asset-modules/)
- [迁移指南](https://webpack.js.org/migrate/5/)

**如果对你有帮助，欢迎点赞收藏！**
