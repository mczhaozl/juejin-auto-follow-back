# Ant Design 出了 LLMs.txt：让 Cursor、Windsurf、Claude 更懂组件库

> 介绍 Ant Design 的 LLMs.txt 是什么、两种资源区别，以及在 Cursor/Windsurf/Claude 等工具里如何配置使用。

---

## 一、什么是 LLMs.txt

**LLMs.txt** 是一种面向大语言模型的文档约定：把「人类可读 + 机器可读」的说明放在固定路径（如 `llms.txt`），方便 AI 工具拉取并理解项目或产品。Ant Design 在此基础上，**为组件库提供了一份面向 LLM 的文档**，让 Cursor、Windsurf、Claude Code、Gemini CLI 等工具在写代码、补全、解释时，能更好地理解 Ant Design 的组件、API 和使用方式。

官方说明：

> 我们支持通过 LLMs.txt 文件向大语言模型（LLMs）提供 Ant Design 文档。此功能可帮助 AI 工具更好地理解我们的组件库、API 及使用模式。

也就是说：**把 Ant Design 的文档「喂」给 AI，让它在你的编辑器里给更准的 Ant Design 代码建议。**

---

## 二、Ant Design 提供了哪两种资源

Ant Design 提供**两个 LLMs.txt 相关路由**，按需选用：

| 资源 | 用途 |
|------|------|
| **llms.txt** | 所有组件的**结构化概览** + 各组件文档链接，体积小，适合「让 AI 知道有哪些组件、该查哪一页」。 |
| **llms-full.txt** | **完整文档**，含实现细节与示例，适合需要深入 API、用法时让 AI 直接参考。 |

- 只想**组件名、API 名不写错、跳转对**：用 `llms.txt` 即可。
- 需要 AI **按文档写法生成示例、对齐最新 API**：可配置 `llms-full.txt` 或两者都引用（视工具是否支持多文档）。

具体 URL 以官方文档为准，入口见文末链接。

---

## 三、在各 AI 工具里怎么用

以下用法均来自 [Ant Design 官方 LLMs 指南](https://ant-design.antgroup.com/docs/react/llms-cn)，配置前建议打开该页核对最新说明。

### 3.1 Cursor

在 Cursor 里用 **@Docs** 把 Ant Design 的 LLMs.txt 纳入上下文：

- 在对话或编辑时使用 `@Docs`，填入 Ant Design 提供的 `llms.txt`（或 `llms-full.txt`）的 URL。
- 这样 Cursor 在给 Ant Design 相关代码建议、补全时会参考这份文档。

详见 Cursor 的 [@Docs 功能说明](https://ant-design.antgroup.com/docs/react/llms-cn#cursor)（官方指南内链）。

### 3.2 Windsurf

- 在对话里用 **`@`** 引用，或  
- 在项目下的 **`.windsurf/rules`** 中配置 LLMs.txt 的 URL，让 Windsurf 把 Ant Design 文档纳入记忆/上下文。

详见 [Windsurf Memories](https://ant-design.antgroup.com/docs/react/llms-cn#windsurf)。

### 3.3 Claude Code

在 Claude Code 的 **知识库（Docs / Context Files）** 里，把 Ant Design 的 **LLMs.txt** 加入可用的上下文文件；之后在代码补全与解释时，Claude 会引用这份文档，对 Ant Design 组件和 API 的理解会更一致。

详见 [Claude Code 文档上下文配置](https://ant-design.antgroup.com/docs/react/llms-cn#claude-code)。

### 3.4 Gemini CLI

- 用 **`--context`** 参数传入 LLMs.txt 的 URL，或  
- 在 **`.gemini/config.json`** 里配置该文件路径。

这样 Gemini 在回答和生成代码时会参考 Ant Design 文档。详见 [Gemini CLI 上下文配置](https://ant-design.antgroup.com/docs/react/llms-cn#gemini-cli)。

### 3.5 Trae

把 **LLMs.txt** 放入 Trae 的 **knowledge sources**，并在设置中开启引用，Trae 在生成或分析代码时会更好地对齐 Ant Design 的用法。

详见 [Trae 知识源](https://ant-design.antgroup.com/docs/react/llms-cn#trae)。

### 3.6 Qoder

- 在 **`.qoder/config.yml`** 里把 LLMs.txt 配成外部知识文件，或  
- 在对话里用 **`@docs LLMs.txt`** 临时引用。

详见 [Qoder 配置](https://ant-design.antgroup.com/docs/react/llms-cn#qoder)。

### 3.7 其他支持 LLMs.txt 的工具

只要工具支持「通过 URL 或文件引用 LLMs.txt」，就可以使用 Ant Design 提供的上述路由，让模型在 Ant Design 场景下表现更好。

---

## 四、小结与参考

- **LLMs.txt** 让 AI 工具能直接读取 Ant Design 的文档，从而在 Cursor、Windsurf、Claude 等里给出更贴合的组件与 API 建议。
- Ant Design 提供 **llms.txt**（概览+链接）和 **llms-full.txt**（完整文档），可按需选用。
- 各工具配置方式不同：Cursor 用 @Docs，Windsurf 用 @ 或 rules，Claude Code 用知识库，Gemini/Trae/Qoder 各有自己的配置项；**以官方指南为准**。

**官方入口**：

- [Ant Design LLMs 指南（中文）](https://ant-design.antgroup.com/docs/react/llms-cn) — 含 llms.txt / llms-full.txt 的获取方式及各工具配置说明。

如果你在用 Ant Design + Cursor/Claude 等，不妨按上面步骤把 LLMs.txt 配进去，生成的组件代码会更贴近文档。觉得有用欢迎点赞、收藏。
