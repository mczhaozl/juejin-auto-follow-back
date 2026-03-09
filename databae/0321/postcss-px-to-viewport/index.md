# postcss-px-to-viewport：移动端适配的终极方案

> px 自动转 vw/vh，告别手动计算，支持设计稿任意尺寸

---

## 一、移动端适配的痛点

传统方案的问题：
- rem 需要动态设置根字体大小
- 媒体查询需要写很多断点
- 手动计算 vw 容易出错

postcss-px-to-viewport 自动将 px 转换为 vw/vh，一劳永逸。

---

## 二、安装配置

```bash
npm install -D postcss-px-to-viewport
```

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    'postcss-px-to-viewport': {
      viewportWidth: 375,  // 设计稿宽度
      viewportHeight: 667,  // 设计稿高度
      unitPrecision: 5,  // 转换精度
      viewportUnit: 'vw',  // 转换单位
      selectorBlackList: ['.ignore'],  // 不转换的类名
      minPixelValue: 1,  // 最小转换值
      mediaQuery: false  // 是否转换媒体查询中的 px
    }
  }
};
```

---

## 三、使用示例

```css
/* 输入 */
.box {
  width: 375px;
  height: 200px;
  font-size: 14px;
  padding: 10px;
}

/* 输出 */
.box {
  width: 100vw;
  height: 53.33333vw;
  font-size: 3.73333vw;
  padding: 2.66667vw;
}
```

---

## 四、进阶配置

### 排除第三方组件

```javascript
{
  selectorBlackList: ['.van-', '.el-'],  // 排除 Vant、Element UI
  exclude: [/node_modules/]  // 排除 node_modules
}
```

### 横竖屏适配

```javascript
{
  landscape: true,  // 支持横屏
  landscapeUnit: 'vw',  // 横屏单位
  landscapeWidth: 667  // 横屏宽度
}
```

---

## 五、与 rem 方案对比

| 特性 | vw 方案 | rem 方案 |
|------|---------|----------|
| 配置复杂度 | 低 | 高 |
| 运行时计算 | 无 | 有 |
| 兼容性 | 好 | 更好 |
| 精确度 | 高 | 中 |

---

## 总结

postcss-px-to-viewport 是移动端适配的最佳方案：
- 配置简单
- 自动转换
- 精确适配
- 无运行时开销

如果这篇文章对你有帮助，欢迎点赞收藏！
