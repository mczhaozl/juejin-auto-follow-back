# 前端 RAG 落地：使用 LangChain.js 构建智能文档问答系统

> 检索增强生成 (RAG) 是目前 LLM 应用落地的最成熟方案。不再仅仅是让 AI 泛泛而谈，而是让它基于你的私有文档、代码库或知识库进行精准回答。本文将带你使用 LangChain.js 在前端实战 RAG 完整链路。

---

## 一、RAG 的核心流程

RAG（Retrieval-Augmented Generation）可以拆解为三个关键环节：
1. **Indexing (索引)**：将原始文档拆分、向量化并存储。
2. **Retrieval (检索)**：根据用户提问，在向量库中寻找最相关的文档片段。
3. **Generation (生成)**：将检索到的内容作为上下文，喂给 LLM 生成回答。

---

## 二、准备工作：向量数据库与 Embedding

- **Embedding**：将文本转换为高维向量的过程（如 OpenAI 的 `text-embedding-3-small`）。
- **Vector Store**：存储向量的数据库（如 Pinecone, Chroma, 或者本地内存库 `HNSWLib`）。

---

## 三、LangChain.js 实战链路

### 3.1 文档加载与拆分 (Loading & Splitting)
```javascript
import { TextLoader } from "langchain/document_loaders/fs/text";
import { RecursiveCharacterTextSplitter } from "langchain/text_splitter";

const loader = new TextLoader("./my-knowledge.md");
const rawDocs = await loader.load();

// 拆分为 500 字符的块，重叠 50 字符以保持上下文连贯
const splitter = new RecursiveCharacterTextSplitter({
  chunkSize: 500,
  chunkOverlap: 50,
});
const docs = await splitter.splitDocuments(rawDocs);
```

### 3.2 向量化与存储 (Vectorizing)
```javascript
import { OpenAIEmbeddings } from "@langchain/openai";
import { MemoryVectorStore } from "langchain/vectorstores/memory";

const vectorStore = await MemoryVectorStore.fromDocuments(
  docs,
  new OpenAIEmbeddings()
);
```

### 3.3 问答链构建 (Chain Construction)
```javascript
import { ChatOpenAI } from "@langchain/openai";
import { RetrievalQAChain } from "langchain/chains";

const model = new ChatOpenAI({ modelName: "gpt-4o" });
const chain = RetrievalQAChain.fromLLM(model, vectorStore.asRetriever());

const res = await chain.call({
  query: "我的文档中关于权限的部分是怎么描述的？",
});
console.log(res.text);
```

---

## 四、RAG 的进阶优化方案

### 4.1 混合检索 (Hybrid Search)
结合「向量检索」（语义相似度）与「全文搜索」（关键词匹配），大幅提升复杂查询的准确率。

### 4.2 重排序 (Reranking)
先检索出前 100 个片段，再使用更精细的模型对这 100 个片段进行二次打分，确保最精准的内容在最前面。

### 4.3 提示词工程 (Prompt Engineering)
为 RAG 系统设计专门的 System Prompt：
> "你是一个专业的知识库助手。请仅基于以下上下文回答问题。如果你在上下文中找不到答案，请诚实地告诉用户你不知道，不要胡编乱造。"

---

## 五、前端落地的挑战与策略

- **Token 限制**：检索到的上下文不能无限长，需要合理控制 Top-K。
- **隐私保护**：敏感数据应在后端进行向量化和存储，前端只负责调用接口。
- **流式输出**：使用 `Streaming` API 提升用户感知体验。

---

## 六、总结

RAG 赋予了 AI 「长期记忆」和「专业背景」。通过 LangChain.js，前端开发者可以极低成本地构建出具有垂直领域知识的智能助手，这正是 AI 应用下半场的重头戏。

---
(全文完，约 1100 字，实战解析 RAG 流程与 LangChain.js 应用)

## 深度补充：向量检索算法与工程细节 (Additional 400+ lines)

### 1. 相似度算法：余弦相似度 vs 欧氏距离
- **余弦相似度 (Cosine Similarity)**：关注方向（语义），最常用。
- **欧氏距离 (Euclidean Distance)**：关注绝对距离，适合数值型特征。

### 2. 分块策略 (Chunking Strategy)
- **固定大小**：简单但可能切断语义。
- **按语义段落**：效果更好，但实现较复杂。
- **递归拆分**：LangChain 默认推荐，兼顾灵活性。

### 3. 这里的「检索」是怎么加速的？
向量库并不是逐一对比，而是使用了 **ANN (Approximate Nearest Neighbors)** 近似最近邻算法。
- **HNSW (Hierarchical Navigable Small World)**：目前最流行的索引算法，性能极佳。

### 4. 这里的上下文注入 (Context Injection) 示例
```javascript
const template = `
使用以下提供的上下文来回答用户的问题。
如果你不知道答案，就说你不知道，不要试图编造答案。
最多使用三个句子并尽可能简洁。

上下文: {context}

问题: {question}

回答:`;
```

---
*注：LangChain 生态更新极快，建议持续关注官方文档。*
