# Go 泛型完全指南

## 一、泛型函数

```go
package main

import "fmt"

// 泛型函数
func Map[T any, U any](slice []T, f func(T) U) []U {
    result := make([]U, len(slice))
    for i, v := range slice {
        result[i] = f(v)
    }
    return result
}

func main() {
    ints := []int{1, 2, 3}
    strings := Map(ints, func(i int) string { return fmt.Sprintf("%d", i) })
    fmt.Println(strings)
}
```

## 二、类型约束

```go
import "golang.org/x/exp/constraints"

// 约束：可比较类型
func Contains[T comparable](slice []T, item T) bool {
    for _, v := range slice {
        if v == item {
            return true
        }
    }
    return false
}

// 约束：可排序类型
func Max[T constraints.Ordered](slice []T) T {
    max := slice[0]
    for _, v := range slice[1:] {
        if v > max {
            max = v
        }
    }
    return max
}
```

## 三、泛型结构体

```go
// 泛型栈
type Stack[T any] struct {
    items []T
}

func (s *Stack[T]) Push(item T) {
    s.items = append(s.items, item)
}

func (s *Stack[T]) Pop() (T, bool) {
    if len(s.items) == 0 {
        var zero T
        return zero, false
    }
    item := s.items[len(s.items)-1]
    s.items = s.items[:len(s.items)-1]
    return item, true
}
```

## 四、接口类型约束

```go
// 自定义约束
type Stringer interface {
    String() string
}

func PrintString[T Stringer](items []T) {
    for _, item := range items {
        fmt.Println(item.String())
    }
}
```

## 五、最佳实践

- 合理使用泛型，避免过度设计
- 使用 constraints 包的预定义约束
- 考虑性能影响（类型特化）
- 文档化泛型类型约束
- 测试不同类型的边界情况
- 与现有非泛型代码集成
