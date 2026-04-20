# Go gRPC 完全指南

## 一、Protocol Buffers

```protobuf
syntax = "proto3";
package user;

option go_package = "./proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);
  rpc StreamUsers(StreamUsersRequest) returns (stream StreamUsersResponse);
}

message GetUserRequest {
  string id = 1;
}

message GetUserResponse {
  User user = 1;
}

message User {
  string id = 1;
  string name = 2;
  int32 age = 3;
}
```

## 二、编译生成代码

```bash
protoc --go_out=. --go-grpc_out=. proto/user.proto
```

## 三、实现服务

```go
package main

import (
  "context"
  "google.golang.org/grpc"
  pb "path/to/proto"
)

type server struct {
  pb.UnimplementedUserServiceServer
}

func (s *server) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
  user := &pb.User{
    Id: req.Id,
    Name: "Alice",
    Age: 30,
  }
  return &pb.GetUserResponse{User: user}, nil
}

func main() {
  lis, err := net.Listen("tcp", ":50051")
  if err != nil { panic(err) }
  
  s := grpc.NewServer()
  pb.RegisterUserServiceServer(s, &server{})
  
  s.Serve(lis)
}
```

## 四、客户端调用

```go
package main

import (
  "context"
  "google.golang.org/grpc"
  pb "path/to/proto"
)

func main() {
  conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
  if err != nil { panic(err) }
  defer conn.Close()
  
  client := pb.NewUserServiceClient(conn)
  
  user, err := client.GetUser(context.Background(), &pb.GetUserRequest{Id: "1"})
  if err != nil { panic(err) }
}
```

## 五、流式调用

```go
func (s *server) StreamUsers(req *pb.StreamUsersRequest, stream pb.UserService_StreamUsersServer) error {
  for i := 0; i < 5; i++ {
    user := &pb.User{
      Id: string(i),
      Name: "User" + string(i),
    }
    stream.Send(&pb.StreamUsersResponse{User: user})
  }
  return nil
}
```

## 六、中间件和拦截器

```go
loggingInterceptor := func(
  ctx context.Context,
  req interface{},
  info *grpc.UnaryServerInfo,
  handler grpc.UnaryHandler,
) (interface{}, error) {
  log.Printf("Calling %s", info.FullMethod)
  return handler(ctx, req)
}

s := grpc.NewServer(grpc.UnaryInterceptor(loggingInterceptor))
```

## 七、最佳实践

- 合理设计 protobuf 消息
- 使用拦截器处理通用逻辑
- 实现连接池
- 添加错误处理
- 考虑超时和重试
- 使用 TLS 加密连接
