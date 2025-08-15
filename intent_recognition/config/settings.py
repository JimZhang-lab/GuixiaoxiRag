"""
意图识别服务配置管理
"""
import os
import yaml
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ServiceConfig(BaseModel):
    """服务配置"""
    name: str = Field(default="意图识别服务")
    version: str = Field(default="1.0.0")
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8003)
    debug: bool = Field(default=False)


class LoggingConfig(BaseModel):
    """日志配置"""
    level: str = Field(default="INFO")
    file: str = Field(default="intent_recognition.log")


class LLMConfig(BaseModel):
    """大模型配置"""
    enabled: bool = Field(default=False)
    provider: str = Field(default="openai")  # openai, azure, ollama, custom
    providers: Dict[str, Dict[str, Any]] = Field(default_factory=dict)


class SafetyConfig(BaseModel):
    """安全检查配置"""
    enabled: bool = Field(default=True)
    sensitive_vocabulary_file: str = Field(default="sensitive_vocabulary")
    dfa: Dict[str, Any] = Field(default_factory=dict)


class IntentConfig(BaseModel):
    """意图识别配置"""
    confidence_threshold: float = Field(default=0.7)
    enhancement: Dict[str, Any] = Field(default_factory=dict)


class MicroserviceConfig(BaseModel):
    """微服务配置"""
    enabled: bool = Field(default=False)
    registry: Dict[str, Any] = Field(default_factory=dict)
    discovery: Dict[str, Any] = Field(default_factory=dict)
    load_balancer: Dict[str, Any] = Field(default_factory=dict)


class CacheConfig(BaseModel):
    """缓存配置"""
    enabled: bool = Field(default=True)
    type: str = Field(default="memory")
    ttl: int = Field(default=3600)
    max_size: int = Field(default=1000)
    redis: Dict[str, Any] = Field(default_factory=dict)


class PerformanceConfig(BaseModel):
    """性能配置"""
    max_concurrent_requests: int = Field(default=100)
    request_timeout: int = Field(default=30)
    enable_metrics: bool = Field(default=True)
    rate_limit: Dict[str, Any] = Field(default_factory=dict)


class APIConfig(BaseModel):
    """API配置"""
    cors: Dict[str, Any] = Field(default_factory=dict)
    docs: Dict[str, Any] = Field(default_factory=dict)


class MonitoringConfig(BaseModel):
    """监控配置"""
    health_check: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    logging: Dict[str, Any] = Field(default_factory=dict)
    alerts: Dict[str, Any] = Field(default_factory=dict)


class Config(BaseModel):
    """完整配置"""
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    safety: SafetyConfig = Field(default_factory=SafetyConfig)
    intent: IntentConfig = Field(default_factory=IntentConfig)
    microservice: MicroserviceConfig = Field(default_factory=MicroserviceConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig)
    api: APIConfig = Field(default_factory=APIConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    @classmethod
    def load_from_yaml(cls, config_path: str = None) -> "Config":
        """从YAML文件加载配置"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.yaml"

        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)

            # 环境变量覆盖
            config_data = cls._apply_env_overrides(config_data)

            return cls(**config_data)
        except Exception as e:
            logger.warning(f"加载配置文件失败: {e}，使用默认配置")
            return cls()

    @staticmethod
    def _apply_env_overrides(config_data: Dict[str, Any]) -> Dict[str, Any]:
        """应用环境变量覆盖"""
        # 服务配置覆盖
        if "INTENT_HOST" in os.environ:
            config_data.setdefault("service", {})["host"] = os.environ["INTENT_HOST"]
        if "INTENT_PORT" in os.environ:
            config_data.setdefault("service", {})["port"] = int(os.environ["INTENT_PORT"])
        if "INTENT_DEBUG" in os.environ:
            config_data.setdefault("service", {})["debug"] = os.environ["INTENT_DEBUG"].lower() == "true"

        # LLM配置覆盖
        if "INTENT_LLM_ENABLED" in os.environ:
            config_data.setdefault("llm", {})["enabled"] = os.environ["INTENT_LLM_ENABLED"].lower() == "true"
        if "INTENT_LLM_PROVIDER" in os.environ:
            config_data.setdefault("llm", {})["provider"] = os.environ["INTENT_LLM_PROVIDER"]

        # OpenAI配置覆盖
        if "INTENT_OPENAI_API_BASE" in os.environ:
            config_data.setdefault("llm", {}).setdefault("openai", {})["api_base"] = os.environ["INTENT_OPENAI_API_BASE"]
        if "INTENT_OPENAI_API_KEY" in os.environ:
            config_data.setdefault("llm", {}).setdefault("openai", {})["api_key"] = os.environ["INTENT_OPENAI_API_KEY"]
        if "INTENT_OPENAI_MODEL" in os.environ:
            config_data.setdefault("llm", {}).setdefault("openai", {})["model"] = os.environ["INTENT_OPENAI_MODEL"]

        return config_data

    def get_llm_config(self) -> Dict[str, Any]:
        """获取当前LLM提供商的配置"""
        provider = self.llm.provider.lower()
        return self.llm.providers.get(provider, {})

    def is_microservice_mode(self) -> bool:
        """是否为微服务模式"""
        return self.microservice.enabled


# 向后兼容的别名
IntentRecognitionConfig = Config
