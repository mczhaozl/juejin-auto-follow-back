# React Context 完全指南：跨组件状态管理

> 深入讲解 React Context，包括 Context 创建、Provider 使用、useContext Hook，以及性能优化和最佳实践。

## 一、Context 基础

### 1.1 创建 Context

```javascript
import { createContext } from 'react';

const ThemeContext = createContext('light');

export default ThemeContext;
```

### 1.2 Provider

```javascript
import ThemeContext from './ThemeContext';

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <Toolbar />
    </ThemeContext.Provider>
  );
}
```

### 1.3 使用 Context

```javascript
import { useContext } from 'react';
import ThemeContext from './ThemeContext';

function Toolbar() {
  const theme = useContext(ThemeContext);
  
  return <div className={theme}>工具栏</div>;
}
```

## 二、实战案例

### 2.1 用户认证

```javascript
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  
  const login = (userData) => setUser(userData);
  const logout = () => setUser(null);
  
  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

function useAuth() {
  return useContext(AuthContext);
}
```

### 2.2 主题切换

```javascript
const ThemeContext = createContext({
  theme: 'light',
  toggleTheme: () => {}
});

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  
  const toggleTheme = () => {
    setTheme(t => t === 'light' ? 'dark' : 'light');
  };
  
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}
```

## 三、性能优化

### 3.1 拆分 Context

```javascript
// 不好 - 一个 Context 包含太多内容
const AppContext = createContext({ user, theme, language, setUser, setTheme, setLanguage });

// 好 - 拆分多个 Context
const UserContext = createContext(null);
const ThemeContext = createContext(null);
const LanguageContext = createContext(null);
```

### 3.2 记忆化

```javascript
const value = useMemo(() => ({
  user,
  login,
  logout
}), [user]);
```

## 四、总结

React Context 核心要点：

1. **createContext**：创建上下文
2. **Provider**：提供值
3. **useContext**：消费值
4. **拆分**：避免重渲染
5. **记忆化**：优化性能

掌握这些，React 状态管理更简单！

---

**推荐阅读**：
- [React Context 官方文档](https://react.dev/learn/passing-data-deeply-with-context)

**如果对你有帮助，欢迎点赞收藏！**
