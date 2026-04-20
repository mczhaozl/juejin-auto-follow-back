# MongoDB 向量搜索完全指南

## 一、创建向量搜索索引

```javascript
// 1. 定义 Atlas Search 索引
db.createIndex(
  {
    "embedding": "vector",
  },
  {
    "name": "vector_search_index",
    "type": "vectorSearch",
    "fields": [
      {
        "type": "vector",
        "path": "embedding",
        "numDimensions": 1536,
        "similarity": "cosine"
      }
    ]
  }
);
```

## 二、向量搜索查询

```javascript
// 查询相似文档
db.collection.aggregate([
  {
    $vectorSearch: {
      queryVector: [0.1, 0.2, 0.3], // 嵌入向量
      path: "embedding",
      numCandidates: 100,
      index: "vector_search_index",
      limit: 10
    }
  },
  { $project: { _id: 1, title: 1, score: { $meta: "vectorSearchScore" } } }
]);
```

## 三、混合搜索

```javascript
// 向量搜索 + 关键词过滤
db.collection.aggregate([
  {
    $vectorSearch: { /* ... */ }
  },
  { $match: { category: "tech" } },
  { $sort: { score: -1 } }
]);
```

## 四、嵌入生成

```javascript
// 使用 OpenAI 生成嵌入
import OpenAI from "openai";
const openai = new OpenAI();

async function embed(text: string) {
  const res = await openai.embeddings.create({
    model: "text-embedding-ada-002",
    input: text
  });
  return res.data[0].embedding;
}

// 插入带嵌入的文档
db.collection.insertOne({
  title: "Hello World",
  embedding: await embed("Hello World")
});
```

## 五、最佳实践

- 选择合适的相似度（cosine, dotProduct, euclidean）
- 优化维度数和精度
- 使用混合搜索提高准确性
- 监控索引性能
- 考虑查询缓存
