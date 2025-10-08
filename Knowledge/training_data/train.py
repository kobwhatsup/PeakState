#!/usr/bin/env python3
"""
巅峰态AI精力管理教练 - 模型微调脚本
"""

from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import load_dataset
import torch

def main():
    # 配置
    MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"
    DATA_FILE = "peakstate_training_full.parquet"
    OUTPUT_DIR = "./peakstate-coach-finetuned"
    
    print("加载数据集...")
    dataset = load_dataset('parquet', data_files=DATA_FILE)
    
    print(f"加载模型: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
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
    
    print("预处理数据...")
    tokenized_dataset = dataset.map(preprocess_function, batched=True)
    
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-5,
        warmup_steps=100,
        logging_steps=10,
        save_steps=100,
        fp16=True,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset['train'],
    )
    
    print("开始训练...")
    trainer.train()
    
    print(f"保存模型到: {OUTPUT_DIR}")
    trainer.save_model(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    
    print("训练完成!")

if __name__ == "__main__":
    main()
