# 微服务架构完全指南：从理论到实战

微服务架构是现代软件开发的主流架构模式。本文将带你从基础到高级，全面掌握微服务架构。

## 一、微服务架构基础

### 1. 什么是微服务

```
单体应用 vs 微服务

单体应用：
- 一个代码库
- 一个数据库
- 一起部署
- 问题：难以扩展、技术栈受限、部署风险高

微服务：
- 多个小型服务
- 每个服务独立部署
- 每个服务有自己的数据库
- 优势：独立扩展、技术栈灵活、部署风险低
```

### 2. 微服务架构图

```
┌─────────────────────────────────────────────────────────┐
│                        Client                             │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                   API Gateway                            │
└─────┬──────────────────┬──────────────────┬─────────────┘
      │                  │                  │
      ▼                  ▼                  ▼
┌───────────┐    ┌───────────┐    ┌───────────┐
│ User      │    │ Order     │    │ Product   │
│ Service   │    │ Service   │    │ Service   │
└─────┬─────┘    └─────┬─────┘    └─────┬─────┘
      │                  │                  │
      ▼                  ▼                  ▼
┌───────────┐    ┌───────────┐    ┌───────────┐
│ User DB   │    │ Order DB  │    │ Product DB│
└───────────┘    └───────────┘    └───────────┘
```

## 二、服务通信

### 1. REST API

```python
# FastAPI 示例
from fastapi import FastAPI
import httpx

app = FastAPI()

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"id": user_id, "name": "John"}

# 服务间调用
@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    async with httpx.AsyncClient() as client:
        user_response = await client.get(f"http://user-service/users/1")
        user = user_response.json()
    
    return {
        "id": order_id,
        "user": user,
        "product": "Product 1"
    }
```

### 2. gRPC

```protobuf
// user.proto
syntax = "proto3";

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
}

message GetUserRequest {
  int32 user_id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message User {
  int32 id = 1;
  string name = 2;
  string email = 3;
}
```

```python
# 服务端
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        return user_pb2.User(
            id=request.user_id,
            name="John Doe",
            email="john@example.com"
        )
    
    def CreateUser(self, request, context):
        return user_pb2.User(
            id=1,
            name=request.name,
            email=request.email
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()

# 客户端
import grpc
import user_pb2
import user_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        response = stub.GetUser(user_pb2.GetUserRequest(user_id=1))
        print(response)

if __name__ == '__main__':
    run()
```

### 3. 消息队列

```python
# RabbitMQ 示例
import pika

# 生产者
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='orders')

channel.basic_publish(
    exchange='',
    routing_key='orders',
    body='Order created'
)
connection.close()

# 消费者
def callback(ch, method, properties, body):
    print(f"Received: {body}")

channel.basic_consume(
    queue='orders',
    on_message_callback=callback,
    auto_ack=True
)
channel.start_consuming()

# Kafka 示例
from kafka import KafkaProducer, KafkaConsumer

# 生产者
producer = KafkaProducer(bootstrap_servers='localhost:9092')
producer.send('orders', b'Order created')

# 消费者
consumer = KafkaConsumer('orders', bootstrap_servers='localhost:9092')
for message in consumer:
    print(message.value)
```

## 三、服务发现

### 1. Consul

```python
import consul

c = consul.Consul()

# 服务注册
c.agent.service.register(
    'user-service',
    service_id='user-service-1',
    address='127.0.0.1',
    port=8000,
    check=consul.Check.http('http://127.0.0.1:8000/health', interval='10s')
)

# 服务发现
index, services = c.health.service('user-service', passing=True)
for service in services[1]:
    address = service['Service']['Address']
    port = service['Service']['Port']
    print(f"{address}:{port}")
```

### 2. Eureka

```java
// Spring Boot Eureka 客户端
@SpringBootApplication
@EnableDiscoveryClient
public class UserServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}

@RestController
public class UserController {
    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return new User(id, "John");
    }
}

// application.yml
spring:
  application:
    name: user-service
eureka:
  client:
    serviceUrl:
      defaultZone: http://localhost:8761/eureka/
```

### 3. Kubernetes Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: user-service
spec:
  selector:
    app: user-service
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP
```

## 四、API Gateway

### 1. Kong

```yaml
# Kong 配置
services:
  - name: user-service
    url: http://user-service:8000
    routes:
      - name: user-route
        paths:
          - /users
        strip_path: false

  - name: order-service
    url: http://order-service:8001
    routes:
      - name: order-route
        paths:
          - /orders
        strip_path: false
```

### 2. Spring Cloud Gateway

```java
@SpringBootApplication
@EnableDiscoveryClient
public class GatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(GatewayApplication.class, args);
    }
}

@Configuration
public class GatewayConfig {
    @Bean
    public RouteLocator customRouteLocator(RouteLocatorBuilder builder) {
        return builder.routes()
            .route("user-service", r -> r
                .path("/users/**")
                .uri("lb://user-service"))
            .route("order-service", r -> r
                .path("/orders/**")
                .uri("lb://order-service"))
            .build();
    }
}
```

### 3. Nginx

```nginx
http {
    upstream user_service {
        server user-service-1:8000;
        server user-service-2:8000;
    }
    
    upstream order_service {
        server order-service-1:8001;
        server order-service-2:8001;
    }
    
    server {
        listen 80;
        
        location /users/ {
            proxy_pass http://user_service/;
        }
        
        location /orders/ {
            proxy_pass http://order_service/;
        }
    }
}
```

## 五、断路器

### 1. Resilience4j

```java
// Spring Boot + Resilience4j
@RestController
public class OrderController {
    
    @GetMapping("/orders/{id}")
    @CircuitBreaker(name = "userService", fallbackMethod = "fallbackGetUser")
    public Order getOrder(@PathVariable Long id) {
        User user = userServiceClient.getUser(1L);
        return new Order(id, user, "Product 1");
    }
    
    public Order fallbackGetUser(Long id, Exception e) {
        return new Order(id, new User(0L, "Fallback"), "Product 1");
    }
}

// application.yml
resilience4j:
  circuitbreaker:
    configs:
      default:
        register-health-indicator: true
        sliding-window-size: 10
        minimum-number-of-calls: 5
        permitted-number-of-calls-in-half-open-state: 3
        automatic-transition-from-open-to-half-open-enabled: true
        wait-duration-in-open-state: 10s
        failure-rate-threshold: 50
    instances:
      userService:
        base-config: default
```

### 2. Hystrix（已废弃，仅作了解）

```java
@HystrixCommand(fallbackMethod = "fallback")
public User getUser(Long id) {
    return restTemplate.getForObject("http://user-service/users/" + id, User.class);
}

public User fallback(Long id) {
    return new User(0L, "Fallback");
}
```

## 六、分布式追踪

### 1. OpenTelemetry

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter

# 配置
trace.set_tracer_provider(TracerProvider())
jaeger_exporter = JaegerExporter(
    agent_host_name="localhost",
    agent_port=6831,
)
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(jaeger_exporter)
)

# 使用
tracer = trace.get_tracer(__name__)

with tracer.start_as_current_span("create_order"):
    with tracer.start_as_current_span("get_user"):
        user = get_user(1)
    with tracer.start_as_current_span("save_order"):
        save_order(user)
```

### 2. Zipkin

```java
// Spring Boot + Zipkin
@SpringBootApplication
public class OrderServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(OrderServiceApplication.class, args);
    }
}

// application.yml
spring:
  zipkin:
    base-url: http://localhost:9411
  sleuth:
    sampler:
      probability: 1.0
```

## 七、分布式事务

### 1. Saga 模式

```python
class OrderSaga:
    def __init__(self):
        self.steps = []
    
    def execute(self):
        try:
            for step in self.steps:
                step.execute()
        except Exception as e:
            for step in reversed(self.steps):
                step.compensate()
            raise
    
    def add_step(self, step):
        self.steps.append(step)

class CreateOrderStep:
    def execute(self):
        print("Creating order")
    
    def compensate(self):
        print("Rolling back order")

class ReserveInventoryStep:
    def execute(self):
        print("Reserving inventory")
    
    def compensate(self):
        print("Releasing inventory")

# 使用
saga = OrderSaga()
saga.add_step(CreateOrderStep())
saga.add_step(ReserveInventoryStep())
saga.execute()
```

### 2. TCC（Try-Confirm-Cancel）

```python
class TccTransaction:
    def __init__(self):
        self.participants = []
    
    def try_all(self):
        for participant in self.participants:
            participant.try_()
    
    def confirm_all(self):
        for participant in self.participants:
            participant.confirm()
    
    def cancel_all(self):
        for participant in self.participants:
            participant.cancel()

class InventoryParticipant:
    def try_(self):
        print("Reserving inventory")
    
    def confirm(self):
        print("Confirming inventory")
    
    def cancel(self):
        print("Canceling inventory")
```

## 八、容器化和编排

### 1. Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 2. Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: user-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: user-service
  template:
    metadata:
      labels:
        app: user-service
    spec:
      containers:
      - name: user-service
        image: user-service:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
          requests:
            cpu: "0.5"
            memory: "256Mi"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 九、最佳实践

1. 服务拆分合理
2. 独立部署
3. API 设计规范
4. 服务发现
5. API Gateway
6. 断路器
7. 分布式追踪
8. 日志聚合
9. 监控告警
10. 安全

## 十、总结

微服务架构核心要点：
- 服务通信（REST、gRPC、消息队列）
- 服务发现（Consul、Eureka、Kubernetes）
- API Gateway（Kong、Spring Cloud Gateway、Nginx）
- 断路器（Resilience4j）
- 分布式追踪（OpenTelemetry、Zipkin）
- 分布式事务（Saga、TCC）
- 容器化和编排（Docker、Kubernetes）
- 最佳实践

开始构建你的微服务架构吧！
