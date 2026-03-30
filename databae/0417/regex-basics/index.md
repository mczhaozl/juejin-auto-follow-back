# 正则表达式完全指南：模式匹配实战

> 深入讲解正则表达式，包括字符类、量词、锚点、分组断言，以及 JavaScript、Python 中的实际应用和调试技巧。

## 一、正则基础

### 1.1 什么是正则

正则表达式是强大的模式匹配工具：

```
┌─────────────────────────────────────────────────────────────┐
│                      正则表达式                              │
│                                                              │
│  文本: "我的邮箱是 test@example.com，请联系"              │
│                                                              │
│  正则: [\w.-]+@[\w.-]+\.\w+                                │
│                                                              │
│  匹配: test@example.com                                    │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 元字符

| 元字符 | 说明 |
|--------|------|
| . | 任意字符 |
| \d | 数字 |
| \w | 字母数字下划线 |
| \s | 空白字符 |
| \D \W \S | 取反 |

## 二、字符类

### 2.1 基本字符集

```regex
[abc]       # a、b、c 任意一个
[^abc]      # 除了 a、b、c
[a-z]       # a 到 z
[A-Z]       # A 到 Z
[0-9]       # 0 到 9
```

### 2.2 预定义字符类

```regex
\d          # 数字 [0-9]
\D          # 非数字 [^0-9]
\w          # 单词字符 [a-zA-Z0-9_]
\W          # 非单词字符
\s          # 空白字符 [ \t\n\r\f]
\S          # 非空白字符
.           # 任意字符（换行符除外）
```

### 2.3 示例

```regex
手机号:    1[3-9]\d{9}
身份证:    \d{17}[\dXx]
邮箱:      [\w.-]+@[\w.-]+\.\w+
URL:       https?://[\w.-]+(?:/[\w.-]*)*/?
```

## 三、量词

### 3.1 数量限定

```regex
*           # 0 次或多次
+           # 1 次或多次
?           # 0 次或 1 次
{n}         # 恰好 n 次
{n,}        # 至少 n 次
{n,m}       # n 到 m 次
```

### 3.2 贪婪与非贪婪

```javascript
// 贪婪匹配（默认）
"aaaa".match(/a+/)   // ["aaaa"]

// 非贪婪匹配
"aaaa".match(/a+?/)  // ["a"]
"aaaa".match(/a{2,4}?/)  // ["aa"]
```

### 3.3 示例

```regex
HTML标签:   <[^>]+>
数字:       \d+
小数:       \d+\.\d+
IP地址:     \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}
```

## 四、锚点

### 4.1 边界匹配

```regex
^           # 字符串开始
$           # 字符串结束
\b          # 单词边界
\B          # 非单词边界
```

### 4.2 示例

```regex
行首:       ^\s*#        # 注释行
行尾:      ;\s*$        # 分号结尾
单词:      \bword\b     # 完整单词
整数:      \b\d+\b
```

## 五、分组

### 5.1 捕获组

```regex
(abc)           # 捕获组 1
(\d)(\d)        # 捕获组 1、2
(?:abc)         # 非捕获组
```

### 5.2 命名组

```javascript
// JavaScript
const regex = /(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/
const result = regex.exec('2024-01-15')
console.log(result.groups.year)  // 2024

# Python
import re
pattern = r'(?P<year>\d{4})-(?P<month>\d{2})'
result = re.match(pattern, '2024-01')
print(result.group('year'))  # 2024
```

### 5.3 反向引用

```regex
重复单词:   \b(\w+)\s+\1\b      # 匹配 "the the"
日期:      (\d{4})-(\d{2})-\2 # 2024-01-01
```

## 六、断言

### 6.1 先行断言

```regex
(?=...)     # 正向先行断言
(?!...)     # 负向先行断言
```

### 6.2 后行断言

```regex
(?<=...)    # 正向后行断言
(?<!...)    # 负向后行断言
```

### 6.3 示例

```regex
密码强度:   (?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}
价格:      \$\d+(?:\.\d{2})?
非数字:    \d+(?!\d)
HTML标签:  (?<=<)\w+(?=>)
```

## 七、实战案例

### 7.1 JavaScript

```javascript
// 验证邮箱
const isEmail = (email) => {
  return /^[\w.-]+@[\w.-]+\.\w+$/.test(email)
}

// 提取 URL
const urls = text.match(/https?:\/\/[\w.-]+(?:/[\w.-]*)*/g)

// 替换
text.replace(/\b(\w+)\b/g, '<span>$1</span>')

// 分割
text.split(/[,\s]+/)
```

### 7.2 Python

```python
import re

# 验证手机号
def is_phone(phone):
    return bool(re.match(r'1[3-9]\d{9}$', phone))

# 提取数字
numbers = re.findall(r'\d+', text)

# 替换
text = re.sub(r'\bword\b', 'WORD', text)

# 分割
parts = re.split(r'[,;]\s*', text)
```

### 7.3 表单验证

```javascript
const validators = {
  username: /^[a-zA-Z]\w{2,15}$/,
  password: /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/,
  email: /^[\w.-]+@[\w.-]+\.\w+$/,
  phone: /1[3-9]\d{9}$/,
  url: /^https?:\/\/[\w.-]+$/,
  date: /^\d{4}-\d{2}-\d{2}$/
}
```

## 八、调试技巧

### 8.1 在线工具

- Regex101
- Regexr
- RegExpal

### 8.2 常见问题

```regex
# 问题：匹配所有
.*          # 贪婪，可能匹配过多

# 解决：非贪婪
.*?         # 最小匹配

# 问题：特殊字符
[.*+?{}()|[\]\\]  # 需要转义

# 解决：使用 \Q \E（Java）
\Q.\E       # 匹配字面量 .
```

## 九、总结

正则表达式核心要点：

1. **字符类**：[abc]、\d、\w
2. **量词**：* + ？ {n}
3. **锚点**：^ $ \b
4. **分组**：( )、(?<name>)
5. **断言**：(?=) (?<=)
6. **转义**：\

掌握这些，文本处理 so easy！

---

**推荐阅读**：
- [Regex101](https://regex101.com/)
- [正则表达式30分钟入门](https://deerchao.cn/tutorials/regex/regex.htm)

**如果对你有帮助，欢迎点赞收藏！**
