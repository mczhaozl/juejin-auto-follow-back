# Go 错误处理完全指南：最佳实践与高级技巧

Go 的错误处理是其设计哲学的重要组成部分。本文将带你全面掌握 Go 的错误处理机制。

## 一、Go 错误基础

### 1. error 接口

```go
type error interface {
    Error() string
}
```

### 2. 简单错误

```go
package main

import (
    "errors"
    "fmt"
)

func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, errors.New("division by zero")
    }
    return a / b, nil
}

func main() {
    result, err := divide(10, 0)
    if err != nil {
        fmt.Println("Error:", err)
        return
    }
    fmt.Println("Result:", result)
}
```

### 3. fmt.Errorf

```go
func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, fmt.Errorf("division by zero: a=%d, b=%d", a, b)
    }
    return a / b, nil
}
```

## 二、自定义错误

### 1. 简单自定义错误

```go
type DivisionError struct {
    a, b int
}

func (e *DivisionError) Error() string {
    return fmt.Sprintf("division by zero: %d / %d", e.a, e.b)
}

func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, &DivisionError{a, b}
    }
    return a / b, nil
}
```

### 2. 类型断言判断错误

```go
result, err := divide(10, 0)
if err != nil {
    if divErr, ok := err.(*DivisionError); ok {
        fmt.Printf("Division error: %d / %d\n", divErr.a, divErr.b)
    } else {
        fmt.Println("Error:", err)
    }
    return
}
```

### 3. errors.Is 和 errors.As

```go
import "errors"

var ErrDivisionByZero = errors.New("division by zero")

func divide(a, b int) (int, error) {
    if b == 0 {
        return 0, ErrDivisionByZero
    }
    return a / b, nil
}

func main() {
    result, err := divide(10, 0)
    if err != nil {
        if errors.Is(err, ErrDivisionByZero) {
            fmt.Println("Cannot divide by zero")
        } else {
            fmt.Println("Error:", err)
        }
        return
    }
    
    var divErr *DivisionError
    if errors.As(err, &divErr) {
        fmt.Printf("Division error: %d / %d\n", divErr.a, divErr.b)
    }
}
```

## 三、错误包装

### 1. %w 格式化动词

```go
import "errors"

func openFile(filename string) error {
    return errors.New("file not found")
}

func readConfig() error {
    err := openFile("config.json")
    if err != nil {
        return fmt.Errorf("read config: %w", err)
    }
    return nil
}

func main() {
    err := readConfig()
    if err != nil {
        fmt.Println(err)
        // read config: file not found
        
        fmt.Println(errors.Unwrap(err))
        // file not found
    }
}
```

### 2. 多层包装

```go
func validateConfig() error {
    err := readConfig()
    if err != nil {
        return fmt.Errorf("validate config: %w", err)
    }
    return nil
}

func main() {
    err := validateConfig()
    if err != nil {
        fmt.Println(err)
        // validate config: read config: file not found
        
        if errors.Is(err, ErrFileNotFound) {
            fmt.Println("Found the root cause!")
        }
    }
}
```

## 四、defer、panic 和 recover

### 1. defer

```go
func readFile(filename string) (string, error) {
    file, err := os.Open(filename)
    if err != nil {
        return "", err
    }
    defer file.Close()
    
    content, err := io.ReadAll(file)
    if err != nil {
        return "", err
    }
    
    return string(content), nil
}
```

### 2. panic

```go
func mustParseInt(s string) int {
    i, err := strconv.Atoi(s)
    if err != nil {
        panic(fmt.Sprintf("cannot parse %q as int", s))
    }
    return i
}
```

### 3. recover

```go
func safeDivision(a, b int) (result int, err error) {
    defer func() {
        if r := recover(); r != nil {
            err = fmt.Errorf("panic: %v", r)
        }
    }()
    
    if b == 0 {
        panic("division by zero")
    }
    return a / b, nil
}
```

## 五、错误处理模式

### 1. 哨兵错误

```go
var (
    ErrNotFound   = errors.New("not found")
    ErrInvalidArg = errors.New("invalid argument")
)

func findUser(id int) (*User, error) {
    if id <= 0 {
        return nil, ErrInvalidArg
    }
    user, ok := users[id]
    if !ok {
        return nil, ErrNotFound
    }
    return user, nil
}
```

### 2. 错误组

```go
import "golang.org/x/sync/errgroup"

func fetchAll() error {
    var g errgroup.Group
    
    g.Go(func() error {
        return fetchUsers()
    })
    
    g.Go(func() error {
        return fetchPosts()
    })
    
    return g.Wait()
}
```

### 3. 错误链

```go
type ErrorChain struct {
    Op  string
    Err error
}

func (e *ErrorChain) Error() string {
    return fmt.Sprintf("%s: %v", e.Op, e.Err)
}

func (e *ErrorChain) Unwrap() error {
    return e.Err
}

func E(op string, err error) error {
    return &ErrorChain{Op: op, Err: err}
}

func readConfig() error {
    err := openFile("config.json")
    if err != nil {
        return E("readConfig", err)
    }
    return nil
}
```

## 六、最佳实践

### 1. 不要忽略错误

```go
// ❌ 不好
file, _ := os.Open("file.txt")

// ✅ 好
file, err := os.Open("file.txt")
if err != nil {
    return err
}
defer file.Close()
```

### 2. 提供有意义的错误信息

```go
// ❌ 不好
return errors.New("error")

// ✅ 好
return fmt.Errorf("open file %q: %w", filename, err)
```

### 3. 只在必要时使用 panic

```go
// ✅ 适合用 panic 的情况
func MustCompile(re string) *regexp.Regexp {
    r, err := regexp.Compile(re)
    if err != nil {
        panic(err)
    }
    return r
}
```

## 七、错误处理库

### 1. pkg/errors

```go
import "github.com/pkg/errors"

func readConfig() error {
    err := openFile("config.json")
    if err != nil {
        return errors.Wrap(err, "read config")
    }
    return nil
}

func main() {
    err := readConfig()
    if err != nil {
        fmt.Printf("%+v\n", err)
    }
}
```

## 八、总结

Go 的错误处理哲学：
- 错误是值，不是异常
- 显式处理错误，不要忽略
- 包装错误，添加上下文
- 使用 errors.Is 和 errors.As
- 只在极端情况下使用 panic

掌握这些技巧，写出更健壮的 Go 代码！
