# Python 装饰器完全指南

## 一、基础装饰器

```python
def my_decorator(func):
    def wrapper():
        print("Before function")
        func()
        print("After function")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
```

## 二、带参数的装饰器

```python
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - start}s")
        return result
    return wrapper

@timer
def slow_function():
    import time
    time.sleep(1)

slow_function()
```

## 三、装饰器带参数

```python
def repeat(n):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(n):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def greet(name):
    print(f"Hello {name}!")

greet("Alice")
```

## 四、类装饰器

```python
class CountCalls:
    def __init__(self, func):
        self.func = func
        self.num_calls = 0
    
    def __call__(self, *args, **kwargs):
        self.num_calls += 1
        return self.func(*args, **kwargs)

@CountCalls
def say_hi():
    print("Hi!")

say_hi()
say_hi()
print(say_hi.num_calls)
```

## 最佳实践
- 使用 functools.wraps 保留元信息
- 装饰器尽量简单
- 考虑装饰器的执行顺序
- 善用内置装饰器 (@property, @staticmethod, @classmethod)
- 注意装饰器与类型注解的配合
