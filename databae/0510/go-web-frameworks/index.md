# Go Web 框架完全指南

## 一、Gin

```go
package main

import "github.com/gin-gonic/gin"

func main() {
    r := gin.Default()
    
    r.GET("/ping", func(c *gin.Context) {
        c.JSON(200, gin.H{
            "message": "pong",
        })
    })
    
    r.Run(":8080")
}
```

## 二、Echo

```go
package main

import "github.com/labstack/echo/v4"

func main() {
    e := echo.New()
    
    e.GET("/ping", func(c echo.Context) error {
        return c.JSON(200, map[string]string{
            "message": "pong",
        })
    })
    
    e.Start(":8080")
}
```

## 三、路由参数

```go
// Gin
r.GET("/users/:id", func(c *gin.Context) {
    id := c.Param("id")
    c.JSON(200, gin.H{"id": id})
})

// Echo
e.GET("/users/:id", func(c echo.Context) error {
    id := c.Param("id")
    return c.JSON(200, map[string]string{"id": id})
})
```

## 四、中间件

```go
// Gin
func Logger() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 日志
        c.Next()
    }
}

r.Use(Logger())
```

## 五、最佳实践

- 使用 gin 或 echo 等成熟框架
- 合理组织路由
- 使用中间件处理跨切面问题
- 统一错误处理
- 使用 validator 验证请求
