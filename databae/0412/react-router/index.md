# React Router 6 完全指南：路由配置与数据加载

> 深入讲解 React Router 6，包括路由配置、嵌套路由、loader、action，以及 SPA 应用中的路由最佳实践。

## 一、快速开始

### 1.1 安装

```bash
npm install react-router-dom@6
```

### 1.2 基础配置

```javascript
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './views/Home';
import About from './views/About';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}
```

## 二、路由配置

### 2.1 动态路由

```javascript
<Route path="/user/:id" element={<User />} />

// 获取参数
import { useParams } from 'react-router-dom';

function User() {
  const { id } = useParams();
  return <div>User {id}</div>;
}
```

### 2.2 嵌套路由

```javascript
<Route path="/user" element={<UserLayout />}>
  <Route path="profile" element={<Profile />} />
  <Route path="posts" element={<Posts />} />
</Route>
```

### 2.3 Outlet

```javascript
import { Outlet } from 'react-router-dom';

function UserLayout() {
  return (
    <div>
      <nav>用户导航</nav>
      <Outlet />
    </div>
  );
}
```

## 三、导航

### 3.1 Link

```javascript
import { Link } from 'react-router-dom';

<Link to="/about">关于</Link>
<Link to="/user/123">用户</Link>
```

### 3.2 Navigate

```javascript
import { Navigate } from 'react-router-dom';

function PrivateRoute({ isAuth }) {
  return isAuth ? <Outlet /> : <Navigate to="/login" />;
}
```

### 3.3 编程式导航

```javascript
import { useNavigate } from 'react-router-dom';

function Login() {
  const navigate = useNavigate();
  
  const handleLogin = () => {
    navigate('/dashboard');
  };
}
```

## 四、数据加载

### 4.1 loader

```javascript
import { useLoaderData } from 'react-router-dom';

async function userLoader({ params }) {
  const res = await fetch(`/api/users/${params.id}`);
  return res.json();
}

<Route path="/user/:id" element={<User />} loader={userLoader} />

function User() {
  const user = useLoaderData();
  return <div>{user.name}</div>;
}
```

### 4.2 action

```javascript
async function createAction({ request }) {
  const formData = await request.formData();
  await fetch('/api/users', {
    method: 'POST',
    body: formData
  });
  return redirect('/users');
}

<Route path="/user/new" action={createAction} element={<NewUser />} />
```

## 五、守卫

### 5.1 认证守卫

```javascript
function ProtectedRoute() {
  const { user } = useAuth();
  
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  
  return <Outlet />;
}

<Route element={<ProtectedRoute />}>
  <Route path="/dashboard" element={<Dashboard />} />
</Route>
```

### 5.2 权限守卫

```javascript
function AdminRoute() {
  const { user } = useAuth();
  
  if (user?.role !== 'admin') {
    return <Navigate to="/" replace />;
  }
  
  return <Outlet />;
}
```

## 六、总结

React Router 6 核心要点：

1. **Routes**：替代 Switch
2. ** Outlet**：嵌套路由出口
3. **useParams**：获取参数
4. **loader**：数据加载
5. **action**：表单提交
6. **Navigate**：重定向

掌握这些，React 路由不再难！

---

**推荐阅读**：
- [React Router 官方文档](https://reactrouter.com/)

**如果对你有帮助，欢迎点赞收藏！**
