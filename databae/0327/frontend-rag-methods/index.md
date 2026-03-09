# 面向前端的 9 大 RAG 进阶方法

> 介绍 RAG（检索增强生成）在前端场景的 9 种进阶优化方法，提升 AI 应用的准确性和用户体验。

---

## 一、什么是 RAG

RAG（Retrieval-Augmented Generation）= 检索 + 生成，核心思路：

1. 从知识库检索相关内容
2. 将检索结果作为上下文
3. 让 LLM 基于上下文生成回答

前端场景：文档问答、代码助手、客服机器人等。

## 二、基础 RAG 流程

```javascript
async function basicRAG(query) {
  // 1. 向量化查询
  const queryEmbedding = await getEmbedding(query);
  
  // 2. 检索相关文档
  const docs = await vectorDB.search(queryEmbedding, topK: 3);
  
  // 3. 构造 prompt
  const context = docs.map(d => d.content).join('\n\n');
  const prompt = `基于以下内容回答问题：\n${context}\n\n问题：${query}`;
  
  // 4. 调用 LLM
  const answer = await llm.generate(prompt);
  return answer;
}
```

问题：准确率不高、响应慢、成本高。下面介绍 9 种进阶方法。

## 三、方法 1：混合检索（Hybrid Search）

### 问题

纯向量检索可能漏掉关键词匹配的结果。

### 方案

结合向量检索（语义）+ 关键词检索（精确）：

```javascript
async function hybridSearch(query, topK = 5) {
  // 向量检索
  const vectorResults = await vectorDB.search(query, topK);
  
  // 关键词检索（BM25）
  const keywordResults = await fullTextSearch(query, topK);
  
  // 融合排序（RRF: Reciprocal Rank Fusion）
  const merged = mergeResults(vectorResults, keywordResults);
  
  return merged.slice(0, topK);
}

function mergeResults(vectorResults, keywordResults) {
  const scores = new Map();
  
  vectorResults.forEach((doc, rank) => {
    scores.set(doc.id, (scores.get(doc.id) || 0) + 1 / (rank + 60));
  });
  
  keywordResults.forEach((doc, rank) => {
    scores.set(doc.id, (scores.get(doc.id) || 0) + 1 / (rank + 60));
  });
  
  return Array.from(scores.entries())
    .sort((a, b) => b[1] - a[1])
    .map(([id]) => findDocById(id));
}
```

## 四、方法 2：查询改写（Query Rewriting）

### 问题

用户输入可能不清晰或表达不准确。

### 方案

用 LLM 改写查询，生成多个变体：

```javascript
async function rewriteQuery(originalQuery) {
  const prompt = `
将以下查询改写为 3 个不同表达方式，保持语义：
原查询：${originalQuery}

改写 1:
改写 2:
改写 3:
`;

  const rewrites = await llm.generate(prompt);
  return [originalQuery, ...parseRewrites(rewrites)];
}

async function multiQueryRAG(query) {
  // 生成多个查询
  const queries = await rewriteQuery(query);
  
  // 并行检索
  const allDocs = await Promise.all(
    queries.map(q => vectorDB.search(q, topK: 2))
  );
  
  // 去重合并
  const uniqueDocs = deduplicateDocs(allDocs.flat());
  
  // 生成答案
  return generateAnswer(query, uniqueDocs);
}
```

## 五、方法 3：重排序（Reranking）

### 问题

向量检索的 top-K 结果可能不是最相关的。

### 方案

用专门的重排序模型（如 Cohere Rerank、BGE Reranker）：

```javascript
async function rerankResults(query, docs) {
  // 调用重排序 API
  const response = await fetch('https://api.cohere.ai/v1/rerank', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      query,
      documents: docs.map(d => d.content),
      top_n: 3
    })
  });
  
  const { results } = await response.json();
  
  // 返回重排序后的文档
  return results.map(r => docs[r.index]);
}

async function ragWithRerank(query) {
  const docs = await vectorDB.search(query, topK: 10);
  const rerankedDocs = await rerankResults(query, docs);
  return generateAnswer(query, rerankedDocs);
}
```

## 六、方法 4：分块策略优化

### 问题

分块太大：上下文冗余，成本高
分块太小：语义不完整

### 方案

滑动窗口 + 父子文档：

```javascript
function chunkWithOverlap(text, chunkSize = 500, overlap = 50) {
  const chunks = [];
  let start = 0;
  
  while (start < text.length) {
    const end = start + chunkSize;
    const chunk = text.slice(start, end);
    chunks.push({
      content: chunk,
      start,
      end,
      parentDoc: text // 保留完整文档引用
    });
    start += chunkSize - overlap; // 重叠部分
  }
  
  return chunks;
}

// 检索时返回小块，生成时用父文档
async function ragWithParentDoc(query) {
  const smallChunks = await vectorDB.search(query, topK: 3);
  
  // 获取父文档（更完整的上下文）
  const parentDocs = smallChunks.map(chunk => chunk.parentDoc);
  
  return generateAnswer(query, parentDocs);
}
```

## 七、方法 5：元数据过滤

### 问题

检索结果可能包含不相关的文档类型或时间范围。

### 方案

在检索时加入元数据过滤：

```javascript
async function searchWithMetadata(query, filters) {
  const queryEmbedding = await getEmbedding(query);
  
  const results = await vectorDB.search({
    vector: queryEmbedding,
    filter: {
      // 文档类型
      type: { $in: filters.types || ['doc', 'api'] },
      // 时间范围
      createdAt: { $gte: filters.startDate },
      // 标签
      tags: { $contains: filters.tag }
    },
    topK: 5
  });
  
  return results;
}

// 使用
const docs = await searchWithMetadata('React Hooks 用法', {
  types: ['tutorial', 'api'],
  startDate: '2023-01-01',
  tag: 'react'
});
```

## 八、方法 6：上下文压缩

### 问题

检索到的文档太长，浪费 token。

### 方案

用 LLM 提取关键信息：

```javascript
async function compressContext(query, docs) {
  const prompt = `
从以下文档中提取与问题相关的关键信息：

问题：${query}

文档：
${docs.map((d, i) => `[${i + 1}] ${d.content}`).join('\n\n')}

只保留与问题直接相关的句子，去掉无关内容。
`;

  const compressed = await llm.generate(prompt, { maxTokens: 500 });
  return compressed;
}

async function ragWithCompression(query) {
  const docs = await vectorDB.search(query, topK: 5);
  const compressed = await compressContext(query, docs);
  
  const finalPrompt = `基于以下信息回答：\n${compressed}\n\n问题：${query}`;
  return llm.generate(finalPrompt);
}
```

## 九、方法 7：自我反思（Self-Reflection）

### 问题

LLM 可能生成不准确或不相关的答案。

### 方案

让 LLM 评估自己的答案，必要时重新检索：

```javascript
async function ragWithReflection(query, maxRetries = 2) {
  let attempt = 0;
  
  while (attempt < maxRetries) {
    const docs = await vectorDB.search(query, topK: 3);
    const answer = await generateAnswer(query, docs);
    
    // 让 LLM 评估答案质量
    const evaluation = await llm.generate(`
评估以下答案是否充分回答了问题（回答 yes 或 no）：

问题：${query}
答案：${answer}

评估：
`);
    
    if (evaluation.includes('yes')) {
      return answer;
    }
    
    // 改写查询重试
    query = await rewriteQuery(query);
    attempt++;
  }
  
  return answer;
}
```

## 十、方法 8：流式响应

### 问题

等待完整答案时间长，用户体验差。

### 方案

边检索边生成，流式返回：

```javascript
async function* streamingRAG(query) {
  // 1. 快速返回检索状态
  yield { type: 'status', message: '正在检索相关文档...' };
  
  const docs = await vectorDB.search(query, topK: 3);
  
  yield { type: 'docs', data: docs.map(d => d.title) };
  
  // 2. 流式生成答案
  const stream = await llm.generateStream({
    prompt: buildPrompt(query, docs)
  });
  
  for await (const chunk of stream) {
    yield { type: 'answer', data: chunk };
  }
}

// 前端使用
for await (const chunk of streamingRAG(query)) {
  if (chunk.type === 'status') {
    showStatus(chunk.message);
  } else if (chunk.type === 'answer') {
    appendAnswer(chunk.data);
  }
}
```

## 十一、方法 9：缓存优化

### 问题

相同或相似问题重复检索和生成，浪费资源。

### 方案

多级缓存：

```javascript
class RAGCache {
  constructor() {
    this.exactCache = new Map(); // 精确匹配
    this.semanticCache = null; // 语义缓存（向量数据库）
  }

  async get(query) {
    // 1. 精确匹配
    if (this.exactCache.has(query)) {
      return this.exactCache.get(query);
    }
    
    // 2. 语义相似匹配
    const similar = await this.findSimilarQuery(query, threshold: 0.95);
    if (similar) {
      return similar.answer;
    }
    
    return null;
  }

  async set(query, answer) {
    this.exactCache.set(query, answer);
    await this.semanticCache.add({ query, answer });
  }

  async findSimilarQuery(query, threshold) {
    const embedding = await getEmbedding(query);
    const results = await this.semanticCache.search(embedding, topK: 1);
    
    if (results[0]?.score > threshold) {
      return results[0];
    }
    return null;
  }
}

// 使用
const cache = new RAGCache();

async function cachedRAG(query) {
  const cached = await cache.get(query);
  if (cached) return cached;
  
  const answer = await basicRAG(query);
  await cache.set(query, answer);
  return answer;
}
```

## 十二、前端集成示例

```javascript
// 完整的前端 RAG 组件
import { useState } from 'react';

function RAGChat() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setAnswer('');
    
    try {
      // 1. 混合检索
      const docs = await hybridSearch(query);
      
      // 2. 重排序
      const reranked = await rerankResults(query, docs);
      setSources(reranked);
      
      // 3. 流式生成
      for await (const chunk of streamingRAG(query, reranked)) {
        if (chunk.type === 'answer') {
          setAnswer(prev => prev + chunk.data);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input value={query} onChange={e => setQuery(e.target.value)} />
      <button onClick={handleSubmit} disabled={loading}>
        {loading ? '生成中...' : '提问'}
      </button>
      
      {answer && <div className="answer">{answer}</div>}
      
      {sources.length > 0 && (
        <div className="sources">
          <h4>参考来源：</h4>
          {sources.map((doc, i) => (
            <div key={i}>{doc.title}</div>
          ))}
        </div>
      )}
    </div>
  );
}
```

## 总结

9 大进阶方法：

1. 混合检索：向量 + 关键词，提升召回率
2. 查询改写：生成多个变体，覆盖更多表达
3. 重排序：用专门模型提升相关性
4. 分块优化：滑动窗口 + 父子文档
5. 元数据过滤：按类型、时间、标签筛选
6. 上下文压缩：提取关键信息，节省 token
7. 自我反思：评估答案质量，必要时重试
8. 流式响应：边检索边生成，提升体验
9. 缓存优化：精确 + 语义缓存，降低成本

实际应用建议：

- 基础场景：混合检索 + 重排序
- 高准确率：加上查询改写 + 自我反思
- 高性能：加上缓存 + 流式响应
- 成本优化：上下文压缩 + 缓存

根据场景选择合适的组合，逐步优化。
