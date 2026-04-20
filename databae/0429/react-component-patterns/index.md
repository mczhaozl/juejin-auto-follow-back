# React 组件设计模式完全指南：从基础到高级

## 一、组件设计原则

### 1.1 单一职责原则
每个组件只负责一件事。

### 1.2 开闭原则
对扩展开放，对修改关闭。

---

## 二、容器与展示组件

```jsx
// 展示组件
function UserList({ users, onDelete }) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          {user.name}
          <button onClick={() => onDelete(user.id)}>Delete</button>
        </li>
      ))}
    </ul>
  );
}

// 容器组件
function UserListContainer() {
  const [users, setUsers] = useState([]);
  
  useEffect(() => {
    fetchUsers().then(setUsers);
  }, []);
  
  const handleDelete = (id) => {
    deleteUser(id).then(() => {
      setUsers(prev => prev.filter(u => u.id !== id));
    });
  };
  
  return <UserList users={users} onDelete={handleDelete} />;
}
```

---

## 三、高阶组件（HOC）

```jsx
function withLoading(Component) {
  return function WithLoading({ isLoading, ...props }) {
    if (isLoading) {
      return <div>Loading...</div>;
    }
    return <Component {...props} />;
  };
}

function DataDisplay({ data }) {
  return <div>{JSON.stringify(data)}</div>;
}

const DataDisplayWithLoading = withLoading(DataDisplay);
```

---

## 四、Render Props

```jsx
class MouseTracker extends React.Component {
  state = { x: 0, y: 0 };
  
  handleMouseMove = (e) => {
    this.setState({ x: e.clientX, y: e.clientY });
  };
  
  render() {
    return (
      <div onMouseMove={this.handleMouseMove}>
        {this.props.render(this.state)}
      </div>
    );
  }
}

function App() {
  return (
    <MouseTracker render={({ x, y }) => (
      <h1>Mouse at ({x}, {y})</h1>
    )} />
  );
}
```

---

## 五、自定义 Hook

```jsx
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    const saved = localStorage.getItem(key);
    return saved ? JSON.parse(saved) : initialValue;
  });
  
  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);
  
  return [value, setValue];
}

function Counter() {
  const [count, setCount] = useLocalStorage('count', 0);
  
  return (
    <div>
      Count: {count}
      <button onClick={() => setCount(count + 1)}>Increment</button>
    </div>
  );
}
```

---

## 六、组合组件

```jsx
const Tabs = ({ children, activeTab, onChange }) => {
  return (
    <div className="tabs">
      {React.Children.map(children, child =>
        React.cloneElement(child, { activeTab, onChange })
      )}
    </div>
  );
};

const Tab = ({ label, id, activeTab, onChange }) => {
  const isActive = activeTab === id;
  return (
    <button 
      className={isActive ? 'active' : ''}
      onClick={() => onChange(id)}
    >
      {label}
    </button>
  );
};

function App() {
  const [active, setActive] = useState('tab1');
  
  return (
    <Tabs activeTab={active} onChange={setActive}>
      <Tab id="tab1" label="Tab 1" />
      <Tab id="tab2" label="Tab 2" />
      <Tab id="tab3" label="Tab 3" />
    </Tabs>
  );
}
```

---

## 七、受控组件

```jsx
function Form() {
  const [values, setValues] = useState({ email: '', password: '' });
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setValues(prev => ({ ...prev, [name]: value }));
  };
  
  return (
    <form>
      <input
        type="email"
        name="email"
        value={values.email}
        onChange={handleChange}
      />
      <input
        type="password"
        name="password"
        value={values.password}
        onChange={handleChange}
      />
    </form>
  );
}
```

---

## 八、非受控组件

```jsx
function Form() {
  const emailRef = useRef();
  const passwordRef = useRef();
  
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log(emailRef.current.value, passwordRef.current.value);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input type="email" ref={emailRef} />
      <input type="password" ref={passwordRef} />
      <button type="submit">Submit</button>
    </form>
  );
}
```

---

## 九、复合组件

```jsx
const Button = ({ variant = 'primary', children, ...props }) => {
  const className = `btn btn-${variant}`;
  return (
    <button className={className} {...props}>
      {children}
    </button>
  );
};

Button.Primary = ({ children, ...props }) => (
  <Button variant="primary" {...props}>{children}</Button>
);

Button.Secondary = ({ children, ...props }) => (
  <Button variant="secondary" {...props}>{children}</Button>
);

function App() {
  return (
    <div>
      <Button.Primary>Primary</Button.Primary>
      <Button.Secondary>Secondary</Button.Secondary>
    </div>
  );
}
```

---

## 十、错误边界

```jsx
class ErrorBoundary extends React.Component {
  state = { hasError: false };
  
  static getDerivedStateFromError() {
    return { hasError: true };
  }
  
  componentDidCatch(error, info) {
    console.error(error, info);
  }
  
  render() {
    if (this.state.hasError) {
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

function App() {
  return (
    <ErrorBoundary>
      <RiskyComponent />
    </ErrorBoundary>
  );
}
```

---

## 十一、Compound Components

```jsx
const Select = ({ value, onChange, children }) => {
  const context = { value, onChange };
  return (
    <SelectContext.Provider value={context}>
      <div className="select">{children}</div>
    </SelectContext.Provider>
  );
};

const SelectOption = ({ value, children }) => {
  const { value: selectedValue, onChange } = useContext(SelectContext);
  return (
    <div
      className={value === selectedValue ? 'selected' : ''}
      onClick={() => onChange(value)}
    >
      {children}
    </div>
  );
};

function App() {
  const [value, setValue] = useState('apple');
  
  return (
    <Select value={value} onChange={setValue}>
      <SelectOption value="apple">Apple</SelectOption>
      <SelectOption value="banana">Banana</SelectOption>
      <SelectOption value="orange">Orange</SelectOption>
    </Select>
  );
}
```

---

## 十二、最佳实践

1. 优先使用函数组件和 Hooks
2. 保持组件小而专注
3. 合理使用 Context 和状态提升
4. 使用 TypeScript 增强类型安全
5. 编写可复用的组合组件

---

## 十三、总结

掌握组件设计模式能编写更优雅、可维护的 React 应用。
