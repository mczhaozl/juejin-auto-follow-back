# GraphQL 实战完全指南：从基础到生产环境

GraphQL 是一种用于 API 的查询语言，让前端可以精确获取所需数据。本文将带你全面掌握 GraphQL。

## 一、GraphQL 基础

### 1. 什么是 GraphQL

GraphQL 是 Facebook 开发的 API 查询语言，提供：
- 精确的数据获取（没有过度获取或获取不足）
- 单一端点
- 强类型系统
- 实时更新（订阅）
- 灵活的查询组合

```
REST API (多个端点):
GET /users
GET /users/1
GET /users/1/posts
GET /posts/1/comments

GraphQL (单一端点):
POST /graphql
{
  user(id: 1) {
    name
    posts {
      title
      comments {
        text
      }
    }
  }
}
```

### 2. 第一个 GraphQL Schema

```graphql
# schema.graphql
type Query {
  hello: String!
  user(id: ID!): User
  users: [User!]!
}

type User {
  id: ID!
  name: String!
  email: String!
  age: Int
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  comments: [Comment!]!
}

type Comment {
  id: ID!
  text: String!
  author: User!
  post: Post!
}
```

### 3. Apollo Server 入门

```javascript
// server.js
const { ApolloServer } = require('@apollo/server');
const { startStandaloneServer } = require('@apollo/server/standalone');

const typeDefs = `#graphql
  type Query {
    hello: String!
    user(id: ID!): User
    users: [User!]!
  }

  type User {
    id: ID!
    name: String!
    email: String!
    age: Int
  }
`;

const users = [
  { id: '1', name: 'Alice', email: 'alice@example.com', age: 30 },
  { id: '2', name: 'Bob', email: 'bob@example.com', age: 25 },
];

const resolvers = {
  Query: {
    hello: () => 'Hello, GraphQL!',
    user: (parent, args) => users.find(u => u.id === args.id),
    users: () => users,
  },
};

const server = new ApolloServer({ typeDefs, resolvers });

async function startServer() {
  const { url } = await startStandaloneServer(server, {
    listen: { port: 4000 },
  });
  console.log(`🚀 Server ready at ${url}`);
}

startServer();
```

```bash
npm install @apollo/server @apollo/server/standalone graphql
node server.js
```

## 二、核心概念

### 1. 查询（Query）

```graphql
# 查询用户
query GetUser {
  user(id: "1") {
    id
    name
    email
    age
  }
}

# 查询多个字段
query GetUsers {
  users {
    id
    name
    posts {
      id
      title
      comments {
        id
        text
      }
    }
  }
}

# 带参数的查询
query GetUserWithPosts($userId: ID!, $postLimit: Int = 10) {
  user(id: $userId) {
    name
    posts(limit: $postLimit) {
      title
    }
  }
}

# 别名
query GetTwoUsers {
  alice: user(id: "1") {
    name
  }
  bob: user(id: "2") {
    name
  }
}

# 片段
query GetUsersWithPosts {
  users {
    ...UserFields
    posts {
      ...PostFields
    }
  }
}

fragment UserFields on User {
  id
  name
  email
}

fragment PostFields on Post {
  id
  title
}
```

### 2. 变更（Mutation）

```graphql
# schema
type Mutation {
  createUser(name: String!, email: String!, age: Int): User!
  updateUser(id: ID!, name: String, email: String, age: Int): User
  deleteUser(id: ID!): Boolean!
  createPost(title: String!, content: String!, authorId: ID!): Post!
}
```

```javascript
// resolvers
const resolvers = {
  Mutation: {
    createUser: (parent, args) => {
      const newUser = {
        id: String(users.length + 1),
        name: args.name,
        email: args.email,
        age: args.age,
      };
      users.push(newUser);
      return newUser;
    },
    updateUser: (parent, args) => {
      const index = users.findIndex(u => u.id === args.id);
      if (index === -1) return null;
      users[index] = { ...users[index], ...args };
      return users[index];
    },
    deleteUser: (parent, args) => {
      const index = users.findIndex(u => u.id === args.id);
      if (index === -1) return false;
      users.splice(index, 1);
      return true;
    },
  },
};
```

```graphql
# 使用变更
mutation CreateUser {
  createUser(name: "Charlie", email: "charlie@example.com", age: 35) {
    id
    name
    email
  }
}

mutation UpdateUser {
  updateUser(id: "1", name: "Alice Smith") {
    id
    name
  }
}

mutation DeleteUser {
  deleteUser(id: "3")
}
```

### 3. 订阅（Subscription）

```graphql
# schema
type Subscription {
  userCreated: User!
  postAdded(userId: ID!): Post!
}
```

```javascript
// 使用 Apollo Server 订阅
const { ApolloServer } = require('@apollo/server');
const { expressMiddleware } = require('@apollo/server/express4');
const { createServer } = require('http');
const { ApolloServerPluginDrainHttpServer } = require('@apollo/server/plugin/drainHttpServer');
const { makeExecutableSchema } = require('@graphql-tools/schema');
const { WebSocketServer } = require('ws');
const { useServer } = require('graphql-ws/lib/use/ws');
const express = require('express');
const { PubSub } = require('graphql-subscriptions');

const pubsub = new PubSub();

const typeDefs = `#graphql
  type Query {
    hello: String!
  }
  
  type Subscription {
    count: Int!
  }
  
  type Mutation {
    incrementCount: Int!
  }
`;

let count = 0;

const resolvers = {
  Query: {
    hello: () => 'Hello World',
  },
  Mutation: {
    incrementCount: () => {
      count++;
      pubsub.publish('COUNT_UPDATED', { count });
      return count;
    },
  },
  Subscription: {
    count: {
      subscribe: () => pubsub.asyncIterator(['COUNT_UPDATED']),
    },
  },
};

const schema = makeExecutableSchema({ typeDefs, resolvers });

async function startServer() {
  const app = express();
  const httpServer = createServer(app);
  
  const wsServer = new WebSocketServer({
    server: httpServer,
    path: '/graphql',
  });
  
  const serverCleanup = useServer({ schema }, wsServer);
  
  const server = new ApolloServer({
    schema,
    plugins: [
      ApolloServerPluginDrainHttpServer({ httpServer }),
      {
        async serverWillStart() {
          return {
            async drainServer() {
              await serverCleanup.dispose();
            },
          };
        },
      },
    ],
  });
  
  await server.start();
  
  app.use('/graphql', express.json(), expressMiddleware(server));
  
  httpServer.listen(4000, () => {
    console.log('🚀 Server ready at http://localhost:4000/graphql');
  });
}

startServer();
```

```graphql
# 订阅
subscription Count {
  count
}

# 触发变更
mutation Increment {
  incrementCount
}
```

## 三、进阶功能

### 1. 输入类型（Input Type）

```graphql
input CreateUserInput {
  name: String!
  email: String!
  age: Int
}

input UpdateUserInput {
  name: String
  email: String
  age: Int
}

type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User
}
```

```graphql
mutation CreateUser {
  createUser(input: {
    name: "Dave"
    email: "dave@example.com"
    age: 28
  }) {
    id
    name
  }
}
```

### 2. 接口和联合类型

```graphql
interface Character {
  id: ID!
  name: String!
}

type Human implements Character {
  id: ID!
  name: String!
  homePlanet: String
}

type Droid implements Character {
  id: ID!
  name: String!
  primaryFunction: String
}

type Query {
  character(id: ID!): Character
  characters: [Character!]!
}

union SearchResult = Human | Droid | Post

type Query {
  search(text: String!): [SearchResult!]!
}
```

```graphql
query GetCharacter {
  character(id: "1") {
    id
    name
    ... on Human {
      homePlanet
    }
    ... on Droid {
      primaryFunction
    }
  }
}

query Search {
  search(text: "an") {
    __typename
    ... on Human {
      name
      homePlanet
    }
    ... on Droid {
      name
      primaryFunction
    }
    ... on Post {
      title
    }
  }
}
```

### 3. 分页

```graphql
type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}

type PostEdge {
  cursor: String!
  node: Post!
}

type PostConnection {
  edges: [PostEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type Query {
  posts(first: Int, after: String, last: Int, before: String): PostConnection!
}
```

```graphql
query GetPosts {
  posts(first: 10, after: "cursor123") {
    edges {
      cursor
      node {
        id
        title
      }
    }
    pageInfo {
      hasNextPage
      endCursor
    }
    totalCount
  }
}
```

### 4. 错误处理

```graphql
type MutationResponse {
  success: Boolean!
  message: String
  code: String
}

type CreateUserResponse implements MutationResponse {
  success: Boolean!
  message: String
  code: String
  user: User
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserResponse!
}
```

```javascript
const resolvers = {
  Mutation: {
    createUser: (parent, args) => {
      if (!args.input.email.includes('@')) {
        return {
          success: false,
          message: 'Invalid email format',
          code: 'INVALID_EMAIL',
          user: null,
        };
      }
      
      const newUser = createUser(args.input);
      return {
        success: true,
        message: 'User created successfully',
        code: 'SUCCESS',
        user: newUser,
      };
    },
  },
};
```

## 四、客户端实战：React + Apollo Client

### 1. 设置 Apollo Client

```javascript
// index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import { ApolloClient, InMemoryCache, ApolloProvider } from '@apollo/client';
import App from './App';

const client = new ApolloClient({
  uri: 'http://localhost:4000/graphql',
  cache: new InMemoryCache(),
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ApolloProvider client={client}>
    <App />
  </ApolloProvider>
);
```

### 2. 使用 Query

```javascript
// Users.js
import { useQuery, gql } from '@apollo/client';

const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
      email
    }
  }
`;

function Users() {
  const { loading, error, data } = useQuery(GET_USERS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <ul>
      {data.users.map(user => (
        <li key={user.id}>
          {user.name} - {user.email}
        </li>
      ))}
    </ul>
  );
}

export default Users;
```

### 3. 使用 Mutation

```javascript
// CreateUser.js
import { useMutation, gql } from '@apollo/client';

const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      success
      message
      user {
        id
        name
      }
    }
  }
`;

const GET_USERS = gql`
  query GetUsers {
    users {
      id
      name
      email
    }
  }
`;

function CreateUser() {
  const [name, setName] = React.useState('');
  const [email, setEmail] = React.useState('');

  const [createUser, { loading, error, data }] = useMutation(CREATE_USER, {
    update(cache, { data: { createUser } }) {
      if (createUser.success) {
        cache.updateQuery({ query: GET_USERS }, (existing) => ({
          users: [...existing.users, createUser.user],
        }));
      }
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createUser({
      variables: {
        input: { name, email },
      },
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="Name"
      />
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <button type="submit" disabled={loading}>
        Create User
      </button>
      {error && <p>Error: {error.message}</p>}
      {data?.createUser.success && <p>{data.createUser.message}</p>}
    </form>
  );
}

export default CreateUser;
```

### 4. 使用 Subscription

```javascript
// CountSubscription.js
import { useSubscription, gql } from '@apollo/client';

const COUNT_SUBSCRIPTION = gql`
  subscription Count {
    count
  }
`;

function CountSubscription() {
  const { data, loading, error } = useSubscription(COUNT_SUBSCRIPTION);

  if (loading) return <p>Waiting for updates...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return <p>Count: {data.count}</p>;
}

export default CountSubscription;
```

## 五、最佳实践

1. 合理设计 Schema
2. 使用分页处理大量数据
3. 实现适当的缓存策略
4. 添加错误处理
5. 使用 Input 类型简化变更
6. 提供接口和联合类型
7. 优化 N+1 查询问题
8. 添加适当的认证和授权
9. 编写测试
10. 监控性能

## 六、总结

GraphQL 核心要点：
- 理解 Schema（类型、查询、变更、订阅）
- 掌握 Resolvers 实现
- 使用 Apollo Server 和 Apollo Client
- 实现分页和错误处理
- 优化 N+1 查询
- 遵循最佳实践

开始用 GraphQL 构建你的 API 吧！
