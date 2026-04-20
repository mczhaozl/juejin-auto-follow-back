# Python asyncio 异步编程完全指南：从 async/await 到实战

## 一、异步编程概述

asyncio 是 Python 3.4+ 引入的异步编程框架，使用单线程协程模型实现高并发。

### 1.1 为什么需要异步

- I/O 密集任务等待时间长
- 多线程开销大、难同步
- 充分利用单线程性能
- 高并发场景表现好

### 1.2 核心概念

| 概念 | 描述 |
|-----|------|
| 协程 (Coroutine) | async 定义的函数 |
| 任务 (Task) | 事件循环调度的执行单元 |
| 事件循环 (Event Loop) | 管理与调度任务 |
| Future | 异步结果容器 |

---

## 二、基础语法

### 2.1 async/await 基础

```python
import asyncio

async def hello(name):
    await asyncio.sleep(1)  # 模拟 I/O
    return f"Hello, {name}!"

async def main():
    # 等待单个任务
    result = await hello("World")
    print(result)

asyncio.run(main())
```

### 2.2 并发运行多个任务

```python
async def main():
    # 创建任务
    task1 = asyncio.create_task(hello("Alice"))
    task2 = asyncio.create_task(hello("Bob"))
    
    # 等待所有任务
    result1 = await task1
    result2 = await task2
    print(result1, result2)
```

---

## 三、并发收集

### 3.1 gather()

```python
import asyncio
import time

async def task(name, delay):
    await asyncio.sleep(delay)
    return f"{name} done in {delay}s"

async def main():
    start = time.time()
    # 并发执行并收集结果
    results = await asyncio.gather(
        task("A", 1),
        task("B", 2),
        task("C", 1),
    )
    print(results)
    print(f"Total: {time.time() - start:.2f}s")
    # 输出约 2s（最长的那个）

asyncio.run(main())
```

### 3.2 as_completed()

```python
async def main():
    tasks = [task(f"Task-{i}", i) for i in range(1, 4)]
    
    for coro in asyncio.as_completed(tasks):
        result = await coro
        print(result)
```

---

## 四、Task 管理

### 4.1 Task 对象

```python
async def main():
    task = asyncio.create_task(task("A", 3))
    
    await asyncio.sleep(1)
    print("Task status:", task.done())
    
    await task
    print("Task result:", task.result())
```

### 4.2 取消任务

```python
async def main():
    task = asyncio.create_task(task("A", 10))
    
    await asyncio.sleep(1)
    task.cancel()  # 取消任务
    
    try:
        await task
    except asyncio.CancelledError:
        print("Task cancelled")
```

---

## 五、实战应用

### 5.1 并发 HTTP 请求

```python
import asyncio
import aiohttp

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = [
        "https://example.com",
        "https://example.org",
        "https://example.net"
    ]
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        responses = await asyncio.gather(*tasks)
        for html in responses:
            print(len(html))

asyncio.run(main())
```

### 5.2 生产者-消费者模式

```python
import asyncio
import random

async def producer(queue):
    for i in range(5):
        await asyncio.sleep(random.random())
        await queue.put(i)
        print(f"Produced {i}")
    await queue.put(None)

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        await asyncio.sleep(random.random())
        print(f"Consumed {item}")

async def main():
    queue = asyncio.Queue(maxsize=3)
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )

asyncio.run(main())
```

---

## 六、锁与同步

### 6.1 Lock

```python
async def safe_task(lock, value):
    async with lock:  # 获取锁
        print(f"Task {value} started")
        await asyncio.sleep(1)
        print(f"Task {value} done")

async def main():
    lock = asyncio.Lock()
    await asyncio.gather(
        safe_task(lock, 1),
        safe_task(lock, 2),
        safe_task(lock, 3),
    )
```

### 6.2 Semaphore

```python
async def limited_task(sem, name):
    async with sem:  # 限制并发数
        print(f"Task {name} running")
        await asyncio.sleep(1)

async def main():
    sem = asyncio.Semaphore(2)  # 最多 2 个并发
    await asyncio.gather(
        limited_task(sem, "A"),
        limited_task(sem, "B"),
        limited_task(sem, "C"),
    )
```

---

## 七、异步上下文

```python
class AsyncResource:
    async def __aenter__(self):
        await asyncio.sleep(0.1)
        print("Acquired resource")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await asyncio.sleep(0.1)
        print("Released resource")

async def main():
    async with AsyncResource():
        print("Using resource")
```

---

## 八、最佳实践

1. **用 asyncio.run() 启动程序**
2. **避免阻塞调用**：使用 aiofiles 替代 open
3. **使用 gather() 管理并发**
4. **适当使用 Semaphore 限流**
5. **注意异常处理**

---

## 九、总结

asyncio 是 Python 异步编程的核心库，掌握它能大幅提升 I/O 密集任务的性能。
