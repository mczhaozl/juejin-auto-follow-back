# ahooks useVirtualList：轻松实现百万数据的虚拟滚动

> 从原理到实战，掌握虚拟列表的性能优化技巧

---

## 一、为什么需要虚拟列表

渲染大量列表项会导致性能问题。

```javascript
// ❌ 渲染 10000 条数据，页面卡死
function List() {
  const data = Array.from({ length: 10000 }, (_, i) => ({ id: i, text: `Item ${i}` }));
  
  return (
    <div>
      {data.map(item => (
        <div key={item.id}>{item.text}</div>
      ))}
    </div>
  );
}
```

虚拟列表只渲染可见区域的项，大幅提升性能。

---

## 二、useVirtualList 基础用法

```javascript
import { useVirtualList } from 'ahooks';

function VirtualList() {
  const data = Array.from({ length: 10000 }, (_, i) => ({ id: i, text: `Item ${i}` }));
  
  const [list, scrollTo] = useVirtualList(data, {
    containerTarget: containerRef,
    wrapperTarget: wrapperRef,
    itemHeight: 50,
    overscan: 5
  });
  
  return (
    <div ref={containerRef} style={{ height: '600px', overflow: 'auto' }}>
      <div ref={wrapperRef}>
        {list.map(item => (
          <div key={item.data.id} style={{ height: '50px' }}>
            {item.data.text}
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 三、配置选项

```javascript
const [list, scrollTo] = useVirtualList(data, {
  // 容器元素
  containerTarget: containerRef,
  
  // 包裹元素
  wrapperTarget: wrapperRef,
  
  // 每项高度
  itemHeight: 50,
  
  // 预渲染数量
  overscan: 5
});
```

---

## 四、实战场景

### 场景 1：固定高度列表

```javascript
function UserList() {
  const [users] = useState(generateUsers(10000));
  const containerRef = useRef(null);
  const wrapperRef = useRef(null);
  
  const [list] = useVirtualList(users, {
    containerTarget: containerRef,
    wrapperTarget: wrapperRef,
    itemHeight: 60,
    overscan: 10
  });
  
  return (
    <div ref={containerRef} style={{ height: '600px', overflow: 'auto' }}>
      <div ref={wrapperRef}>
        {list.map(item => (
          <div key={item.data.id} style={{ height: '60px', padding: '10px' }}>
            <div>{item.data.name}</div>
            <div>{item.data.email}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 场景 2：滚动到指定位置

```javascript
function ScrollableList() {
  const [list, scrollTo] = useVirtualList(data, options);
  
  return (
    <>
      <button onClick={() => scrollTo(100)}>滚动到第 100 项</button>
      <button onClick={() => scrollTo(0)}>回到顶部</button>
      
      <div ref={containerRef} style={{ height: '600px', overflow: 'auto' }}>
        <div ref={wrapperRef}>
          {list.map(item => (
            <div key={item.index}>{item.data.text}</div>
          ))}
        </div>
      </div>
    </>
  );
}
```

---

## 五、性能对比

| 数据量 | 普通列表 | 虚拟列表 |
|--------|---------|---------|
| 100 | 流畅 | 流畅 |
| 1000 | 卡顿 | 流畅 |
| 10000 | 卡死 | 流畅 |
| 100000 | 崩溃 | 流畅 |

---

## 六、注意事项

1. **固定高度**：每项高度必须一致
2. **容器高度**：容器必须有固定高度
3. **key 值**：使用稳定的 key

---

## 总结

useVirtualList 让大数据列表渲染变得简单：

- 只渲染可见项
- 性能提升数十倍
- API 简单易用
- 支持滚动定位

处理大列表时，虚拟滚动是必备技术。

如果这篇文章对你有帮助，欢迎点赞收藏！
