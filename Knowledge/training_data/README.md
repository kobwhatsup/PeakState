# 巅峰态AI精力管理教练 - 训练数据集

## 数据集概述

本数据集专门为训练"巅峰态"AI精力管理教练而设计,包含 **213** 条高质量训练样本。

## 数据来源

所有训练数据基于以下来源:
1. **100篇精力管理领域权威研究文献** - 涵盖睡眠科学、运动与认知、营养、压力管理等10个核心领域
2. **真实健康教练对话场景** - 参考UIC健康教练对话语料库
3. **精力管理最佳实践** - 来自《精力管理》《深度工作》《原子习惯》等经典著作

## 数据格式

### 文件列表

| 文件名 | 格式 | 样本数 | 用途 |
|--------|------|--------|------|
| `instruction_tuning.jsonl` | JSONL | 141 | 指令微调 |
| `conversational.jsonl` | JSONL | 24 | 对话训练 |
| `multi_turn.jsonl` | JSONL | 2 | 多轮对话 |
| `qa_pairs.jsonl` | JSONL | 40 | 问答对 |
| `role_play.jsonl` | JSONL | 1 | 角色扮演 |
| `peakstate_training_full.parquet` | Parquet | 213 | 完整数据集(推荐) |
| `peakstate_training_full.csv` | CSV | 213 | 完整数据集(便于查看) |

### 字段说明

**标准格式 (instruction_tuning):**
- `instruction`: 用户的问题或指令
- `input`: 额外的输入信息(通常为空)
- `output`: AI教练的专业回答
- `category`: 知识类别
- `type`: 数据类型

**对话格式 (conversational, multi_turn):**
- `messages`: 对话消息列表
  - `role`: "user" 或 "assistant"
  - `content`: 消息内容
- `category`: 对话场景类别
- `type`: 对话类型

**问答格式 (qa_pairs):**
- `question`: 问题
- `answer`: 答案
- `category`: 知识类别
- `source`: 来源文献

## 数据集统计

- **总样本数:** 213
- **覆盖领域:** 10个核心精力管理领域
- **对话类型:** 初次咨询、问题诊断、知识教育、行动计划、进度跟踪、动机激励、多轮深度对话
- **平均instruction长度:** 21 字符
- **平均output长度:** 112 字符

### 类别分布

```
category
睡眠科学     19
运动与认知    18
营养与大脑    18
压力管理     18
正念冥想     18
习惯养成     18
心流状态     18
工作倦怠     18
时间管理     18
可穿戴设备    18
睡眠问题      8
精力不足      8
压力过大      8
睡眠改善      4
运动习惯      4
```

### 类型分布

```
type
实践建议      60
概念解释      51
问答        40
科学依据      30
初次咨询      24
多轮深度对话     8
```

## 使用方法

### 在Hugging Face上使用

```python
from datasets import load_dataset

# 从Parquet文件加载(推荐)
dataset = load_dataset('parquet', data_files='peakstate_training_full.parquet')

# 或从JSONL文件加载
dataset = load_dataset('json', data_files='instruction_tuning.jsonl')
```

### 微调示例

```python
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import load_dataset

# 1. 加载数据
dataset = load_dataset('parquet', data_files='peakstate_training_full.parquet')

# 2. 加载模型
model_name = "Qwen/Qwen2.5-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 3. 数据预处理
def preprocess_function(examples):
    prompts = []
    for instruction, input_text, output in zip(
        examples['instruction'], 
        examples['input'], 
        examples['output']
    ):
        if input_text:
            prompt = f"指令: {instruction}\n输入: {input_text}\n回答: {output}"
        else:
            prompt = f"指令: {instruction}\n回答: {output}"
        prompts.append(prompt)
    
    return tokenizer(prompts, truncation=True, padding='max_length', max_length=2048)

tokenized_dataset = dataset.map(preprocess_function, batched=True)

# 4. 训练配置
training_args = TrainingArguments(
    output_dir="./peakstate-coach",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=4,
    learning_rate=2e-5,
    warmup_steps=100,
    logging_steps=10,
    save_steps=100,
)

# 5. 训练
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
)

trainer.train()
```

## 推荐模型

适合微调的中文大模型:
- **Qwen/Qwen2.5-7B-Instruct** (推荐)
- THUDM/chatglm3-6b
- baichuan-inc/Baichuan2-7B-Chat
- 01-ai/Yi-6B-Chat
- deepseek-ai/deepseek-llm-7b-chat

## 数据质量保证

1. **科学性:** 所有内容基于权威研究文献
2. **实用性:** 包含大量实践建议和具体方法
3. **多样性:** 涵盖多种对话场景和问题类型
4. **真实性:** 模拟真实的教练-用户交互
5. **个性化:** 考虑不同用户背景和需求

## 许可证

本数据集仅供"巅峰态"项目内部使用。

## 引用

如果使用本数据集,请引用相关的科学文献来源。

## 版本历史

- **v1.0** (2025-10-07): 初始版本,包含213条训练样本

## 联系方式

如有问题,请联系项目团队。

---

**创建日期:** 2025-10-07  
**最后更新:** 2025-10-07  
**数据集版本:** 1.0
