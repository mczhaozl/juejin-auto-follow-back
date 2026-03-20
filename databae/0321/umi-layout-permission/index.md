# umi/layout：企业级布局与权限控制一体化解决方案

> 深入解析umi/layout如何通过配置化布局、动态菜单、权限控制、面包屑导航等特性，解决企业级应用中布局复杂、权限混乱、菜单动态化等核心难题。

---

## 一、背景：企业级应用布局的挑战

在企业级应用中，我们经常面临以下挑战：

1. **布局复杂**：不同页面需要不同的布局结构
2. **权限控制复杂**：不同角色看到不同的菜单和功能
3. **菜单动态化**：菜单需要根据权限动态生成
4. **面包屑导航**：复杂的路由结构需要清晰的导航
5. **响应式布局**：需要适配不同设备

## 二、umi/layout 核心特性

### 1. 配置化布局

```typescript
// config/config.ts
export default {
  layout: {
    // 基础布局配置
    name: 'Ant Design Pro',
    logo: '/logo.svg',
    layout: 'side',
    contentWidth: 'Fluid',
    fixedHeader: true,
    fixSiderbar: true,
    pwa: true,
    locale: 'zh-CN',
    siderWidth: 208,
  },
  routes: [
    {
      path: '/',
      component: '../layouts/BasicLayout',
      routes: [
        {
          path: '/dashboard',
          name: 'dashboard',
          icon: 'dashboard',
          routes: [
            {
              path: '/dashboard/analysis',
              name: 'analysis',
              component: './Dashboard/Analysis',
            },
          ],
        },
      ],
    },
  ],
};
```

### 2. 动态菜单与权限控制

```typescript
// 动态菜单配置
export const menuData = [
  {
    name: 'dashboard',
    path: '/dashboard',
    icon: 'dashboard',
    children: [
      {
        name: 'analysis',
        path: '/dashboard/analysis',
        authority: ['admin', 'user'], // 权限控制
      },
    ],
  },
  {
    name: 'system',
    path: '/system',
    icon: 'setting',
    children: [
      {
        name: 'user',
        path: '/system/user',
        authority: ['admin'], // 仅管理员可见
      },
    ],
  },
];
```

### 3. 权限控制集成

```typescript
// 权限控制组件
import { Access, useAccess } from 'umi';

// 1. 组件级权限控制
function AdminPage() {
  return (
    <Access accessible={hasPermission('admin')}>
      <AdminContent />
    </Access>
  );
}

// 2. 路由级权限控制
export const routes = [
  {
    path: '/admin',
    component: './Admin',
    wrappers: [
      'wrappers/auth', // 权限校验
      'wrappers/access', // 访问控制
    ],
  },
];
```

## 三、解决的实际问题

### 问题1：复杂的布局需求

**传统方式**：
```jsx
// 每个页面都需要重复的布局代码
function Layout({ children }) {
  return (
    <div className="app">
      <Header />
      <Sidebar />
      <div className="content">
        <Breadcrumb />
        <div className="content-inner">
          {children}
        </div>
      </div>
      <Footer />
    </div>
  );
}
```

**umi/layout 解决方案**：
```typescript
// config/config.ts
export default {
  layout: {
    // 全局布局配置
    layout: 'side',
    // 自动处理布局
  },
  routes: [
    {
      path: '/',
      component: '../layouts/BasicLayout',
      routes: [
        // 自动应用布局
      ],
    },
  ],
};
```

### 问题2：动态菜单与权限

**传统方式**：
```javascript
// 手动管理菜单和权限
const menuItems = [];
if (user.role === 'admin') {
  menuItems.push({ path: '/admin', name: 'Admin' });
}
// 每个页面都要重复权限检查
```

**umi/layout 解决方案**：
```typescript
// 自动根据权限生成菜单
export const menuData = [
  {
    name: 'dashboard',
    path: '/dashboard',
    icon: 'dashboard',
    // 权限控制
    access: 'canViewDashboard',
  },
  {
    name: 'admin',
    path: '/admin',
    icon: 'setting',
    access: 'canViewAdmin', // 权限控制
  },
];

// 自动过滤无权限菜单
const accessibleMenu = menuData.filter(item => 
  checkAccess(item.access)
);
```

### 问题3：面包屑导航

**传统方式**：
```jsx
// 手动管理面包屑
function Breadcrumb() {
  const location = useLocation();
  const pathSnippets = location.pathname.split('/').filter(i => i);
  
  return (
    <Breadcrumb>
      {pathSnippets.map((item, index) => (
        <Breadcrumb.Item key={index}>
          {item}
        </Breadcrumb.Item>
      ))}
    </Breadcrumb>
  );
}
```

**umi/layout 解决方案**：
```typescript
// 自动生成面包屑
import { PageContainer } from '@ant-design/pro-layout';

function Page() {
  return (
    <PageContainer
      header={{
        title: '页面标题',
        breadcrumb: {
          // 自动生成面包屑
          routes: [
            { path: '/', breadcrumbName: '首页' },
            { path: '/dashboard', breadcrumbName: '仪表盘' },
          ],
        },
      }}
    >
      {/* 页面内容 */}
    </PageContainer>
  );
}
```

## 四、高级特性

### 1. 多标签页支持
```typescript
// 配置多标签页
export default {
  layout: {
    // 开启多标签页
    multiTab: true,
    // 标签页配置
    multiTabProps: {
      hideWhenSingle: true, // 只有一个标签时隐藏
      keepAlive: true, // 保持页面状态
    },
  },
};
```

### 2. 响应式布局
```typescript
// 自动响应式布局
export default {
  layout: {
    // 移动端适配
    mobile: {
      // 移动端配置
    },
    // 桌面端配置
    desktop: {
      layout: 'side',
      contentWidth: 'fluid',
    },
  },
};
```

### 3. 主题切换
```typescript
// 主题配置
export default {
  theme: {
    // 亮色主题
    light: {
      colorPrimary: '#1890ff',
      borderRadius: 2,
    },
    // 暗色主题
    dark: {
      colorPrimary: '#1890ff',
      colorBgContainer: '#141414',
    },
  },
  // 主题切换
  themeSwitch: {
    light: '亮色',
    dark: '暗色',
  },
};
```

### 4. 权限控制集成
```typescript
// 权限控制配置
export default {
  access: {
    // 权限定义
    canViewDashboard: (user) => {
      return user.role === 'admin' || user.role === 'user';
    },
    canEdit: (user) => {
      return user.role === 'admin';
    },
  },
  
  // 路由权限配置
  routes: [
    {
      path: '/admin',
      access: 'canEdit', // 需要canEdit权限
      component: './Admin',
    },
  ],
};
```

## 五、实际应用场景

### 场景1：后台管理系统
```typescript
// 后台管理系统的布局配置
export default {
  layout: {
    // 侧边栏布局
    layout: 'side',
    // 固定头部
    fixedHeader: true,
    // 固定侧边栏
    fixSiderbar: true,
    // 菜单配置
    menu: {
      // 根据权限动态生成菜单
      filterMenu: (menuData, access) => {
        return menuData.filter(item => {
          // 根据权限过滤菜单
          if (item.access && !checkAccess(item.access)) {
            return false;
          }
          return true;
        });
      },
    },
  },
};
```

### 场景2：多租户系统
```typescript
// 多租户布局配置
export default {
  layout: {
    // 根据租户显示不同布局
    getLayout: (tenant) => {
      if (tenant === 'admin') {
        return {
          layout: 'top',
          theme: 'dark',
        };
      }
      return {
        layout: 'side',
        theme: 'light',
      };
    },
  },
};
```

### 场景3：移动端适配
```typescript
// 移动端配置
export default {
  layout: {
    // 移动端配置
    mobile: {
      layout: 'top',
      header: {
        // 移动端头部配置
        fixed: true,
        height: 48,
      },
    },
    // 桌面端配置
    desktop: {
      layout: 'side',
      siderWidth: 200,
    },
  },
};
```

## 六、最佳实践

### 1. 权限控制最佳实践
```typescript
// 1. 定义权限
const access = {
  canViewDashboard: (user) => user.role === 'admin',
  canEdit: (user) => user.role === 'admin',
};

// 2. 路由级权限控制
const routes = [
  {
    path: '/admin',
    component: './Admin',
    access: 'canEdit', // 需要canEdit权限
  },
];

// 3. 组件级权限控制
function AdminPage() {
  return (
    <Access accessible={hasAccess('admin')}>
      <AdminContent />
    </Access>
  );
}
```

### 2. 布局配置最佳实践
```typescript
// 按环境配置布局
const layoutConfig = {
  development: {
    layout: 'side',
    theme: 'light',
    showBreadcrumb: true,
  },
  production: {
    layout: 'top',
    theme: 'dark',
    showBreadcrumb: false,
  },
};
```

### 3. 性能优化
```typescript
// 1. 按需加载布局
const Layout = dynamic(() => import('./Layout'), {
  loading: () => <Loading />,
});

// 2. 代码分割
const routes = [
  {
    path: '/admin',
    component: dynamicWrapper(app, ['admin'], () => import('./Admin')),
  },
];

// 3. 缓存布局
const LayoutWrapper = memo(Layout, (prevProps, nextProps) => {
  // 优化渲染
  return prevProps.location === nextProps.location;
});
```

## 七、总结

umi/layout 通过以下方式解决企业级应用布局的核心问题：

1. **配置化布局**：通过配置而非代码定义布局
2. **动态权限**：基于权限的动态菜单和路由控制
3. **响应式设计**：自动适配不同设备和屏幕尺寸
4. **主题系统**：灵活的主题和样式定制
5. **性能优化**：按需加载、代码分割、缓存优化

通过 umi/layout，开发者可以：

- 减少重复的布局代码
- 统一权限控制逻辑
- 提升开发效率
- 保证用户体验一致性
- 便于维护和扩展

无论是简单的后台管理系统，还是复杂的企业级应用，umi/layout 都提供了完整的解决方案。