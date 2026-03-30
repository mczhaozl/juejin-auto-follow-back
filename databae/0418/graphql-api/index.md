# GraphQL 完全指南：API 查询语言与实践

> 深入讲解 GraphQL，包括 Schema 定义、查询语法、Mutations、Subscriptions，以及 Apollo Server/Client 的实际应用和性能优化。

## 一、GraphQL 基础

### 1.1 什么是 GraphQL

API 查询语言：

```
┌─────────────────────────────────────────────────────────────┐
│                    REST vs GraphQL                          │
│                                                              │
│  REST                                                        │
│  GET /users/1          →  返回 user                       │
│  GET /users/1/posts    →  返回 posts                      │
│  GET /users/1/followers → 返回 followers                   │
│                                                              │
│  GraphQL                                                      │
│  POST /graphql                                             │
│  {                                                          │
│    user(id: 1) {                                            │
│      name                                                   │
│      posts { title }                                        │
│      followers { name }                                     │
│    }                                                        │
│  }                                                          │
│  → 一次请求获取所有数据                                      │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 核心概念

| 概念 | 说明 |
|------|------|
| Schema | 类型定义 |
| Query | 查询 |
| Mutation | 修改 |
| Subscription | 订阅 |
| Resolver | 解析器 |

## 二、Schema

### 2.1 类型定义

```graphql
type User {
  id: ID!
  name: String!
  email: String
  age: Int
  posts: [Post!]!
  friends: [User!]!
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!
  comments: [Comment!]!
  createdAt: DateTime!
}

type Comment {
  id: ID!
  text: String!
  author: User!
}

# 标量类型
scalar DateTime
```

### 2.2 Query

```graphql
type Query {
  # 查询单个
  user(id: ID!): User
  
  # 查询列表
  users(limit: Int, offset: Int): [User!]!
  
  # 嵌套查询
  post(id: ID!): Post
  
  # 别名
  userByName(name: String!): User
}
```

### 2.3 Mutation

```graphql
type Mutation {
  # 创建
  createUser(input: CreateUserInput!): User!
  
  # 更新
  updateUser(id: ID!, input: UpdateUserInput!): User!
  
  # 删除
  deleteUser(id: ID!): Boolean!
  
  # 复杂修改
  createPost(input: CreatePostInput!): Post!
}

input CreateUserInput {
  name: String!
  email: String
  age: Int
}
```

## 三、查询

### 3.1 基本查询

```graphql
# 查询单个字段
query {
  user(id: "1") {
    name
  }
}

# 查询多个字段
query {
  user(id: "1") {
    id
    name
    email
  }
}
```

### 3.2 嵌套查询

```graphql
query {
  user(id: "1") {
    name
    posts {
      title
      comments {
        text
        author {
          name
        }
      }
    }
  }
}
```

### 3.3 变量与参数

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    name
    email
  }
}

# 变量
{
  "id": "1"
}
```

### 3.4 别名与片段

```graphql
query {
  user1: user(id: "1") {
    name
  }
  user2: user(id: "2") {
    name
  }
}

# 片段
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

## 四、Apollo Server

### 4.1 快速开始

```javascript
const { ApolloServer, gql } = require('apollo-server')

const typeDefs = gql`
  type Query {
    hello: String
  }
`

const resolvers = {
  Query: {
    hello: () => 'Hello World!'
  }
}

const server = new ApolloServer({
  typeDefs,
  resolvers
})

server.listen().then(({ url }) => {
  console.log(`Server ready at ${url}`)
})
```

### 4.2 完整示例

```javascript
const { ApolloServer, gql } = require('apollo-server')
const { GraphQLScalarType, Kind } = require('graphql')

const typeDefs = gql`
  scalar DateTime

  type User {
    id: ID!
    name: String!
    email: String
    posts: [Post!]!
    createdAt: DateTime!
  }

  type Post {
    id: ID!
    title: String!
    author: User!
    createdAt: DateTime!
  }

  type Query {
    users: [User!]!
    user(id: ID!): User
    posts: [Post!]!
  }

  type Mutation {
    createUser(name: String!, email: String): User!
    createPost(title: String!, authorId: ID!): Post!
  }
`

const users = []
const posts = []

const resolvers = {
  Query: {
    users: () => users,
    user: (_, { id }) => users.find(u => u.id === id),
    posts: () => posts
  },
  
  Mutation: {
    createUser: (_, { name, email }) => {
      const user = { id: String(users.length + 1), name, email }
      users.push(user)
      return user
    },
    createPost: (_, { title, authorId }) => {
      const post = { 
        id: String(posts.length + 1), 
        title, 
        authorId 
      }
      posts.push(post)
      return post
    }
  },
  
  User: {
    posts: (user) => posts.filter(p => p.authorId === user.id)
  },
  
  Post: {
    author: (post) => users.find(u => u.id === post.authorId)
  },
  
  DateTime: new GraphQLScalarType({
    name: 'DateTime',
    serialize(value) {
      return value.toISOString()
    },
    parseValue(value) {
      return new Date(value)
    },
    parseLiteral(ast) {
      if (ast.kind === Kind.STRING) {
        return new Date(ast.value)
      }
    }
  })
}
```

## 五、Apollo Client

### 5.1 基本使用

```javascript
import { ApolloClient, InMemoryCache, gql } from '@apollo/client'

const client = new ApolloClient({
  uri: 'http://localhost:4000/graphql',
  cache: new InMemoryCache()
})

// 查询
const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
      email
      posts {
        title
      }
    }
  }
`

// 执行
const { data } = await client.query({
  query: GET_USER,
  variables: { id: '1' }
})
```

### 5.2 React 集成

```javascript
import { useQuery, gql } from '@apollo/client'

const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
    }
  }
`

function UserList() {
  const { loading, error, data } = useQuery(GET_USERS)

  if (loading) return <p>Loading...</p>
  if (error) return <p>Error: {error.message}</p>

  return (
    <ul>
      {data.users.map(user => (
        <li key={user.id}>{user.name}</li>
      ))}
    </ul>
  )
}
```

## 六、实战案例

### 6.1 认证

```javascript
const server = new ApolloServer({
  typeDefs,
  resolvers,
  context: async ({ req }) => {
    const token = req.headers.authorization
    const user = await verifyToken(token)
    return { user }
  }
})

const resolvers = {
  Query: {
    me: (_, __, { user }) => user
  }
}
```

### 7.1 分页

```graphql
type Query {
  users(limit: Int, offset: Int): UsersConnection!
}

type UsersConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
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

## 七、总结

GraphQL 核心要点：

1. **Schema**：类型定义
2. **Query**：查询
3. **Mutation**：修改
4. **Resolver**：解析器
5. **Apollo**：Server/Client
6. **N+1**：DataLoader

掌握这些，API 开发 so easy！

---

**推荐阅读**：
- [GraphQL 官方文档](https://graphql.org/learn/)
- [Apollo 文档](https://www.apollographql.com/docs/)

**如果对你有帮助，欢迎点赞收藏！**
