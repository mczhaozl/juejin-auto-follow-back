# GraphQL vs REST：API 设计架构全面对比

GraphQL 和 REST 是两种主流的 API 设计架构。本文将深入对比它们的特点、优势和适用场景。

## 一、REST 概述

REST（Representational State Transfer）是一种基于 HTTP 协议的 API 设计风格。

### REST 的核心原则

1. **资源（Resources）**：一切皆资源
2. **HTTP 方法**：GET、POST、PUT、DELETE、PATCH
3. **状态码**：200、201、400、404、500 等
4. **无状态**：每个请求包含所有必要信息

### REST API 示例

```javascript
// 获取用户列表
GET /api/users

// 获取单个用户
GET /api/users/1

// 创建用户
POST /api/users
{
  "name": "张三",
  "email": "zhangsan@example.com"
}

// 更新用户
PUT /api/users/1
{
  "name": "张三",
  "email": "zhangsan_new@example.com"
}

// 删除用户
DELETE /api/users/1

// 获取用户的文章
GET /api/users/1/articles

// 获取文章的评论
GET /api/articles/1/comments
```

### REST 的优势

1. **简单易用**：学习曲线低
2. **成熟稳定**：广泛应用，生态完善
3. **缓存友好**：HTTP 缓存机制完善
4. **调试方便**：浏览器直接访问

### REST 的劣势

1. **过度获取（Over-fetching）**：返回不需要的数据
2. **获取不足（Under-fetching）**：需要多次请求
3. **版本管理困难**：API 升级复杂
4. **端点爆炸**：资源关系复杂时端点数量激增

## 二、GraphQL 概述

GraphQL 是 Facebook 开发的一种用于 API 的查询语言。

### GraphQL 的核心概念

1. **Schema（模式）**：定义类型系统
2. **Query（查询）**：获取数据
3. **Mutation（变更）**：修改数据
4. **Subscription（订阅）**：实时数据推送

### GraphQL Schema 示例

```graphql
type User {
  id: ID!
  name: String!
  email: String!
  age: Int
  articles: [Article!]!
  createdAt: String!
}

type Article {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
  createdAt: String!
}

type Comment {
  id: ID!
  content: String!
  author: User!
  article: Article!
  createdAt: String!
}

type Query {
  users: [User!]!
  user(id: ID!): User
  articles: [Article!]!
  article(id: ID!): Article
}

type Mutation {
  createUser(name: String!, email: String!): User!
  updateUser(id: ID!, name: String, email: String): User!
  deleteUser(id: ID!): Boolean!
  createArticle(title: String!, content: String!, authorId: ID!): Article!
}
```

### GraphQL 查询示例

```graphql
# 获取用户列表（只需要 name 和 email）
query {
  users {
    id
    name
    email
  }
}

# 获取用户及其文章
query {
  user(id: "1") {
    id
    name
    email
    articles {
      id
      title
      createdAt
    }
  }
}

# 获取文章及其作者和评论
query {
  article(id: "1") {
    id
    title
    content
    author {
      id
      name
    }
    comments {
      id
      content
      author {
        id
        name
      }
    }
  }
}

# 使用变量
query GetUser($userId: ID!) {
  user(id: $userId) {
    id
    name
    email
  }
}

# 多个查询
query {
  users {
    id
    name
  }
  articles {
    id
    title
  }
}
```

### GraphQL Mutation 示例

```graphql
# 创建用户
mutation {
  createUser(name: "张三", email: "zhangsan@example.com") {
    id
    name
    email
  }
}

# 更新用户
mutation {
  updateUser(id: "1", name: "张三新", email: "zhangsan_new@example.com") {
    id
    name
    email
  }
}

# 删除用户
mutation {
  deleteUser(id: "1")
}

# 创建文章
mutation {
  createArticle(
    title: "GraphQL 入门",
    content: "GraphQL 是一种 API 查询语言...",
    authorId: "1"
  ) {
    id
    title
    author {
      id
      name
    }
  }
}
```

### GraphQL 的优势

1. **精确获取**：只请求需要的数据
2. **单一端点**：所有请求都走一个端点
3. **类型安全**：强类型系统，自动验证
4. **自我文档化**：Schema 就是文档
5. **批量请求**：一次请求获取多个资源

### GraphQL 的劣势

1. **学习曲线**：需要学习新的概念
2. **复杂度控制**：需要防止复杂查询
3. **缓存困难**：HTTP 缓存不如 REST 简单
4. **文件上传**：需要额外处理

## 三、对比分析

### 1. 数据获取对比

#### REST（多次请求）

```javascript
// 请求 1：获取用户
const user = await fetch('/api/users/1').then(r => r.json());

// 请求 2：获取用户的文章
const articles = await fetch('/api/users/1/articles').then(r => r.json());

// 请求 3：获取每篇文章的评论
for (const article of articles) {
  const comments = await fetch(`/api/articles/${article.id}/comments`).then(r => r.json());
  article.comments = comments;
}
```

#### GraphQL（一次请求）

```graphql
query {
  user(id: "1") {
    id
    name
    email
    articles {
      id
      title
      comments {
        id
        content
      }
    }
  }
}
```

### 2. 过度获取 vs 精确获取

#### REST（过度获取）

```javascript
// GET /api/users/1
{
  "id": 1,
  "name": "张三",
  "email": "zhangsan@example.com",
  "age": 28,
  "address": "北京市",
  "phone": "13800138000",
  "createdAt": "2024-01-01",
  "updatedAt": "2024-01-15"
  // 更多不需要的字段...
}

// 我们只需要 name 和 email
```

#### GraphQL（精确获取）

```graphql
query {
  user(id: "1") {
    name
    email
  }
}

// 返回：
{
  "data": {
    "user": {
      "name": "张三",
      "email": "zhangsan@example.com"
    }
  }
}
```

### 3. 性能对比

| 指标 | REST | GraphQL |
|------|------|---------|
| 请求次数 | 多次 | 一次 |
| 数据传输量 | 通常较大 | 精确控制 |
| 服务器复杂度 | 较低 | 较高 |
| 缓存实现 | 简单 | 较复杂 |

### 4. 适用场景对比

#### REST 适用场景

- 简单的 CRUD 操作
- 资源关系不复杂
- 需要 HTTP 缓存
- 团队熟悉 REST
- 快速原型开发

#### GraphQL 适用场景

- 复杂的数据关系
- 移动端应用（节省带宽）
- 需要灵活的数据查询
- 前后端分离项目
- 需要类型安全

## 四、实战案例

### 1. REST API 实现（Express）

```javascript
const express = require('express');
const app = express();
app.use(express.json());

const users = [
  { id: 1, name: '张三', email: 'zhangsan@example.com' },
  { id: 2, name: '李四', email: 'lisi@example.com' }
];

const articles = [
  { id: 1, title: '文章1', content: '内容1', authorId: 1 },
  { id: 2, title: '文章2', content: '内容2', authorId: 1 }
];

app.get('/api/users', (req, res) => {
  res.json(users);
});

app.get('/api/users/:id', (req, res) => {
  const user = users.find(u => u.id === parseInt(req.params.id));
  if (!user) {
    return res.status(404).json({ error: '用户不存在' });
  }
  res.json(user);
});

app.get('/api/users/:id/articles', (req, res) => {
  const userArticles = articles.filter(a => a.authorId === parseInt(req.params.id));
  res.json(userArticles);
});

app.post('/api/users', (req, res) => {
  const newUser = {
    id: users.length + 1,
    name: req.body.name,
    email: req.body.email
  };
  users.push(newUser);
  res.status(201).json(newUser);
});

app.listen(3000, () => {
  console.log('REST API 服务器运行在 http://localhost:3000');
});
```

### 2. GraphQL API 实现（Apollo Server）

```javascript
const { ApolloServer, gql } = require('apollo-server');

const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
    articles: [Article!]!
  }

  type Article {
    id: ID!
    title: String!
    content: String!
    author: User!
  }

  type Query {
    users: [User!]!
    user(id: ID!): User
    articles: [Article!]!
    article(id: ID!): Article
  }

  type Mutation {
    createUser(name: String!, email: String!): User!
    createArticle(title: String!, content: String!, authorId: ID!): Article!
  }
`;

const users = [
  { id: '1', name: '张三', email: 'zhangsan@example.com' },
  { id: '2', name: '李四', email: 'lisi@example.com' }
];

const articles = [
  { id: '1', title: '文章1', content: '内容1', authorId: '1' },
  { id: '2', title: '文章2', content: '内容2', authorId: '1' }
];

const resolvers = {
  Query: {
    users: () => users,
    user: (_, { id }) => users.find(u => u.id === id),
    articles: () => articles,
    article: (_, { id }) => articles.find(a => a.id === id)
  },
  User: {
    articles: (user) => articles.filter(a => a.authorId === user.id)
  },
  Article: {
    author: (article) => users.find(u => u.id === article.authorId)
  },
  Mutation: {
    createUser: (_, { name, email }) => {
      const newUser = {
        id: String(users.length + 1),
        name,
        email
      };
      users.push(newUser);
      return newUser;
    },
    createArticle: (_, { title, content, authorId }) => {
      const newArticle = {
        id: String(articles.length + 1),
        title,
        content,
        authorId
      };
      articles.push(newArticle);
      return newArticle;
    }
  }
};

const server = new ApolloServer({ typeDefs, resolvers });

server.listen().then(({ url }) => {
  console.log(`GraphQL 服务器运行在 ${url}`);
});
```

### 3. 前端调用示例

#### REST 调用

```javascript
async function fetchUserData(userId) {
  try {
    const user = await fetch(`/api/users/${userId}`).then(r => r.json());
    const articles = await fetch(`/api/users/${userId}/articles`).then(r => r.json());
    
    for (const article of articles) {
      const comments = await fetch(`/api/articles/${article.id}/comments`).then(r => r.json());
      article.comments = comments;
    }
    
    return { user, articles };
  } catch (error) {
    console.error('获取数据失败:', error);
  }
}
```

#### GraphQL 调用

```javascript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://localhost:4000/graphql',
  cache: new InMemoryCache()
});

async function fetchUserData(userId) {
  try {
    const { data } = await client.query({
      query: gql`
        query GetUser($userId: ID!) {
          user(id: $userId) {
            id
            name
            email
            articles {
              id
              title
              comments {
                id
                content
              }
            }
          }
        }
      `,
      variables: { userId }
    });
    return data.user;
  } catch (error) {
    console.error('获取数据失败:', error);
  }
}
```

## 五、最佳实践

### REST 最佳实践

1. **使用正确的 HTTP 方法**

```javascript
// ✅ 正确
GET /api/users          // 获取列表
GET /api/users/:id      // 获取单个
POST /api/users         // 创建
PUT /api/users/:id      // 完整更新
PATCH /api/users/:id    // 部分更新
DELETE /api/users/:id   // 删除
```

2. **使用正确的状态码**

```javascript
// 200 OK - 成功
// 201 Created - 创建成功
// 400 Bad Request - 请求错误
// 401 Unauthorized - 未授权
// 403 Forbidden - 禁止访问
// 404 Not Found - 未找到
// 500 Internal Server Error - 服务器错误
```

3. **版本管理**

```javascript
// URL 版本化
/api/v1/users
/api/v2/users

// 头部版本化
Accept: application/vnd.example.v1+json
```

### GraphQL 最佳实践

1. **复杂度控制**

```javascript
const { ApolloServer, gql } = require('apollo-server');
const depthLimit = require('graphql-depth-limit');

const server = new ApolloServer({
  typeDefs,
  resolvers,
  validationRules: [depthLimit(5)] // 限制查询深度
});
```

2. **分页实现**

```graphql
type Query {
  users(first: Int, after: String): UserConnection!
}

type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
}

type UserEdge {
  cursor: String!
  node: User!
}

type PageInfo {
  hasNextPage: Boolean!
  endCursor: String
}
```

3. **错误处理**

```javascript
const resolvers = {
  Query: {
    user: async (_, { id }) => {
      const user = await getUser(id);
      if (!user) {
        throw new Error('用户不存在');
      }
      return user;
    }
  }
};
```

## 六、混合使用

很多项目会同时使用 REST 和 GraphQL：

```javascript
// GraphQL：复杂查询
query {
  dashboard {
    user { name }
    stats { views, likes }
    recentPosts { title, date }
  }
}

// REST：文件上传
POST /api/upload
Content-Type: multipart/form-data

// REST：简单的 CRUD
GET /api/config
PUT /api/settings
```

## 七、总结

| 特性 | REST | GraphQL |
|------|------|---------|
| 学习曲线 | 低 | 中 |
| 请求次数 | 多次 | 一次 |
| 数据获取 | 可能过度 | 精确 |
| 类型安全 | 否 | 是 |
| 缓存 | 简单 | 较复杂 |
| 生态 | 成熟 | 快速发展 |
| 适用场景 | 简单 CRUD | 复杂查询 |

**选择建议：**

- **简单项目**：使用 REST，快速上手
- **复杂应用**：使用 GraphQL，灵活高效
- **混合方案**：核心功能用 GraphQL，简单功能用 REST

没有最好的，只有最适合的！根据项目需求选择合适的架构。

## 参考资料

- [REST API 设计指南](https://restfulapi.net/)
- [GraphQL 官方文档](https://graphql.org/)
- [Apollo GraphQL](https://www.apollographql.com/)
- [GitHub GraphQL API](https://docs.github.com/en/graphql)
