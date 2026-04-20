# React Redux Toolkit 完全指南

## 一、创建 Store

```ts
// store.ts
import { configureStore } from '@reduxjs/toolkit';
import userReducer from './userSlice';

export const store = configureStore({
  reducer: {
    user: userReducer,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

## 二、创建 Slice

```ts
// userSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';

interface User {
  id: number;
  name: string;
}

interface UserState {
  currentUser: User | null;
  loading: boolean;
}

const initialState: UserState = {
  currentUser: null,
  loading: false,
};

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUser: (state, action: PayloadAction<User>) => {
      state.currentUser = action.payload;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
  },
});

export const { setUser, setLoading } = userSlice.actions;
export default userSlice.reducer;
```

## 三、React 组件使用

```tsx
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store';

function UserProfile() {
  const user = useSelector((state: RootState) => state.user.currentUser);
  const dispatch = useDispatch<AppDispatch>();

  const handleLogin = () => {
    dispatch(setUser({ id: 1, name: 'Alice' }));
  };

  return (
    <div>
      {user ? <h1>Hello, {user.name}</h1> : <button onClick={handleLogin}>Login</button>}
    </div>
  );
}
```

## 四、RTK Query - API 数据获取

```ts
// services/api.ts
import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react';

interface Post {
  id: number;
  title: string;
}

export const api = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({ baseUrl: '/api' }),
  endpoints: (builder) => ({
    getPosts: builder.query<Post[], void>({
      query: () => '/posts',
    }),
    addPost: builder.mutation({
      query: (post) => ({
        url: '/posts',
        method: 'POST',
        body: post,
      }),
    }),
  }),
});

export const { useGetPostsQuery, useAddPostMutation } = api;
```

```tsx
// 使用
function PostsList() {
  const { data, error, isLoading } = useGetPostsQuery();

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error!</div>;

  return (
    <ul>
      {data?.map(post => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

## 五、配置 Provider

```tsx
import { Provider } from 'react-redux';
import { store } from './store';

function App() {
  return (
    <Provider store={store}>
      <UserProfile />
      <PostsList />
    </Provider>
  );
}
```

## 六、最佳实践

- 使用 createSlice 简化 reducer 逻辑
- 使用 RTK Query 处理 API 调用
- 按功能组织代码
- 利用 Immer 的不可变更新
- 使用 TypeScript 增强类型安全
- 使用 DevTools 调试
