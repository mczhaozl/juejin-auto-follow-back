# AI 大模型上下文窗口完全指南：策略、优化与实战

> 一句话摘要：深入解析 AI 大模型的上下文窗口机制，涵盖 token 计算、上下文管理、内存优化、实践技巧，帮助你在有限窗口内实现最佳 AI 性能。

## 一、背景与问题

### 1.1 上下文窗口的重要性

在 AI 大模型应用中，上下文窗口（Context Window）是决定模型能力边界的核心因素之一。它指的是模型在单次推理过程中能够处理的最大 token 数量，直接影响：

- **对话连贯性**：多轮对话时模型能否"记住"之前的内容
- **任务复杂度**：能否处理长文档、复杂代码库、详细分析
- **信息完整性**：输入和输出的总长度是否足够完成复杂任务

### 1.2 常见痛点

开发者在实际应用中经常遇到：

- **上下文溢出**：输入超出模型支持的最大 token 数
- **早期信息遗忘**：长对话中前面的关键信息被"遗忘"
- **性能下降**：接近窗口上限时模型表现明显变差
- **成本浪费**：无效的填充 token 导致资源浪费

### 1.3 本文目标

通过系统性的策略讲解和代码示例，帮助你：

1. 理解上下文窗口的工作原理
2. 掌握 token 计算与预算管理
3. 学会优化上下文使用的各种技巧
4. 在实际项目中灵活应用这些策略

## 二、上下文窗口基础

### 2.1 什么是 Token

Token 是模型处理文本的基本单位。对于英文，1 token 约等于 4 个字符或 0.75 个单词；对于中文，1 token 通常等于 1-2 个汉字。不同的 tokenizer 会产生不同的 token 划分结果。

```javascript
// 使用 tiktoken 计算 token 数（Node.js）
import tiktoken from 'tiktoken';

const enc = tiktoken.encoding_for_model("gpt-4o");
const text = "Hello, world! 你好世界！";
const tokens = enc.encode(text);
console.log(`文本: ${text}`);
console.log(`Token 数: ${tokens.length}`);
console.log(`Token IDs: ${tokens}`);

// 输出示例
// 文本: Hello, world! 你好世界！
// Token 数: 18
// Token IDs: [9906, 11, 1917, 0, 12886, 1917, 233, 136]
```

### 2.2 主流模型的上下文窗口

| 模型 | 上下文窗口 | 输出限制 | 备注 |
|------|-----------|---------|------|
| GPT-4o | 128K tokens | 16K tokens | 128K 版本 |
| GPT-4 Turbo | 128K tokens | 4K tokens | 128K 版本 |
| Claude 3.5 Sonnet | 200K tokens | 8K tokens | 支持超长上下文 |
| Claude 3 Opus | 200K tokens | 8K tokens | 最强推理能力 |
| Gemini 1.5 Pro | 1M tokens | 8K tokens | 超长上下文 |
| Llama 3.1 70B | 128K tokens | - | 开源模型 |

### 2.3 Token 计算方式

```python
# Python 中使用 tiktoken 计算
import tiktoken

def count_tokens(text: str, model: str = "gpt-4o") -> int:
    """计算文本的 token 数量"""
    enc = tiktoken.encoding_for_model(model)
    tokens = enc.encode(text)
    return len(tokens)

def count_messages_tokens(messages: list, model: str = "gpt-4o") -> int:
    """计算对话消息的总 token 数（包含格式开销）"""
    enc = tiktoken.encoding_for_model(model)
    
    num_tokens = 0
    for message in messages:
        # 每条消息的基础开销
        num_tokens += 4  # 每条消息的 overhead
        
        # 计算内容 token
        if isinstance(message.get("content"), str):
            num_tokens += len(enc.encode(message["content"]))
        elif isinstance(message.get("content"), list):
            for item in message["content"]:
                if item.get("type") == "text":
                    num_tokens += len(enc.encode(item["text"]))
                elif item.get("type") == "image_url":
                    # 图片 token 估算（简化版）
                    num_tokens += 85  # 固定开销
                    # 实际应按分辨率计算
        
        # 角色名称
        num_tokens += len(enc.encode(message.get("role", "")))
    
    # 对话前缀开销
    num_tokens += 3  # system message overhead
    
    return num_tokens

# 使用示例
messages = [
    {"role": "system", "content": "你是一个专业的技术顾问"},
    {"role": "user", "content": "解释一下什么是微服务架构"},
    {"role": "assistant", "content": "微服务架构是一种..."},
]

total = count_messages_tokens(messages)
print(f"对话总 token 数: {total}")
```

### 2.4 上下文窗口的内部机制

模型处理上下文时采用**注意力机制**（Attention Mechanism）。在 Transformer 架构中，自注意力允许输入序列中的每个位置都关注其他所有位置：

```
输入序列: [Token1, Token2, Token3, ..., TokenN]
           ↓        ↓        ↓           ↓
        [Attention weights for each token]
           ↓        ↓        ↓           ↓
      Output: 每个 token 的表示包含了全局上下文信息
```

然而，**计算复杂度是 O(N²)**，这意味着 token 数量增加时，内存和计算成本急剧上升。不同模型采用各种优化技术来突破这一限制：

- **稀疏注意力**：只计算部分位置间的注意力
- **滑动窗口**：只关注附近 token
- **分段处理**：将长序列分成多个段
- **递归机制**：用之前段的摘要增强当前段

## 三、上下文管理策略

### 3.1 固定窗口策略

最简单的策略是限制上下文长度，只保留最近的消息：

```javascript
class FixedWindowContextManager {
    constructor(maxTokens = 16000) {
        this.maxTokens = maxTokens;
    }
    
    manage(messages) {
        const enc = tiktoken.encoding_for_model("gpt-4o");
        
        // 计算系统消息（如果存在）
        let systemTokens = 0;
        let systemMessage = null;
        const nonSystemMessages = [];
        
        for (const msg of messages) {
            if (msg.role === "system") {
                systemMessage = msg;
                systemTokens = len(enc.encode(msg.content));
            } else {
                nonSystemMessages.push(msg);
            }
        }
        
        // 预留输出空间
        const outputBuffer = 2000;
        const availableTokens = this.maxTokens - systemTokens - outputBuffer;
        
        // 从最新消息开始，保留在限制内的消息
        const keptMessages = [];
        let currentTokens = 0;
        
        for (let i = nonSystemMessages.length - 1; i >= 0; i--) {
            const msg = nonSystemMessages[i];
            const msgTokens = len(enc.encode(msg.content));
            
            if (currentTokens + msgTokens <= availableTokens) {
                keptMessages.unshift(msg);
                currentTokens += msgTokens;
            } else {
                break;
            }
        }
        
        // 如果系统消息太长，需要截断
        if (systemMessage) {
            const systemEncTokens = enc.encode(systemMessage.content);
            if (systemEncTokens.length > 4000) {
                // 截断系统消息
                const truncatedContent = enc.decode(systemEncTokens.slice(0, 4000));
                systemMessage = {...systemMessage, content: truncatedContent + "\n\n[系统消息已截断]"};
            }
            keptMessages.unshift(systemMessage);
        }
        
        return keptMessages;
    }
}
```

### 3.2 摘要压缩策略

当消息太长时，生成摘要来压缩历史记录：

```python
class SummarizingContextManager:
    def __init__(self, max_tokens=16000, summary_tokens=500):
        self.max_tokens = max_tokens
        self.summary_tokens = summary_tokens
    
    async def summarize_old_messages(self, messages_to_summarize: list) -> str:
        """将旧消息压缩为摘要"""
        prompt = f"""请将以下对话内容压缩为一个简洁的摘要，保留所有关键信息：

{messages_to_summarize}

摘要格式要求：
1. 包含对话的主要话题和目标
2. 记录重要的结论或决定
3. 保留关键的上下文信息（如用户偏好、约束条件等）
4. 使用简洁的语言，不超过 {self.summary_tokens} 个 token

摘要："""
        
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=self.summary_tokens
        )
        
        return response.choices[0].message.content
    
    def manage(self, messages: list) -> list:
        enc = tiktoken.encoding_for_model("gpt-4o")
        
        total_tokens = sum(len(enc.encode(m["content"])) for m in messages)
        
        if total_tokens <= self.max_tokens:
            return messages
        
        # 保留最近的消息
        recent_messages = []
        historical_messages = []
        current_tokens = 0
        output_buffer = 2000
        
        for msg in reversed(messages):
            msg_tokens = len(enc.encode(msg["content"]))
            if current_tokens + msg_tokens <= self.max_tokens - output_buffer:
                recent_messages.insert(0, msg)
                current_tokens += msg_tokens
            else:
                historical_messages.insert(0, msg)
        
        # 摘要历史消息
        if historical_messages:
            import asyncio
            summary = asyncio.run(
                self.summarize_old_messages(
                    [m["content"] for m in historical_messages]
                )
            )
            
            summary_msg = {
                "role": "system",
                "content": f"[早期对话摘要] {summary}"
            }
            
            # 如果摘要后的总长度仍然超限，继续截断
            result = [summary_msg] + recent_messages
            total = sum(len(enc.encode(m["content"])) for m in result)
            
            if total > self.max_tokens:
                # 进一步截断 recent_messages
                kept = []
                tokens = 0
                for msg in recent_messages:
                    msg_tokens = len(enc.encode(msg["content"]))
                    if tokens + msg_tokens <= self.max_tokens - output_buffer - len(enc.encode(summary_msg["content"])):
                        kept.append(msg)
                        tokens += msg_tokens
                return [summary_msg] + kept
        
        return recent_messages
```

### 3.3 重要性加权策略

根据消息内容的重要性决定保留什么：

```javascript
class ImportanceWeightedContextManager {
    constructor(maxTokens = 16000) {
        this.maxTokens = maxTokens;
    }
    
    async scoreMessageImportance(message) {
        const prompt = `评估以下消息的上下文重要性（0-10分）：
        
消息内容：${message.content}
角色：${message.role}

考虑因素：
- 是否包含关键约束或要求
- 是否包含重要的上下文信息
- 是否包含后续对话依赖的前置信息
- 是否包含结论或决定

只输出一个数字，不要其他内容。`;
        
        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [{ role: "user", content: prompt }],
            max_tokens: 5,
            temperature: 0
        });
        
        return parseInt(response.choices[0].message.content.trim()) || 5;
    }
    
    async manage(messages) {
        const enc = tiktoken.encoding_for_model("gpt-4o");
        
        // 为每条消息评分
        const scoredMessages = [];
        for (const msg of messages) {
            if (msg.role === "system") {
                scoredMessages.push({ ...msg, importance: 10 }); // 系统消息最高优先级
            } else {
                const importance = await this.scoreMessageImportance(msg);
                scoredMessages.push({ ...msg, importance });
            }
        }
        
        // 按重要性排序
        scoredMessages.sort((a, b) => b.importance - a.importance);
        
        // 贪心选择最重要的消息
        const selected = [];
        let currentTokens = 0;
        const outputBuffer = 2000;
        
        for (const msg of scoredMessages) {
            const msgTokens = len(enc.encode(msg.content));
            
            if (currentTokens + msgTokens <= this.maxTokens - outputBuffer) {
                selected.push(msg);
                currentTokens += msgTokens;
            }
            
            if (currentTokens >= this.maxTokens - outputBuffer) {
                break;
            }
        }
        
        // 恢复原始顺序
        selected.sort((a, b) => {
            return messages.indexOf(a) - messages.indexOf(b);
        });
        
        return selected;
    }
}
```

## 四、Token 优化技巧

### 4.1 提示词优化

```javascript
// 优化前：冗长模糊的提示词
const prompt1 = `
请帮我写一段代码，实现以下功能：
我有一个用户列表，每个用户有 id、name、email 等字段
我需要从这个列表中筛选出符合条件的用户
条件是：name 以 '张' 开头，或者 email 包含 '@company.com'
筛选后我需要对结果进行排序
按 name 升序排列
最后我需要把结果转换为 JSON 格式输出
请用 JavaScript 实现
`;

// 优化后：简洁结构化的提示词
const prompt2 = `用 JavaScript 实现用户筛选：

输入：用户对象数组 [{id, name, email}, ...]

筛选条件：
- name 以 '张' 开头 OR
- email 包含 '@company.com'

排序：按 name 升序

输出：JSON 格式

要求：简洁、可运行、带注释`;

// Token 对比
console.log(countTokens(prompt1)); // 约 180 tokens
console.log(countTokens(prompt2)); // 约 80 tokens
// 节省约 55% 的 token
```

### 4.2 结构化输出

使用 JSON 模式减少输出 token：

```python
# 使用 JSON 模式控制输出
response = await openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "你是一个数据分析师"},
        {"role": "user", "content": "分析以下销售数据，找出 Top 3 产品"},
    ],
    response_format={"type": "json_object"},
    # 设置严格模式
    extra_body={"response_format": {"type": "json_object", "schema": {
        "top_products": [
            {"name": "产品名", "revenue": 金额, "growth_rate": "增长率"}
        ],
        "summary": "整体分析摘要"
    }}}
)

# 输出固定 JSON 格式，便于解析和处理
result = json.loads(response.choices[0].message.content)
```

### 4.3 Few-shot 示例优化

```javascript
// 优化前：冗余的示例
const examples1 = [
    {
        input: "把 'hello' 转换成大写",
        output: "HELLO"
    },
    {
        input: "把 'world' 转换成大写", 
        output: "WORLD"
    },
    {
        input: "把 'foo' 转换成大写",
        output: "FOO"
    }
];

// 优化后：精简的示例
const examples2 = [
    { in: "hello", out: "HELLO" },
    { in: "world", out: "WORLD" }
];

// 或使用更简洁的格式
const examples3 = `"hello" → "HELLO"
"world" → "WORLD"`;

// Token 对比
console.log(countTokens(JSON.stringify(examples1))); // 约 95 tokens
console.log(countTokens(JSON.stringify(examples2))); // 约 42 tokens
console.log(countTokens(examples3)); // 约 25 tokens
```

### 4.4 避免重复格式开销

```python
# 优化前：多次使用相同的分隔符
prompt1 = """
=== 用户信息 ===
姓名：张三
=== 订单信息 ===
订单号：12345
=== 物流信息 ===
快递单号：SF123456
===

请根据以上信息处理用户请求。
"""

# 优化后：简化格式
prompt2 = """用户信息：姓名=张三
订单信息：订单号=12345
物流信息：快递单号=SF123456

请根据以上信息处理用户请求。"""

# 或使用结构化标记
prompt3 = {
    "user": {"name": "张三"},
    "order": {"id": "12345"},
    "logistics": {"tracking": "SF123456"}
}

# 对于 API 调用，直接传 dict 而非文本
response = await openai.chat.completions.create(
    model="gpt-4o",
    messages=[{
        "role": "user", 
        "content": "处理用户请求",
        "metadata": {
            "user_name": "张三",
            "order_id": "12345",
            "tracking": "SF123456"
        }
    }]
)
```

## 五、实战场景与解决方案

### 5.1 长文档分析

```python
class DocumentAnalyzer:
    def __init__(self, chunk_size=4000, overlap=200):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def split_document(self, text: str) -> list:
        """将长文档分割成块"""
        enc = tiktoken.encoding_for_model("gpt-4o")
        tokens = enc.encode(text)
        
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = enc.decode(chunk_tokens)
            chunks.append(chunk_text)
            
            start = end - self.overlap  # 保留重叠区域
        
        return chunks
    
    async def analyze_document(self, text: str, query: str) -> dict:
        """分析长文档"""
        chunks = self.split_document(text)
        
        # 为每个块生成摘要
        chunk_summaries = []
        for i, chunk in enumerate(chunks):
            summary_prompt = f"""分析以下文档片段，完成指定任务。

文档片段 {i+1}/{len(chunks)}：
{chunk}

任务：{query}

输出格式：
{{
    "relevant_findings": ["发现1", "发现2"],
    "key_insights": ["洞察1", "洞察2"],
    "confidence": "high/medium/low"
}}"""
            
            response = await openai.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": summary_prompt}],
                response_format={"type": "json_object"}
            )
            
            chunk_summaries.append({
                "chunk_index": i,
                "summary": json.loads(response.choices[0].message.content)
            })
        
        # 综合分析
        synthesis_prompt = f"""基于以下文档片段的分析结果，综合回答用户查询。

用户查询：{query}

片段分析结果：
{json.dumps(chunk_summaries, ensure_ascii=False, indent=2)}

请综合所有片段的信息，给出完整回答。
如各片段有矛盾之处，明确指出并给出最佳判断。
如信息不足，明确说明哪些问题无法回答。"""
        
        final_response = await openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": synthesis_prompt}]
        )
        
        return {
            "answer": final_response.choices[0].message.content,
            "chunks_analyzed": len(chunks),
            "chunk_summaries": chunk_summaries
        }
```

### 5.2 多轮对话管理

```javascript
class ConversationManager {
    constructor(options = {}) {
        this.maxTokens = options.maxTokens || 16000;
        this.summaryThreshold = options.summaryThreshold || 8000;
        this.enc = tiktoken.encoding_for_model("gpt-4o");
        
        this.messages = [];
        this.summaries = [];  // 历史摘要
    }
    
    addMessage(role, content) {
        this.messages.push({ role, content, timestamp: Date.now() });
        this.checkAndCompact();
    }
    
    getTokenCount() {
        return sum(len(this.enc.encode(m.content)) for m in this.messages);
    }
    
    async checkAndCompact() {
        if (this.getTokenCount() > this.summaryThreshold) {
            await this.generateSummary();
        }
    }
    
    async generateSummary() {
        // 将早期消息摘要化
        const oldMessages = this.messages.slice(0, -10);  // 保留最近10条
        const recentMessages = this.messages.slice(-10);
        
        if (oldMessages.length < 3) return;
        
        const summaryPrompt = `将以下对话摘要为简洁的要点列表：

${oldMessages.map((m, i) => `[${i+1}] ${m.role}: ${m.content}`).join('\n')}

摘要要求：
1. 保留所有关键信息和结论
2. 记录重要的上下文和约束
3. 使用列表格式，每条一行
4. 不超过 500 字`;
        
        const response = await openai.chat.completions.create({
            model: "gpt-4o",
            messages: [{ role: "user", content: summaryPrompt }],
            max_tokens: 500
        });
        
        const summary = response.choices[0].message.content;
        this.summaries.push({
            content: summary,
            messageCount: oldMessages.length,
            timestamp: Date.now()
        });
        
        this.messages = [
            { 
                role: "system", 
                content: `[早期对话摘要]\n${summary}`
            },
            ...recentMessages
        ];
    }
    
    getMessages() {
        return this.messages;
    }
}

// 使用示例
const conv = new ConversationManager({ maxTokens: 16000, summaryThreshold: 8000 });

// 添加消息
conv.addMessage("user", "我需要一个用户认证系统");
conv.addMessage("assistant", "好的，请问你需要支持哪些认证方式？");
conv.addMessage("user", "需要支持邮箱密码和手机验证码登录");
// ... 更多对话

// 获取处理后的消息
const messages = conv.getMessages();
```

### 5.3 代码库问答

```python
class CodebaseQ&A:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.file_index = {}  # 文件路径 -> 摘要信息
        self.build_index()
    
    def build_index(self):
        """构建代码库索引"""
        for file_path in self.repo_path.rglob("*.py"):
            if "venv" in str(file_path) or "__pycache__" in str(file_path):
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8")
                summary = self._summarize_file(content, str(file_path))
                self.file_index[str(file_path)] = {
                    "summary": summary,
                    "lines": len(content.splitlines()),
                    "key_functions": self._extract_functions(content)
                }
            except Exception:
                continue
    
    def _summarize_file(self, content: str, file_path: str) -> str:
        """生成文件摘要"""
        prompt = f"""为以下 Python 文件生成简短摘要：

文件路径：{file_path}
代码：
{content[:3000]}  # 只取前3000字符

输出格式：
文件名：[名称]
功能：[一句话描述]
主要类/函数：[列表]"""
        
        # 简化版：直接解析
        functions = self._extract_functions(content)
        imports = self._extract_imports(content)
        
        return f"包含 {len(functions)} 个函数/类，主要依赖 {len(imports)} 个模块"
    
    def _extract_functions(self, content: str) -> list:
        """提取函数定义"""
        import re
        pattern = r'^(?:def|class)\s+(\w+)'
        return re.findall(pattern, content, re.MULTILINE)
    
    def _extract_imports(self, content: str) -> list:
        """提取导入语句"""
        import re
        pattern = r'^(?:import|from)\s+(\w+)'
        return re.findall(pattern, content, re.MULTILINE)
    
    async def query(self, question: str) -> str:
        """回答关于代码库的问题"""
        # 1. 找出相关文件
        relevant_files = self._find_relevant_files(question)
        
        # 2. 获取相关文件内容
        file_contents = {}
        for file_path in relevant_files[:5]:  # 限制文件数
            try:
                content = Path(file_path).read_text(encoding="utf-8")
                # 截断过长文件
                if len(content) > 5000:
                    content = content[:5000] + "\n... [内容已截断]"
                file_contents[file_path] = content
            except Exception:
                continue
        
        # 3. 构建查询提示
        prompt = f"""基于以下代码库内容回答问题。

问题：{question}

相关代码文件：
{json.dumps(file_contents, ensure_ascii=False, indent=2)[:15000]}

请直接基于代码内容回答，如果不确定或信息不足，明确说明。"""
        
        response = await openai.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.choices[0].message.content
    
    def _find_relevant_files(self, question: str) -> list:
        """根据问题找出相关文件"""
        # 简化实现：基于关键词匹配
        keywords = self._extract_keywords(question)
        scores = {}
        
        for file_path, info in self.file_index.items():
            score = 0
            summary_lower = info["summary"].lower()
            
            for keyword in keywords:
                if keyword.lower() in summary_lower:
                    score += 1
            
            if score > 0:
                scores[file_path] = score
        
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
    
    def _extract_keywords(self, text: str) -> list:
        """提取关键词"""
        # 简化：去除停用词
        stopwords = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好", "自己", "这", "那", "什么", "怎么", "如何", "为什么", "吗", "呢", "吧"}
        words = text.split()
        return [w for w in words if w not in stopwords and len(w) > 1]
```

## 六、高级优化技术

### 6.1 自适应上下文

```javascript
class AdaptiveContextManager {
    constructor() {
        this.baseEncoder = tiktoken.encoding_for_model("gpt-4o");
        this.contextBudgets = {
            "simple": 2000,
            "medium": 8000,
            "complex": 16000,
            "ultra": 32000
        };
    }
    
    estimateTaskComplexity(messages) {
        const prompt = `评估以下对话的复杂度：

${messages.map((m, i) => `[${i+1}] ${m.role}: ${m.content.substring(0, 200)}`).join('\n')}

复杂度等级：
- simple：简单问答、基础生成
- medium：多轮对话、简单分析
- complex：复杂推理、长文档处理
- ultra：超长上下文、高级推理

只输出一个词：simple/medium/complex/ultra`;

        // 这里简化处理，实际应该调用 LLM
        const avgLength = messages.reduce((sum, m) => sum + m.content.length, 0) / messages.length;
        
        if (avgLength > 5000) return "complex";
        if (avgLength > 2000) return "medium";
        return "simple";
    }
    
    calculateOptimalAllocation(taskComplexity, totalBudget) {
        const allocation = {
            "system": 0,
            "history": 0,
            "current": 0,
            "output": 2000  // 固定输出缓冲
        };
        
        const remaining = totalBudget - allocation.output;
        
        switch(taskComplexity) {
            case "simple":
                allocation.system = Math.min(1000, remaining * 0.2);
                allocation.history = remaining * 0.4;
                allocation.current = remaining * 0.4;
                break;
            case "medium":
                allocation.system = Math.min(1500, remaining * 0.15);
                allocation.history = remaining * 0.5;
                allocation.current = remaining * 0.35;
                break;
            case "complex":
                allocation.system = Math.min(2000, remaining * 0.1);
                allocation.history = remaining * 0.6;
                allocation.current = remaining * 0.3;
                break;
            case "ultra":
                allocation.system = Math.min(3000, remaining * 0.08);
                allocation.history = remaining * 0.65;
                allocation.current = remaining * 0.27;
                break;
        }
        
        return allocation;
    }
    
    manage(messages, taskComplexity = null) {
        if (!taskComplexity) {
            taskComplexity = this.estimateTaskComplexity(messages);
        }
        
        const totalBudget = this.contextBudgets[taskComplexity];
        const allocation = this.calculateOptimalAllocation(taskComplexity, totalBudget);
        
        const enc = this.baseEncoder;
        const result = [];
        let usedTokens = 0;
        
        // 1. 处理系统消息
        for (const msg of messages) {
            if (msg.role !== "system") continue;
            
            const tokens = len(enc.encode(msg.content));
            if (usedTokens + tokens <= allocation.system) {
                result.push(msg);
                usedTokens += tokens;
            } else if (tokens > allocation.system) {
                // 截断系统消息
                const truncatedContent = enc.decode(
                    enc.encode(msg.content).slice(0, allocation.system - usedTokens - 10)
                );
                result.push({ ...msg, content: truncatedContent + "\n[系统消息已截断]" });
                break;
            }
        }
        
        // 2. 处理历史消息
        const historyMessages = messages.filter(m => m.role !== "system");
        const recentFirst = historyMessages.reverse();
        
        for (const msg of recentFirst) {
            const tokens = len(enc.encode(msg.content));
            
            if (usedTokens + tokens <= allocation.system + allocation.history) {
                result.unshift(msg);
                usedTokens += tokens;
            }
        }
        
        // 3. 添加当前消息（如果还有空间）
        for (const msg of historyMessages) {
            if (msg.role === "user") {
                const tokens = len(enc.encode(msg.content));
                
                if (usedTokens + tokens <= totalBudget - allocation.output) {
                    result.push(msg);
                    usedTokens += tokens;
                }
                break;
            }
        }
        
        return result;
    }
}
```

### 6.2 RAG 与上下文结合

```python
class HybridRAGContextManager:
    def __init__(self, vector_store, max_context_tokens=16000):
        self.vector_store = vector_store
        self.max_context_tokens = max_context_tokens
    
    async def retrieve_and_augment(self, query: str, top_k: int = 5) -> list:
        """检索相关文档并增强上下文"""
        # 1. 检索相关文档
        relevant_docs = await self.vector_store.similarity_search(
            query, 
            top_k=top_k,
            filter={"status": "published"}  # 可选过滤
        )
        
        # 2. 评估是否需要外部知识
        query_prompt = f"""评估以下用户查询是否需要参考外部知识来回答：

用户查询：{query}

考虑：
1. 查询是否涉及特定事实、数据或详细信息？
2. 当前对话上下文是否已包含回答所需的所有信息？
3. 是否需要引用具体的文档、代码或数据？

回答：yes 或 no"""
        
        # 简化：始终使用检索（实际可调用 LLM 判断）
        use_retrieval = len(relevant_docs) > 0
        
        return {
            "use_retrieval": use_retrieval,
            "retrieved_docs": relevant_docs,
            "context_tokens": sum(len(doc.content) // 4 for doc in relevant_docs)
        }
    
    def build_augmented_prompt(self, original_messages: list, retrieved_docs: list) -> list:
        """构建增强后的提示"""
        # 构建检索上下文
        retrieval_context = "\n\n".join([
            f"[文档 {i+1}] {doc.content}"
            for i, doc in enumerate(retrieved_docs)
        ])
        
        # 估算 token
        enc = tiktoken.encoding_for_model("gpt-4o")
        retrieval_tokens = len(enc.encode(retrieval_context))
        
        # 如果检索内容太长，截断
        if retrieval_tokens > self.max_context_tokens * 0.4:
            truncated = enc.decode(enc.encode(retrieval_context)[:int(self.max_context_tokens * 0.4)])
            retrieval_context = truncated + "\n\n[文档内容已截断]"
        
        # 构建新消息
        augmented_messages = original_messages.copy()
        
        # 在合适位置插入检索上下文
        insert_index = 1  # 通常在系统消息之后
        for i, msg in enumerate(augmented_messages):
            if msg.role == "system":
                insert_index = i + 1
        
        augmented_messages.insert(insert_index, {
            "role": "system",
            "content": f"[参考文档]\n{retrieval_context}\n[/参考文档]\n\n回答用户问题时，可参考上述文档内容。"
        })
        
        return augmented_messages
    
    async def query(self, messages: list, query: str) -> dict:
        """执行混合查询"""
        # 1. 决定是否检索
        retrieval_info = await self.retrieve_and_augment(query)
        
        # 2. 根据需要构建增强上下文
        if retrieval_info["use_retrieval"]:
            augmented_messages = self.build_augmented_prompt(
                messages, 
                retrieval_info["retrieved_docs"]
            )
        else:
            augmented_messages = messages
        
        # 3. 执行查询
        response = await openai.chat.completions.create(
            model="gpt-4o",
            messages=augmented_messages
        )
        
        return {
            "response": response.choices[0].message.content,
            "retrieval_used": retrieval_info["use_retrieval"],
            "docs_retrieved": len(retrieval_info["retrieved_docs"])
        }
```

## 七、性能与成本优化

### 7.1 Token 使用监控

```javascript
class TokenMonitor {
    constructor() {
        this.enc = tiktoken.encoding_for_model("gpt-4o");
        this.history = [];
    }
    
    logRequest(messages, response, cost_per_1k_tokens = 0.002) {
        const prompt_tokens = this.countMessagesTokens(messages);
        const completion_tokens = len(this.enc.encode(response.content));
        const total_tokens = prompt_tokens + completion_tokens;
        
        const entry = {
            timestamp: Date.now(),
            prompt_tokens,
            completion_tokens,
            total_tokens,
            cost: (total_tokens / 1000) * cost_per_1k_tokens,
            message_count: messages.length
        };
        
        this.history.push(entry);
        return entry;
    }
    
    countMessagesTokens(messages) {
        let total = 0;
        for (const msg of messages) {
            total += len(this.enc.encode(msg.content));
            total += 4; // 每条消息的 overhead
        }
        return total + 3; // 对话前缀
    }
    
    getStats() {
        const total = this.history.reduce((sum, e) => sum + e.total_tokens, 0);
        const total_cost = this.history.reduce((sum, e) => sum + e.cost, 0);
        const avg_tokens = total / this.history.length;
        
        return {
            total_requests: this.history.length,
            total_tokens: total,
            total_cost: total_cost,
            average_tokens_per_request: avg_tokens,
            most_expensive: Math.max(...this.history.map(e => e.cost)),
            largest_request: Math.max(...this.history.map(e => e.total_tokens))
        };
    }
    
    generateReport() {
        const stats = this.getStats();
        
        return `
=== Token 使用报告 ===

总请求数：${stats.total_requests}
总 Token 消耗：${stats.total_tokens.toLocaleString()}
总成本：$${stats.total_cost.toFixed(4)}
平均每请求 Token：${Math.round(stats.average_tokens_per_request).toLocaleString()}
单请求最大 Token：${stats.largest_request.toLocaleString()}
最高单次成本：$${stats.most_expensive.toFixed(4)}

建议优化方向：
${stats.average_tokens_per_request > 8000 ? "- 考虑使用摘要压缩历史消息" : ""}
${stats.largest_request > 15000 ? "- 某些请求过大，建议分块处理" : ""}
${stats.total_cost > 10 ? "- 成本较高，考虑使用更小的模型处理简单任务" : ""}
        `.trim();
    }
}
```

### 7.2 智能模型路由

```python
class SmartModelRouter:
    def __init__(self):
        self.models = {
            "fast": {
                "name": "gpt-4o-mini",
                "cost_per_1k": 0.00015,
                "strengths": ["简单问答", "格式转换", "快速分类"],
                "max_tokens": 128000
            },
            "balanced": {
                "name": "gpt-4o",
                "cost_per_1k": 0.002,
                "strengths": ["多轮对话", "代码生成", "分析推理"],
                "max_tokens": 128000
            },
            "powerful": {
                "name": "gpt-4-turbo",
                "cost_per_1k": 0.01,
                "strengths": ["复杂推理", "长文档处理", "高精度任务"],
                "max_tokens": 128000
            }
        }
    
    def estimate_task_type(self, messages: list) -> str:
        """估计任务类型"""
        total_length = sum(len(m["content"]) for m in messages)
        
        # 简单启发式判断
        if total_length < 500:
            return "fast"
        elif total_length < 3000:
            return "balanced"
        else:
            return "powerful"
    
    def route(self, messages: list, preferred_model: str = None) -> str:
        """选择最佳模型"""
        if preferred_model and preferred_model in self.models:
            return preferred_model
        
        task_type = self.estimate_task_type(messages)
        
        # 检查 token 限制
        enc = tiktoken.encoding_for_model("gpt-4o")
        total_tokens = sum(len(enc.encode(m["content"])) for m in messages)
        
        for model_key in ["fast", "balanced", "powerful"]:
            if total_tokens < self.models[model_key]["max_tokens"] * 0.9:
                return model_key
        
        return "powerful"  # 默认使用最强模型
    
    async def execute(self, messages: list, preferred: str = None) -> dict:
        """执行智能路由"""
        model_key = self.route(messages, preferred)
        model_info = self.models[model_key]
        
        start_time = time.time()
        
        response = await openai.chat.completions.create(
            model=model_info["name"],
            messages=messages
        )
        
        duration = time.time() - start_time
        
        return {
            "model": model_info["name"],
            "model_key": model_key,
            "response": response.choices[0].message.content,
            "duration": duration,
            "cost": (response.usage.total_tokens / 1000) * model_info["cost_per_1k"]
        }
```

## 八、最佳实践与建议

### 8.1 设计原则

1. **预算意识**：始终考虑 token 成本，不要让模型处理不必要的上下文
2. **渐进式设计**：先简单后复杂，先验证后优化
3. **可观测性**：记录和监控 token 使用，及时发现问题
4. **容错处理**：为上下文溢出等异常情况准备降级方案
5. **用户知情**：让用户了解上下文限制，避免期望落差

### 8.2 反模式

```javascript
// 反模式 1：无限累积上下文
function badPattern1() {
    const allMessages = [];
    setInterval(() => {
        const newMessage = getUserInput();
        allMessages.push(newMessage);  // 永远只增不减
        askLLM(allMessages);
    }, 1000);
}

// 反模式 2：不考虑格式开销
function badPattern2() {
    const context = `
        === 系统提示 ===
        ${longSystemPrompt}
        
        === 用户历史 ===
        ${JSON.stringify(allUserHistory)}
        
        === 当前请求 ===
        ${userRequest}
    `;  // 大量无用的格式字符消耗 token
    
    askLLM(context);
}

// 反模式 3：重复包含相似上下文
function badPattern3() {
    const messages = [
        { role: "system", content: "你是 XX 公司的 AI 助手" },
        { role: "system", content: "公司名叫 XX，成立于 2020 年" },
        { role: "system", content: "公司的使命是 YY" },
        // ... 更多重复的公司信息
        { role: "user", content: "你们公司叫什么？" }  // 答案已在上下文多次重复
    ];
}
```

### 8.3 检查清单

在部署生产环境前，确认以下事项：

- [ ] 已实现上下文长度限制和截断策略
- [ ] 已实现历史消息摘要或压缩机制
- [ ] 已监控 token 使用量和成本
- [ ] 已测试边缘情况（空消息、超长消息等）
- [ ] 已实现错误处理和降级方案
- [ ] 已考虑不同任务的模型选择策略
- [ ] 已优化提示词，减少无效 token
- [ ] 已记录关键指标用于后续优化

## 九、总结

### 9.1 核心要点

1. **理解 Token**：Token 是上下文的基本单位，不同语言和模型的 token 效率不同
2. **管理预算**：始终在预算内思考，为输出预留空间
3. **智能压缩**：使用摘要、重要性评分等策略保留关键信息
4. **持续优化**：通过监控和分析不断改进上下文使用效率
5. **场景适配**：不同场景需要不同的上下文管理策略

### 9.2 工具推荐

| 工具 | 用途 | 链接 |
|------|------|------|
| tiktoken | Token 计算 | npm install tiktoken |
| LangChain | 上下文管理框架 | pip install langchain |
| LlamaIndex | RAG 与上下文增强 | pip install llama-index |

### 9.3 进阶阅读

- **《Attention is All You Need》**：Transformer 架构原论文
- **《LLM Powered Applications》**：构建 LLM 应用的实践指南
- ** Anthropic 上下文窗口研究**：深入分析上下文窗口对模型性能的影响

> 如果这篇文章对你有帮助，欢迎点赞、收藏！有任何问题可以在评论区留言，我会尽力解答。
