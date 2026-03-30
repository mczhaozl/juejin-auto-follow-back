# GraphQL 完全指南：API 查询语言实战

> 深入讲解 GraphQL，包括 schema 定义、Query/Mutation、Resolver，以及 Apollo Server/Client 的使用和 REST 对比。

## 一、GraphQL 简介

### 1.1 什么是 GraphQL

Facebook 开发的 API 查询语言：

```
REST: 多个端点
GET /users/1
GET /users/1/posts
GET /posts/1/comments

GraphQL: 一个端点
POST /graphql
{
  user(id: "1") {
    name
    posts {
      title
      comments {
        body
      }
    }
  }
}
```

### 1.2 vs REST

| 特性 | REST | GraphQL |
|------|------|---------|
| 数据获取 | 多个端点 | 单个端点 |
| 字段选择 | 固定返回 | 按需获取 |
| 类型 | 无类型 | 强类型 |

## 二、Schema

### 2.1 类型定义

```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!
}

type Query {
  user(id: ID!): User
  users: [User!]!
  post(id: ID!): Post
}

type Mutation {
  createUser(name: String!, email: String): User
  updateUser(id: ID!, name: String): User
  deleteUser(id: ID!): Boolean
}
```

### 2.2 标量类型

```graphql
scalar DateTime

type Post {
  id: ID!
  title: String!
  createdAt: DateTime!
}
```

## 三、Resolver

### 3.1 定义 Resolver

```javascript
const resolvers = {
  Query: {
    user: (_, { id }) => db.users.find(id),
    users: () => db.users.all()
  },
  Mutation: {
    createUser: (_, { name, email }) => {
      const user = { id: generateId(), name, email };
      db.users.save(user);
      return user;
    }
  },
  User: {
    posts: (user) => db.posts.findByUserId(user.id)
  }
};
```

### 3.2 服务端

```javascript
const { ApolloServer } = require('apollo-server');

const server = new ApolloServer({
  typeDefs,
  resolvers
});

server.listen().then(({ url }) => {
  console.log(`Server ready at ${url}`);
});
```

## 四、查询

### 4.1 Query

```graphql
# 查询单个
query GetUser {
  user(id: "1") {
    name
    email
  }
}

# 查询列表
query GetUsers {
  users {
    id
    name
  }
}

# 嵌套查询
query GetUserWithPosts {
  user(id: "1") {
    name
    posts {
      title
    }
  }
}
```

### 4.2 Variables

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    name
  }
}

# Variables
{
  "id": "1"
}
```

## 五、变更

### 5.1 Mutation

```graphql
mutation CreateUser {
  createUser(name: "张三", email: "zhangsan@example.com") {
    id
    name
  }
}
```

### 5.2 Input 类型

```graphql
input CreateUserInput {
  name: String!
  email: String
}

type Mutation {
  createUser(input: CreateUserInput!): User
}
```

## 六、Apollo Client

### 6.1 基础使用

```javascript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client';

const client = new ApolloClient({
  uri: 'http://localhost:4000',
  cache: new InMemoryCache()
});

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      name
      email
    }
  }
`;

const { data } = await client.query({
  query: GET_USER,
  variables: { id: '1' }
});
```

### 6.2 React 集成

```javascript
import { useQuery, gql } from '@apollo/client';

const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
    }
  }
`;

function UserList() {
  const { loading, error, data } = useQuery(GET_USERS);
  
  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error</p>;
  
  return data.users.map(user => <div key={user.id}>{user.name}</div>);
}
```

## 七、总结

GraphQL 核心要点：

1. **Schema**：类型定义
2. **Query**：查询
3. **Mutation**：变更
4. **Resolver**：数据解析
5. **Apollo**：全栈方案

掌握这些，API 开发更灵活！

---

**推荐阅读**：
- [GraphQL 官方文档](https://graphql.org/learn/)

**如果对你有帮助，欢迎点赞收藏！**
