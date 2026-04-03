# GraphQL 完全入门指南：从基础到实战

GraphQL 是一种用于 API 的查询语言。本文将带你从基础到高级，全面掌握 GraphQL。

## 一、GraphQL 基础

### 1. 什么是 GraphQL

```
GraphQL vs REST:

REST:
- GET /api/users - 获取用户列表
- GET /api/users/1 - 获取单个用户
- GET /api/users/1/posts - 获取用户文章
- 问题：过获取（over-fetching）或获取不足（under-fetching）

GraphQL:
- 一个端点：/graphql
- 灵活查询：请求你需要的数据
```

### 2. 第一个 GraphQL 查询

```graphql
# 查询
query {
  user(id: 1) {
    id
    name
    email
    posts {
      title
      content
    }
  }
}

# 响应
{
  "data": {
    "user": {
      "id": 1,
      "name": "John Doe",
      "email": "john@example.com",
      "posts": [
        {
          "title": "First Post",
          "content": "Hello World"
        }
      ]
    }
  }
}
```

### 3. 字段和参数

```graphql
# 基本查询
query {
  user(id: 1) {
    id
    name
  }
}

# 多个查询
query {
  user(id: 1) {
    id
    name
  }
  posts {
    title
  }
}

# 参数
query {
  posts(limit: 5, offset: 0) {
    id
    title
  }
}

# 别名
query {
  user1: user(id: 1) {
    name
  }
  user2: user(id: 2) {
    name
  }
}

# 片段
query {
  user1: user(id: 1) {
    ...userFields
  }
  user2: user(id: 2) {
    ...userFields
  }
}

fragment userFields on User {
  id
  name
  email
}
```

## 二、变量和操作

### 1. 变量

```graphql
# 查询定义变量
query GetUser($userId: ID!) {
  user(id: $userId) {
    id
    name
    email
  }
}

# 变量
{
  "userId": "1"
}

# 多个变量
query GetPosts($limit: Int = 10, $offset: Int = 0) {
  posts(limit: $limit, offset: $offset) {
    id
    title
  }
}

# 变量
{
  "limit": 5,
  "offset": 0
}
```

### 2. 操作名称

```graphql
# 命名查询
query GetUser {
  user(id: 1) {
    name
  }
}

# 多个操作
query GetUser {
  user(id: 1) {
    name
  }
}

query GetPosts {
  posts {
    title
  }
}
```

### 3. 指令

```graphql
# @include 和 @skip
query GetUser($withEmail: Boolean!) {
  user(id: 1) {
    id
    name
    email @include(if: $withEmail)
  }
}

# 变量
{
  "withEmail": true
}

# @skip
query GetUser($skipEmail: Boolean!) {
  user(id: 1) {
    id
    name
    email @skip(if: $skipEmail)
  }
}
```

## 三、变更（Mutation）

### 1. 基础 Mutation

```graphql
# 创建用户
mutation CreateUser {
  createUser(input: {
    name: "Jane Doe",
    email: "jane@example.com"
  }) {
    id
    name
    email
  }
}

# 更新用户
mutation UpdateUser {
  updateUser(id: 1, input: {
    name: "John Smith"
  }) {
    id
    name
  }
}

# 删除用户
mutation DeleteUser {
  deleteUser(id: 1) {
    success
    message
  }
}
```

### 2. Mutation 变量

```graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    name
    email
  }
}

# 变量
{
  "input": {
    "name": "Jane Doe",
    "email": "jane@example.com"
  }
}
```

### 3. 多个 Mutation

```graphql
mutation CreateUserAndPost {
  user: createUser(input: {
    name: "Jane Doe",
    email: "jane@example.com"
  }) {
    id
  }
  
  post: createPost(input: {
    title: "Hello",
    content: "World",
    authorId: 1
  }) {
    id
    title
  }
}
```

## 四、订阅（Subscription）

```graphql
# 订阅新帖子
subscription {
  postCreated {
    id
    title
    author {
      name
    }
  }
}

# 订阅用户更新
subscription {
  userUpdated(userId: 1) {
    id
    name
    email
  }
}

# 带参数的订阅
subscription {
  messageAdded(roomId: "123") {
    id
    content
    sender {
      name
    }
  }
}
```

## 五、Schema 定义

### 1. 类型定义

```graphql
# 对象类型
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
  createdAt: String!
}

# 查询类型
type Query {
  user(id: ID!): User
  users(limit: Int = 10, offset: Int = 0): [User!]!
  post(id: ID!): Post
  posts(limit: Int = 10, offset: Int = 0): [Post!]!
}

# 变更类型
type Mutation {
  createUser(input: CreateUserInput!): User!
  updateUser(id: ID!, input: UpdateUserInput!): User!
  deleteUser(id: ID!): DeleteResponse!
  createPost(input: CreatePostInput!): Post!
}

# 输入类型
input CreateUserInput {
  name: String!
  email: String!
}

input UpdateUserInput {
  name: String
  email: String
}

input CreatePostInput {
  title: String!
  content: String!
  authorId: ID!
}

# 响应类型
type DeleteResponse {
  success: Boolean!
  message: String!
}

# 接口
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

# 联合类型
union SearchResult = User | Post

type Query {
  search(query: String!): [SearchResult!]!
}

# 枚举类型
enum Role {
  ADMIN
  USER
  GUEST
}

type User {
  role: Role!
}
```

## 六、Apollo Server（Node.js）

### 1. 基础设置

```javascript
// server.js
const { ApolloServer, gql } = require('apollo-server');

const typeDefs = gql`
  type Query {
    hello: String
  }
`;

const resolvers = {
  Query: {
    hello: () => 'Hello world!',
  },
};

const server = new ApolloServer({ typeDefs, resolvers });

server.listen().then(({ url }) => {
  console.log(`🚀 Server ready at ${url}`);
});
```

### 2. 完整示例

```javascript
const { ApolloServer, gql } = require('apollo-server');

const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
    posts: [Post!]!
  }

  type Post {
    id: ID!
    title: String!
    content: String!
    author: User!
  }

  type Query {
    user(id: ID!): User
    users: [User!]!
    post(id: ID!): Post
    posts: [Post!]!
  }

  type Mutation {
    createUser(name: String!, email: String!): User!
    createPost(title: String!, content: String!, authorId: ID!): Post!
  }
`;

const users = [
  { id: '1', name: 'John Doe', email: 'john@example.com' },
  { id: '2', name: 'Jane Doe', email: 'jane@example.com' },
];

const posts = [
  { id: '1', title: 'First Post', content: 'Hello World', authorId: '1' },
  { id: '2', title: 'Second Post', content: 'GraphQL is cool', authorId: '2' },
];

const resolvers = {
  Query: {
    user: (_, { id }) => users.find(u => u.id === id),
    users: () => users,
    post: (_, { id }) => posts.find(p => p.id === id),
    posts: () => posts,
  },
  User: {
    posts: (user) => posts.filter(p => p.authorId === user.id),
  },
  Post: {
    author: (post) => users.find(u => u.id === post.authorId),
  },
  Mutation: {
    createUser: (_, { name, email }) => {
      const newUser = {
        id: String(users.length + 1),
        name,
        email,
      };
      users.push(newUser);
      return newUser;
    },
    createPost: (_, { title, content, authorId }) => {
      const newPost = {
        id: String(posts.length + 1),
        title,
        content,
        authorId,
      };
      posts.push(newPost);
      return newPost;
    },
  },
};

const server = new ApolloServer({ typeDefs, resolvers });

server.listen().then(({ url }) => {
  console.log(`🚀 Server ready at ${url}`);
});
```

### 3. 数据源

```javascript
const { ApolloServer, gql } = require('apollo-server');
const { RESTDataSource } = require('apollo-datasource-rest');

class UsersAPI extends RESTDataSource {
  constructor() {
    super();
    this.baseURL = 'https://api.example.com/';
  }

  async getUser(id) {
    return this.get(`users/${id}`);
  }

  async getUsers() {
    return this.get('users');
  }
}

const typeDefs = gql`
  type User {
    id: ID!
    name: String!
    email: String!
  }

  type Query {
    user(id: ID!): User
    users: [User!]!
  }
`;

const resolvers = {
  Query: {
    user: async (_, { id }, { dataSources }) => {
      return dataSources.usersAPI.getUser(id);
    },
    users: async (_, __, { dataSources }) => {
      return dataSources.usersAPI.getUsers();
    },
  },
};

const server = new ApolloServer({
  typeDefs,
  resolvers,
  dataSources: () => ({
    usersAPI: new UsersAPI(),
  }),
});

server.listen().then(({ url }) => {
  console.log(`🚀 Server ready at ${url}`);
});
```

## 七、Apollo Client（React）

### 1. 基础设置

```jsx
// index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import { ApolloClient, InMemoryCache, ApolloProvider } from '@apollo/client';
import App from './App';

const client = new ApolloClient({
  uri: 'http://localhost:4000',
  cache: new InMemoryCache(),
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <ApolloProvider client={client}>
    <App />
  </ApolloProvider>
);
```

### 2. useQuery

```jsx
// App.js
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

function App() {
  const { loading, error, data } = useQuery(GET_USERS);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  return (
    <div>
      <h1>Users</h1>
      <ul>
        {data.users.map(user => (
          <li key={user.id}>
            {user.name} ({user.email})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
```

### 3. useMutation

```jsx
import { useMutation, gql } from '@apollo/client';

const CREATE_USER = gql`
  mutation CreateUser($name: String!, $email: String!) {
    createUser(name: $name, email: $email) {
      id
      name
      email
    }
  }
`;

function CreateUserForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');

  const [createUser, { loading, error, data }] = useMutation(CREATE_USER, {
    update(cache, { data: { createUser } }) {
      cache.modify({
        fields: {
          users(existingUsers = []) {
            const newUserRef = cache.writeFragment({
              data: createUser,
              fragment: gql`
                fragment NewUser on User {
                  id
                  name
                  email
                }
              `,
            });
            return [...existingUsers, newUserRef];
          },
        },
      });
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    createUser({ variables: { name, email } });
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

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
      <button type="submit">Create User</button>
    </form>
  );
}
```

## 八、GraphQL.js（Node.js）

```javascript
const { graphql, buildSchema } = require('graphql');

const schema = buildSchema(`
  type Query {
    hello: String
    user(id: ID!): User
  }

  type User {
    id: ID!
    name: String!
  }
`);

const root = {
  hello: () => 'Hello world!',
  user: ({ id }) => ({
    id,
    name: 'John Doe',
  }),
};

graphql({
  schema,
  source: '{ user(id: "1") { id name } }',
  rootValue: root,
}).then((response) => {
  console.log(response);
});
```

## 九、最佳实践

1. 合理设计 Schema
2. 使用分页
3. 实现缓存
4. 错误处理
5. 认证和授权
6. N+1 查询问题
7. 版本管理
8. 文档化
9. 性能优化
10. 测试

## 十、总结

GraphQL 核心要点：
- 查询语言和 Schema
- 查询、变更、订阅
- 变量和指令
- Apollo Server
- Apollo Client
- 数据源
- 缓存
- 最佳实践

开始用 GraphQL 构建你的 API 吧！
