# CSS 属性选择器完全指南：从基础到高级技巧

CSS 属性选择器是一个强大但经常被忽视的工具。本文将带你全面掌握属性选择器的各种用法。

## 一、基础属性选择器

### 1. 存在性选择器

```css
/* 选择有 href 属性的 a 标签 */
a[href] {
    color: blue;
}

/* 选择有 data-tooltip 属性的元素 */
[data-tooltip] {
    position: relative;
}
```

### 2. 精确匹配选择器

```css
/* 选择 type="text" 的 input */
input[type="text"] {
    border: 1px solid #ccc;
}

/* 选择 class="button" 的元素 */
[class="button"] {
    padding: 10px 20px;
}
```

### 3. 包含选择器

```css
/* 选择 href 包含 "example.com" 的链接 */
a[href*="example.com"] {
    color: green;
}

/* 选择 class 包含 "btn-" 的元素 */
[class*="btn-"] {
    border-radius: 4px;
}
```

## 二、高级属性选择器

### 1. 开头匹配选择器

```css
/* 选择 href 以 "https://" 开头的链接 */
a[href^="https://"]::before {
    content: "🔒";
}

/* 选择 class 以 "icon-" 开头的元素 */
[class^="icon-"] {
    display: inline-block;
}
```

### 2. 结尾匹配选择器

```css
/* 选择 href 以 ".pdf" 结尾的链接 */
a[href$=".pdf"]::after {
    content: " (PDF)";
}

/* 选择 src 以 ".png" 结尾的图片 */
img[src$=".png"] {
    border: 1px solid #ddd;
}
```

### 3. 单词匹配选择器

```css
/* 选择 class 包含 "warning" 单词的元素 */
[class~="warning"] {
    color: orange;
}

/* 选择 rel 包含 "noopener" 的链接 */
a[rel~="noopener"] {
    target: "_blank";
}
```

### 4. 语言匹配选择器

```css
/* 选择 lang="zh" 或以 "zh-" 开头的元素 */
[lang|="zh"] {
    font-family: "Microsoft YaHei", sans-serif;
}

[lang|="en"] {
    font-family: "Arial", sans-serif;
}
```

## 三、组合使用

### 1. 多个属性选择器

```css
/* 选择 type="text" 且 name="username" 的 input */
input[type="text"][name="username"] {
    background: #f0f0f0;
}

/* 选择有 data-id 且 data-type="user" 的元素 */
[data-id][data-type="user"] {
    border: 1px solid blue;
}
```

### 2. 与其他选择器组合

```css
/* 选择表单内的 type="submit" 的 input */
form input[type="submit"] {
    background: #007bff;
    color: white;
}

/* 选择导航栏内 href 以 "/" 开头的链接 */
nav a[href^="/"] {
    font-weight: bold;
}
```

### 3. 伪类组合

```css
/* 选择必填且有 pattern 属性的 input，在无效时显示红色 */
input[required][pattern]:invalid {
    border-color: red;
}

/* 选择有 disabled 属性的按钮 */
button[disabled] {
    opacity: 0.5;
    cursor: not-allowed;
}
```

## 四、实战案例

### 1. 外部链接样式

```css
/* 外部链接 */
a[href^="http"]:not([href*="your-domain.com"])::after {
    content: " ↗";
    font-size: 0.8em;
}

/* 安全链接 */
a[href^="https://"]::before {
    content: "🔒";
    margin-right: 4px;
}

/* 邮件链接 */
a[href^="mailto:"]::before {
    content: "✉️";
    margin-right: 4px;
}
```

### 2. 表单样式

```css
/* 不同类型的 input */
input[type="text"],
input[type="email"],
input[type="password"] {
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
}

/* 必填字段 */
input[required] {
    border-left: 3px solid #ff6b6b;
}

/* 只读字段 */
input[readonly] {
    background: #f5f5f5;
}
```

### 3. 数据属性工具提示

```css
[data-tooltip] {
    position: relative;
}

[data-tooltip]::after {
    content: attr(data-tooltip);
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    padding: 4px 8px;
    background: #333;
    color: white;
    font-size: 12px;
    border-radius: 4px;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: 0.2s;
}

[data-tooltip]:hover::after {
    opacity: 1;
    visibility: visible;
}
```

### 4. 文件类型图标

```css
/* PDF 文件 */
a[href$=".pdf"]::before {
    content: "📄";
    margin-right: 4px;
}

/* 图片文件 */
a[href$=".jpg"]::before,
a[href$=".jpeg"]::before,
a[href$=".png"]::before,
a[href$=".gif"]::before {
    content: "🖼️";
    margin-right: 4px;
}

/* 压缩文件 */
a[href$=".zip"]::before,
a[href$=".rar"]::before {
    content: "📦";
    margin-right: 4px;
}
```

## 五、性能与最佳实践

### 1. 性能考虑

```css
/* ✅ 好：结合标签名 */
input[type="text"] {
}

/* ❌ 避免：全局属性选择器 */
[type="text"] {
}
```

### 2. 优先使用类名

```css
/* ✅ 好：使用类名 */
.btn-primary {
}

/* ❌ 避免：过度依赖属性选择器 */
button[class*="primary"] {
}
```

## 六、总结

CSS 属性选择器是一个非常强大的工具：

1. 存在性选择器：`[attr]`
2. 精确匹配：`[attr="value"]`
3. 包含匹配：`[attr*="value"]`
4. 开头匹配：`[attr^="value"]`
5. 结尾匹配：`[attr$="value"]`
6. 单词匹配：`[attr~="value"]`
7. 语言匹配：`[attr|="value"]`

合理使用属性选择器，可以让你的 CSS 更加简洁和强大！
