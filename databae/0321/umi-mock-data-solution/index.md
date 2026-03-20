# umi/mock：本地Mock数据解决方案，告别前后端联调等待

> 深入解析umi/mock如何通过零配置Mock、智能路由匹配、动态数据生成、延迟模拟等特性，解决前端开发中的数据依赖、接口联调、测试数据等核心难题，提升开发效率。

---

## 一、背景：前端开发中的数据困境

在前端开发中，我们经常面临以下问题：

1. **后端接口未完成**：前端开发被后端进度阻塞
2. **测试数据不真实**：手动构造的测试数据不完整
3. **联调成本高**：前后端联调需要等待后端接口
4. **数据场景覆盖不全**：难以模拟各种边界情况
5. **网络延迟模拟**：无法模拟真实网络环境

## 二、umi/mock 核心特性

### 1. 零配置Mock
```javascript
// mock/users.js
export default {
  // 支持标准RESTful API
  'GET /api/users': (req, res) => {
    res.json({
      success: true,
      data: [
        { id: 1, name: '张三', age: 25 },
        { id: 2, name: '李四', age: 30 }
      ]
    });
  },
  
  // 支持RESTful参数
  'GET /api/users/:id': (req, res) => {
    const { id } = req.params;
    res.json({
      success: true,
      data: { id, name: '张三', age: 25 }
    });
  },
  
  // 支持POST请求
  'POST /api/users': (req, res) => {
    const { name, age } = req.body;
    res.json({
      success: true,
      data: { id: Date.now(), name, age }
    });
  }
};
```

### 2. 智能路由匹配
umi/mock支持多种路由匹配模式：

```javascript
export default {
  // 1. 精确匹配
  'GET /api/users': { users: [] },
  
  // 2. 通配符匹配
  'GET /api/users/*': { 
    success: true,
    data: '匹配所有/users/开头的路径'
  },
  
  // 3. 正则表达式匹配
  '/^\/api\/users\/\d+$/': (req, res) => {
    const id = req.path.split('/').pop();
    res.json({ id, name: '用户' + id });
  },
  
  // 4. 支持RESTful风格
  'GET /api/users/:id': (req, res) => {
    res.json({ id: req.params.id, name: '用户' });
  }
};
```

### 3. 动态数据生成
```javascript
import { mock } from 'umi';

export default {
  // 使用mockjs生成随机数据
  'GET /api/users/random': (req, res) => {
    const Mock = require('mockjs');
    const data = Mock.mock({
      'list|10': [{
        'id|+1': 1,
        'name': '@cname',
        'age|18-60': 1,
        'email': '@email',
        'address': '@county(true)',
        'avatar': '@image("200x200", "#50B347", "#FFF", "Mock.js")'
      }]
    });
    res.json(data);
  }
};
```

### 4. 延迟响应与错误模拟
```javascript
export default {
  // 模拟网络延迟
  'GET /api/users': (req, res) => {
    // 模拟1-3秒的延迟
    setTimeout(() => {
      res.json({
        success: true,
        data: users
      });
    }, Math.random() * 2000 + 1000); // 1-3秒延迟
  },
  
  // 模拟错误响应
  'GET /api/error': (req, res) => {
    res.status(500).json({
      success: false,
      error: '服务器内部错误',
      code: 500
    });
  },
  
  // 模拟网络错误
  'GET /api/network-error': (req, res) => {
    // 模拟网络错误
    res.status(500).end();
  }
};
```

## 三、解决的实际问题

### 问题1：后端接口未完成时的开发阻塞

**传统方式**：
```javascript
// 前端开发被阻塞，需要等待后端接口
const response = await fetch('/api/users'); // 接口未完成，无法开发
```

**umi/mock解决方案**：
```javascript
// mock/users.js
export default {
  'GET /api/users': (req, res) => {
    res.json({
      success: true,
      data: [
        { id: 1, name: '张三', role: 'admin' },
        { id: 2, name: '李四', role: 'user' }
      ]
    });
  }
};
```

### 问题2：测试数据不真实

**传统方式**：
```javascript
// 手动创建测试数据，不真实
const mockData = [
  { id: 1, name: '用户1' },
  { id: 2, name: '用户2' }
];
```

**umi/mock解决方案**：
```javascript
import Mock from 'mockjs';

export default {
  'GET /api/users': (req, res) => {
    const data = Mock.mock({
      'list|10': [{
        'id|+1': 1,
        'name': '@cname',
        'email': '@email',
        'age|18-60': 1,
        'address': '@county(true)',
        'avatar': '@image("200x200", "#50B347", "#FFF", "Avatar")',
        'createdAt': '@datetime',
        'status|1': ['active', 'inactive', 'pending']
      }]
    });
    res.json(data);
  }
};
```

### 问题3：边界情况测试困难

**传统方式**：
```javascript
// 难以测试各种边界情况
// 1. 空数据
// 2. 大数据量
// 3. 错误情况
// 4. 网络延迟
```

**umi/mock解决方案**：
```javascript
export default {
  // 测试空数据
  'GET /api/users/empty': (req, res) => {
    res.json({ data: [] });
  },
  
  // 测试大数据量
  'GET /api/users/large': (req, res) => {
    const data = Array.from({ length: 1000 }, (_, i) => ({
      id: i + 1,
      name: `用户${i + 1}`,
      age: Math.floor(Math.random() * 50) + 18
    }));
    res.json({ data });
  },
  
  // 测试错误情况
  'GET /api/users/error': (req, res) => {
    res.status(500).json({
      error: '服务器内部错误',
      code: 500
    });
  },
  
  // 测试网络延迟
  'GET /api/users/slow': (req, res) => {
    setTimeout(() => {
      res.json({ 
        success: true,
        message: '延迟响应'
      });
    }, 3000); // 3秒延迟
  }
};
```

## 四、高级特性

### 1. 数据关联与关系
```javascript
export default {
  'GET /api/users/:id': (req, res) => {
    const userId = req.params.id;
    const user = {
      id: userId,
      name: '张三',
      posts: [
        { id: 1, title: '文章1', content: '内容1' },
        { id: 2, title: '文章2', content: '内容2' }
      ],
      comments: [
        { id: 1, content: '评论1', postId: 1 },
        { id: 2, content: '评论2', postId: 1 }
      ]
    };
    res.json(user);
  }
};
```

### 2. 分页与过滤
```javascript
export default {
  'GET /api/users': (req, res) => {
    const { page = 1, pageSize = 10, name } = req.query;
    const allUsers = generateUsers(100); // 生成100个用户
    
    // 过滤
    let filtered = allUsers;
    if (name) {
      filtered = filtered.filter(user => 
        user.name.includes(name)
      );
    }
    
    // 分页
    const start = (page - 1) * pageSize;
    const end = start + pageSize;
    const pagedData = filtered.slice(start, end);
    
    res.json({
      data: pagedData,
      total: filtered.length,
      page,
      pageSize,
      totalPages: Math.ceil(filtered.length / pageSize)
    });
  }
};
```

### 3. 文件上传模拟
```javascript
export default {
  'POST /api/upload': (req, res) => {
    // 模拟文件上传
    const file = req.file;
    res.json({
      success: true,
      url: '/uploads/' + file.originalname,
      size: file.size,
      mimetype: file.mimetype
    });
  }
};
```

### 4. WebSocket 模拟
```javascript
export default {
  'WS /ws': (ws, req) => {
    ws.on('message', (message) => {
      const data = JSON.parse(message);
      
      // 处理不同类型的消息
      switch (data.type) {
        case 'chat':
          ws.send(JSON.stringify({
            type: 'chat',
            from: 'server',
            message: '收到消息'
          }));
          break;
        case 'ping':
          ws.send(JSON.stringify({ type: 'pong' }));
          break;
      }
    });
  }
};
```

## 五、实际应用场景

### 场景1：用户管理系统
```javascript
// mock/user.js
export default {
  // 用户登录
  'POST /api/login': (req, res) => {
    const { username, password } = req.body;
    if (username === 'admin' && password === '123456') {
      res.json({
        success: true,
        data: {
          token: 'mock-jwt-token',
          user: {
            id: 1,
            username: 'admin',
            role: 'admin'
          }
        }
      });
    } else {
      res.status(401).json({
        success: false,
        message: '用户名或密码错误'
      });
    }
  },
  
  // 获取用户信息
  'GET /api/user/info': (req, res) => {
    const token = req.headers.authorization;
    if (token === 'Bearer mock-jwt-token') {
      res.json({
        success: true,
        data: {
          id: 1,
          username: 'admin',
          email: 'admin@example.com',
          role: 'admin'
        }
      });
    } else {
      res.status(401).json({
        success: false,
        message: '未授权'
      });
    }
  }
};
```

### 场景2：电商商品列表
```javascript
export default {
  'GET /api/products': (req, res) => {
    const { category, page = 1, pageSize = 10 } = req.query;
    
    const products = generateProducts(100); // 生成100个商品
    
    // 按分类过滤
    let filtered = products;
    if (category) {
      filtered = products.filter(p => p.category === category);
    }
    
    // 分页
    const start = (page - 1) * pageSize;
    const paged = filtered.slice(start, start + pageSize);
    
    res.json({
      data: paged,
      pagination: {
        page: parseInt(page),
        pageSize: parseInt(pageSize),
        total: filtered.length,
        totalPages: Math.ceil(filtered.length / pageSize)
      }
    });
  }
};
```

## 六、最佳实践

### 1. 目录结构组织
```
mock/
├── users.js        # 用户相关接口
├── products.js     # 商品相关接口
├── orders.js       # 订单相关接口
└── utils.js        # 公共工具函数
```

### 2. 数据工厂模式
```javascript
// mock/factories/userFactory.js
export const createUser = (overrides = {}) => ({
  id: 1,
  name: '张三',
  email: 'user@example.com',
  role: 'user',
  ...overrides
});

// 在mock中使用
export default {
  'GET /api/user': (req, res) => {
    res.json(createUser({ name: '测试用户' }));
  }
};
```

### 3. 环境配置
```javascript
// .umirc.js
export default {
  mock: {
    // 开发环境使用mock
    include: process.env.NODE_ENV === 'development' 
      ? ['mock/**/*.js'] 
      : []
  }
};
```

## 七、总结

umi/mock 通过以下方式解决前端开发中的数据难题：

1. **零配置启动**：开箱即用，无需复杂配置
2. **智能路由匹配**：支持RESTful、通配符、正则等多种匹配方式
3. **真实数据生成**：支持Mock.js，生成真实测试数据
4. **网络环境模拟**：延迟、错误、超时等真实场景模拟
5. **类型安全**：完整的TypeScript支持

通过 umi/mock，前端开发可以：
- 不依赖后端接口，独立开发
- 模拟各种边界情况和异常场景
- 提高测试覆盖率
- 加速开发迭代速度

无论是简单的CRUD接口，还是复杂的业务场景，umi/mock 都能提供完整的解决方案，让前端开发更加高效、独立。