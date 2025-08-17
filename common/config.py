"""
GuiXiaoXiRag FastAPI服务配置文件
优化版本 - 支持 .env 文件和环境变量配置
"""
import os
from pathlib import Path
from typing import Optional, List
try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
except ImportError:
    from pydantic import BaseSettings, Field


def get_project_root() -> Path:
    """获取项目根目录"""
    current_file = Path(__file__).resolve()
    # 从 server_new/common/config.py 向上三级到达项目根目录
    return current_file.parent.parent.parent


def find_env_file() -> Optional[Path]:
    """查找 .env 文件，按优先级顺序查找"""
    project_root = get_project_root()
    possible_locations = [
        project_root / ".env",
        project_root / ".env.local",
        # project_root / "server_new" / ".env",
        Path.cwd() / ".env"
    ]

    for env_file in possible_locations:
        if env_file.exists():
            return env_file

    return None


class Settings(BaseSettings):
    """应用配置 - 支持从 .env 文件和环境变量读取"""

    # 应用信息
    app_name: str = Field(default="GuiXiaoXiRag FastAPI Service", description="应用名称")
    app_version: str = Field(default="2.0.0", description="应用版本")

    # 服务配置
    host: str = Field(default="0.0.0.0", description="服务器主机地址")
    port: int = Field(default=8002, description="服务器端口")
    debug: bool = Field(default=False, description="调试模式")
    workers: int = Field(default=1, description="工作进程数")

    # GuiXiaoXiRag配置
    working_dir: str = Field(default="./knowledgeBase/default", description="知识库工作目录")

    # 大模型配置 - 支持用户自定义，未配置时使用默认值
    openai_api_base: str = Field(default="http://localhost:8100/v1", description="OpenAI API 基础URL")
    openai_embedding_api_base: str = Field(default="http://localhost:8200/v1", description="OpenAI Embedding API 基础URL")
    openai_chat_api_key: str = Field(default="your_api_key_here", description="OpenAI Chat API 密钥")
    openai_embedding_api_key: str = Field(default="your_api_key_here", description="OpenAI Embedding API 密钥")
    openai_chat_model: str = Field(default="qwen14b", description="OpenAI Chat 模型")
    openai_embedding_model: str = Field(default="embedding_qwen", description="OpenAI Embedding 模型")

    # LLM意图识别配置
    llm_enabled: bool = Field(default=True, description="启用LLM意图识别")
    llm_provider: str = Field(default="openai", description="LLM提供商: openai, azure, ollama, custom")
    llm_temperature: float = Field(default=0.1, description="LLM温度参数")
    llm_max_tokens: int = Field(default=2048, description="LLM最大token数")
    llm_timeout: int = Field(default=30, description="LLM请求超时时间(秒)")

    # Embedding配置
    embedding_enabled: bool = Field(default=True, description="启用Embedding服务")
    embedding_provider: str = Field(default="openai", description="Embedding提供商: openai, azure, ollama, custom")
    embedding_timeout: int = Field(default=30, description="Embedding请求超时时间(秒)")

    # Rerank配置
    rerank_enabled: bool = Field(default=False, description="启用Rerank服务")
    rerank_provider: str = Field(default="openai", description="Rerank提供商: openai, azure, custom")
    rerank_model: str = Field(default="rerank-multilingual-v3.0", description="Rerank模型")
    rerank_timeout: int = Field(default=30, description="Rerank请求超时时间(秒)")
    rerank_top_k: int = Field(default=10, description="Rerank返回的top-k结果数量")

    # 可选的自定义配置
    custom_llm_provider: Optional[str] = Field(default=None, description="自定义LLM提供商")
    custom_embedding_provider: Optional[str] = Field(default=None, description="自定义Embedding提供商")
    azure_api_version: Optional[str] = Field(default="2023-12-01-preview", description="Azure API版本")
    azure_deployment_name: Optional[str] = Field(default="gpt-35-turbo", description="Azure部署名称")

    # Ollama 配置
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama 基础URL")
    ollama_chat_model: str = Field(default="llama2", description="Ollama Chat 模型")
    ollama_embedding_model: Optional[str] = Field(default=None, description="Ollama Embedding 模型")

    # Embedding配置
    embedding_dim: int = Field(default=2560, description="向量维度")
    max_token_size: int = Field(default=8192, description="最大token数量")

    # 日志配置
    log_level: str = Field(default="INFO", description="日志级别")
    log_dir: str = Field(default="./logs", description="日志目录")

    # 文件上传配置
    max_file_size: int = Field(default=50 * 1024 * 1024, description="最大文件大小(字节)")
    allowed_file_types: List[str] = Field(
        default=[".txt", ".pdf", ".docx", ".doc", ".md", ".json", ".xml", ".csv"],
        description="允许的文件类型"
    )
    upload_dir: str = Field(default="./uploads", description="上传目录")

    # Streamlit配置
    streamlit_host: str = Field(default="0.0.0.0", description="Streamlit主机地址")
    streamlit_port: int = Field(default=8501, description="Streamlit端口")
    streamlit_api_url: str = Field(default="http://localhost:8002", description="Streamlit API URL")
    streamlit_timeout: int = Field(default=120, description="Streamlit超时时间")

    # 性能配置
    enable_cache: bool = Field(default=True, description="启用缓存")
    cache_ttl: int = Field(default=3600, description="缓存TTL(秒)")
    max_concurrent_requests: int = Field(default=100, description="最大并发请求数")

    # 安全配置
    cors_origins: List[str] = Field(default=["*"], description="CORS允许的源")
    cors_methods: List[str] = Field(default=["*"], description="CORS允许的方法")
    cors_headers: List[str] = Field(default=["*"], description="CORS允许的头部")

    class Config:
        # 动态查找 .env 文件
        env_file = find_env_file()
        env_file_encoding = "utf-8"
        case_sensitive = False
        # 忽略额外的字段，避免验证错误
        extra = "ignore"
        # 支持从多个位置读取环境文件
        env_files = [
            get_project_root() / ".env",
            get_project_root() / ".env.local",
            # get_project_root() / "server_new" / ".env",
            Path.cwd() / ".env"
        ]


# 全局配置实例
def create_settings() -> Settings:
    """创建配置实例并显示加载信息"""
    env_file = find_env_file()
    if env_file:
        print(f"✅ 找到配置文件: {env_file}")
    else:
        print("⚠️  未找到 .env 文件，使用默认配置")
        print(f"💡 建议在项目根目录 {get_project_root()} 创建 .env 文件")

    return Settings()

settings = create_settings()


def ensure_directories():
    """确保必要的目录存在"""
    directories = [
        settings.working_dir,
        settings.log_dir,
        settings.upload_dir,
        Path(settings.working_dir).parent,  # knowledgeBase目录
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def validate_config():
    """验证配置的有效性"""
    errors = []
    warnings = []

    # 验证端口范围
    if not (1 <= settings.port <= 65535):
        errors.append(f"端口号无效: {settings.port}")

    if not (1 <= settings.streamlit_port <= 65535):
        errors.append(f"Streamlit端口号无效: {settings.streamlit_port}")

    # 智能验证API配置
    if settings.openai_chat_api_key == "your_api_key_here":
        warnings.append("使用默认LLM API密钥，请在生产环境中设置有效的API密钥")

    if settings.openai_embedding_api_key == "your_api_key_here":
        warnings.append("使用默认Embedding API密钥，请在生产环境中设置有效的API密钥")

    # 验证API基础URL格式
    if not settings.openai_api_base.startswith(('http://', 'https://')):
        errors.append(f"LLM API基础URL格式无效: {settings.openai_api_base}")

    if not settings.openai_embedding_api_base.startswith(('http://', 'https://')):
        errors.append(f"Embedding API基础URL格式无效: {settings.openai_embedding_api_base}")

    # 验证目录路径
    try:
        Path(settings.working_dir).resolve()
        Path(settings.log_dir).resolve()
        Path(settings.upload_dir).resolve()
    except Exception as e:
        errors.append(f"目录路径无效: {e}")

    # 验证文件大小
    if settings.max_file_size <= 0:
        errors.append("文件大小限制必须大于0")

    # 输出验证结果
    if warnings:
        print("⚠️  配置警告:")
        for warning in warnings:
            print(f"   - {warning}")

    if errors:
        print("❌ 配置错误:")
        for error in errors:
            print(f"   - {error}")

    return len(errors) == 0


def get_effective_config():
    """获取有效的配置信息，处理用户自定义和默认值"""
    config = {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "host": settings.host,
        "port": settings.port,
        "debug": settings.debug,
        "working_dir": settings.working_dir,
        "log_level": settings.log_level,

        # LLM配置
        "llm": {
            "api_base": settings.openai_api_base,
            "api_key": "***" if settings.openai_chat_api_key != "your_api_key_here" else "未配置",
            "model": settings.openai_chat_model,
            "provider": settings.custom_llm_provider or "openai",
        },

        # Embedding配置
        "embedding": {
            "api_base": settings.openai_embedding_api_base,
            "api_key": "***" if settings.openai_embedding_api_key != "your_api_key_here" else "未配置",
            "model": settings.openai_embedding_model,
            "dim": settings.embedding_dim,
            "provider": settings.custom_embedding_provider or "openai",
        },

        # 其他配置
        "max_file_size_mb": settings.max_file_size // (1024 * 1024),
        "streamlit_port": settings.streamlit_port,
        "max_token_size": settings.max_token_size,
    }

    # 添加Azure特定配置（如果配置了）
    if settings.azure_api_version:
        config["azure"] = {
            "api_version": settings.azure_api_version,
            "deployment_name": settings.azure_deployment_name,
        }

    return config


def get_llm_config():
    """获取LLM配置"""
    provider = settings.llm_provider.lower()

    base_config = {
        "temperature": settings.llm_temperature,
        "max_tokens": settings.llm_max_tokens,
        "timeout": settings.llm_timeout,
    }

    if provider == "openai":
        return {
            **base_config,
            "api_base": settings.openai_api_base,
            "api_key": settings.openai_chat_api_key,
            "model": settings.openai_chat_model,
        }
    elif provider == "azure":
        return {
            **base_config,
            "api_base": settings.openai_api_base,
            "api_key": settings.openai_chat_api_key,
            "api_version": settings.azure_api_version,
            "deployment_name": settings.azure_deployment_name,
        }
    elif provider == "ollama":
        return {
            **base_config,
            "api_base": settings.ollama_base_url,
            "model": settings.ollama_chat_model,
        }
    elif provider == "custom":
        return {
            **base_config,
            "api_base": settings.openai_api_base,
            "api_key": settings.openai_chat_api_key,
            "model": settings.openai_chat_model,
        }
    else:
        return base_config


def get_embedding_config():
    """获取Embedding配置"""
    provider = settings.embedding_provider.lower()

    base_config = {
        "timeout": settings.embedding_timeout,
    }

    if provider == "openai":
        return {
            **base_config,
            "api_base": settings.openai_embedding_api_base,
            "api_key": settings.openai_embedding_api_key,
            "model": settings.openai_embedding_model,
        }
    elif provider == "azure":
        return {
            **base_config,
            "api_base": settings.openai_embedding_api_base,
            "api_key": settings.openai_embedding_api_key,
            "api_version": settings.azure_api_version,
            "deployment_name": settings.openai_embedding_model,
        }
    elif provider == "ollama":
        return {
            **base_config,
            "api_base": settings.ollama_base_url,
            "model": settings.ollama_embedding_model or "nomic-embed-text",
        }
    elif provider == "custom":
        return {
            **base_config,
            "api_base": settings.openai_embedding_api_base,
            "api_key": settings.openai_embedding_api_key,
            "model": settings.openai_embedding_model,
        }
    else:
        return base_config


def get_rerank_config():
    """获取Rerank配置"""
    provider = settings.rerank_provider.lower()

    base_config = {
        "timeout": settings.rerank_timeout,
        "top_k": settings.rerank_top_k,
    }

    if provider == "openai":
        return {
            **base_config,
            "api_base": settings.openai_api_base,
            "api_key": settings.openai_chat_api_key,
            "model": settings.rerank_model,
        }
    elif provider == "azure":
        return {
            **base_config,
            "api_base": settings.openai_api_base,
            "api_key": settings.openai_chat_api_key,
            "api_version": settings.azure_api_version,
            "deployment_name": settings.rerank_model,
        }
    elif provider == "custom":
        return {
            **base_config,
            "api_base": settings.openai_api_base,
            "api_key": settings.openai_chat_api_key,
            "model": settings.rerank_model,
        }
    else:
        return base_config


def get_config_summary():
    """获取配置摘要信息"""
    effective_config = get_effective_config()
    return {
        "app_name": effective_config["app_name"],
        "version": effective_config["version"],
        "host": effective_config["host"],
        "port": effective_config["port"],
        "debug": effective_config["debug"],
        "working_dir": effective_config["working_dir"],
        "log_level": effective_config["log_level"],
        "openai_chat_model": effective_config["llm"]["model"],
        "openai_embedding_model": effective_config["embedding"]["model"],
        "embedding_dim": effective_config["embedding"]["dim"],
        "max_file_size_mb": effective_config["max_file_size_mb"],
        "streamlit_port": effective_config["streamlit_port"],
        "llm_enabled": settings.llm_enabled,
        "llm_provider": settings.llm_provider,
    }


# 初始化目录
ensure_directories()

# 导出常用配置
__all__ = [
    "settings",
    "ensure_directories",
    "validate_config",
    "get_config_summary",
    "get_effective_config",
    "get_llm_config",
    "get_embedding_config",
    "get_rerank_config",
    "get_project_root"
]
