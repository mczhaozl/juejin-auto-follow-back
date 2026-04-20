# Go & Terraform 基础设施即代码完全指南

## 一、Terraform 基础

```hcl
# main.tf
provider "aws" {
  region = "us-east-1"
}

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "Main VPC"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  
  map_public_ip_on_launch = true
  
  tags = {
    Name = "Public Subnet"
  }
}
```

## 二、模块组织

```hcl
# modules/vpc/main.tf
variable "vpc_cidr" {
  type = string
  default = "10.0.0.0/16"
}

resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
}

output "vpc_id" {
  value = aws_vpc.main.id
}
```

```hcl
# main.tf
module "vpc" {
  source  = "./modules/vpc"
  vpc_cidr = "10.0.0.0/16"
}
```

## 三、EC2 实例

```hcl
resource "aws_instance" "web" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"
  
  subnet_id     = aws_subnet.public.id
  
  tags = {
    Name = "Web Server"
  }
  
  user_data = <<-EOF
              #!/bin/bash
              echo "Hello, World!" > index.html
              nohup python -m SimpleHTTPServer 80 &
              EOF
}
```

## 四、Terraform 状态

```bash
# 初始化
terraform init

# 计划
terraform plan

# 应用
terraform apply

# 销毁
terraform destroy
```

## 五、使用 Go 与 Terraform

```go
package main

import (
  "github.com/hashicorp/terraform-exec/tfexec"
)

func main() {
  // 配置 Terraform
  tf, err := tfexec.NewTerraform("./infra")
  if err != nil {
    panic(err)
  }
  
  // 初始化
  err = tf.Init(context.Background())
  if err != nil {
    panic(err)
  }
  
  // 应用
  err = tf.Apply(context.Background())
  if err != nil {
    panic(err)
  }
}
```

## 六、最佳实践

- 使用模块复用代码
- 保持状态文件安全
- 使用变量和输出
- 合理的 tfstate 管理
- 版本控制配置文件
- 测试基础设施代码
- 使用工作空间管理环境
