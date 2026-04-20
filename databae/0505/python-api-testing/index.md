# Python API 测试完全指南

## 一、FastAPI 应用

```python
# main.py
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class User(BaseModel):
    id: int
    name: str

users = {}

@app.get("/users/{user_id}")
def get_user(user_id: int):
    if user_id in users:
        return users[user_id]
    return {"error": "User not found"}, 404

@app.post("/users")
def create_user(user: User):
    users[user.id] = user
    return user
```

## 二、Pytest 测试

```python
# test_api.py
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user():
    response = client.post(
        "/users",
        json={"id": 1, "name": "Alice"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"

def test_get_user():
    client.post(
        "/users",
        json={"id": 1, "name": "Alice"}
    )
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Alice"
```

## 三、Mock 数据库

```python
import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_db():
    with patch('main.Database') as mock:
        mock.return_value.get_user.return_value = User(id=1, name="Alice")
        yield mock

def test_with_mock_db(mock_db):
    client = TestClient(app)
    response = client.get("/users/1")
    assert response.status_code == 200
```

## 四、fixtures

```python
import pytest
from fastapi.testclient import TestClient

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def authenticated_client(client):
    # 添加认证
    client.headers["Authorization"] = "Bearer token"
    return client

def test_authorized_endpoint(authenticated_client):
    response = authenticated_client.get("/protected")
    assert response.status_code == 200
```

## 五、参数化测试

```python
import pytest

@pytest.mark.parametrize("user_id, expected_status", [
    (1, 200),
    (999, 404),
])
def test_get_user(client, user_id, expected_status):
    response = client.get(f"/users/{user_id}")
    assert response.status_code == expected_status
```

## 六、最佳实践

- 使用 fixtures 复用代码
- 模拟外部依赖
- 测试各种场景（成功、失败、边界条件）
- 保持测试独立
- 使用参数化测试覆盖多种情况
- 定期运行测试套件
