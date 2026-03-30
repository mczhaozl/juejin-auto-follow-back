# 正则表达式入门：Python/JavaScript 实战指南

> 全面介绍正则表达式核心语法，包括字符匹配、分组、断言，以及 Python 和 JavaScript 中的实际应用案例。

## 一、基础语法

### 1.1 元字符

| 字符 | 说明 |
|------|------|
| `.` | 任意字符 |
| `\d` | 数字 |
| `\w` | 字母数字下划线 |
| `\s` | 空白字符 |
| `\b` | 单词边界 |

### 1.2 量词

| 量词 | 说明 |
|------|------|
| `*` | 0 或多次 |
| `+` | 1 或多次 |
| `?` | 0 或 1 次 |
| `{n}` | n 次 |
| `{n,m}` | n 到 m 次 |

## 二、字符类

### 2.1 范围

```regex
[abc]       # a、b、c 任意一个
[^abc]      # 非 a、b、c
[a-z]       # a 到 z
[0-9]       # 0 到 9
```

### 2.2 预定义

```regex
\d          # [0-9]
\D          # [^0-9]
\w          # [a-zA-Z0-9_]
\W          # [^a-zA-Z0-9_]
\s          # [\t\n\r\f]
\S          # [^\t\n\r\f]
```

## 三、锚点

### 3.1 边界

```regex
^           # 字符串开始
$           # 字符串结束
\b          # 单词边界
\B          # 非单词边界
```

### 3.2 示例

```regex
^Hello$     # 精确匹配 Hello
^\d{3}$     # 精确 3 位数字
\bis\b      # 独立的 is
```

## 四、分组

### 4.1 捕获组

```regex
(\d{4})-(\d{2})    # 捕获年份和月份
```

### 4.2 非捕获组

```regex
(?:\d{4})           # 不捕获
(?<year>\d{4})     # 命名捕获
```

### 4.3 反向引用

```regex
(\w)\1             # 匹配重复字符，如 aa、bb
```

## 五、断言

### 5.1 先行断言

```regex
\d+(?=px)          # 数字后跟 px（不包含 px）
```

### 5.2 负向先行

```regex
\d+(?!px)          # 数字后不跟 px
```

### 5.3 后行断言

```regex
(?<=\$)\d+         # $ 后面的数字（不包含 $）
```

## 六、Python 应用

### 6.1 re 模块

```python
import re

# 匹配
pattern = r'\d+'
text = 'abc123def456'
result = re.findall(pattern, text)
print(result)  # ['123', '456']

# 替换
text = 'hello world'
result = re.sub(r'world', 'python', text)
print(result)  # hello python
```

### 6.2 捕获组

```python
pattern = r'(\d{4})-(\d{2})-(\d{2})'
text = '2024-01-15'

match = re.search(pattern, text)
if match:
    print(match.group(0))  # 2024-01-15
    print(match.group(1))  # 2024
    print(match.group(2))  # 01
    print(match.group(3))  # 15
    
    # 命名分组
pattern = r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})'
match = re.search(pattern, text)
print(match.group('year'))  # 2024
```

### 6.3 编译

```python
pattern = re.compile(r'\d+')
result = pattern.findall('abc123def456')
```

## 七、JavaScript 应用

### 7.1 基本使用

```javascript
const str = 'abc123def456';

// match
console.log(str.match(/\d+/));  // ['123', ...]

// replace
console.log(str.replace(/\d+/g, 'X'));  // abcXdefX

// test
console.log(/\d+/.test('abc123'));  // true

// exec
console.log(/\d+/.exec('abc123'));  // ['123']
```

### 7.2 捕获组

```javascript
const str = '2024-01-15';
const result = str.match(/(\d{4})-(\d{2})-(\d{2})/);

console.log(result[0]);  // 2024-01-15
console.log(result[1]);  // 2024
console.log(result[2]);  // 01

// 命名分组
const named = str.match(/(?<year>\d{4})-(?<month>\d{2})-(?<day>\d{2})/);
console.log(named.groups.year);  // 2024
```

### 7.3 replace 回调

```javascript
const str = 'hello world';
const result = str.replace(/\b\w/g, (char) => {
  return char.toUpperCase();
});
console.log(result);  // Hello World
```

## 八、实战案例

### 8.1 邮箱验证

```python
# Python
import re

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

print(validate_email('test@example.com'))  # True
```

```javascript
// JavaScript
const validateEmail = (email) => {
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return pattern.test(email);
};

console.log(validateEmail('test@example.com'));  // true
```

### 8.2 手机号验证

```python
# 中国手机号
pattern = r'^1[3-9]\d{9}$'
```

### 8.3 提取 URL

```python
text = '访问 https://example.com 或 http://test.org'
urls = re.findall(r'https?://[^\s]+', text)
print(urls)  # ['https://example.com', 'http://test.org']
```

## 九、总结

正则表达式核心要点：

1. **元字符**：.、\d、\w、\s
2. **量词**：*、+、?、{n,m}
3. **字符类**：[]、^
4. **锚点**：^、$、\b
5. **分组**：()、?:
6. **断言**：?=、?!
7. **Python**：re 模块
8. **JavaScript**：RegExp 对象

掌握这些，正则不再难！

---

**推荐阅读**：
- [正则表达式 MDN](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions)
- [Regex101](https://regex101.com/)

**如果对你有帮助，欢迎点赞收藏！**
