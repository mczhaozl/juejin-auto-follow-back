# 前端测试策略：单元测试、集成测试与 E2E 测试实战

> 全面介绍前端测试策略，包括 Jest、React Testing Library、Cypress 等工具的使用，以及测试最佳实践。

## 一、测试金字塔

### 1.1 测试分层

```
        /\
       /E2E\        ← 少：慢、维护成本高
      /------\
     /Integration\   ← 中：接口、业务逻辑
    /------------\
   /  Unit Test  \  ← 多：快、可靠
  /--------------\
```

### 1.2 比例建议

- **单元测试**：70%
- **集成测试**：20%
- **E2E 测试**：10%

## 二、单元测试

### 2.1 Jest 基础

```javascript
describe('Calculator', () => {
  test('adds two numbers', () => {
    expect(1 + 2).toBe(3);
  });

  test('subtracts two numbers', () => {
    expect(5 - 3).toBe(2);
  });
});
```

### 2.2 测试异步

```javascript
test('fetches user', async () => {
  const user = await fetchUser(1);
  expect(user.name).toBe('张三');
});
```

### 2.3 Mock

```javascript
jest.mock('./api');

test('getUser', async () => {
  const user = await getUser(1);
  expect(user).toEqual({ id: 1, name: '张三' });
});
```

## 三、React 测试

### 3.1 Testing Library

```javascript
import { render, screen, fireEvent } from '@testing-library/react';

test('counter increments', () => {
  render(<Counter />);
  
  const button = screen.getByText('Count: 0');
  fireEvent.click(button);
  
  expect(screen.getByText('Count: 1')).toBeInTheDocument();
});
```

### 3.2 组件测试

```javascript
test('renders user info', () => {
  render(<UserInfo user={{ name: '张三', email: 'test@example.com' }} />);
  
  expect(screen.getByText('张三')).toBeInTheDocument();
  expect(screen.getByText('test@example.com')).toBeInTheDocument();
});
```

### 3.3 表单测试

```javascript
test('form submission', () => {
  const onSubmit = jest.fn();
  render(<LoginForm onSubmit={onSubmit} />);
  
  fireEvent.change(screen.getByLabelText(/username/i), {
    target: { value: 'zhangsan' }
  });
  
  fireEvent.click(screen.getByRole('button', { name: /submit/i }));
  
  expect(onSubmit).toHaveBeenCalledWith({
    username: 'zhangsan'
  });
});
```

## 四、集成测试

### 4.1 API 测试

```javascript
import request from 'supertest';
import app from '../app';

describe('API', () => {
  test('GET /users', async () => {
    const res = await request(app).get('/api/users');
    
    expect(res.status).toBe(200);
    expect(res.body).toHaveLength(2);
  });
  
  test('POST /users', async () => {
    const res = await request(app)
      .post('/api/users')
      .send({ name: '张三' });
    
    expect(res.status).toBe(201);
    expect(res.body).toHaveProperty('id');
  });
});
```

### 4.2 组件集成

```javascript
test('user list loads and displays', async () => {
  render(<UserList />);
  
  expect(screen.getByText(/loading/i)).toBeInTheDocument();
  
  await waitFor(() => {
    expect(screen.getByText('张三')).toBeInTheDocument();
  });
});
```

## 五、E2E 测试

### 5.1 Cypress 基础

```javascript
describe('Login', () => {
  it('should login successfully', () => {
    cy.visit('/login');
    
    cy.get('[data-testid=username]').type('zhangsan');
    cy.get('[data-testid=password]').type('password123');
    cy.get('[data-testid=submit]').click();
    
    cy.url().should('include', '/dashboard');
    cy.contains('Welcome').should('be.visible');
  });
});
```

### 5.2 断言

```javascript
// 元素存在
cy.get('[data-testid=button]').should('exist');

// 文本匹配
cy.contains('Hello').should('be.visible');

// 类名
cy.get('.active').should('have.class', 'active');

// 值
cy.get('input').should('have.value', 'test');
```

### 5.3 网络请求

```javascript
cy.intercept('GET', '/api/users', { fixture: 'users.json' }).as('getUsers');

cy.visit('/users');

cy.wait('@getUsers');
cy.get('[data-testid=user]').should('have.length', 2);
```

## 六、测试覆盖率

### 6.1 配置

```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  }
};
```

### 6.2 报告

```bash
npm test -- --coverage
```

## 七、最佳实践

### 7.1 AAA 模式

```javascript
test('adds item to list', () => {
  // Arrange - 准备
  const list = [];
  
  // Act - 执行
  const result = addItem(list, 'test');
  
  // Assert - 断言
  expect(result).toHaveLength(1);
});
```

### 7.2 测试命名

```javascript
describe('Calculator', () => {
  it('should return correct sum for two positive numbers', () => {});
  it('should handle negative numbers correctly', () => {});
  it('should throw error when dividing by zero', () => {});
});
```

## 八、总结

测试核心要点：

1. **测试金字塔**：单元→集成→E2E
2. **Jest**：单元测试
3. **Testing Library**：React 组件测试
4. **Cypress**：E2E 测试
5. **覆盖率**：关注关键路径
6. **最佳实践**：AAA 模式、清晰命名

掌握这些，代码质量有保障！

---

**推荐阅读**：
- [Jest 文档](https://jestjs.io/)
- [Testing Library](https://testing-library.com/)
- [Cypress 文档](https://www.cypress.io/)

**如果对你有帮助，欢迎点赞收藏！**
