# Python Pytest 完全指南

## 一、基础测试

```python
# test_sample.py
def test_add():
    assert 1 + 1 == 2
```

## 二、Fixture

```python
import pytest

@pytest.fixture
def db():
    return {'a': 1}

def test_db(db):
    assert db['a'] == 1
```

## 三、parametrize

```python
import pytest

@pytest.mark.parametrize('a,b,expected', [
    (1, 2, 3),
    (4, 5, 9),
])
def test_sum(a, b, expected):
    assert a + b == expected
```

## 四、mock

```python
from unittest.mock import Mock

def test_something():
    m = Mock()
    m.return_value = 'expected'
    assert m() == 'expected'
```

## 最佳实践
- fixture 管理依赖
- parametrize 参数化
- 使用 mock 隔离外部
- 保持测试快速
- 组织测试结构
