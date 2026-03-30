# Cypress 完全指南：端到端测试实战

> 深入讲解 Cypress E2E 测试，包括测试编写、选择器、API 测试、模拟.stub，以及 CI 集成和测试最佳实践。

## 一、快速开始

### 1.1 安装

```bash
npm install cypress --save-dev
npx cypress open
```

### 1.2 配置

```javascript
// cypress.config.js
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: false,
    screenshotOnRunFailure: true
  }
});
```

## 二、基础测试

### 2.1 编写测试

```javascript
// cypress/e2e/login.cy.js
describe('登录测试', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('应该能正常登录', () => {
    cy.get('[data-testid="username"]').type('admin');
    cy.get('[data-testid="password"]').type('password');
    cy.get('[data-testid="login-btn"]').click();
    
    cy.url().should('include', '/dashboard');
  });

  it('应该显示错误提示', () => {
    cy.get('[data-testid="login-btn"]').click();
    cy.contains('用户名不能为空').should('be.visible');
  });
});
```

## 三、选择器

### 3.1 常用选择器

```javascript
// ID 选择器
cy.get('#username');

// Class 选择器
cy.get('.btn-primary');

// 属性选择器
cy.get('[data-testid="login-btn"]');
cy.get('[type="text"]');
cy.get('[name="username"]');

// 文本选择器
cy.contains('登录');
cy.contains('用户名', '请输入');

// 组合选择器
cy.get('.form-group input');
cy.get('form button[type="submit"]');
```

### 3.2 最佳实践

```javascript
// 推荐：data-testid
cy.get('[data-testid="submit-btn"]');

// 不推荐：复杂选择器
cy.get('.btn-primary.btn-large.btn-active');
```

## 四、交互操作

### 4.1 常见操作

```javascript
// 点击
cy.click();
cy.dblclick();
cy.rightclick();

// 输入
cy.type('hello');
cy.type('password', { sensitive: true });

// 选择
cy.select('Option 1');
cy.select(['Option 1', 'Option 2']);

// 勾选
cy.check();
cy.uncheck();
cy.check(['checkbox1', 'checkbox2']);

// 悬停
cy.trigger('mouseover');
```

### 4.2 等待

```javascript
// 等待元素
cy.get('.loading').should('not.exist');

// 等待请求
cy.wait('@getUser');

// 等待时间（不推荐）
cy.wait(1000);
```

## 五、断言

### 5.1 .should

```javascript
cy.get('.title').should('have.text', 'Hello');
cy.get('.title').should('contain', 'Hello');
cy.get('.input').should('have.value', 'default');
cy.get('.checkbox').should('be.checked');
cy.get('.loading').should('not.be.visible');
```

### 5.2 链式断言

```javascript
cy.get('.user')
  .should('have.class', 'active')
  .and('contain', 'John')
  .and('be.visible');
```

## 六、API 测试

### 6.1 请求

```javascript
cy.request('GET', '/api/users').then((response) => {
  expect(response.status).to.eq(200);
  expect(response.body).to.have.length(10);
});

cy.request('POST', '/api/login', {
  username: 'admin',
  password: 'password'
});
```

### 6.2 Mock

```javascript
cy.intercept('GET', '/api/users', {
  statusCode: 200,
  body: [
    { id: 1, name: '张三' },
    { id: 2, name: '李四' }
  ]
}).as('getUsers');

cy.visit('/users');
cy.wait('@getUsers');
```

## 七、总结

Cypress 核心要点：

1. **describe/it**：测试结构
2. **cy.get**：获取元素
3. **cy.click/type**：交互操作
4. **should**：断言
5. **cy.request**：API 测试
6. **cy.intercept**：Mock 请求

掌握这些，E2E 测试 so easy！

---

**推荐阅读**：
- [Cypress 官方文档](https://docs.cypress.io/)

**如果对你有帮助，欢迎点赞收藏！**
