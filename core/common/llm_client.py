"""
大模型客户端
"""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import aiohttp
from common.config import settings, get_llm_config, get_embedding_config, get_rerank_config

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """LLM客户端基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get("timeout", 30)

    @abstractmethod
    async def chat_completion(self, messages: list, **kwargs) -> str:
        """聊天完成接口"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass


class BaseEmbeddingClient(ABC):
    """Embedding客户端基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get("timeout", 30)

    @abstractmethod
    async def create_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """创建文本嵌入向量"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass


class BaseRerankClient(ABC):
    """Rerank客户端基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get("timeout", 30)
        self.top_k = config.get("top_k", 10)

    @abstractmethod
    async def rerank(self, query: str, documents: List[str], **kwargs) -> List[Tuple[int, float]]:
        """重排序文档

        Args:
            query: 查询文本
            documents: 文档列表
            **kwargs: 其他参数

        Returns:
            List[Tuple[int, float]]: 排序后的文档索引和分数列表
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI客户端
        Args:
            api_base: OpenAI API地址
            api_key: OpenAI API密钥
            model: 模型名称
            temperature: 温度
            max_tokens: 最大Token数
            timeout: 超时时间
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = config.get("api_base", "").rstrip("/")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 2048)
    
    async def chat_completion(self, messages: list, **kwargs) -> str:
        """OpenAI聊天完成"""
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI API错误: {response.status} - {error_text}")
                        raise Exception(f"OpenAI API错误: {response.status}")
        except Exception as e:
            logger.error(f"OpenAI请求失败: {e}")
            raise
    
    async def health_check(self) -> bool:
        """OpenAI健康检查"""
        try:
            messages = [{"role": "user", "content": "Hello"}]
            await self.chat_completion(messages)
            return True
        except Exception as e:
            logger.warning(f"OpenAI健康检查失败: {e}")
            return False


class OpenAIEmbeddingClient(BaseEmbeddingClient):
    """OpenAI Embedding客户端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = config.get("api_base", "").rstrip("/")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "text-embedding-ada-002")
        self.embedding_dim = config.get("dim", 2560)

    async def create_embeddings(self, texts: List[str], **kwargs) -> List[List[float]]:
        """创建OpenAI文本嵌入向量"""
        url = f"{self.api_base}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "input": texts,
            **kwargs
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return [item["embedding"] for item in result["data"]]
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI Embedding API错误: {response.status} - {error_text}")
                        raise Exception(f"OpenAI Embedding API错误: {response.status}")
        except Exception as e:
            logger.error(f"OpenAI Embedding请求失败: {e}")
            raise

    async def health_check(self) -> bool:
        """OpenAI Embedding健康检查"""
        try:
            await self.create_embeddings(["Hello"])
            return True
        except Exception as e:
            logger.warning(f"OpenAI Embedding健康检查失败: {e}")
            return False


class OpenAIRerankClient(BaseRerankClient):
    """OpenAI Rerank客户端（使用Chat API模拟）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = config.get("api_base", "").rstrip("/")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "gpt-3.5-turbo")

    async def rerank(self, query: str, documents: List[str], **kwargs) -> List[Tuple[int, float]]:
        """使用OpenAI Chat API进行文档重排序"""
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # 构建重排序提示词
        docs_text = "\n".join([f"{i}: {doc}" for i, doc in enumerate(documents)])
        prompt = f"""请根据查询"{query}"对以下文档进行相关性排序，返回JSON格式的结果。

文档列表:
{docs_text}

请返回格式如下的JSON:
{{"rankings": [{{"index": 0, "score": 0.95}}, {{"index": 2, "score": 0.87}}, ...]}}

只返回最相关的{min(self.top_k, len(documents))}个文档，按相关性从高到低排序。"""

        messages = [{"role": "user", "content": prompt}]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 1000,
            **kwargs
        }

        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        content = result["choices"][0]["message"]["content"]

                        # 解析JSON响应
                        try:
                            # 清理响应格式
                            content_clean = content.strip()
                            if content_clean.startswith('```json'):
                                content_clean = content_clean[7:]
                            if content_clean.endswith('```'):
                                content_clean = content_clean[:-3]
                            content_clean = content_clean.strip()

                            parsed = json.loads(content_clean)
                            rankings = parsed.get("rankings", [])

                            # 转换为所需格式
                            result_rankings = []
                            for item in rankings:
                                idx = item.get("index", 0)
                                score = item.get("score", 0.0)
                                if 0 <= idx < len(documents):
                                    result_rankings.append((idx, score))

                            return result_rankings[:self.top_k]

                        except json.JSONDecodeError as e:
                            logger.warning(f"Rerank响应解析失败: {e}, 使用默认排序")
                            # 返回默认排序
                            return [(i, 1.0 - i * 0.1) for i in range(min(self.top_k, len(documents)))]
                    else:
                        error_text = await response.text()
                        logger.error(f"OpenAI Rerank API错误: {response.status} - {error_text}")
                        raise Exception(f"OpenAI Rerank API错误: {response.status}")
        except Exception as e:
            logger.error(f"OpenAI Rerank请求失败: {e}")
            raise

    async def health_check(self) -> bool:
        """OpenAI Rerank健康检查"""
        try:
            await self.rerank("test", ["document 1", "document 2"])
            return True
        except Exception as e:
            logger.warning(f"OpenAI Rerank健康检查失败: {e}")
            return False


class AzureOpenAIClient(BaseLLMClient):
    """Azure OpenAI客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = config.get("api_base", "").rstrip("/")
        self.api_key = config.get("api_key", "")
        self.api_version = config.get("api_version", "2023-12-01-preview")
        self.deployment_name = config.get("deployment_name", "gpt-35-turbo")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 2048)
    
    async def chat_completion(self, messages: list, **kwargs) -> str:
        """Azure OpenAI聊天完成"""
        url = f"{self.api_base}/openai/deployments/{self.deployment_name}/chat/completions"
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        params = {"api-version": self.api_version}
        
        payload = {
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, headers=headers, params=params, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"Azure OpenAI API错误: {response.status} - {error_text}")
                        raise Exception(f"Azure OpenAI API错误: {response.status}")
        except Exception as e:
            logger.error(f"Azure OpenAI请求失败: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Azure OpenAI健康检查"""
        try:
            messages = [{"role": "user", "content": "Hello"}]
            await self.chat_completion(messages)
            return True
        except Exception as e:
            logger.warning(f"Azure OpenAI健康检查失败: {e}")
            return False


class OllamaClient(BaseLLMClient):
    """Ollama客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = config.get("api_base", "http://localhost:11434").rstrip("/")
        self.model = config.get("model", "llama2")
        self.temperature = config.get("temperature", 0.1)
    
    async def chat_completion(self, messages: list, **kwargs) -> str:
        """Ollama聊天完成"""
        url = f"{self.api_base}/api/chat"
        
        # 转换消息格式
        prompt = self._messages_to_prompt(messages)
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature
            }
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "")
                    else:
                        error_text = await response.text()
                        logger.error(f"Ollama API错误: {response.status} - {error_text}")
                        raise Exception(f"Ollama API错误: {response.status}")
        except Exception as e:
            logger.error(f"Ollama请求失败: {e}")
            raise
    
    def _messages_to_prompt(self, messages: list) -> str:
        """将消息转换为提示词"""
        prompt_parts = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt_parts.append(f"System: {content}")
            elif role == "user":
                prompt_parts.append(f"User: {content}")
            elif role == "assistant":
                prompt_parts.append(f"Assistant: {content}")
        return "\n".join(prompt_parts) + "\nAssistant:"
    
    async def health_check(self) -> bool:
        """Ollama健康检查"""
        try:
            url = f"{self.api_base}/api/tags"
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(url) as response:
                    return response.status == 200
        except Exception as e:
            logger.warning(f"Ollama健康检查失败: {e}")
            return False


class CustomLLMClient(BaseLLMClient):
    """自定义LLM客户端"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_base = config.get("api_base", "").rstrip("/")
        self.api_key = config.get("api_key", "")
        self.model = config.get("model", "")
        self.headers = config.get("headers", {})
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 2048)
    
    async def chat_completion(self, messages: list, **kwargs) -> str:
        """自定义LLM聊天完成"""
        url = f"{self.api_base}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            **self.headers
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **kwargs
        }
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"自定义LLM API错误: {response.status} - {error_text}")
                        raise Exception(f"自定义LLM API错误: {response.status}")
        except Exception as e:
            logger.error(f"自定义LLM请求失败: {e}")
            raise
    
    async def health_check(self) -> bool:
        """自定义LLM健康检查"""
        try:
            messages = [{"role": "user", "content": "Hello"}]
            await self.chat_completion(messages)
            return True
        except Exception as e:
            logger.warning(f"自定义LLM健康检查失败: {e}")
            return False


class LLMClientFactory:
    """LLM客户端工厂"""

    @staticmethod
    def create_client() -> Optional[BaseLLMClient]:
        """创建LLM客户端"""
        if not settings.llm_enabled:
            return None

        provider = settings.llm_provider.lower()
        llm_config = get_llm_config()

        if provider == "openai":
            return OpenAIClient(llm_config)
        elif provider == "azure":
            return AzureOpenAIClient(llm_config)
        elif provider == "ollama":
            return OllamaClient(llm_config)
        elif provider == "custom":
            return CustomLLMClient(llm_config)
        else:
            logger.error(f"不支持的LLM提供商: {provider}")
            return None


class EmbeddingClientFactory:
    """Embedding客户端工厂"""

    @staticmethod
    def create_client() -> Optional[BaseEmbeddingClient]:
        """创建Embedding客户端"""
        if not settings.embedding_enabled:
            return None

        provider = settings.embedding_provider.lower()
        embedding_config = get_embedding_config()

        if provider == "openai":
            return OpenAIEmbeddingClient(embedding_config)
        elif provider == "azure":
            # Azure Embedding客户端可以后续添加
            logger.warning("Azure Embedding客户端暂未实现，使用OpenAI客户端")
            return OpenAIEmbeddingClient(embedding_config)
        elif provider == "custom":
            return OpenAIEmbeddingClient(embedding_config)
        else:
            logger.error(f"不支持的Embedding提供商: {provider}")
            return None


class RerankClientFactory:
    """Rerank客户端工厂"""

    @staticmethod
    def create_client() -> Optional[BaseRerankClient]:
        """创建Rerank客户端"""
        if not settings.rerank_enabled:
            return None

        provider = settings.rerank_provider.lower()
        rerank_config = get_rerank_config()

        if provider == "openai":
            return OpenAIRerankClient(rerank_config)
        elif provider == "azure":
            # Azure Rerank客户端可以后续添加
            logger.warning("Azure Rerank客户端暂未实现，使用OpenAI客户端")
            return OpenAIRerankClient(rerank_config)
        elif provider == "custom":
            return OpenAIRerankClient(rerank_config)
        else:
            logger.error(f"不支持的Rerank提供商: {provider}")
            return None


async def create_llm_function(**kwargs) -> Optional[callable]:
    """创建LLM函数"""
    client = LLMClientFactory.create_client()
    if not client:
        return None

    # 先进行健康检查
    try:
        if not await client.health_check():
            logger.warning("LLM客户端健康检查失败")
            return None
    except Exception as e:
        logger.warning(f"LLM客户端健康检查异常: {e}")
        return None

    async def llm_function(prompt: str) -> str:
        """LLM函数包装器"""
        messages = [{"role": "user", "content": prompt}]
        return await client.chat_completion(messages, **kwargs)

    return llm_function


async def create_embedding_function() -> Optional[callable]:
    """创建Embedding函数"""
    client = EmbeddingClientFactory.create_client()
    if not client:
        return None

    # 先进行健康检查
    try:
        if not await client.health_check():
            logger.warning("Embedding客户端健康检查失败")
            return None
    except Exception as e:
        logger.warning(f"Embedding客户端健康检查异常: {e}")
        return None

    async def embedding_function(texts: List[str], **kwargs) -> List[List[float]]:
        """Embedding函数包装器"""
        return await client.create_embeddings(texts, **kwargs)

    # 添加embedding_dim属性到函数对象
    embedding_function.embedding_dim = getattr(client, 'embedding_dim', 2560)

    return embedding_function


async def create_rerank_function() -> Optional[callable]:
    """创建Rerank函数"""
    client = RerankClientFactory.create_client()
    if not client:
        return None

    # 先进行健康检查
    try:
        if not await client.health_check():
            logger.warning("Rerank客户端健康检查失败")
            return None
    except Exception as e:
        logger.warning(f"Rerank客户端健康检查异常: {e}")
        return None

    async def rerank_function(query: str, documents: List[str]) -> List[Tuple[int, float]]:
        """Rerank函数包装器"""
        return await client.rerank(query, documents)

    return rerank_function


# 便捷的客户端获取函数
async def get_llm_client() -> Optional[BaseLLMClient]:
    """获取LLM客户端实例"""
    return LLMClientFactory.create_client()


async def get_embedding_client() -> Optional[BaseEmbeddingClient]:
    """获取Embedding客户端实例"""
    return EmbeddingClientFactory.create_client()


async def get_rerank_client() -> Optional[BaseRerankClient]:
    """获取Rerank客户端实例"""
    return RerankClientFactory.create_client()
