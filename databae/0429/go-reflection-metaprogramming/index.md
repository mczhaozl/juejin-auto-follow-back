# Go 反射与元编程完全指南：从基础到实战

## 一、反射基础

### 1.1 什么是反射
反射是在运行时检查和操作类型、变量和函数的能力。

### 1.2 reflect 包
Go 使用 `reflect` 包来提供反射功能。

---

## 二、Type 和 Value

```go
package main

import (
	"fmt"
	"reflect"
)

func main() {
	x := 3.14
	t := reflect.TypeOf(x)
	v := reflect.ValueOf(x)
	
	fmt.Printf("type: %s\n", t.Name())
	fmt.Printf("value: %v\n", v)
	fmt.Printf("type kind: %v\n", t.Kind())
}
```

---

## 三、Type 的种类（Kind）

```go
package main

import (
	"fmt"
	"reflect"
)

func inspectType(x interface{}) {
	t := reflect.TypeOf(x)
	fmt.Printf("Type: %v, Kind: %v\n", t, t.Kind())
}

func main() {
	type MyInt int
	var x MyInt = 42
	
	inspectType(x)       // Type: main.MyInt, Kind: int
	inspectType(&x)      // Type: *main.MyInt, Kind: ptr
	inspectType([]int{}) // Type: []int, Kind: slice
}
```

---

## 四、获取字段信息

```go
package main

import (
	"fmt"
	"reflect"
)

type Person struct {
	Name string `json:"name"`
	Age  int    `json:"age"`
}

func main() {
	p := Person{"Alice", 30}
	t := reflect.TypeOf(p)
	
	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		fmt.Printf("Field %d: %s (%s), tag: %v\n", 
			i, field.Name, field.Type, field.Tag.Get("json"))
	}
}
```

---

## 五、设置值

```go
package main

import (
	"fmt"
	"reflect"
)

func main() {
	x := 42
	fmt.Println("before:", x)
	
	v := reflect.ValueOf(&x).Elem()
	v.SetInt(100)
	fmt.Println("after:", x)
}
```

---

## 六、调用方法

```go
package main

import (
	"fmt"
	"reflect"
)

type Calculator struct{}

func (c Calculator) Add(a, b int) int {
	return a + b
}

func (c Calculator) Multiply(a, b int) int {
	return a * b
}

func main() {
	c := Calculator{}
	t := reflect.TypeOf(c)
	v := reflect.ValueOf(c)
	
	for i := 0; i < t.NumMethod(); i++ {
		method := t.Method(i)
		fmt.Printf("Method %d: %s\n", i, method.Name)
	}
	
	// 调用 Add 方法
	addMethod := v.MethodByName("Add")
	args := []reflect.Value{reflect.ValueOf(10), reflect.ValueOf(20)}
	result := addMethod.Call(args)
	fmt.Println("10 + 20 =", result[0].Int())
}
```

---

## 七、动态创建对象

```go
package main

import (
	"fmt"
	"reflect"
)

type Config struct {
	Host    string
	Port    int
	Debug   bool
}

func createInstance(t reflect.Type) interface{} {
	return reflect.New(t).Elem().Interface()
}

func main() {
	configType := reflect.TypeOf(Config{})
	config := createInstance(configType).(Config)
	
	config.Host = "localhost"
	config.Port = 8080
	config.Debug = true
	
	fmt.Printf("Config: %+v\n", config)
}
```

---

## 八、解析标签（Tag）

```go
package main

import (
	"fmt"
	"reflect"
	"strconv"
)

type Person struct {
	Name string `db:"name" maxLen:"50"`
	Age  int    `db:"age" min:"0" max:"150"`
}

func validateStruct(s interface{}) error {
	v := reflect.ValueOf(s)
	t := v.Type()
	
	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		fieldValue := v.Field(i)
		
		switch field.Type.Kind() {
		case reflect.String:
			if maxLen, ok := field.Tag.Lookup("maxLen"); ok {
				max, _ := strconv.Atoi(maxLen)
				if len(fieldValue.String()) > max {
					return fmt.Errorf("%s exceeds max length %d", field.Name, max)
				}
			}
		case reflect.Int:
			if min, ok := field.Tag.Lookup("min"); ok {
				m, _ := strconv.Atoi(min)
				if fieldValue.Int() < int64(m) {
					return fmt.Errorf("%s below min %d", field.Name, m)
				}
			}
			if max, ok := field.Tag.Lookup("max"); ok {
				m, _ := strconv.Atoi(max)
				if fieldValue.Int() > int64(m) {
					return fmt.Errorf("%s above max %d", field.Name, m)
				}
			}
		}
	}
	return nil
}

func main() {
	p := Person{Name: "Alice", Age: 25}
	err := validateStruct(p)
	if err != nil {
		fmt.Println("Validation error:", err)
	} else {
		fmt.Println("Validation passed!")
	}
}
```

---

## 九、JSON 序列化与反序列化模拟

```go
package main

import (
	"fmt"
	"reflect"
	"strconv"
	"strings"
)

func toJSON(obj interface{}) string {
	v := reflect.ValueOf(obj)
	t := v.Type()
	
	var fields []string
	
	for i := 0; i < t.NumField(); i++ {
		field := t.Field(i)
		value := v.Field(i)
		
		var valueStr string
		switch field.Type.Kind() {
		case reflect.String:
			valueStr = fmt.Sprintf(`"%s"`, value.String())
		case reflect.Int:
			valueStr = fmt.Sprintf("%d", value.Int())
		case reflect.Bool:
			valueStr = fmt.Sprintf("%t", value.Bool())
		}
		
		fields = append(fields, fmt.Sprintf(`"%s":%s`, field.Name, valueStr))
	}
	
	return fmt.Sprintf("{%s}", strings.Join(fields, ","))
}

func main() {
	type Person struct {
		Name string
		Age  int
		Alive bool
	}
	
	p := Person{"Bob", 35, true}
	fmt.Println(toJSON(p))
}
```

---

## 十、依赖注入容器

```go
package main

import (
	"fmt"
	"reflect"
)

type Container struct {
	services map[reflect.Type]reflect.Value
}

func NewContainer() *Container {
	return &Container{services: make(map[reflect.Type]reflect.Value)}
}

func (c *Container) Register(service interface{}) {
	t := reflect.TypeOf(service)
	c.services[t] = reflect.ValueOf(service)
}

func (c *Container) Resolve(target interface{}) {
	v := reflect.ValueOf(target).Elem()
	t := v.Type()
	
	for i := 0; i < t.NumField(); i++ {
		fieldType := t.Field(i).Type
		if service, ok := c.services[fieldType]; ok {
			v.Field(i).Set(service)
		}
	}
}

type Logger struct{}

func (l Logger) Log(msg string) {
	fmt.Println(msg)
}

type UserService struct {
	Logger Logger
}

func (us UserService) CreateUser(name string) {
	us.Logger.Log("Creating user: " + name)
}

func main() {
	container := NewContainer()
	logger := Logger{}
	container.Register(logger)
	
	var us UserService
	container.Resolve(&us)
	us.CreateUser("Alice")
}
```

---

## 十一、最佳实践

1. 反射性能较差，尽量避免在热路径使用
2. 优先使用接口而非反射
3. 反射代码难以理解，充分注释
4. 处理类型错误时进行适当检查
5. 使用结构体标签简化反射逻辑

---

## 十二、总结

Go 的反射功能强大，能实现动态编程，但需注意性能和可维护性的平衡。
