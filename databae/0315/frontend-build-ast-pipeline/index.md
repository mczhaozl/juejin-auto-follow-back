# 现代前端构建：从 AST、依赖图到产物分块的完整管线解析

> 从源码解析、AST 变换、模块图与 chunk 划分到 Tree-shaking 与代码生成，系统梳理打包器核心链路与工程化实践。

---

## 一、构建管线在解决什么问题

前端工程里，源码往往以**多模块、多格式**（TS、JSX、Vue、CSS）存在，且存在**依赖关系**；浏览器无法直接跑 TS、无法按「裸模块」请求 node_modules。构建管线要完成：**解析**（把各格式转成 AST）、**转换**（AST 变换、降级、CSS 处理）、**依赖分析**（从入口建模块图）、**打包/分块**（合并或按策略拆 chunk）、**代码生成**（AST → 目标代码 + sourcemap）。理解这条管线，能更好配置 Webpack/Vite/Rollup、写 Babel/PostCSS 插件、排构建慢与产物异常。

## 二、解析阶段：从源码到 AST

**解析器** 把源码变成 **AST（抽象语法树）**。不同语言用不同解析器：JS/TS 常用 **acorn**、**@babel/parser**、**swc**；CSS 用 **postcss** 的解析；Vue SFC 先拆成 script/style/template 再分别解析。解析结果是一棵带节点类型的树，后续 **转换** 和 **生成** 都基于 AST，不直接操作字符串。解析阶段会报语法错误、可产出 **location** 信息供 sourcemap 与报错定位。

## 三、转换与 Loader / 插件

**转换** 在 AST 上做增删改：Babel 做语法降级、JSX 转 JS、TS 擦除类型；PostCSS 做 autoprefixer、嵌套；Vue/React 的 loader 可能做 SFC 拆块或 JSX 编译。在 Webpack 里，**Loader** 是「单文件进单文件出」的转换管道；在 Rollup/Vite 里，**插件** 的 `transform` 钩子对模块内容做转换。共同点是：**输入是源码或 AST，输出是下一阶段可消费的代码（或 AST）**。转换顺序通常由配置顺序决定，可串联多个 loader/插件。

## 四、模块图与依赖分析

从**入口**（如 `main.js`）开始，根据 **import/require** 静态分析依赖，递归解析每个模块，得到一张**模块图（Module Graph）**：节点是模块，边是依赖关系。图中会记录模块的**绝对路径、类型（JS/CSS）、依赖列表、解析后的内容**。动态 import（`import()`）会生成**异步边界**：依赖的模块单独成 chunk，在运行时再加载。模块图是后续 **Tree-shaking**、**分块**、**代码生成** 的基础；图错了（如循环依赖未处理、动态路径未展开）会导致打包结果错误或冗余。

## 五、Tree-shaking 与 Dead Code Elimination

**Tree-shaking** 指利用 **ESM 的静态结构**，在模块图上做**可达性分析**：从入口出发，只保留「被引用」的 export；未被引用的 export 及其内部未使用代码可视为 **dead code** 并在生成时去掉。前提是：**模块必须是 ESM**（CommonJS 的 require 是动态的，难以静态分析）；**无副作用**或通过 package.json 的 `sideEffects` 声明。Rollup 是 Tree-shaking 的典型实现者；Webpack 在 production 模式下也会做类似优化。写库时注意 **export 粒度** 和 **sideEffects** 配置，能减少业务方打包体积。

## 六、分块（Chunk）策略与代码分割

**分块** 决定哪些模块打进同一个 bundle、哪些单独成 chunk。常见策略：**按入口**（多页应用每个入口一个 chunk）、**按动态 import**（每个 `import()` 边界一个 async chunk）、**按 vendor**（把 node_modules 打成单独 chunk 利于缓存）、**manualChunks**（手动指定某类模块进某 chunk）。分块会影响**请求数**、**缓存命中**、**首屏体积**；过细会请求多，过粗会单包过大。需要结合 **preload/prefetch**、**懒加载时机** 做权衡。

## 七、代码生成与运行时

**代码生成** 把**模块图 + 分块结果**转成最终的可执行代码：每个 chunk 对应一个**运行时**（如 Webpack 的 runtime：模块 id 与 chunk 加载、模块缓存）加**模块内容**（可能被包装成函数、按 id 注册）。要保证：**依赖顺序正确**（被依赖的模块先执行）、**全局变量/IIFE 不冲突**、**sourcemap 正确映射回源码**。产物格式可以是 **IIFE**、**ESM**、**CJS**，由配置的 **output.format** 等决定。

## 八、总结与工具对照

整条管线：**解析 → 转换（Loader/插件）→ 模块图 → Tree-shaking → 分块 → 代码生成**。Webpack 的 loader 链对应「解析+转换」、Module Graph 对应模块图、SplitChunks 对应分块；Vite 开发时跳过打包、按需编译，生产用 Rollup 走完整管线。写插件或排错时，抓住「当前处在哪一阶段、输入输出是什么」，就能快速定位问题。

## 九、延伸阅读

- Webpack 文档：Concepts、Module Graph、Code Splitting。
- Rollup 文档：Plugin API、output options。
- Babel 插件手册：AST 节点类型与 visit 写法。

## 十、实践：写一个简单的 Babel 转换插件

理解 AST 后，可以写一个最小 Babel 插件：用 **@babel/parser** 解析得到 AST，用 **@babel/traverse** 的 `visitor` 遍历并修改节点（如把某个函数名全部替换），再用 **@babel/generator** 生成代码。插件形式是导出一个函数，返回带 `visitor` 的对象；在 Babel 配置的 `plugins` 里引用即可。这样能直观感受「解析 → 转换 → 生成」的闭环，并推广到 PostCSS、Rollup 的 transform 钩子：本质都是在 AST 或中间表示上做变换，构建管线只是把这些步骤串起来并加上模块图与分块。动手写一个小插件后，再回头看 Webpack/Vite 的文档，会更容易抓住重点。

---