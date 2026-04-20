# Go CGo 完全指南

## 一、基础 CGo 调用

```go
/*
#cgo LDFLAGS: -lm
#include <stdio.h>
void hello() {
    printf("Hello from C!\n");
}
*/
import "C"
import "fmt"

func main() {
    C.hello()
    
    // 调用 C 函数
    var x C.int = 42
    fmt.Println("C int:", int(x))
}
```

## 二、Go 调用 C 函数

```go
/*
#include <stdlib.h>
#include <string.h>
*/
import "C"
import "unsafe"

func GoStringToCString(s string) *C.char {
    return C.CString(s)
}

func FreeCString(c *C.char) {
    C.free(unsafe.Pointer(c))
}
```

## 三、C 调用 Go 函数

```go
/*
extern void go_callback();

static void call_go() {
    go_callback();
}
*/
import "C"

//export go_callback
func go_callback() {
    println("Go function called from C!")
}

func main() {
    C.call_go()
}
```

## 四、类型转换

```go
import (
    "C"
    "unsafe"
)

func StringToC(s string) *C.char {
    return C.CString(s)
}

func CToString(cs *C.char) string {
    return C.GoString(cs)
}

func GoIntToC(i int) C.int {
    return C.int(i)
}
```

## 五、最佳实践

- 避免过度使用 CGo（破坏跨编译）
- 正确管理内存（free C strings）
- 使用 cgo 标记（#cgo LDFLAGS）
- 线程安全注意事项
- 性能影响评估
- 考虑纯 Go 替代方案
