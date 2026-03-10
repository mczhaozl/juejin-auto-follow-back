# 前端必学：完美组件封装的 7 个原则

> 从可复用、可维护、可测试三个维度，教你写出团队都爱用的组件。

---

## 一、为什么要封装组件

在实际项目中，我们经常遇到这些问题：

- 同样的 UI 逻辑在多处复制粘贴
- 改一个地方要改十几个文件
- 新人接手代码看不懂，不敢改
- 组件参数一大堆，不知道哪些必填

好的组件封装能解决这些痛点，让代码：

- **可复用**：一次编写，多处使用
- **可维护**：逻辑集中，改动影响范围小
- **可测试**：职责单一，容易写单测
- **易理解**：接口清晰，文档完善

## 二、原则 1：单一职责

一个组件只做一件事，不要把多个功能塞进一个组件。

### 反例：职责混乱

```javascript
// ❌ 一个组件干了太多事
function UserCard({ userId }) {
  const [user, setUser] = useState(null);
  const [posts, setPosts] = useState([]);
  const [comments, setComments] = useState([]);

  useEffect(() => {
    // 获取用户信息
    fetch(`/api/users/${userId}`).then(res => setUser(res.json()));
    // 获取用户文章
    fetch(`/api/users/${userId}/posts`).then(res => setPosts(res.json()));
    // 获取用户评论
    fetch(`/api/users/${userId}/comments`).then(res => setComments(res.json()));
  }, [userId]);

  return (
    <div>
      <div>{user?.name}</div>
      <div>{posts.map(p => <Post key={p.id} {...p} />)}</div>
      <div>{comments.map(c => <Comment key={c.id} {...c} />)}</div>
    </div>
  );
}
```

### 正例：职责分离

```javascript
// ✅ 拆成多个组件
function UserCard({ userId }) {
  return (
    <div>
      <UserInfo userId={userId} />
      <UserPosts userId={userId} />
      <UserComments userId={userId} />
    </div>
  );
}

function UserInfo({ userId }) {
  const { data: user } = useUser(userId);
  return <div>{user?.name}</div>;
}

function UserPosts({ userId }) {
  const { data: posts } = useUserPosts(userId);
  return <div>{posts?.map(p => <Post key={p.id} {...p} />)}</div>;
}
```

好处：每个组件职责清晰，可以独立测试和复用。

## 三、原则 2：Props 设计要合理

### 2.1 必填与可选分明

用 TypeScript 或 PropTypes 明确标注：

```typescript
interface ButtonProps {
  // 必填
  children: React.ReactNode;
  onClick: () => void;
  
  // 可选
  type?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
}

function Button({ 
  children, 
  onClick, 
  type = 'primary',
  size = 'medium',
  disabled = false,
  loading = false 
}: ButtonProps) {
  // ...
}
```

### 2.2 避免过多 Props

超过 5 个 props 就要考虑是否设计有问题：

```javascript
// ❌ Props 太多
<Modal
  visible={visible}
  title="标题"
  content="内容"
  okText="确定"
  cancelText="取消"
  onOk={handleOk}
  onCancel={handleCancel}
  width={600}
  centered={true}
  maskClosable={false}
/>

// ✅ 用对象或 children 简化
<Modal
  visible={visible}
  config={{
    title: "标题",
    okText: "确定",
    cancelText: "取消",
    width: 600
  }}
  onOk={handleOk}
  onCancel={handleCancel}
>
  内容
</Modal>
```

### 2.3 用组合代替配置

```javascript
// ❌ 用 props 控制所有变体
<Button type="primary" icon="search" iconPosition="left" />

// ✅ 用组合
<Button type="primary">
  <Icon name="search" />
  搜索
</Button>
```

## 四、原则 3：状态提升与下沉

### 3.1 状态提升

当多个组件需要共享状态时，提升到最近的公共父组件：

```javascript
// ❌ 状态分散
function Parent() {
  return (
    <>
      <ChildA />  {/* 内部有 count 状态 */}
      <ChildB />  {/* 内部也有 count 状态 */}
    </>
  );
}

// ✅ 状态提升
function Parent() {
  const [count, setCount] = useState(0);
  return (
    <>
      <ChildA count={count} onChange={setCount} />
      <ChildB count={count} />
    </>
  );
}
```

### 3.2 状态下沉

不需要共享的状态，放在最近的使用者内部：

```javascript
// ❌ 状态过度提升
function Parent() {
  const [inputValue, setInputValue] = useState('');  // 只有 Child 用
  return <Child value={inputValue} onChange={setInputValue} />;
}

// ✅ 状态下沉
function Parent() {
  return <Child />;
}

function Child() {
  const [inputValue, setInputValue] = useState('');
  return <input value={inputValue} onChange={e => setInputValue(e.target.value)} />;
}
```

## 五、原则 4：逻辑与 UI 分离

### 5.1 自定义 Hook 抽离逻辑

```javascript
// ❌ 逻辑和 UI 混在一起
function UserList() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/users')
      .then(res => res.json())
      .then(data => setUsers(data))
      .catch(err => setError(err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error.message}</div>;
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

// ✅ 逻辑抽成 Hook
function useUsers() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetch('/api/users')
      .then(res => res.json())
      .then(data => setUsers(data))
      .catch(err => setError(err))
      .finally(() => setLoading(false));
  }, []);

  return { users, loading, error };
}

function UserList() {
  const { users, loading, error } = useUsers();

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误: {error.message}</div>;
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

好处：`useUsers` 可以在其他组件复用，且可以单独测试。

### 5.2 Render Props 或 HOC

```javascript
// Render Props
function DataFetcher({ url, children }) {
  const { data, loading, error } = useFetch(url);
  return children({ data, loading, error });
}

<DataFetcher url="/api/users">
  {({ data, loading, error }) => {
    if (loading) return <div>加载中...</div>;
    if (error) return <div>错误</div>;
    return <ul>{data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
  }}
</DataFetcher>
```

## 六、原则 5：可扩展性

### 6.1 预留扩展点

```javascript
// ❌ 写死了渲染逻辑
function List({ items }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{item.name}</li>
      ))}
    </ul>
  );
}

// ✅ 允许自定义渲染
function List({ items, renderItem }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id}>{renderItem(item)}</li>
      ))}
    </ul>
  );
}

// 使用
<List 
  items={users} 
  renderItem={user => (
    <div>
      <img src={user.avatar} />
      <span>{user.name}</span>
    </div>
  )}
/>
```

### 6.2 支持样式覆盖

```javascript
function Button({ className, style, ...props }) {
  return (
    <button
      className={`btn ${className || ''}`}
      style={{ ...defaultStyle, ...style }}
      {...props}
    />
  );
}
```

### 6.3 转发 Ref

```javascript
const Input = forwardRef((props, ref) => {
  return <input ref={ref} {...props} />;
});

// 使用
const inputRef = useRef();
<Input ref={inputRef} />
inputRef.current.focus();
```

## 七、原则 6：错误处理与边界情况

### 6.1 加载、错误、空状态

```javascript
function UserList() {
  const { data, loading, error } = useUsers();

  if (loading) return <Spinner />;
  if (error) return <ErrorMessage error={error} />;
  if (!data || data.length === 0) return <EmptyState />;

  return (
    <ul>
      {data.map(user => <UserItem key={user.id} user={user} />)}
    </ul>
  );
}
```

### 6.2 Error Boundary

```javascript
class ErrorBoundary extends React.Component {
  state = { hasError: false };

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('组件错误:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return <div>出错了，请刷新页面</div>;
    }
    return this.props.children;
  }
}

// 使用
<ErrorBoundary>
  <UserList />
</ErrorBoundary>
```

### 6.3 参数校验

```javascript
function Button({ children, onClick, type = 'primary' }) {
  if (!children) {
    console.warn('Button: children is required');
    return null;
  }

  if (typeof onClick !== 'function') {
    console.warn('Button: onClick must be a function');
  }

  // ...
}
```

## 八、原则 7：文档与示例

### 7.1 JSDoc 注释

```javascript
/**
 * 按钮组件
 * @param {Object} props
 * @param {React.ReactNode} props.children - 按钮文本
 * @param {Function} props.onClick - 点击回调
 * @param {'primary'|'secondary'|'danger'} [props.type='primary'] - 按钮类型
 * @param {'small'|'medium'|'large'} [props.size='medium'] - 按钮尺寸
 * @param {boolean} [props.disabled=false] - 是否禁用
 * @param {boolean} [props.loading=false] - 是否加载中
 * @example
 * <Button type="primary" onClick={handleClick}>
 *   提交
 * </Button>
 */
function Button({ children, onClick, type = 'primary', ...props }) {
  // ...
}
```

### 7.2 Storybook

```javascript
// Button.stories.js
export default {
  title: 'Components/Button',
  component: Button
};

export const Primary = () => <Button type="primary">Primary</Button>;
export const Secondary = () => <Button type="secondary">Secondary</Button>;
export const Disabled = () => <Button disabled>Disabled</Button>;
export const Loading = () => <Button loading>Loading</Button>;
```

### 7.3 README

```markdown
# Button 组件

## 基本用法

\`\`\`jsx
<Button type="primary" onClick={handleClick}>
  提交
</Button>
\`\`\`

## API

| 参数 | 说明 | 类型 | 默认值 |
|------|------|------|--------|
| children | 按钮文本 | ReactNode | - |
| onClick | 点击回调 | Function | - |
| type | 按钮类型 | 'primary' \| 'secondary' \| 'danger' | 'primary' |
| size | 按钮尺寸 | 'small' \| 'medium' \| 'large' | 'medium' |
| disabled | 是否禁用 | boolean | false |
| loading | 是否加载中 | boolean | false |
```

## 九、实战案例：封装一个 Modal

```typescript
// Modal.tsx
import { useEffect, useRef } from 'react';
import { createPortal } from 'react-dom';

interface ModalProps {
  visible: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  width?: number;
  maskClosable?: boolean;
}

function Modal({
  visible,
  onClose,
  title,
  children,
  footer,
  width = 520,
  maskClosable = true
}: ModalProps) {
  const modalRef = useRef<HTMLDivElement>(null);

  // ESC 关闭
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && visible) onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [visible, onClose]);

  // 阻止滚动
  useEffect(() => {
    if (visible) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  }, [visible]);

  if (!visible) return null;

  const handleMaskClick = (e: React.MouseEvent) => {
    if (maskClosable && e.target === e.currentTarget) {
      onClose();
    }
  };

  return createPortal(
    <div className="modal-mask" onClick={handleMaskClick}>
      <div className="modal-wrapper">
        <div className="modal" ref={modalRef} style={{ width }}>
          {title && (
            <div className="modal-header">
              <h3>{title}</h3>
              <button onClick={onClose}>×</button>
            </div>
          )}
          <div className="modal-body">{children}</div>
          {footer && <div className="modal-footer">{footer}</div>}
        </div>
      </div>
    </div>,
    document.body
  );
}

export default Modal;
```

使用：

```typescript
function App() {
  const [visible, setVisible] = useState(false);

  return (
    <>
      <button onClick={() => setVisible(true)}>打开弹窗</button>
      
      <Modal
        visible={visible}
        onClose={() => setVisible(false)}
        title="确认删除"
        footer={
          <>
            <button onClick={() => setVisible(false)}>取消</button>
            <button onClick={handleDelete}>确定</button>
          </>
        }
      >
        确定要删除这条记录吗？
      </Modal>
    </>
  );
}
```

## 十、检查清单

封装组件前，问自己这些问题：

- [ ] 职责是否单一？能否拆得更细？
- [ ] Props 是否清晰？必填和可选是否标注？
- [ ] 状态放在哪一层？是否需要提升或下沉?
- [ ] 逻辑是否可以抽成 Hook？
- [ ] 是否预留了扩展点（renderItem、className 等）？
- [ ] 是否处理了加载、错误、空状态？
- [ ] 是否有文档和示例？
- [ ] 是否可测试？

## 总结

完美组件封装的 7 个原则：

1. **单一职责**：一个组件只做一件事
2. **Props 合理**：必填可选分明，避免过多参数
3. **状态管理**：该提升提升，该下沉下沉
4. **逻辑分离**：用 Hook 抽离业务逻辑
5. **可扩展**：预留 renderItem、className 等扩展点
6. **错误处理**：加载、错误、空状态都要考虑
7. **文档完善**：JSDoc + Storybook + README

遵循这些原则，你的组件会更易用、易维护、易测试。
