# 前端打包工具变更史：从手写脚本到 Vite、Turbopack

> 按时间线梳理前端构建与打包工具的演变：任务流时代、Webpack 统治、Rollup/Parcel 并存，再到 Vite 与新一代高性能工具，每段配标志事件与典型写法。

---

## 一、前打包时代：手写脚本与手工拼接（约 2005–2011）

### 历史背景

在单页应用（SPA）和模块化尚未普及之前，前端页面多是**多页 + 少量 JS**：每个页面直接写 `<script src="a.js"></script>`、`b.js`、`c.js`，顺序不能错，否则依赖就乱。没有「打包」这个概念，顶多是**把几个文件拼成一个**、或压缩一下，用 Make、Ant 或自己写的脚本跑一遍。那时 JS 体量小，没有 npm、没有 node_modules，浏览器也不支持模块，**依赖全靠人肉排顺序**。

### 标志性事件

- **2009 年**：Node.js 诞生，CommonJS（`require`/`module.exports`）在服务端普及，前端开始羡慕「模块化」。
- **2010 年前后**：npm 成为 Node 包管理器标配，前端库逐渐以 npm 包形式发布，但**浏览器不能直接 require**，需要有人把「模块」变成「浏览器能跑的一坨脚本」。
- **2011 年**：**Browserify** 出现，首次让「在浏览器里用 CommonJS 写法」成为可能：在 Node 环境里解析 `require()`，把依赖树打成一个 bundle.js，供前端引用。

### 解决的问题与局限

Browserify 解决了「用 CommonJS 组织前端代码」的问题，但**只做 JS**，CSS、图片、多入口、代码分割等仍要自己拼或靠后续工具。这一阶段奠定了「**前端也需要构建管线**」的共识，为后来的 Grunt/Gulp（任务流）和 Webpack（模块打包）铺路。

### 典型形态（概念性）

```html
<!-- 当时常见：多个 script，顺序敏感 -->
<script src="lib/jquery.js"></script>
<script src="lib/utils.js"></script>
<script src="app/main.js"></script>
```

```javascript
// Browserify 之后：在源码里写 require，构建时打成 bundle
// main.js
var $ = require('jquery');
var utils = require('./utils');
// ... 浏览器里实际加载的是 bundle.js
```

---

## 二、任务流时代：Grunt、Gulp（2012–2015）

### 历史背景

前端项目开始变复杂：要**压缩 JS/CSS**、**合并文件**、**编译 Less/Sass**、**刷新前清缓存**……大家需要的是「按顺序执行一堆任务」的**任务流工具**，而不是只解决模块依赖。Node 生态里于是出现了**以任务（task）为中心**的构建工具：**Grunt** 用配置描述任务，**Gulp** 用流（stream）和代码描述任务，二者都是「你定义任务，我按顺序跑」。

### 标志性事件

- **2012 年**：**Grunt** 发布并快速流行，成为前端自动化的事实标准之一；通过 Gruntfile 配置 concat、uglify、watch 等任务。
- **2013 年**：**Gulp** 发布，用「流 + 代码」替代「配置」，写法更简洁，插件生态迅速增长。
- **2013–2015 年**：Grunt/Gulp 与 Browserify 常一起用：Browserify 打 JS bundle，Grunt/Gulp 负责压缩、拷贝、编译 CSS、启动本地服务等。

### 解决的问题与局限

任务流把**重复劳动**自动化了，但**没有解决「模块依赖图」**：合并、压缩仍是「对一堆文件做操作」，而不是「从入口出发解析依赖再打包」。一旦项目变大、依赖变多，**依赖顺序、重复打包、按需加载**都成了痛点，这为「以模块为中心」的 Webpack 创造了空间。

### 典型形态

```javascript
// Gruntfile.js 概念示例：配置任务
module.exports = function (grunt) {
  grunt.initConfig({
    concat: { dist: { src: ['src/*.js'], dest: 'dist/bundle.js' } },
    uglify: { dist: { files: { 'dist/bundle.min.js': ['dist/bundle.js'] } } }
  });
  grunt.loadNpmTasks('grunt-contrib-concat');
  grunt.registerTask('default', ['concat', 'uglify']);
};
```

```javascript
// Gulp：流式处理
const gulp = require('gulp');
const concat = require('gulp-concat');
const uglify = require('gulp-uglify');
gulp.task('js', () =>
  gulp.src('src/*.js').pipe(concat('bundle.js')).pipe(uglify()).pipe(gulp.dest('dist'))
);
```

---

## 三、模块打包时代：Webpack 崛起（2012–2019）

### 历史背景

**Webpack** 由 Tobias Koppers 在 2012 年发起，2014 年前后文档与 1.x 逐渐成型。它的核心思想是：**一切皆模块**——JS、CSS、图片、字体都是「模块」，从**入口**出发递归解析依赖，形成依赖图，再打包成少量（或按需）产出文件。这与 Grunt/Gulp 的「任务列表」完全不同：**以依赖图为中心**，天然支持代码分割、懒加载、Tree Shaking（配合 ES Module）等。React、Vue 等 SPA 框架的脚手架纷纷选用 Webpack，使其在 2016 年后成为**前端打包的事实标准**。

### 标志性事件

- **2012 年**：Webpack 项目诞生（Tobias Koppers）。
- **2014 年**：Webpack 文档与 1.x 传播，Loader（处理各类文件）、Plugin（钩子）机制确立。
- **2015–2016 年**：Webpack 2 支持 ES Module、Tree Shaking；与 React/Vue 生态深度绑定，**统治前端构建**。
- **2017–2019 年**：Webpack 4（零配置模式）、Webpack 5（持久化缓存、Module Federation）发布，生态与可配置性达到顶峰，同时**配置复杂、构建慢**的批评也越来越多。

### 解决的问题与局限

Webpack 统一了**模块解析、多类型资源、代码分割、懒加载**，并形成庞大插件生态；但**配置重、冷启动与增量构建慢**在超大型项目中成为瓶颈。社区开始期待「更简单、更快」的替代品，Rollup、Parcel、以及后来的 Vite 应运而生。

### 典型形态

```javascript
// webpack.config.js 简化示例
module.exports = {
  entry: './src/index.js',
  output: { filename: 'bundle.js', path: __dirname + '/dist' },
  module: {
    rules: [
      { test: /\.js$/, use: 'babel-loader' },
      { test: /\.css$/, use: ['style-loader', 'css-loader'] }
    ]
  }
};
```

---

## 四、分流与并存：Rollup、Parcel（2015–2020）

### 历史背景

**Rollup**（2015）主打 **ES Module 静态分析**，产出更小、更干净的 bundle，适合**库与框架**的发布构建；**Parcel**（2017 首版、2018 1.0）主打**零配置**，开箱即用，用多进程与缓存提升速度。二者与 Webpack 形成「Webpack 主攻应用、Rollup 主攻库、Parcel 主攻体验」的分工，但都仍是**打包时构建**：改一行代码要重新跑一遍打包（或依赖 HMR），在项目变大时冷启动与热更仍会变慢。

### 标志性事件

- **2015 年**：Rollup 发布，Tree Shaking 与 ESM 输出成为库作者首选；Vue、React 等库的构建曾大量采用 Rollup。
- **2017–2018 年**：Parcel 1.0 发布，零配置、多语言（JS/TS/CSS/HTML）开箱，吸引大量「不想写配置」的开发者。
- **2019 年前后**：Rollup 1.0 稳定；Webpack 5 酝酿；社区对「构建速度」的诉求越来越强，为 Vite 的「开发时不打包」铺路。

### 解决的问题与局限

Rollup 把**库的构建质量**提到新高度；Parcel 把**上手成本**压到最低。但二者都未从根本上改变「开发阶段也要先打包再看效果」的模式，**开发体验与构建速度**仍是下一阶段的主题。

---

## 五、开发时零打包与高性能：Vite、esbuild、Turbopack（2020 至今）

### 历史背景

**Vite**（尤雨溪，2020）提出「**开发用原生 ESM + 按需编译，生产用 Rollup 打包**」：开发时浏览器直接请求 ES 模块，只对当前用到的文件做即时编译（用 **esbuild**），**冷启动极快**；生产构建仍用 Rollup 保证兼容与体积。**esbuild**（Go 编写）和后来的 **Rspack**（Rust）、**Turbopack**（Rust，Vercel/Next）则把「打包器本身」用高性能语言重写，进一步缩短构建时间。前端打包工具进入「**开发体验优先 + 构建性能优先**」双线并进的时代。

### 标志性事件

- **2020 年**：**Vite 1.0** 发布，开发阶段基于原生 ESM + esbuild 预构建，生产用 Rollup；Vue 3 官方推荐。
- **2020 年前后**：**esbuild** 广泛被采用为「编译/压缩」层，与 Vite、各类 CLI 集成。
- **2022–2023 年**：**Turbopack**（Next.js） alpha；**Rspack**（字节）开源；**Webpack** 5 持续迭代；**Vite 4/5** 成为新项目主流选择之一。
- **2024–2025 年**：Vite 与 Rolldown（Rollup 的 Rust 实现）等下一代内核的探索；Turbopack 逐步稳定。

### 解决的问题与局限

Vite 解决了**开发时冷启动与热更新慢**的问题；esbuild/Rspack/Turbopack 解决了**打包与编译本身**的 CPU 瓶颈。当前局面是：**新项目多用 Vite 或框架自带工具（Next/SvelteKit 等）**，**老项目与超大型应用仍大量使用 Webpack**；库作者继续用 Rollup。没有单一「赢家」，而是**按场景选型**。

### 典型形态

```bash
# Vite：开发即起，无需先打包
npm create vite@latest my-app -- --template vue
cd my-app && npm run dev
```

```javascript
// vite.config.js 简化示例
import { defineConfig } from 'vite';
export default defineConfig({
  build: { rollupOptions: { output: { manualChunks: {} } } }
});
```

---

## 六、总结：一条时间线串起来

- **约 2005–2011**：手写 script、手工拼接；Browserify 让 CommonJS 进浏览器，前端构建意识萌芽。
- **2012–2015**：Grunt、Gulp 任务流时代；自动化合并、压缩、编译，但不做「依赖图」，复杂度上来后不够用。
- **2012–2019**：Webpack 从诞生到统治；一切皆模块、Loader/Plugin、代码分割；配置重、构建慢成为后续被替代的主因之一。
- **2015–2020**：Rollup（库）、Parcel（零配置）与 Webpack 并存；ESM、Tree Shaking、体验与速度被反复打磨。
- **2020 至今**：Vite 带火「开发时 ESM + 按需编译」；esbuild、Rspack、Turbopack 用 Go/Rust 拉高构建性能；前端打包进入**多工具按场景选型**的阶段。

若对你有用，欢迎点赞、收藏；你若有从 Grunt/Webpack 迁移到 Vite 的实战经历，也欢迎在评论区分享。
