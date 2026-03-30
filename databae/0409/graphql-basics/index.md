# GraphQL 基础入门：构建灵活的 API 接口

> 全面介绍 GraphQL 的核心概念、Schema 定义、查询语法，以及与 RESTful 的对比和实际项目应用。

## 一、GraphQL 简介

### 1.1 什么是 GraphQL

GraphQL 是 Facebook 开发的 API 查询语言：

```graphql
# 查询
query {
  user(id: "1") {
    name
    email
    posts {
      title
    }
  }
}

# 响应
{
  "data": {
    "user": {
      "name": "张三",
      "email": "zhangsan@example.com",
      "posts": [
        { "title": "GraphQL 教程" },
        { "title": "React 入门" }
      ]
    }
  }
}
```

### 1.2 REST vs GraphQL

| REST | GraphQL |
|------|---------|
| 多个端点 | 单个端点 |
| 固定返回 | 按需获取 |
| 过度获取 | 精确获取 |

## 二、Schema 定义

### 2.1 基础类型

```graphql
type User {
  id: ID!
  name: String!
  email: String
  age: Int
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!
}

# 根类型
type Query {
  user(id: ID!): User
  users: [User!]!
}

type Mutation {
  createUser(name: String!, email: String!): User!
  deleteUser(id: ID!): Boolean!
}
```

### 2.2 标量类型

```graphql
scalar DateTime

type Event {
  id: ID!
  name: String!
  timestamp: DateTime!
}
```

### 2.3 接口

```graphql
interface Node {
  id: ID!
}

type User implements Node {
  id: ID!
  name: String!
}

type Post implements Node {
  id: ID!
  title: String!
}
```

## 三、查询

### 3.1 基本查询

```graphql
query {
  user(id: "1") {
    name
    email
  }
}
```

### 3.2 参数

```graphql
query {
  posts(limit: 5, offset: 10) {
    title
    author {
      name
    }
  }
}
```

### 3.3 别名

```graphql
query {
  user1: user(id: "1") { name }
  user2: user(id: "2") { name }
}
```

### 3.4 片段

```graphql
fragment UserFields on User {
  id
  name
  email
}

query {
  user(id: "1") {
    ...UserFields
  }
}
```

## 四、变更

### 4.1 Mutation

```graphql
mutation {
  createUser(name: "张三", email: "zhangsan@example.com") {
    id
    name
  }
}
```

### 4.2 更新和删除

```graphql
mutation {
  updateUser(id: "1", name: "李四") {
    id
    name
  }
}

mutation {
  deleteUser(id: "1")
}
```

## 五、订阅

### 5.1 实时更新

```graphql
subscription {
  newPost {
    id
    title
    author {
      name
    }
  }
}
```

## 六、解析器

### 6.1 JavaScript 实现

```javascript
const resolvers = {
  Query: {
    user: (parent, { id }, context) => {
      return db.users.find(id);
    },
    users: () => db.users.findAll(),
  },
  Mutation: {
    createUser: (parent, { name, email }, context) => {
      return db.users.create({ name, email });
    },
  },
  User: {
    posts: (user, args, context) => {
      return db.posts.findByUserId(user.id);
    },
  },
};
```

### 6.2 服务器

```javascript
const { ApolloServer } = require('apollo-server');

const server = new ApolloServer({
  typeDefs,
  resolvers,
});

server.listen().then(({ url }) => {
  console.log(`🚀 Server ready at ${url}`);
});
```

## 七、实战案例

### 7.1 前端请求

```javascript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://localhost:4000/graphql',
  cache: new InMemoryCache(),
});

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      name
      email
      posts {
        title
      }
    }
  }
`;

client.query({
  query: GET_USER,
  variables: { id: '1' },
});
```

### 7.2 嵌套查询优化

```graphql
# 一次获取所有数据
query {
  users {
    name
    posts {
      title
      comments {
        content
      }
    }
  }
}
```

## 八、总结

GraphQL 核心要点：

1. **Schema**：定义类型和关系
2. **Query**：查询数据
3. **Mutation**：修改数据
4. **Subscription**：实时更新
5. **Resolver**：实现业务逻辑

相比 REST，GraphQL 更灵活，特别适合复杂数据场景！

---

**推荐阅读**：
- [GraphQL 官方文档](https://graphql.org/learn/)
- [Apollo Server](https://www.apollographql.com/docs/apollo-server/)

**如果对你有帮助，欢迎点赞收藏！**
