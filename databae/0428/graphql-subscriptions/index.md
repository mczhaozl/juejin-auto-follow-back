# GraphQL Subscriptions 实时通信完全指南：从 WebSocket 到实战

## 一、Subscriptions 概述

GraphQL Subscriptions 是用于实时数据推送的功能，基于 WebSocket 协议。

### 1.1 三种操作类型对比

| 类型 | 用途 | HTTP 方法 |
|-----|------|---------|
| Query | 查询数据 | GET |
| Mutation | 修改数据 | POST |
| Subscription | 实时推送 | WebSocket |

### 1.2 核心概念

- **发布-订阅模式**：服务端推送事件
- **WebSocket**：双向通信
- **实时更新**：数据变化时主动通知

---

## 二、基础实现（Node.js）

### 2.1 Schema 定义

```graphql
type Subscription {
  messageAdded(channelId: ID!): Message!
  userOnlineStatusChanged: UserStatus!
}

type Message {
  id: ID!
  content: String!
  user: User!
  channelId: ID!
}
```

### 2.2 服务端实现

```javascript
import { createServer } from 'http';
import { execute, subscribe } from 'graphql';
import { SubscriptionServer } from 'subscriptions-transport-ws';
import { makeExecutableSchema } from '@graphql-tools/schema';

const typeDefs = `
  type Query {
    dummy: String
  }
  type Subscription {
    countdown(from: Int!): Int!
  }
`;

const resolvers = {
  Subscription: {
    countdown: {
      subscribe: async function* (_, { from }) {
        for (let i = from; i >= 0; i--) {
          await new Promise(resolve => setTimeout(resolve, 1000));
          yield { countdown: i };
        }
      }
    }
  }
};

const schema = makeExecutableSchema({ typeDefs, resolvers });

const server = createServer();

SubscriptionServer.create(
  {
    schema,
    execute,
    subscribe,
    onConnect: (connectionParams) => {
      console.log('Client connected');
    },
    onDisconnect: () => {
      console.log('Client disconnected');
    }
  },
  { server, path: '/graphql' }
);

server.listen(4000, () => console.log('Server on port 4000'));
```

---

## 三、使用 Apollo Server

### 3.1 Apollo Server 配置

```javascript
import { ApolloServer } from '@apollo/server';
import { startStandaloneServer } from '@apollo/server/standalone';
import { useServer } from 'graphql-ws/lib/use/ws';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';

const typeDefs = `
  type Message {
    id: ID!
    content: String!
  }
  type Subscription {
    messageAdded: Message!
  }
  type Query {
    _: Boolean
  }
`;

const resolvers = {
  Subscription: {
    messageAdded: {
      subscribe: () => pubsub.subscribe('MESSAGE_ADDED'),
      resolve: (payload) => payload
    }
  }
};

const httpServer = createServer();

const wsServer = new WebSocketServer({ server: httpServer, path: '/graphql' });
useServer({ schema }, wsServer);

const server = new ApolloServer({ typeDefs, resolvers });
const { url } = await startStandaloneServer(server, { listen: { port: 4000 } });
console.log(url);
```

---

## 四、实时聊天应用实战

### 4.1 完整 Schema

```graphql
type User {
  id: ID!
  name: String!
}

type Message {
  id: ID!
  content: String!
  user: User!
  channelId: ID!
  createdAt: String!
}

type Query {
  channelMessages(channelId: ID!): [Message!]!
}

type Mutation {
  sendMessage(content: String!, channelId: ID!): Message!
}

type Subscription {
  messageAdded(channelId: ID!): Message!
  userOnline: User!
}
```

### 4.2 发布订阅实现

```javascript
import { PubSub } from 'graphql-subscriptions';

const pubsub = new PubSub();

const resolvers = {
  Query: {
    channelMessages: (_, { channelId }) => getMessages(channelId)
  },
  Mutation: {
    sendMessage: async (_, { content, channelId }, { user }) => {
      const message = await createMessage({ content, channelId, userId: user.id });
      pubsub.publish(`MESSAGE_ADDED_${channelId}`, { messageAdded: message });
      return message;
    }
  },
  Subscription: {
    messageAdded: {
      subscribe: (_, { channelId }) => 
        pubsub.asyncIterator(`MESSAGE_ADDED_${channelId}`),
    }
  }
};
```

---

## 五、客户端实现

### 5.1 React + Apollo Client

```jsx
import { ApolloClient, InMemoryCache, ApolloProvider, split, HttpLink } from '@apollo/client';
import { getMainDefinition } from '@apollo/client/utilities';
import { GraphQLWsLink } from '@apollo/client/link/subscriptions';
import { createClient } from 'graphql-ws';

const httpLink = new HttpLink({ uri: 'http://localhost:4000/graphql' });
const wsLink = new GraphQLWsLink(createClient({ url: 'ws://localhost:4000/graphql' }));

const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return definition.kind === 'OperationDefinition' && definition.operation === 'subscription';
  },
  wsLink,
  httpLink
);

const client = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache()
});

function App() {
  return (
    <ApolloProvider client={client}>
      <Chat />
    </ApolloProvider>
  );
}
```

### 5.2 使用 Subscription Hook

```jsx
import { useSubscription, gql } from '@apollo/client';

const MESSAGE_ADDED_SUBSCRIPTION = gql`
  subscription MessageAdded($channelId: ID!) {
    messageAdded(channelId: $channelId) {
      id
      content
      user { name }
    }
  }
`;

function Chat({ channelId }) {
  useSubscription(MESSAGE_ADDED_SUBSCRIPTION, {
    variables: { channelId },
    onData: ({ data }) => {
      console.log('New message:', data);
    }
  });
  // ...
}
```

---

## 六、高级场景

### 6.1 过滤与条件订阅

```javascript
Subscription: {
  messageAdded: {
    subscribe: withFilter(
      () => pubsub.asyncIterator('MESSAGE_ADDED'),
      (payload, variables) => payload.channelId === variables.channelId
    )
  }
}
```

### 6.2 连接认证

```javascript
SubscriptionServer.create({
  schema,
  execute,
  subscribe,
  onConnect: async (connectionParams) => {
    const user = await validateToken(connectionParams.token);
    if (!user) throw new Error('Unauthorized');
    return { user };
  }
})
```

---

## 七、最佳实践

1. **用 Redis PubSub 扩展**（多实例场景）
2. **正确处理连接中断**
3. **避免发送过大的更新**
4. **认证在 onConnect 中完成**

---

## 八、总结

GraphQL Subscriptions 是构建实时应用的强大工具，通过 WebSocket 提供了优雅的实时通信方案。
