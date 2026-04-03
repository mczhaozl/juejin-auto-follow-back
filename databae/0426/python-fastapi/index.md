# Python FastAPI 完全实战指南

FastAPI 是 Python 中最流行的现代 Web 框架之一。本文将带你从基础到高级，全面掌握 FastAPI。

## 一、FastAPI 基础

### 1. 安装和第一个应用

```python
# 安装
pip install fastapi uvicorn

# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# 运行
uvicorn main:app --reload
```

### 2. 路径参数和查询参数

```python
from fastapi import FastAPI

app = FastAPI()

# 路径参数
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}

# 路径参数验证
@app.get("/products/{product_id}")
async def get_product(product_id: int):
    return {"product_id": product_id}

# 查询参数
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# 必需查询参数
@app.get("/users/")
async def read_users(user_id: int, name: str):
    return {"user_id": user_id, "name": name}

# 可选查询参数
@app.get("/search/")
async def search_items(q: str | None = None):
    if q:
        return {"q": q}
    return {"message": "No query"}
```

### 3. 请求体和 Pydantic 模型

```python
from fastapi import FastAPI
from pydantic import BaseModel, Field, EmailStr
from typing import Optional

app = FastAPI()

class Item(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None
    tax: Optional[float] = None

class User(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    age: Optional[int] = Field(None, ge=0, le=120)

@app.post("/items/")
async def create_item(item: Item):
    return item

@app.post("/users/")
async def create_user(user: User):
    return user

# 路径参数 + 请求体
@app.put("/items/{item_id}")
async def update_item(item_id: int, item: Item):
    return {"item_id": item_id, **item.dict()}
```

### 4. 响应模型

```python
from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from typing import List

app = FastAPI()

class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserOut(BaseModel):
    username: str
    email: EmailStr

class Item(BaseModel):
    name: str
    price: float

@app.post("/users/", response_model=UserOut)
async def create_user(user: UserIn):
    return user

@app.get("/items/", response_model=List[Item])
async def read_items():
    return [
        {"name": "Item 1", "price": 10.99},
        {"name": "Item 2", "price": 20.99},
    ]
```

## 二、路径操作装饰器

### 1. HTTP 方法

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/")
async def read_items():
    return {"method": "GET"}

@app.post("/items/")
async def create_item():
    return {"method": "POST"}

@app.put("/items/{item_id}")
async def update_item(item_id: int):
    return {"method": "PUT", "item_id": item_id}

@app.delete("/items/{item_id}")
async def delete_item(item_id: int):
    return {"method": "DELETE", "item_id": item_id}

@app.patch("/items/{item_id}")
async def patch_item(item_id: int):
    return {"method": "PATCH", "item_id": item_id}
```

### 2. 状态码和响应头

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item():
    return {"message": "Item created"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    if item_id == 404:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Item not found"}
        )
    return {"item_id": item_id}

# 自定义响应头
@app.get("/headers/")
async def get_headers():
    content = {"message": "Hello World"}
    headers = {"X-Custom-Header": "custom value"}
    return JSONResponse(content=content, headers=headers)
```

## 三、表单数据和文件上传

### 1. 表单数据

```python
from fastapi import FastAPI, Form

app = FastAPI()

@app.post("/login/")
async def login(username: str = Form(...), password: str = Form(...)):
    return {"username": username}

@app.post("/contact/")
async def contact(
    name: str = Form(...),
    email: str = Form(...),
    message: str = Form(...)
):
    return {
        "name": name,
        "email": email,
        "message": message
    }
```

### 2. 文件上传

```python
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
from pathlib import Path

app = FastAPI()

# 单个文件上传
@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile = File(...)):
    return {"filename": file.filename}

# 多个文件上传
@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile] = File(...)):
    return {"filenames": [file.filename for file in files]}

# 保存文件
@app.post("/savefile/")
async def save_file(file: UploadFile = File(...)):
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    file_path = upload_dir / file.filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "path": str(file_path)}

# 文件下载
@app.get("/download/{filename}")
async def download_file(filename: str):
    file_path = Path("uploads") / filename
    if file_path.exists():
        return FileResponse(file_path)
    return {"error": "File not found"}
```

## 四、依赖注入

### 1. 基础依赖

```python
from fastapi import FastAPI, Depends

app = FastAPI()

async def common_parameters(q: str | None = None, skip: int = 0, limit: int = 100):
    return {"q": q, "skip": skip, "limit": limit}

@app.get("/items/")
async def read_items(commons: dict = Depends(common_parameters)):
    return commons

@app.get("/users/")
async def read_users(commons: dict = Depends(common_parameters)):
    return commons
```

### 2. 类作为依赖

```python
from fastapi import FastAPI, Depends

app = FastAPI()

class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit: int = 100):
        self.q = q
        self.skip = skip
        self.limit = limit

@app.get("/items/")
async def read_items(commons: CommonQueryParams = Depends(CommonQueryParams)):
    return commons

@app.get("/users/")
async def read_users(commons: CommonQueryParams = Depends()):
    return commons
```

### 3. 子依赖

```python
from fastapi import FastAPI, Depends

app = FastAPI()

def query_extractor(q: str | None = None):
    return q

def query_or_cookie_extractor(
    q: str = Depends(query_extractor),
    last_query: str | None = None
):
    if not q:
        return last_query
    return q

@app.get("/items/")
async def read_query(query_or_default: str = Depends(query_or_cookie_extractor)):
    return {"q_or_cookie": query_or_default}
```

### 4. 路径操作装饰器中的依赖

```python
from fastapi import FastAPI, Depends, HTTPException, status

app = FastAPI()

async def verify_token(x_token: str):
    if x_token != "fake-super-secret-token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.get("/items/", dependencies=[Depends(verify_token)])
async def read_items():
    return {"items": "all items"}
```

## 五、安全和认证

### 1. OAuth2 密码流

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError

app = FastAPI()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class User(BaseModel):
    username: str
    email: str | None = None
    disabled: bool | None = None

class UserInDB(User):
    hashed_password: str

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    }
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return fake_users_db[plain_password]["hashed_password"] == hashed_password

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = UserInDB(**user_dict)
    if not form_data.password == user.hashed_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
```

### 2. API Key 认证

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security.api_key import APIKeyQuery, APIKeyCookie, APIKeyHeader

app = FastAPI()

API_KEY = "secret-api-key"
API_KEY_NAME = "access_token"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
api_key_cookie = APIKeyCookie(name=API_KEY_NAME, auto_error=False)

async def get_api_key(
    api_key_query: str = Depends(api_key_query),
    api_key_header: str = Depends(api_key_header),
    api_key_cookie: str = Depends(api_key_cookie),
):
    if api_key_query == API_KEY:
        return api_key_query
    if api_key_header == API_KEY:
        return api_key_header
    if api_key_cookie == API_KEY:
        return api_key_cookie
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate credentials"
    )

@app.get("/secure")
async def secure_endpoint(api_key: str = Depends(get_api_key)):
    return {"message": "Secure endpoint accessed", "api_key": api_key}
```

## 六、数据库集成

### 1. SQLAlchemy 集成

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String, index=True)

Base.metadata.create_all(bind=engine)

class ItemBase(BaseModel):
    name: str
    price: float
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        orm_mode = True

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/items/", response_model=Item)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[Item])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(ItemDB).offset(skip).limit(limit).all()
    return items

@app.get("/items/{item_id}", response_model=Item)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemDB).filter(ItemDB.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}
```

### 2. 异步数据库（SQLAlchemy 2.0）

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import select, Column, Integer, String, Float
from pydantic import BaseModel

DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()

class ItemDB(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String, index=True)

class ItemBase(BaseModel):
    name: str
    price: float
    description: str | None = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    class Config:
        orm_mode = True

app = FastAPI()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.post("/items/", response_model=Item)
async def create_item(item: ItemCreate, db: AsyncSession = Depends(get_db)):
    db_item = ItemDB(**item.dict())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[Item])
async def read_items(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ItemDB).offset(skip).limit(limit))
    items = result.scalars().all()
    return items
```

## 七、中间件和 CORS

### 1. 中间件

```python
from fastapi import FastAPI, Request
import time

app = FastAPI()

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

### 2. CORS

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}
```

## 八、测试

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/")
async def read_main():
    return {"msg": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Hello World"}

def test_read_item():
    response = client.get("/items/42")
    assert response.status_code == 200
    assert response.json() == {"item_id": 42}
```

## 九、最佳实践

1. 使用 Pydantic 进行数据验证
2. 合理使用依赖注入
3. 实现认证和授权
4. 使用异步数据库提高性能
5. 添加适当的中间件
6. 配置 CORS
7. 编写完整的测试
8. 使用响应模型
9. 合理组织代码结构
10. 使用环境变量配置

## 十、总结

FastAPI 核心要点：
- 路径操作和参数
- Pydantic 模型和验证
- 请求体和响应模型
- 依赖注入
- 安全和认证
- 数据库集成（SQLAlchemy）
- 中间件和 CORS
- 测试
- 最佳实践

开始用 FastAPI 构建你的 API 吧！
