# Go 语言微服务开发完全指南

## 一、微服务架构基础

### 1.1 服务拆分原则

- 单一职责
- 独立部署
- 数据隔离

## 二、Gin HTTP 服务

```go
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    
    r.GET("/api/users", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "pong"})
    })
    
    r.Run(":8080")
}
```

## 三、gRPC 服务

```protobuf
// user.proto
syntax = "proto3";
service UserService {
    rpc GetUser(GetUserRequest) returns (GetUserResponse);
}
message GetUserRequest { string id = 1; }
message GetUserResponse { User user = 1; }
message User { string id = 1; string name = 2; }
```

```go
// server.go
package main

import (
    "context"
    "google.golang.org/grpc"
)

type server struct {
    UnimplementedUserServiceServer
}

func (s *server) GetUser(ctx context.Context, req *GetUserRequest) (*GetUserResponse, error) {
    return &GetUserResponse{User: &User{Id: req.Id, Name: "Alice"}}, nil
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")
    s := grpc.NewServer()
    RegisterUserServiceServer(s, &server{})
    s.Serve(lis)
}
```

## 四、服务发现

```go
// 使用 Consul
package main

import (
    "github.com/hashicorp/consul/api"
)

func registerService() {
    client, _ := api.NewClient(api.DefaultConfig())
    reg := &api.AgentServiceRegistration{
        Name: "user-service",
        ID: "user-service-1",
        Port: 8080,
    }
    client.Agent().ServiceRegister(reg)
}
```

## 五、分布式追踪

```go
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/trace"
)

func handleRequest(ctx context.Context) {
    tracer := otel.Tracer("user-service")
    ctx, span := tracer.Start(ctx, "handleRequest")
    defer span.End()
}
```

## 六、配置管理

```go
// 使用 Viper
package main

import "github.com/spf13/viper"

func initConfig() {
    viper.SetConfigFile("config.yaml")
    viper.ReadInConfig()
    viper.GetString("database.url")
}
```

## 七、最佳实践

- 使用标准库 HTTP 或 Gin
- gRPC 用于高性能内部通信
- 实现熔断和限流
- 完善的日志和监控
- 使用 Docker 和 Kubernetes 部署
