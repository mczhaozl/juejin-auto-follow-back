# 后端架构设计模式：构建高可用分布式系统的核心实践

> 从单体到微服务，系统梳理后端架构设计的关键模式与最佳实践

---

## 一、后端架构的演进

后端架构经历了从单体应用到微服务的演进：

- **单体架构**：所有功能在一个应用中，开发简单但扩展困难
- **SOA 架构**：服务化思想初步形成，但仍然重量级
- **微服务架构**：服务独立部署、独立扩展，但复杂度增加
- **云原生架构**：容器化、服务网格、Serverless 成为主流

理解这些架构模式，能帮助你在不同阶段做出正确的技术决策。

## 二、服务拆分模式

### 2.1 按业务能力拆分

```python
# 用户服务 - user-service/
class UserService:
    def get_user(self, user_id: int) -> User:
        """获取用户信息"""
        pass
    
    def update_profile(self, user_id: int, profile: Profile) -> User:
        """更新用户资料"""
        pass
    
    def check_permission(self, user_id: int, resource: str) -> bool:
        """权限检查"""
        pass

# 订单服务 - order-service/
class OrderService:
    def create_order(self, user_id: int, items: List[OrderItem]) -> Order:
        """创建订单"""
        pass
    
    def get_orders(self, user_id: int, status: str = None) -> List[Order]:
        """获取订单列表"""
        pass
    
    def cancel_order(self, order_id: int) -> bool:
        """取消订单"""
        pass

# 支付服务 - payment-service/
class PaymentService:
    def process_payment(self, order_id: int, method: str) -> PaymentResult:
        """处理支付"""
        pass
    
    def refund(self, payment_id: int, amount: float) -> bool:
        """退款"""
        pass
```

### 2.2 按领域拆分

```
src/
├── domain/                    # 领域层
│   ├── user/                  # 用户领域
│   │   ├── entities/          # 实体
│   │   ├── value_objects/     # 值对象
│   │   ├── aggregates/        # 聚合根
│   │   ├── repositories/      # 仓储接口
│   │   └── services/          # 领域服务
│   ├── order/                 # 订单领域
│   │   ├── entities/
│   │   ├── value_objects/
│   │   ├── aggregates/
│   │   ├── repositories/
│   │   └── services/
│   └── payment/               # 支付领域
│       ├── entities/
│       ├── value_objects/
│       ├── aggregates/
│       ├── repositories/
│       └── services/
├── application/               # 应用层
│   ├── user/
│   │   ├── dto/               # 数据传输对象
│   │   ├── services/          # 应用服务
│   │   └── facades/           # 服务门面
│   ├── order/
│   └── payment/
├── infrastructure/            # 基础设施层
│   ├── persistence/           # 持久化
│   ├── messaging/             # 消息队列
│   └── external/              # 外部服务
└── interfaces/                # 接口层
    ├── rest/
    ├── grpc/
    └── webhooks/
```

## 三、数据访问模式

### 3.1 仓储模式

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    @abstractmethod
    def find_by_id(self, user_id: int) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    def find_all(self, page: int, size: int) -> List[User]:
        pass
    
    @abstractmethod
    def save(self, user: User) -> User:
        pass
    
    @abstractmethod
    def delete(self, user_id: int) -> bool:
        pass

# PostgreSQL 实现
class PostgresUserRepository(UserRepository):
    def __init__(self, connection: Connection):
        self.connection = connection
    
    def find_by_id(self, user_id: int) -> Optional[User]:
        with self.connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE id = %s",
                (user_id,)
            )
            row = cursor.fetchone()
            return User.from_row(row) if row else None
    
    def save(self, user: User) -> User:
        if user.id:
            # 更新
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    UPDATE users SET 
                        name = %s, email = %s, updated_at = NOW()
                    WHERE id = %s
                """, (user.name, user.email, user.id))
        else:
            # 插入
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO users (name, email, created_at, updated_at)
                    VALUES (%s, %s, NOW(), NOW())
                    RETURNING id
                """, (user.name, user.email))
                user.id = cursor.fetchone()[0]
        return user
```

### 3.2 工作单元模式

```python
class UnitOfWork:
    def __init__(self, connection: Connection):
        self.connection = connection
        self._new_objects = []
        self._dirty_objects = []
        self._removed_objects = []
    
    def register_new(self, obj):
        self._new_objects.append(obj)
    
    def register_dirty(self, obj):
        self._dirty_objects.append(obj)
    
    def register_removed(self, obj):
        self._removed_objects.append(obj)
    
    def commit(self):
        try:
            # 插入新对象
            for obj in self._new_objects:
                if hasattr(obj, '_insert'):
                    obj._insert(self.connection)
            
            # 更新脏对象
            for obj in self._dirty_objects:
                if hasattr(obj, '_update'):
                    obj._update(self.connection)
            
            # 删除对象
            for obj in self._removed_objects:
                if hasattr(obj, '_delete'):
                    obj._delete(self.connection)
            
            self.connection.commit()
            
            # 清空缓存
            self._new_objects.clear()
            self._dirty_objects.clear()
            self._removed_objects.clear()
            
        except Exception as e:
            self.connection.rollback()
            raise e
    
    def rollback(self):
        self.connection.rollback()
        self._new_objects.clear()
        self._dirty_objects.clear()
        self._removed_objects.clear()
```

### 3.3 CQRS 模式

```python
# 命令端 - 写操作
class CreateOrderCommand:
    def __init__(self, user_id: int, items: List[OrderItem]):
        self.user_id = user_id
        self.items = items

class CreateOrderHandler:
    def __init__(self, order_repository, event_bus):
        self.order_repository = order_repository
        self.event_bus = event_bus
    
    def handle(self, command: CreateOrderCommand):
        # 验证
        user = self._validate_user(command.user_id)
        items = self._validate_items(command.items)
        
        # 创建订单
        order = Order.create(user, items)
        self.order_repository.save(order)
        
        # 发布事件
        self.event_bus.publish(OrderCreatedEvent(order.id))
        
        return order.id

# 查询端 - 读操作
class OrderQueryService:
    def __init__(self, read_database: Connection):
        self.read_db = read_database
    
    def get_order_summary(self, order_id: int) -> OrderSummaryDTO:
        with self.read_db.cursor() as cursor:
            cursor.execute("""
                SELECT o.id, o.status, o.total_amount,
                       u.name as user_name, u.email,
                       json_agg(json_build_object(
                           'product_name', p.name,
                           'quantity', oi.quantity,
                           'price', oi.price
                       )) as items
                FROM orders o
                JOIN users u ON o.user_id = u.id
                JOIN order_items oi ON o.id = oi.order_id
                JOIN products p ON oi.product_id = p.id
                WHERE o.id = %s
                GROUP BY o.id, o.status, o.total_amount, u.name, u.email
            """, (order_id,))
            return OrderSummaryDTO.from_row(cursor.fetchone())
    
    def get_user_orders(self, user_id: int, page: int = 1) -> List[OrderListItem]:
        offset = (page - 1) * 20
        with self.read_db.cursor() as cursor:
            cursor.execute("""
                SELECT id, status, total_amount, created_at
                FROM orders
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 20 OFFSET %s
            """, (user_id, offset))
            return [OrderListItem.from_row(row) for row in cursor.fetchall()]
```

## 四、消息通信模式

### 4.1 事件驱动架构

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class DomainEvent(ABC):
    @property
    @abstractmethod
    def event_type(self) -> str:
        pass
    
    @property
    @abstractmethod
    def aggregate_id(self) -> str:
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'event_type': self.event_type,
            'aggregate_id': self.aggregate_id,
            'timestamp': datetime.utcnow().isoformat(),
            'payload': self._get_payload()
        }
    
    @abstractmethod
    def _get_payload(self) -> Dict[str, Any]:
        pass

class OrderCreatedEvent(DomainEvent):
    def __init__(self, order_id: int, user_id: int, total_amount: float):
        self._order_id = order_id
        self._user_id = user_id
        self._total_amount = total_amount
    
    @property
    def event_type(self) -> str:
        return 'order.created'
    
    @property
    def aggregate_id(self) -> str:
        return str(self._order_id)
    
    def _get_payload(self) -> Dict[str, Any]:
        return {
            'order_id': self._order_id,
            'user_id': self._user_id,
            'total_amount': self._total_amount
        }

# 事件总线
class EventBus:
    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}
    
    def subscribe(self, event_type: str, handler: Callable):
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
    
    def publish(self, event: DomainEvent):
        event_type = event.event_type
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                try:
                    handler(event)
                except Exception as e:
                    # 记录错误但不影响其他处理器
                    logger.error(f"Handler failed: {e}")
    
    def publish_async(self, event: DomainEvent):
        # 异步发布 - 使用消息队列
        message = json.dumps(event.to_dict())
        redis.publish('events', message)
```

### 4.2 Saga 模式

```python
class OrderSaga:
    def __init__(self, order_service, payment_service, inventory_service, notification_service):
        self.steps = [
            self._create_order,
            self._reserve_inventory,
            self._process_payment,
            self._confirm_order,
            self._send_notification
        ]
        self.compensating_steps = [
            self._cancel_order,
            self._release_inventory,
            self._refund_payment
        ]
    
    async def execute(self, order_data: dict) -> SagaResult:
        context = SagaContext()
        
        try:
            for step in self.steps:
                result = await step(order_data, context)
                context.add_step_result(step.__name__, result)
            
            return SagaResult.success(context)
            
        except Exception as e:
            # 执行补偿操作
            await self._execute_compensation(context)
            return SagaResult.failed(str(e))
    
    async def _create_order(self, order_data: dict, context: SagaContext) -> dict:
        order = await self.order_service.create(order_data)
        context.set('order_id', order.id)
        return {'order_id': order.id, 'status': 'created'}
    
    async def _reserve_inventory(self, order_data: dict, context: SagaContext) -> dict:
        order_id = context.get('order_id')
        result = await self.inventory_service.reserve(order_id)
        context.set('inventory_reserved', True)
        return {'inventory_id': result.id, 'status': 'reserved'}
    
    async def _process_payment(self, order_data: dict, context: SagaContext) -> dict:
        order_id = context.get('order_id')
        result = await self.payment_service.charge(order_id)
        context.set('payment_id', result.payment_id)
        return {'payment_id': result.payment_id, 'status': 'paid'}
    
    async def _cancel_order(self, context: SagaContext):
        order_id = context.get('order_id')
        await self.order_service.cancel(order_id)
    
    async def _release_inventory(self, context: SagaContext):
        if context.get('inventory_reserved'):
            inventory_id = context.get('inventory_id')
            await self.inventory_service.release(inventory_id)
    
    async def _refund_payment(self, context: SagaContext):
        if context.get('payment_id'):
            payment_id = context.get('payment_id')
            await self.payment_service.refund(payment_id)
```

### 4.3 消息队列模式

```python
import asyncio
from typing import Callable, Any

class MessageQueue:
    def __init__(self, broker: str):
        self.broker = broker
        self._consumers: Dict[str, List[Callable]] = {}
        self._running = False
    
    async def publish(self, topic: str, message: Any, priority: int = 0):
        """发布消息"""
        if self.broker == 'rabbitmq':
            await self._publish_rabbitmq(topic, message, priority)
        elif self.broker == 'kafka':
            await self._publish_kafka(topic, message)
        elif self.broker == 'redis':
            await self._publish_redis(topic, message)
    
    async def subscribe(self, topic: str, handler: Callable, group_id: str = None):
        """订阅消息"""
        if topic not in self._consumers:
            self._consumers[topic] = []
        self._consumers[topic].append(handler)
        
        if not self._running:
            self._running = True
            await self._start_consuming()
    
    async def _start_consuming(self):
        """开始消费消息"""
        for topic, handlers in self._consumers.items():
            asyncio.create_task(self._consume_loop(topic, handlers))
    
    async def _consume_loop(self, topic: str, handlers: List[Callable]):
        """消费循环"""
        while self._running:
            try:
                message = await self._get_message(topic)
                for handler in handlers:
                    try:
                        await handler(message)
                    except Exception as e:
                        logger.error(f"Handler error: {e}")
                        # 可以发送到死信队列
                        await self._send_to_dlq(topic, message, e)
            except Exception as e:
                logger.error(f"Consume error: {e}")
                await asyncio.sleep(1)  # 避免空转

# 使用示例
async def handle_order_created(message: dict):
    order_id = message['order_id']
    # 发送通知
    await notification_service.send_order_confirmation(order_id)
    # 更新库存
    await inventory_service.update(order_id)

mq = MessageQueue('rabbitmq')
await mq.subscribe('order.created', handle_order_created)
await mq.publish('order.created', {
    'order_id': 12345,
    'user_id': 678,
    'total': 99.99
})
```

## 五、缓存模式

### 5.1 多级缓存

```python
class MultiLevelCache:
    def __init__(self):
        # L1: 本地内存缓存
        self._l1 = {}
        # L2: Redis 分布式缓存
        self._l2 = None  # Redis client
        # L3: 数据库
    
    async def get(self, key: str) -> Any:
        # 先查 L1
        if key in self._l1:
            return self._l1[key]
        
        # 再查 L2
        if self._l2:
            value = await self._l2.get(key)
            if value:
                # 回填 L1
                self._l1[key] = value
                return value
        
        # 查 L3（数据库）
        value = await self._fetch_from_db(key)
        if value:
            # 回填 L1 和 L2
            self._l1[key] = value
            if self._l2:
                await self._l2.set(key, value, ttl=3600)
        
        return value
    
    async def set(self, key: str, value: Any, ttl: int = None):
        # 设置 L1
        self._l1[key] = value
        # 设置 L2
        if self._l2:
            await self._l2.set(key, value, ttl=ttl or 3600)
    
    async def delete(self, key: str):
        # 删除 L1
        self._l1.pop(key, None)
        # 删除 L2
        if self._l2:
            await self._l2.delete(key)
```

### 5.2 缓存穿透防护

```python
class CacheWithBloomFilter:
    def __init__(self, cache: MultiLevelCache, bloom_filter):
        self.cache = cache
        self.bloom_filter = bloom_filter
    
    async def get(self, key: str) -> Any:
        # 先检查布隆过滤器
        if not self.bloom_filter.might_contain(key):
            return None  # 一定不存在
        
        # 查缓存
        return await self.cache.get(key)
    
    async def set(self, key: str, value: Any, ttl: int = None):
        # 设置布隆过滤器
        self.bloom_filter.add(key)
        # 设置缓存
        await self.cache.set(key, value, ttl)

# 缓存空值防止缓存击穿
class CacheWithNullValue:
    def __init__(self):
        self._cache = {}
        self._null_cache = {}  # 存储空值
    
    async def get(self, key: str) -> Any:
        # 查普通缓存
        if key in self._cache:
            return self._cache[key]
        
        # 查空值缓存
        if key in self._null_cache:
            # 检查是否过期
            if time.time() - self._null_cache[key]['time'] < 60:
                return None  # 返回空，不查询数据库
            del self._null_cache[key]
        
        # 查数据库
        value = await self._fetch_from_db(key)
        if value:
            self._cache[key] = value
        else:
            # 写入空值缓存
            self._null_cache[key] = {'time': time.time()}
        
        return value
```

### 5.3 缓存一致性

```python
class CacheAsidePattern:
    def __init__(self, cache: MultiLevelCache, repository):
        self.cache = cache
        self.repository = repository
    
    async def get(self, key: str) -> Any:
        # 读缓存
        value = await self.cache.get(key)
        if value is not None:
            return value
        
        # 读数据库
        value = await self.repository.find_by_id(key)
        if value:
            # 写缓存
            await self.cache.set(key, value)
        
        return value
    
    async def set(self, key: str, value: Any):
        # 写数据库
        await self.repository.save(value)
        # 删除缓存（不是更新）
        await self.cache.delete(key)
    
    async def delete(self, key: str):
        # 删除数据库
        await self.repository.delete(key)
        # 删除缓存
        await self.cache.delete(key)
    
    async def update(self, key: str, updates: dict):
        # 更新数据库
        await self.repository.update(key, updates)
        # 删除缓存
        await self.cache.delete(key)
```

## 六、容错模式

### 6.1 断路器

```python
import asyncio
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = 'closed'      # 正常
    OPEN = 'open'          # 断开
    HALF_OPEN = 'half_open'  # 半开

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 5, 
                 recovery_timeout: int = 60, half_open_success_threshold: int = 2):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_success_threshold = half_open_success_threshold
        
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = None
        self._half_open_attempts = 0
    
    @property
    def state(self) -> CircuitState:
        if self._state == CircuitState.OPEN:
            if datetime.now() - self._last_failure_time > timedelta(seconds=self.recovery_timeout):
                self._state = CircuitState.HALF_OPEN
                self._half_open_attempts = 0
        return self._state
    
    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            raise CircuitOpenError(f"Circuit {self.name} is open")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        if self._state == CircuitState.HALF_OPEN:
            self._half_open_attempts += 1
            if self._half_open_attempts >= self.half_open_success_threshold:
                self._state = CircuitState.CLOSED
                self._failure_count = 0
        else:
            self._failure_count = 0
    
    def _on_failure(self):
        self._failure_count += 1
        self._last_failure_time = datetime.now()
        
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN

# 使用
circuit_breaker = CircuitBreaker('payment-service')

async def process_payment(order_id: int):
    return await circuit_breaker.call(payment_service.charge, order_id)
```

### 6.2 重试模式

```python
import asyncio
from typing import Callable, TypeVar, Optional

T = TypeVar('T')

class RetryPolicy:
    def __init__(self, max_attempts: int = 3, 
                 initial_delay: float = 1.0,
                 max_delay: float = 60.0,
                 exponential_base: float = 2.0,
                 retryable_exceptions: tuple = (Exception,)):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retryable_exceptions = retryable_exceptions
    
    async def execute(self, func: Callable[..., T], *args, **kwargs) -> T:
        last_exception = None
        
        for attempt in range(self.max_attempts):
            try:
                return await func(*args, **kwargs)
            except self.retryable_exceptions as e:
                last_exception = e
                if attempt < self.max_attempts - 1:
                    delay = self._calculate_delay(attempt)
                    await asyncio.sleep(delay)
        
        raise last_exception
    
    def _calculate_delay(self, attempt: int) -> float:
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)

# 使用
retry_policy = RetryPolicy(
    max_attempts=3,
    initial_delay=0.5,
    exponential_base=2.0,
    retryable_exceptions=(ConnectionError, TimeoutError, TransientError)
)

async def fetch_user(user_id: int):
    return await retry_policy.execute(user_service.get_by_id, user_id)
```

### 6.3 限流模式

```python
import asyncio
from collections import deque
from datetime import datetime, timedelta

class TokenBucket:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_update = datetime.now()
        self._lock = asyncio.Lock()
    
    async def acquire(self, tokens: int = 1) -> bool:
        async with self._lock:
            now = datetime.now()
            # 添加 tokens
            elapsed = (now - self.last_update).total_seconds()
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_update = now
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False

class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._windows: Dict[str, deque] = {}
        self._lock = asyncio.Lock()
    
    async def is_allowed(self, key: str) -> bool:
        async with self._lock:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds)
            
            if key not in self._windows:
                self._windows[key] = deque()
            
            window = self._windows[key]
            
            # 移除过期的请求
            while window and window[0] < window_start:
                window.popleft()
            
            # 检查是否超限
            if len(window) >= self.max_requests:
                return False
            
            # 记录新请求
            window.append(now)
            return True

# 使用
rate_limiter = SlidingWindowRateLimiter(max_requests=100, window_seconds=60)

async def handle_request(request_id: str):
    if not await rate_limiter.is_allowed(request_id):
        raise RateLimitExceeded()
    return await process_request(request_id)
```

## 七、总结

后端架构设计的关键模式：

- **服务拆分**：按业务能力或领域拆分，保持服务边界清晰
- **数据访问**：使用仓储模式、UOW、CQRS 分离读写操作
- **消息通信**：事件驱动、Saga 模式处理分布式事务
- **缓存策略**：多级缓存、缓存穿透防护、缓存一致性
- **容错设计**：断路器、重试、限流保护系统稳定

掌握这些模式，能帮助你构建高可用、可扩展的后端系统。

如果这篇文章对你有帮助，欢迎点赞收藏。
