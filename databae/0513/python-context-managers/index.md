# Python 上下文管理器完全指南

## 一、基础用法

```python
# 1. 文件操作
with open('file.txt', 'r') as f:
    content = f.read()
print(content)

# 2. 锁
from threading import Lock
lock = Lock()

with lock:
    print("Critical section")

# 3. 数据库连接
with db_conn.cursor() as cursor:
    cursor.execute("SELECT * FROM users")
```

## 二、自定义上下文管理器

```python
# 1. 类方式
class Timer:
    def __enter__(self):
        import time
        self.start = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        print(f"Took {time.time() - self.start}s")

with Timer():
    # 耗时操作
    import time
    time.sleep(1)
```

## 三、contextlib

```python
from contextlib import contextmanager

@contextmanager
def timer():
    import time
    start = time.time()
    yield
    print(f"Took {time.time() - start}s")

with timer():
    time.sleep(1)
```

## 四、嵌套上下文管理器

```python
# with X as a, Y as b
with open('file1.txt') as f1, open('file2.txt') as f2:
    a = f1.read()
    b = f2.read()
```

## 最佳实践
- 优先使用内置上下文管理器
- contextlib 简化简单场景
- 注意 __exit__ 中的异常处理
- 资源清理要健壮
- contextlib.closing 包装没有上下文管理器的对象
