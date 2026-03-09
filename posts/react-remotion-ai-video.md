# 用 React + Remotion 做视频：入门与 AI 驱动生成

> 科普向：Remotion 是什么、能做什么、官方在哪看；从零创建项目、做一个可导出的 demo；并介绍 AI（Remotion Skills）结合 React 做视频的思路与周边生态。

## 一、这东西是什么

**Remotion** 是一个用 **React 组件** 来「写」视频的框架。你可以把它理解成：**视频 = 按时间轴一帧一帧渲染出来的 React 页面**。

- **和传统视频的区别**：传统用 After Effects、Premiere 做剪辑，改文案要重新做一版；用 FFmpeg 写脚本又很难和业务数据、前端技术栈打通。Remotion 把**每一帧**都交给 React 渲染：你用组件描述「这一帧长什么样」，用 **当前帧号**（`useCurrentFrame()`）算动画进度，最后由 Remotion 用 Chromium 逐帧截图并合成 MP4。
- **核心抽象**：  
  - **Composition**：一个「视频画布」，规定宽、高、帧率（fps）、总帧数（durationInFrames）。  
  - **Sequence**：时间轴上的一个片段，在指定帧区间内渲染某个组件，用来排先后顺序。  
  - **useCurrentFrame() / useVideoConfig()**：在组件里拿到当前帧号和画布配置，用来算透明度、位移、缩放等，实现关键帧动画。

所以：**会写 React，就能用同一套技能做可编程、数据驱动的视频**；改数据或文案后重新渲染即可，适合模板化、批量和 CI 集成。

---

## 二、这东西有什么用

- **数据驱动视频**：接口、配置、文案都从 props 或 API 来，改数据即改视频，无需手剪。适合：产品介绍、数据可视化、个性化贺卡、批量短视频。
- **复用前端能力**：CSS、Canvas、SVG、Three.js、Lottie 等都能用，和写页面一致，学习成本低。
- **可编程与自动化**：和 Node 脚本、CI 结合，批量生成不同分辨率、不同文案的视频；也可和 **AI**（如 Remotion Skills 或自建 LLM）结合，用自然语言描述「做一个 15 秒产品介绍」，由 AI 生成脚本，Remotion 负责渲染，实现「描述 → 视频」。

适用人群：前端/全栈、需要做产品动画或批量视频的团队、想用代码替代部分剪辑工作的开发者。

---

## 三、官方链接

- **官网**：https://www.remotion.dev  
- **文档**：https://www.remotion.dev/docs  
- **GitHub**：https://github.com/remotion-dev/remotion  
- **模板/示例**：`npx create-video@latest` 会拉取官方脚手架；文档中有多语言、多分辨率等示例。  
- **Remotion Skills（AI 生成视频）**：见官网或仓库关于 Skills 的说明，用自然语言驱动 Remotion 渲染。

写文时 API 与用法以**当前官方文档**为准。

---

## 四、从零跑起来一个项目

### 环境要求

- **Node.js**：建议 18+（以 Remotion 当前文档为准）。  
- **系统**：macOS / Windows / Linux 均可；渲染依赖 Chromium，首次可能需下载。

### 创建与运行

```bash
npx create-video@latest my-video
cd my-video
npm run dev
```

执行后会在浏览器打开本地预览：左侧是时间轴，右侧是当前帧的 React 渲染结果，改代码会热更新。默认带一个示例 Composition，可直接改着玩。

### 目录结构（常见）

- `src/Root.tsx`：入口，里面对应多个 `<Composition>`，每个代表一个可选的「视频」。  
- `src/Compositions/` 或类似：各个视频的组件，例如 `HelloWorld.tsx`。  
- `remotion.config.ts`：Remotion 配置（如 Chromium 路径、并发数等）。  
- `package.json` 里会有 `remotion`、`@remotion/cli`、`@remotion/bundler` 等依赖。

首次跑通后，你会看到一个几秒的示例动画；接下来就是在组件里用 `useCurrentFrame()` 做自己的内容。

---

## 五、如何做一个 demo 出来

下面是一个**最小可运行 demo**：一个 5 秒的标题渐显 + 一段副标题在 2 秒后出现。

### 1. 在 Root 里注册一个 Composition

在 `src/Root.tsx`（或你项目中的根组件）里增加：

```tsx
import { Composition } from "remotion";
import { MyFirstVideo } from "./Compositions/MyFirstVideo";

export const RemotionRoot: React.FC = () => {
    return (
        <>
            <Composition
                id="MyFirstVideo"
                component={MyFirstVideo}
                durationInFrames={150}
                fps={30}
                width={1920}
                height={1080}
                defaultProps={{ title: "Remotion + React", subtitle: "用代码做视频" }}
            />
        </>
    );
};
```

- `durationInFrames={150}` 且 `fps={30}` → 5 秒。  
- `defaultProps` 会传给下面的 `MyFirstVideo` 组件。

### 2. 写 MyFirstVideo 组件（用帧号做动画）

新建 `src/Compositions/MyFirstVideo.tsx`：

```tsx
import React from "react";
import { useCurrentFrame, useVideoConfig } from "remotion";

export const MyFirstVideo: React.FC<{ title: string; subtitle: string }> = ({ title, subtitle }) => {
    const frame = useCurrentFrame();
    const { fps } = useVideoConfig();

    const titleOpacity = Math.min(1, frame / (fps * 0.8));
    const subtitleStart = fps * 2;
    const subtitleOpacity = frame < subtitleStart ? 0 : Math.min(1, (frame - subtitleStart) / (fps * 0.5));

    return (
        <div style={{ flex: 1, justifyContent: "center", alignItems: "center", display: "flex", flexDirection: "column", background: "#0a0a0a", color: "#fff" }}>
            <div style={{ fontSize: 72, opacity: titleOpacity }}>{title}</div>
            <div style={{ fontSize: 36, marginTop: 24, opacity: subtitleOpacity }}>{subtitle}</div>
        </div>
    );
};
```

- 前 0.8 秒标题渐显；2 秒后副标题渐显。  
- 改 `title`、`subtitle` 或时长，保存即可在预览里看到效果。

### 3. 导出为 MP4

在项目根目录执行：

```bash
npx remotion render MyFirstVideo out/my-first-video.mp4
```

会在 `out/` 下得到 `my-first-video.mp4`。  
服务端批量渲染可用 `@remotion/renderer` 在 Node 里调同样逻辑（见官方文档）。

---

## 六、AI + React 做视频：Remotion Skills 思路

**Remotion Skills** 是 Remotion 官方推出的、用**自然语言**驱动视频生成的方案：你描述「做一个 15 秒的产品介绍，突出三个卖点」，AI 解析意图并生成 Remotion 可用的脚本/结构，再交给 Remotion 渲染。

- **典型流程**：用户输入描述 → LLM 输出分镜或组件配置（如每段文案、时长）→ 映射成 `Sequence` 和组件 props → Remotion 渲染。  
- **自建方式**：不用官方 Skills 时，可用任意 LLM API 根据描述生成 JSON（每段文案、时长、图片 URL 等），再在 Node 里转成 Remotion 的 Composition/Sequence 与 props，用 `@remotion/renderer` 渲染。这样「AI 生成脚本 + React 组件渲染」就打通了，适合产品动画、批量短视频、数据可视化讲解。

---

## 七、周边生态推荐

- **模板**：`create-video` 自带示例；GitHub / 社区有「字幕模板」「数据图表视频」等，可搜 `remotion template`。  
- **相关库**：Remotion 官方包如 `@remotion/lottie`、`@remotion/media-utils` 等，文档中有列表；与 Three.js、Framer Motion 等结合可做更复杂动效。  
- **社区**：GitHub Discussions、Discord（见官网），有问题可查 issue 或提问。  
- **进阶**：服务端渲染（Lambda / 自建 Node）、多分辨率输出、与 CI 集成自动生成发布视频，文档里都有示例。

---

## 八、注意点与总结

- **性能**：复杂动画或大画布会拉长渲染时间，可先用低分辨率预览再全分辨率导出。  
- **字体与资源**：服务端渲染时注意字体路径、图片/视频 URL 在渲染环境可访问。  
- **版本**：Remotion 更新较快，API 以当前官方文档为准。

**总结**：Remotion 用 **React 组件 + 帧号** 描述视频，数据驱动、易和前端与 CI 集成；配合 **AI**（Remotion Skills 或自建 LLM）可实现「描述 → 视频」的自动化。科普部分你只要记住：是什么、有什么用、官方链接、从零跑起来、做一个 demo、周边生态，就能把 Remotion 讲清楚、带读者上手。

如果这篇对你有帮助，欢迎点赞 / 收藏；想深入可看 [Remotion 文档](https://www.remotion.dev/docs) 与 Remotion Skills 相关介绍。

---

**标签**：`React`、`Remotion`、`前端`、`人工智能`、`视频`
