"""
意图识别服务配置
"""
import os
from typing import Optional
from pydantic import BaseModel, Field


class IntentRecognitionConfig(BaseModel):
    """意图识别服务配置"""
    
    # 服务配置
    host: str = Field(default="0.0.0.0", description="服务主机")
    port: int = Field(default=8003, description="服务端口")
    log_level: str = Field(default="INFO", description="日志级别")
    
    # LLM配置
    llm_enabled: bool = Field(default=False, description="是否启用LLM")
    llm_api_url: Optional[str] = Field(None, description="LLM API地址")
    llm_api_key: Optional[str] = Field(None, description="LLM API密钥")
    llm_model: str = Field(default="gpt-3.5-turbo", description="LLM模型名称")
    llm_timeout: int = Field(default=30, description="LLM请求超时时间")
    
    # 安全配置
    enable_safety_check: bool = Field(default=True, description="是否启用安全检查")
    enable_query_enhancement: bool = Field(default=True, description="是否启用查询增强")
    safety_threshold: float = Field(default=0.7, description="安全阈值")
    
    # 缓存配置
    enable_cache: bool = Field(default=True, description="是否启用缓存")
    cache_ttl: int = Field(default=3600, description="缓存TTL（秒）")
    
    class Config:
        env_prefix = "INTENT_"
        env_file = ".env"
    
    @classmethod
    def from_env(cls) -> "IntentRecognitionConfig":
        """从环境变量创建配置"""
        return cls(
            host=os.getenv("INTENT_HOST", "0.0.0.0"),
            port=int(os.getenv("INTENT_PORT", "8003")),
            log_level=os.getenv("INTENT_LOG_LEVEL", "INFO"),
            llm_enabled=os.getenv("INTENT_LLM_ENABLED", "false").lower() == "true",
            llm_api_url=os.getenv("INTENT_LLM_API_URL"),
            llm_api_key=os.getenv("INTENT_LLM_API_KEY"),
            llm_model=os.getenv("INTENT_LLM_MODEL", "gpt-3.5-turbo"),
            llm_timeout=int(os.getenv("INTENT_LLM_TIMEOUT", "30")),
            enable_safety_check=os.getenv("INTENT_ENABLE_SAFETY_CHECK", "true").lower() == "true",
            enable_query_enhancement=os.getenv("INTENT_ENABLE_QUERY_ENHANCEMENT", "true").lower() == "true",
            safety_threshold=float(os.getenv("INTENT_SAFETY_THRESHOLD", "0.7")),
            enable_cache=os.getenv("INTENT_ENABLE_CACHE", "true").lower() == "true",
            cache_ttl=int(os.getenv("INTENT_CACHE_TTL", "3600"))
        )
