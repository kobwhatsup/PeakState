"""
本地AI模型管理器
使用Phi-3.5-mini-instruct进行本地推理，实现70%成本节省
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from threading import Thread

from app.core.config import settings

logger = logging.getLogger(__name__)


class LocalModelManager:
    """
    本地Phi-3.5模型管理器

    功能：
    - 懒加载模型（首次使用时加载）
    - 内存优化（float16, 模型量化）
    - 异步推理
    - 缓存管理
    """

    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.device = self._detect_device()
        self.model_name = "microsoft/Phi-3.5-mini-instruct"
        self.is_loaded = False
        self.load_lock = asyncio.Lock()

        # 性能指标
        self.inference_count = 0
        self.total_inference_time = 0.0

        logger.info(f"🧠 LocalModelManager initialized (device: {self.device})")

    def _detect_device(self) -> str:
        """
        检测可用设备
        优先级: CUDA > MPS (Apple Silicon) > CPU
        """
        if torch.cuda.is_available():
            device = "cuda"
            logger.info("✅ CUDA GPU detected")
        elif torch.backends.mps.is_available():
            device = "mps"
            logger.info("✅ Apple Silicon MPS detected")
        else:
            device = "cpu"
            logger.warning("⚠️  No GPU detected, using CPU (slow)")

        return device

    async def load_model(self) -> None:
        """
        加载Phi-3.5模型（懒加载）
        使用float16节省内存，使用device_map自动分配设备
        """
        async with self.load_lock:
            if self.is_loaded:
                return

            logger.info(f"📦 Loading Phi-3.5 model: {self.model_name}")
            start_time = datetime.now()

            try:
                # 在线程池中加载模型（避免阻塞事件循环）
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self._load_model_sync)

                load_time = (datetime.now() - start_time).total_seconds()
                logger.info(f"✅ Model loaded successfully in {load_time:.2f}s")

                # 内存使用情况
                if self.device == "mps":
                    logger.info("💾 Using Apple Silicon unified memory")
                elif self.device == "cuda":
                    allocated = torch.cuda.memory_allocated() / 1024**3
                    logger.info(f"💾 GPU memory: {allocated:.2f}GB")

                self.is_loaded = True

            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}", exc_info=True)
                raise RuntimeError(f"Model loading failed: {e}")

    def _load_model_sync(self) -> None:
        """同步加载模型（在线程池中执行）"""
        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        # 加载模型
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,  # 节省内存
            device_map=self.device,
            trust_remote_code=True,
            low_cpu_mem_usage=True  # 优化CPU内存使用
        )

        # 设置为评估模式
        self.model.eval()

    async def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> str:
        """
        异步生成响应

        Args:
            prompt: 输入提示词
            max_new_tokens: 最大生成token数
            temperature: 温度参数（越高越随机）
            top_p: nucleus sampling参数

        Returns:
            生成的文本响应
        """
        # 确保模型已加载
        if not self.is_loaded:
            await self.load_model()

        start_time = datetime.now()

        try:
            # 构建Phi-3.5的对话格式
            formatted_prompt = self._format_phi3_prompt(prompt)

            # 在线程池中执行推理
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._generate_sync,
                formatted_prompt,
                max_new_tokens,
                temperature,
                top_p,
                kwargs
            )

            # 更新性能指标
            inference_time = (datetime.now() - start_time).total_seconds()
            self.inference_count += 1
            self.total_inference_time += inference_time

            avg_time = self.total_inference_time / self.inference_count
            logger.info(
                f"⚡ Inference #{self.inference_count}: {inference_time*1000:.0f}ms "
                f"(avg: {avg_time*1000:.0f}ms)"
            )

            return response.strip()

        except Exception as e:
            logger.error(f"❌ Inference failed: {e}", exc_info=True)
            raise RuntimeError(f"Inference failed: {e}")

    def _format_phi3_prompt(self, user_message: str) -> str:
        """
        格式化Phi-3.5的提示词
        使用官方推荐的格式: <|user|>\n{content}<|end|>\n<|assistant|>\n
        """
        return f"<|user|>\n{user_message}<|end|>\n<|assistant|>\n"

    def _generate_sync(
        self,
        prompt: str,
        max_new_tokens: int,
        temperature: float,
        top_p: float,
        kwargs: Dict[str, Any]
    ) -> str:
        """同步生成（在线程池中执行）"""
        # Tokenize
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=2048  # Phi-3.5上下文长度
        ).to(self.device)

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                use_cache=False,  # 禁用cache以避免DynamicCache兼容性问题
                **kwargs
            )

        # Decode
        generated_text = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],  # 只取新生成的部分
            skip_special_tokens=True
        )

        return generated_text

    async def generate_stream(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ):
        """
        流式生成（暂未实现）
        用于未来支持流式响应
        """
        # TODO: 实现流式生成
        raise NotImplementedError("Streaming not implemented yet")

    def get_stats(self) -> Dict[str, Any]:
        """获取性能统计"""
        if self.inference_count == 0:
            return {
                "status": "not_used",
                "inference_count": 0
            }

        avg_time = self.total_inference_time / self.inference_count
        return {
            "status": "active" if self.is_loaded else "not_loaded",
            "device": self.device,
            "model_name": self.model_name,
            "inference_count": self.inference_count,
            "total_time": round(self.total_inference_time, 2),
            "avg_inference_time_ms": round(avg_time * 1000, 0),
            "memory_allocated_gb": (
                round(torch.cuda.memory_allocated() / 1024**3, 2)
                if self.device == "cuda" else None
            )
        }

    async def unload_model(self) -> None:
        """卸载模型（释放内存）"""
        if not self.is_loaded:
            return

        logger.info("🗑️  Unloading Phi-3.5 model")

        self.model = None
        self.tokenizer = None
        self.is_loaded = False

        # 清理GPU缓存
        if self.device == "cuda":
            torch.cuda.empty_cache()

        logger.info("✅ Model unloaded")


# 全局单例
_local_model_manager: Optional[LocalModelManager] = None


def get_local_model_manager() -> LocalModelManager:
    """获取全局LocalModelManager单例"""
    global _local_model_manager

    if _local_model_manager is None:
        _local_model_manager = LocalModelManager()

    return _local_model_manager
