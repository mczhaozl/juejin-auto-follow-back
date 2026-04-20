# Go unsafe 包完全指南

## 一、unsafe.Pointer

```go
package main

import (
  "unsafe"
)

func main() {
  i := 42
  p := &i
  
  // 转换指针
  fp := (*float64)(unsafe.Pointer(p))
  *fp = 3.14
  
  println(i) // 1078523392
}
```

## 二、访问私有字段

```go
import (
  "reflect"
  "unsafe"
)

func main() {
  type T struct {
    x int
  }
  
  t := &T{x: 42}
  // 获取字段地址
  rf := reflect.ValueOf(t).Elem().Field(0)
  ptr := unsafe.Pointer(rf.UnsafeAddr())
  // 修改
  *(*int)(ptr) = 100
  
  println(t.x) // 100
}
```

## 三、字符串与切片转换

```go
func BytesToString(b []byte) string {
  return *(*string)(unsafe.Pointer(&b))
}

func StringToBytes(s string) []byte {
  return *(*[]byte)(unsafe.Pointer(&struct {
    string
    int
  }{s, len(s)}))
}
```

## 最佳实践
- 尽量避免使用 unsafe
- 注意内存布局
- 编译器版本兼容性
- 充分测试
- 性能关键路径才考虑
