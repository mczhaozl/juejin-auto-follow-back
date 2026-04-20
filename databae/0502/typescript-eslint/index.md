# TypeScript ESLint 完全指南：代码检查与自动修复

## 一、ESLint 概述

### 1.1 什么是 ESLint

可插拔的 JavaScript/TypeScript 代码检查工具。

### 1.2 核心功能

- 语法检查
- 代码质量检查
- 代码风格检查
- 自动修复

---

## 二、安装配置

### 2.1 安装依赖

```bash
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
```

### 2.2 配置文件

```javascript
// .eslintrc.js
module.exports = {
  root: true,
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    project: './tsconfig.json'
  },
  plugins: ['@typescript-eslint'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking'
  ],
  rules: {
    // 自定义规则
  }
};
```

### 2.3 忽略文件

```
# .eslintignore
node_modules
dist
build
*.js
*.d.ts
```

---

## 三、常用规则配置

### 3.1 基础规则

```javascript
rules: {
  // 禁止 console
  'no-console': 'warn',
  
  // 禁止 debugger
  'no-debugger': 'error',
  
  // 分号
  'semi': ['error', 'always'],
  
  // 引号
  'quotes': ['error', 'single'],
  
  // 缩进
  'indent': ['error', 2],
  
  // 逗号
  'comma-dangle': ['error', 'always-multiline']
}
```

### 3.2 TypeScript 规则

```javascript
rules: {
  // 类型注解
  '@typescript-eslint/explicit-function-return-type': 'error',
  
  // any 类型
  '@typescript-eslint/no-explicit-any': 'warn',
  
  // 非空断言
  '@typescript-eslint/no-non-null-assertion': 'warn',
  
  // 推断类型
  '@typescript-eslint/no-inferrable-types': 'off',
  
  // unused 变量
  '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
  
  // 类型导入
  '@typescript-eslint/consistent-type-imports': 'error',
  
  // 严格类型检查
  '@typescript-eslint/strict-boolean-expressions': 'error'
}
```

---

## 四、使用 Prettier

### 4.1 安装

```bash
npm install --save-dev prettier eslint-config-prettier eslint-plugin-prettier
```

### 4.2 配置

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:prettier/recommended'
  ]
};
```

### 4.3 Prettier 配置

```json
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "es5",
  "printWidth": 100
}
```

---

## 五、NPM Scripts

```json
{
  "scripts": {
    "lint": "eslint . --ext .ts,.tsx",
    "lint:fix": "eslint . --ext .ts,.tsx --fix",
    "lint:ci": "eslint . --ext .ts,.tsx --quiet"
  }
}
```

---

## 六、编辑器集成

### 6.1 VS Code

```json
// .vscode/settings.json
{
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.validate": ["typescript", "typescriptreact"]
}
```

---

## 七、自定义规则

### 7.1 创建规则

```javascript
// eslint-rules/no-console-error.js
module.exports = {
  meta: {
    type: 'problem',
    docs: { description: '禁止使用 console.error' },
    fixable: null,
    schema: []
  },
  create(context) {
    return {
      MemberExpression(node) {
        if (
          node.object.type === 'Identifier' &&
          node.object.name === 'console' &&
          node.property.type === 'Identifier' &&
          node.property.name === 'error'
        ) {
          context.report({
            node,
            message: '不要使用 console.error'
          });
        }
      }
    };
  }
};
```

### 7.2 使用自定义规则

```javascript
// .eslintrc.js
module.exports = {
  plugins: ['custom'],
  rules: {
    'custom/no-console-error': 'error'
  }
};
```

---

## 八、Git Hooks

### 8.1 安装 husky

```bash
npm install --save-dev husky lint-staged
npx husky install
npm set-script prepare "husky install"
```

### 8.2 配置 pre-commit

```bash
npx husky add .husky/pre-commit "npx lint-staged"
```

```json
{
  "lint-staged": {
    "*.{ts,tsx}": [
      "eslint --fix"
    ]
  }
}
```

---

## 九、推荐配置

### 9.1 React 项目

```bash
npm install --save-dev eslint-plugin-react eslint-plugin-react-hooks eslint-plugin-jsx-a11y
```

```javascript
module.exports = {
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:react/recommended',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
    'plugin:prettier/recommended'
  ],
  settings: {
    react: { version: 'detect' }
  }
};
```

---

## 总结

ESLint + TypeScript 可以大幅提升代码质量，配合 Prettier 和 Git Hooks 可以实现自动化的代码规范检查。
