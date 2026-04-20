# Go Cobra CLI 完全指南

## 一、基础命令

```go
// cmd/root.go
var rootCmd = &cobra.Command{
    Use:   "myapp",
    Short: "A brief description of your application",
    Long: `A longer description`,
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("Hello from root")
    },
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}
```

## 二、子命令

```go
// cmd/version.go
var versionCmd = &cobra.Command{
    Use:   "version",
    Short: "Print the version",
    Run: func(cmd *cobra.Command, args []string) {
        fmt.Println("v1.0.0")
    },
}

func init() {
    rootCmd.AddCommand(versionCmd)
}
```

## 三、Flags

```go
var (
    name string
    age  int
)

func init() {
    helloCmd.Flags().StringVarP(&name, "name", "n", "", "Your name")
    helloCmd.Flags().IntVarP(&age, "age", "a", 0, "Your age")
}
```

## 四、Viper 配置

```go
// 使用 Viper 读取配置
import "github.com/spf13/viper"

viper.SetConfigName("config")
viper.ReadInConfig()
```

## 五、最佳实践

- 组织代码结构（cmd/ 目录）
- 使用 viper 管理配置
- 提供完善的帮助信息
- 支持 shell 补全
- 友好的错误信息
