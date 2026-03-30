# Vue Router 4 完全指南：路由配置与导航守卫

> 深入讲解 Vue Router 4，包括路由配置、动态路由、嵌套路由、导航守卫，以及路由守卫的实战应用。

## 一、快速开始

### 1.1 安装

```bash
npm install vue-router@4
```

### 1.2 基础配置

```javascript
import { createRouter, createWebHistory } from 'vue-router';
import Home from './views/Home.vue';
import About from './views/About.vue';

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
```

## 二、路由配置

### 2.1 动态路由

```javascript
const routes = [
  { path: '/user/:id', component: User },
  { path: '/post/:category/:id', component: Post }
];

// 获取参数
const User = {
  template: '<div>User {{ $route.params.id }}</div>'
};
```

### 2.2 路由props

```javascript
const routes = [
  { path: '/user/:id', component: User, props: true }
];

const User = {
  props: ['id'],
  template: '<div>User {{ id }}</div>'
};
```

### 2.3 嵌套路由

```javascript
const routes = [
  {
    path: '/user/:id',
    component: User,
    children: [
      { path: 'profile', component: UserProfile },
      { path: 'posts', component: UserPosts }
    ]
  }
];
```

## 三、编程式导航

### 3.1 跳转

```javascript
router.push('/home');
router.push({ path: '/home' });
router.push({ name: 'Home' });

router.replace('/about');
router.go(-1);
```

### 3.2 导航参数

```javascript
router.push({
  name: 'User',
  params: { id: 123 },
  query: { page: 1 }
});
```

## 四、导航守卫

### 4.1 全局守卫

```javascript
// 全局前置守卫
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !isAuthenticated) {
    next('/login');
  } else {
    next();
  }
});

// 全局解析守卫
router.beforeResolve(async (to, from, next) => {
  // 导航确认前执行
  next();
});

// 全局后置钩子
router.afterEach((to, from) => {
  document.title = to.meta.title || 'App';
});
```

### 4.2 路由独享守卫

```javascript
const routes = [
  {
    path: '/admin',
    component: Admin,
    beforeEnter: (to, from, next) => {
      if (isAdmin) {
        next();
      } else {
        next('/');
      }
    }
  }
];
```

### 4.3 组件内守卫

```javascript
const User = {
  beforeRouteEnter(to, from, next) {
    next(vm => {
      console.log(vm);
    });
  },
  beforeRouteUpdate(to, from, next) {
    this.id = to.params.id;
    next();
  },
  beforeRouteLeave(to, from, next) {
    if (hasChanges) {
      next(false);
    } else {
      next();
    }
  }
};
```

## 五、元信息

### 5.1 定义meta

```javascript
const routes = [
  {
    path: '/admin',
    component: Admin,
    meta: { requiresAuth: true, title: '管理后台' }
  }
];
```

### 5.2 访问meta

```javascript
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth) {
    // 需要认证
  }
  next();
});
```

## 六、路由懒加载

### 6.1 方式

```javascript
const Home = () => import('./views/Home.vue');
const About = () => import('./views/About.vue');

const routes = [
  { path: '/', component: Home },
  { path: '/about', component: About }
];
```

### 6.2 分组

```javascript
const Admin = () => import(/* webpackChunkName: "admin" */ './views/Admin.vue');
const User = () => import(/* webpackChunkName: "user" */ './views/User.vue');
```

## 七、总结

Vue Router 核心要点：

1. **动态路由**：/:id 参数
2. **嵌套路由**：children
3. **导航守卫**：beforeEach/afterEach
4. **编程式导航**：push/replace
5. **元信息**：meta 字段
6. **懒加载**：() => import()

掌握这些，Vue 路由不再难！

---

**推荐阅读**：
- [Vue Router 官方文档](https://router.vuejs.org/)

**如果对你有帮助，欢迎点赞收藏！**
