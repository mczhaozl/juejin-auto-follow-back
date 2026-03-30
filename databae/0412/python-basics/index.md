# Python 基础入门：从变量到函数

> 全面介绍 Python 基础语法，包括变量、数据类型、控制流程、函数，以及 Python 独特的列表推导式和生成器。

## 一、基础语法

### 1.1 变量

```python
# 变量定义
name = "张三"
age = 25
is_active = True

# 多变量赋值
x, y, z = 1, 2, 3
a = b = c = 0
```

### 1.2 数据类型

```python
# 基本类型
int_num = 10        # 整数
float_num = 3.14    # 浮点数
str_text = "hello"  # 字符串
bool_val = True     # 布尔值

# 容器类型
my_list = [1, 2, 3]        # 列表
my_tuple = (1, 2, 3)       # 元组
my_dict = {"name": "张三"}   # 字典
my_set = {1, 2, 3}         # 集合
```

## 二、控制流

### 2.1 条件判断

```python
age = 18

if age >= 18:
    print("成年")
elif age >= 12:
    print("青少年")
else:
    print("未成年")
```

### 2.2 循环

```python
# for 循环
for i in range(5):
    print(i)

for item in [1, 2, 3]:
    print(item)

# while 循环
count = 0
while count < 5:
    print(count)
    count += 1
```

### 2.3 推导式

```python
# 列表推导式
squares = [x**2 for x in range(10)]

# 字典推导式
words = ["hello", "world"]
word_len = {w: len(w) for w in words}
```

## 三、函数

### 3.1 定义函数

```python
def greet(name):
    return f"Hello, {name}!"

# 默认参数
def greet(name, greeting="Hello"):
    return f"{greeting}, {name}!"
```

### 3.2 可变参数

```python
def sum_all(*args):
    return sum(args)

def print_info(**kwargs):
    for key, value in kwargs.items():
        print(f"{key}: {value}")

sum_all(1, 2, 3)  # 6
print_info(name="张三", age=25)
```

### 3.3 匿名函数

```python
add = lambda x, y: x + y
square = lambda x: x ** 2
```

## 四、字符串

### 4.1 格式化

```python
name = "张三"
age = 25

# f-string
print(f"我叫{name}, 今年{age}岁")

# format
print("我叫{}, 今年{}岁".format(name, age))
```

### 4.2 常用方法

```python
s = "Hello, World!"

s.upper()        # HELLO, WORLD!
s.lower()        # hello, world!
s.split(",")     # ['Hello', ' World!']
s.replace("World", "Python")  # Hello, Python!
```

## 五、面向对象

### 5.1 类定义

```python
class User:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, I'm {self.name}"

user = User("张三", 25)
print(user.greet())
```

### 5.2 继承

```python
class Animal:
    def __init__(self, name):
        self.name = name
    
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"
```

## 六、总结

Python 基础核心要点：

1. **变量**：动态类型
2. **容器**：list/dict/set/tuple
3. **推导式**：列表、字典
4. **函数**：def、lambda
5. **字符串**：f-string、常用方法
6. **类**：定义、继承

掌握这些，Python 入门不再难！

---

**推荐阅读**：
- [Python 官方文档](https://docs.python.org/3/)

**如果对你有帮助，欢迎点赞收藏！**
