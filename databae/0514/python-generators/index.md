# Python 生成器与协程完全指南

## 一、基础生成器

```python
def fib(n):
    a, b = 0, 1
    for _ in range(n):
        yield b
        a, b = b, a + b

for num in fib(10):
    print(num)
```

## 二、send() 和 next()

```python
def generator():
    while True:
        val = yield
        print('Got:', val)

g = generator()
next(g)
g.send(1) # Got:1
g.send(2) # Got:2
```

## 三、yield from

```python
def sub_generator():
    yield 1
    yield 2

def main_gen():
    yield from sub_generator()
    yield 3

for num in main_gen():
    print(num)
```

## 四、asyncio

```python
import asyncio

async def hello(name):
    await asyncio.sleep(1)
    print(f'Hello {name}')

async def main():
    await asyncio.gather(
        hello('Alice'),
        hello('Bob')
    )

asyncio.run(main())
```

## 最佳实践
- 生成器处理大数据流
- 理解 send/throw/close
- yield from 组合协程
- async/await 替代回调
- 避免协程中阻塞操作
