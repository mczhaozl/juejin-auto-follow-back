# Styled Components 完全指南：CSS-in-JS 实战

> 深入讲解 CSS-in-JS 方案 Styled Components，包括动态样式、主题系统、响应式样式，以及与 Emotion 的对比。

## 一、快速开始

### 1.1 安装

```bash
npm install styled-components
```

### 1.2 基础用法

```javascript
import styled from 'styled-components';

const Button = styled.button`
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  
  &:hover {
    background: #0056b3;
  }
`;

function App() {
  return <Button>点击我</Button>;
}
```

## 二、动态样式

### 2.1 Props 传递

```javascript
const Button = styled.button`
  background: ${props => props.primary ? '#007bff' : '#6c757d'};
  color: ${props => props.primary ? 'white' : 'white'};
  padding: ${props => props.size || '10px 20px'};
`;

<Button primary>主要按钮</Button>
<Button size="20px">大按钮</Button>
```

### 2.2 条件样式

```javascript
const Container = styled.div`
  display: flex;
  flex-direction: ${props => props.column ? 'column' : 'row'};
  gap: ${props => props.gap || '0'};
`;
```

## 三、主题系统

### 3.1 创建主题

```javascript
const theme = {
  colors: {
    primary: '#007bff',
    secondary: '#6c757d',
    success: '#28a745'
  },
  spacing: {
    sm: '8px',
    md: '16px',
    lg: '24px'
  }
};
```

### 3.2 使用主题

```javascript
import { ThemeProvider } from 'styled-components';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <Button>使用主题色</Button>
    </ThemeProvider>
  );
}

const Button = styled.button`
  background: ${props => props.theme.colors.primary};
  padding: ${props => props.theme.spacing.md};
`;
```

## 四、扩展样式

### 4.1 继承

```javascript
const Button = styled.button`
  padding: 10px 20px;
`;

const PrimaryButton = styled(Button)`
  background: #007bff;
  color: white;
`;
```

### 4.2 混入

```javascript
const flexCenter = `
  display: flex;
  justify-content: center;
  align-items: center;
`;

const Box = styled.div`
  ${flexCenter}
  height: 100vh;
`;
```

## 五、响应式

### 5.1 媒体查询

```javascript
const Container = styled.div`
  display: grid;
  grid-template-columns: 1fr;
  
  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }
  
  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }
`;
```

## 六、总结

Styled Components 核心要点：

1. **styled.**：创建组件
2. **Props**：动态样式
3. **ThemeProvider**：主题系统
4. **styled()**：样式继承
5. **媒体查询**：响应式布局

掌握这些，CSS-in-JS 不再难！

---

**推荐阅读**：
- [Styled Components 文档](https://styled-components.com/)

**如果对你有帮助，欢迎点赞收藏！**
