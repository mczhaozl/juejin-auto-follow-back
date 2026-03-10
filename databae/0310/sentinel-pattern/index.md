# 前端哨兵模式（Sentinel Pattern）：优雅实现无限滚动加载

> 用一个不可见元素作为触发器，告别复杂的滚动计算，让无限加载变得简单又高效。

---

## 一、什么是哨兵模式

在实现无限滚动加载时，传统做法是监听 `scroll` 事件，计算滚动位置、元素高度、视口距离等，代码复杂且性能开销大。哨兵模式（Sentinel Pattern）换了个思路：在列表底部放一个「哨兵元素」，当它进入视口时触发加载，利用浏览器原生的 Intersection Observer API 实现，代码简洁、性能更好。

核心思想：用一个不可见的 DOM 元素作为触发器，浏览器帮你监测它是否可见，你只需关注「可见时做什么」。

## 二、为什么选择哨兵模式

传统 scroll 方案的痛点：

- 需要手动计算 `scrollTop`、`scrollHeight`、`clientHeight`
- 高频触发事件，即使加了节流也有性能损耗
- 代码可读性差，维护成本高

哨兵模式的优势：

- 浏览器原生 API 支持，性能优化由浏览器完成
- 代码量少，逻辑清晰
- 支持多个哨兵（比如顶部加载更多、底部加载更多）
- 自动处理元素进入/离开视口的状态

## 三、基础实现

### 3.1 HTML 结构

```html
<div class="list-container">
  <div class="list-item">Item 1</div>
  <div class="list-item">Item 2</div>
  <!-- 更多列表项 -->
  
  <!-- 哨兵元素 -->
  <div class="sentinel" id="sentinel"></div>
</div>

<div class="loading">加载中...</div>
```

### 3.2 CSS 样式

```css
.sentinel {
  height: 1px;
  /* 不可见但占据空间 */
  visibility: hidden;
}

.loading {
  display: none;
  text-align: center;
  padding: 20px;
}

.loading.active {
  display: block;
}
```

### 3.3 JavaScript 核心逻辑

```javascript
let page = 1;
let isLoading = false;

// 创建观察器
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    // 哨兵进入视口且未在加载中
    if (entry.isIntersecting && !isLoading) {
      loadMore();
    }
  });
}, {
  // 提前 100px 触发
  rootMargin: '100px'
});

// 开始观察哨兵元素
const sentinel = document.getElementById('sentinel');
observer.observe(sentinel);

// 加载更多数据
async function loadMore() {
  isLoading = true;
  document.querySelector('.loading').classList.add('active');
  
  try {
    const data = await fetchData(page);
    renderItems(data);
    page++;
  } catch (error) {
    console.error('加载失败', error);
  } finally {
    isLoading = false;
    document.querySelector('.loading').classList.remove('active');
  }
}

// 模拟数据获取
async function fetchData(page) {
  const response = await fetch(`/api/items?page=${page}`);
  return response.json();
}

// 渲染列表项
function renderItems(items) {
  const container = document.querySelector('.list-container');
  const sentinel = document.getElementById('sentinel');
  
  items.forEach(item => {
    const div = document.createElement('div');
    div.className = 'list-item';
    div.textContent = item.title;
    // 插入到哨兵之前
    container.insertBefore(div, sentinel);
  });
}
```

## 四、React 实现

```javascript
import { useEffect, useRef, useState } from 'react';

function InfiniteList() {
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const sentinelRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && !loading && hasMore) {
          loadMore();
        }
      },
      { rootMargin: '100px' }
    );

    if (sentinelRef.current) {
      observer.observe(sentinelRef.current);
    }

    return () => observer.disconnect();
  }, [loading, hasMore]);

  const loadMore = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/items?page=${page}`);
      const data = await response.json();
      
      if (data.length === 0) {
        setHasMore(false);
      } else {
        setItems(prev => [...prev, ...data]);
        setPage(prev => prev + 1);
      }
    } catch (error) {
      console.error('加载失败', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      {items.map((item, index) => (
        <div key={index} className="list-item">
          {item.title}
        </div>
      ))}
      
      {/* 哨兵元素 */}
      <div ref={sentinelRef} style={{ height: 1, visibility: 'hidden' }} />
      
      {loading && <div className="loading">加载中...</div>}
      {!hasMore && <div className="no-more">没有更多了</div>}
    </div>
  );
}
```

## 五、进阶技巧

### 5.1 双向加载

同时支持向上和向下加载：

```javascript
// 顶部哨兵
const topSentinel = document.getElementById('top-sentinel');
const bottomSentinel = document.getElementById('bottom-sentinel');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.target === topSentinel && entry.isIntersecting) {
      loadPrevious(); // 加载上一页
    }
    if (entry.target === bottomSentinel && entry.isIntersecting) {
      loadNext(); // 加载下一页
    }
  });
});

observer.observe(topSentinel);
observer.observe(bottomSentinel);
```

### 5.2 虚拟滚动结合

对于超长列表，结合虚拟滚动优化性能：

```javascript
// 只渲染可见区域 + 缓冲区的元素
const visibleItems = items.slice(startIndex, endIndex);

return (
  <div style={{ height: totalHeight }}>
    <div style={{ transform: `translateY(${offsetY}px)` }}>
      {visibleItems.map(item => (
        <div key={item.id}>{item.title}</div>
      ))}
    </div>
    <div ref={sentinelRef} />
  </div>
);
```

### 5.3 错误重试

加载失败时显示重试按钮：

```javascript
const [error, setError] = useState(null);

const loadMore = async () => {
  setLoading(true);
  setError(null);
  
  try {
    // 加载逻辑
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};

// 渲染
{error && (
  <div className="error">
    加载失败：{error}
    <button onClick={loadMore}>重试</button>
  </div>
)}
```

## 六、注意事项

1. **防止重复触发**：用 `isLoading` 标志位避免并发请求
2. **提前加载**：通过 `rootMargin` 设置提前触发距离，提升体验
3. **结束判断**：后端返回空数组时停止观察，避免无效请求
4. **内存泄漏**：组件卸载时记得 `observer.disconnect()`
5. **兼容性**：Intersection Observer 支持 IE11+，旧浏览器需 polyfill

## 七、与其他方案对比

| 方案 | 性能 | 代码复杂度 | 兼容性 |
|------|------|-----------|--------|
| scroll 事件 | 中 | 高 | 好 |
| Intersection Observer | 高 | 低 | IE11+ |
| 第三方库（react-infinite-scroll） | 中 | 低 | 好 |

哨兵模式适合现代浏览器环境，追求性能和代码简洁的场景。

## 总结

哨兵模式用一个不可见元素作为触发器，配合 Intersection Observer API 实现无限滚动，代码简洁、性能优秀。核心要点：

- 在列表底部放置哨兵元素
- 用 IntersectionObserver 监听其可见性
- 可见时触发加载，加防重复逻辑
- 支持双向加载、虚拟滚动等进阶场景

比传统 scroll 方案更优雅，推荐在新项目中使用。
