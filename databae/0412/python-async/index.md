# Python 异步编程完全指南：asyncio 与 async/await

> 深入讲解 Python 异步编程，包括 asyncio、async/await 语法、协程、任务管理，以及实际项目中的异步应用案例。

## 一、asyncio 基础

### 1.1 协程

```python
import asyncio

# 定义协程
async def hello():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

# 运行协程
asyncio.run(hello())
```

### 1.2 async/await

```python
async def fetch_data():
    print("开始获取数据")
    await asyncio.sleep(2)
    print("数据获取完成")
    return {"data": "test"}

async def main():
    result = await fetch_data()
    print(result)

asyncio.run(main())
```

## 二、并发任务

### 2.1 创建多个任务

```python
async def task(name, delay):
    print(f"{name} 开始")
    await asyncio.sleep(delay)
    print(f"{name} 完成")
    return name

async def main():
    # 创建任务
    t1 = asyncio.create_task(task("任务1", 2))
    t2 = asyncio.create_task(task("任务2", 1))
    
    # 等待所有任务
    results = await asyncio.gather(t1, t2)
    print(results)

asyncio.run(main())
```

### 2.2 Task 管理

```python
async def main():
    # 创建任务
    task = asyncio.create_task(some_coroutine())
    
    # 取消任务
    task.cancel()
    
    try:
        await task
    except asyncio.CancelledError:
        print("任务被取消")
```

## 三、异步迭代

### 3.1 异步生成器

```python
async def async_range(start, stop):
    for i in range(start, stop):
        await asyncio.sleep(0.1)
        yield i

async def main():
    async for i in async_range(0, 5):
        print(i)
```

### 3.2 异步列表推导

```python
async def main():
    # 使用 gather 收集结果
    results = await asyncio.gather(*[fetch(i) for i in range(5)])
```

## 四、异步上下文管理

### 4.1 异步 with

```python
class AsyncConnection:
    async def __aenter__(self):
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

async def main():
    async with AsyncConnection() as conn:
        await conn.query("SELECT * FROM users")
```

## 五、实战案例

### 5.1 异步 HTTP 请求

```python
import aiohttp

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

async def main():
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, f"https://api.example.com/{i}") for i in range(5)]
        results = await asyncio.gather(*tasks)

asyncio.run(main())
```

### 5.2 异步数据库

```python
import asyncio
import asyncpg

async def query_db():
    conn = await asyncpg.connect(host='localhost', database='mydb')
    users = await conn.fetch('SELECT * FROM users')
    await conn.close()
    return users
```

### 5.3 限流控制

```python
async def limited_task(semaphore, task_id):
    async with semaphore:
        print(f"任务 {task_id} 开始")
        await asyncio.sleep(1)
        print(f"任务 {task_id} 完成")

async def main():
    semaphore = asyncio.Semaphore(3)  # 最多3个并发
    
    tasks = [limited_task(semaphore, i) for i in range(10)]
    await asyncio.gather(*tasks)

asyncio.run(main())
```

## 六、总结

Python 异步核心要点：

1. **async/await**：定义和等待协程
2. **asyncio.run()**：运行入口
3. **create_task**：创建并发任务
4. **gather**：收集结果
5. **Semaphore**：并发控制
6. **async with**：异步上下文

掌握这些，Python 异步不再难！

---

**推荐阅读**：
- [Python asyncio 文档](https://docs.python.org/3/library/asyncio.html)

**如果对你有帮助，欢迎点赞收藏！**
