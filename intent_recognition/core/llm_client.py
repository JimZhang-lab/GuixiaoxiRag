"""
大模型客户端
"""
import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import aiohttp
from config.settings import Config

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


class OpenAIClient(BaseLLMClient):
    """OpenAI客户端"""
    
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
    def create_client(config: Config) -> Optional[BaseLLMClient]:
        """创建LLM客户端"""
        if not config.llm.enabled:
            return None
        
        provider = config.llm.provider.lower()
        llm_config = config.get_llm_config()
        
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


async def create_llm_function(config: Config) -> Optional[callable]:
    """创建LLM函数"""
    client = LLMClientFactory.create_client(config)
    if not client:
        return None
    
    async def llm_function(prompt: str) -> str:
        """LLM函数包装器"""
        messages = [{"role": "user", "content": prompt}]
        return await client.chat_completion(messages)
    
    return llm_function
